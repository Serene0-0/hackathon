from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from deps import get_db, get_current_user_demo
from models.user import User
from models.emergency_contact import EmergencyContact as EmergencyContactModel
from models.checkin_settings import (CheckinReminder as CheckinReminderModel,
                                     MissCheckinRule as MissCheckinRuleModel,
                                     PauseStatus as PauseStatusModel,
                                     FrequencyType as FrequencyTypeModel)
from schemas.emergency_contact import (
    EmergencyContactUpsert,
    EmergencyContact as EmergencyContactSchema,
    ApiResponseEmergencyContact,
)
from schemas.checkin_settings import (CheckinReminder, CheckinFrequencyType, CheckinReminderUpdate,
                                      ApiResponseCheckinReminder, MissCheckinRule, MissCheckinRuleUpdate,
                                      ApiResponseMissCheckinRule, PauseStatus, PauseStatusUpdate, ApiResponsePauseStatus)


router = APIRouter(tags=["Safety"])

DEFAULT_TEMPLATE = (
    "Hi, this is Lumenary. We haven't heard from {username} in {interval_days} days. "
    "Please consider reaching out to them to make sure they’re okay."
)

# ======= Emergency Contact =========
@router.get("/users/me/emergency-contact", response_model=ApiResponseEmergencyContact)
async def get_emergency_contact(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo),
):
    stmt = select(EmergencyContactModel).where(EmergencyContactModel.user_id == user.user_id)
    contact = (await db.execute(stmt)).scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not set")

    data = EmergencyContactSchema (
        contact_id=contact.contact_id,
        name=contact.name,
        email=contact.email,
        relationship=contact.contact_relationship,
    )

    return ApiResponseEmergencyContact (data=data, message="OK")


@router.put("/users/me/emergency-contact", response_model=ApiResponseEmergencyContact)
async def upsert_emergency_contact(
        payload: EmergencyContactUpsert,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo),
):
    stmt = select(EmergencyContactModel).where(EmergencyContactModel.user_id == user.user_id)
    contact = (await db.execute(stmt)).scalar_one_or_none()

    if contact:
        contact.name = payload.name
        contact.email = payload.email
        contact.contact_relationship = payload.relationship
    else:
        contact = EmergencyContactModel(
            user_id=user.user_id,
            name=payload.name,
            email=payload.email,
            contact_relationship=payload.relationship,
        )
        db.add(contact)

    await db.commit()
    await db.refresh(contact)

    data = EmergencyContactSchema(
        contact_id=UUID(str(contact.contact_id)),
        name=str(contact.name),
        email=str(contact.email),
        relationship=None if contact.contact_relationship is None else str(contact.contact_relationship),
    )

    return ApiResponseEmergencyContact (data=data, message="OK")

# ======= Check in Reminder =========
@router.get("/users/me/checkin-reminder", response_model=ApiResponseCheckinReminder)
async def get_checkin_reminder(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo)
):
    stmt = select(CheckinReminderModel).where(CheckinReminderModel.user_id == user.user_id)
    reminder = (await db.execute(stmt)).scalar_one_or_none()

    if not reminder:
        reminder = CheckinReminderModel(user_id=user.user_id)
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)

    data = CheckinReminder(
        enabled=bool(reminder.enabled),
        time_local=str(reminder.time_local),
        frequency_type=CheckinFrequencyType(
            str(reminder.frequency_type.value) if hasattr(reminder.frequency_type, "value") else str(reminder.frequency_type)),
        interval_days=None if reminder.interval_days is None else reminder.interval_days
    )

    return ApiResponseCheckinReminder (data=data, message="OK")


@router.put("/users/me/checkin-reminder", response_model=ApiResponseCheckinReminder)
async def get_checkin_reminder(
        payload: CheckinReminderUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo)
):
    stmt = select(CheckinReminderModel).where(CheckinReminderModel.user_id == user.user_id)
    reminder = (await db.execute(stmt)).scalar_one_or_none()

    if not reminder:
        reminder = CheckinReminderModel(user_id=user.user_id)
        db.add(reminder)

    reminder.enabled = payload.enabled
    reminder.time_local = payload.time_local

    freq_val = payload.frequency_type.value if hasattr(payload.frequency_type, "value") else str(payload.frequency_type)
    if freq_val == "daily":
        reminder.frequency_type = FrequencyTypeModel.DAILY
    elif freq_val == "every_n_days":
        reminder.frequency_type = FrequencyTypeModel.EVERY_N_DAYS
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid frequency_type")

    reminder.interval_days = payload.interval_days

    await db.commit()
    await db.refresh(reminder)

    data = CheckinReminder(
        enabled=bool(reminder.enabled),
        time_local=str(reminder.time_local),
        frequency_type=CheckinFrequencyType(freq_val),
        interval_days=None if reminder.interval_days is None else reminder.interval_days
    )

    return ApiResponseCheckinReminder (data=data, message="OK")


# ======= Miss Check-in Rule =========
@router.get("/users/me/miss-checkin-rule", response_model=ApiResponseMissCheckinRule)
async def get_miss_checkin_rule(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo)
):
    stmt = select(MissCheckinRuleModel).where(MissCheckinRuleModel.user_id == user.user_id)
    obj = (await db.execute(stmt)).scalar_one_or_none()

    if not obj:
        obj = MissCheckinRuleModel(user_id=user.user_id)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

    data = MissCheckinRule.model_validate(obj)

    return ApiResponseMissCheckinRule (data=data, message="OK")


@router.put("/users/me/miss-checkin-rule", response_model=ApiResponseMissCheckinRule)
async def update_miss_checkin_rule(
        payload: MissCheckinRuleUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo)
):
    stmt = select(MissCheckinRuleModel).where(MissCheckinRuleModel.user_id == user.user_id)
    obj = (await db.execute(stmt)).scalar_one_or_none()

    if not obj:
        obj = MissCheckinRuleModel(user_id=user.user_id)
        db.add(obj)

    obj.threshold_days = payload.threshold_days

    if hasattr(payload, "message_template"):
        if payload.message_template is not None:
            obj.message_template = payload.message_template

    await db.commit()
    await db.refresh(obj)

    data = MissCheckinRule.model_validate(obj)
    return ApiResponseMissCheckinRule (data=data, message="OK")


# ======= Pause Check-in =========
@router.get("/users/me/pause-checkin", response_model=ApiResponsePauseStatus)
async def get_pause_status(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo)
):
    stmt = select(PauseStatusModel).where(PauseStatusModel.user_id == user.user_id)
    obj = (await db.execute(stmt)).scalar_one_or_none()

    if not obj:
        obj = PauseStatusModel(user_id=user.user_id)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

    data = PauseStatus.model_validate(obj)
    return ApiResponsePauseStatus (data=data, message="OK")


@router.post("/users/me/pause-checkin", response_model=ApiResponsePauseStatus)
async def set_pause_status(
        payload: PauseStatusUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo)
):
    stmt = select(PauseStatusModel).where(PauseStatusModel.user_id == user.user_id)
    obj = (await db.execute(stmt)).scalar_one_or_none()

    if not obj:
        obj = PauseStatusModel(user_id=user.user_id)
        db.add(obj)

    obj.paused = payload.paused
    obj.paused_at = datetime.utcnow() if payload.paused else None
    await db.commit()
    await db.refresh(obj)

    data = PauseStatus.model_validate(obj)
    return ApiResponsePauseStatus (data=data, message="OK")