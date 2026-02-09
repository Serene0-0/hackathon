from collections import defaultdict
from datetime import timezone, datetime

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ai.gemini_client import GeminiClient
from models.journal import Journal
from models.warm_message import WarmMessageGroup, WarmMessage, warm_msg_tags
from schemas.warm_messages import AIWarmMessageLists

async def load_warm_message_group(
    db: AsyncSession,
    journal_id,
) -> WarmMessageGroup | None:
    stmt = (select(WarmMessageGroup)
            .where(WarmMessageGroup.journal_id == journal_id)
            .options(selectinload(WarmMessageGroup.alternatives)))
    return (await db.execute(stmt)).scalar_one_or_none()


async def build_ai_lists_from_group(db: AsyncSession,group: WarmMessageGroup) -> AIWarmMessageLists:
    # 1) collect alternative message_ids
    msg_ids = [m.message_id for m in (group.alternatives or [])]
    tags_map: dict = defaultdict(list)

    # 2) query tags for these messages
    if msg_ids:
        stmt = select(warm_msg_tags.c.message_id, warm_msg_tags.c.tag).where(
            warm_msg_tags.c.message_id.in_(msg_ids)
        )
        rows = (await db.execute(stmt)).all()  # list[tuple[UUID, WarmMessageTags/str]]

        for mid, tag in rows:
            tags_map[mid].append(tag)

    # 3) build alternatives
    alternatives = []
    for m in group.alternatives or []:
        alternatives.append(
            {
                "warm_message": m.content,
                "tags": tags_map.get(m.message_id, []),
            }
        )

    # 4) return schema (schema field is message_id, ORM is group_id via alias)
    return AIWarmMessageLists(
        message_id=group.group_id,          # schema will map to message_id via alias
        alternatives=alternatives,
        generated_at=group.generated_at,
    )


async def save_warm_message_lists(db: AsyncSession,
    journal_id,
    ai: AIWarmMessageLists,
) -> AIWarmMessageLists:
    group = WarmMessageGroup(journal_id = journal_id,
                             generated_at=ai.generated_at or datetime.now(timezone.utc))
    db.add(group)
    await db.flush()

    tag_rows = []

    for alt in ai.alternatives:
        msg = WarmMessage(
            journal_id=journal_id,
            group_id=group.group_id,
            content=alt.warm_message,
        )
        db.add(msg)
        await db.flush()  # get msg.message_id

        for t in (alt.tags or []):
            tag_rows.append({"message_id": msg.message_id, "tag": t})

    # insert tags
    if tag_rows:
        await db.execute(insert(warm_msg_tags).values(tag_rows))

    await db.commit()
    await db.refresh(group)

    ai.message_id = group.group_id

    return ai


async def get_or_generate_warm_message_for_journal(
    db: AsyncSession,
    journal: Journal,
    gemini: GeminiClient,
) -> AIWarmMessageLists:

    existing = await load_warm_message_group(db, journal.journal_id)
    if existing:
        return await build_ai_lists_from_group(db, existing)

    ai = await gemini.generate_warm_message(journal.content)
    return await save_warm_message_lists(db, journal.journal_id, ai)