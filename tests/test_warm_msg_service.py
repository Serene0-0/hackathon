import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from schemas.warm_messages import AIWarmMessageLists, AIWarmMessage
from models.journal import Journal

from services.warm_msg_service import get_or_generate_warm_message_for_journal

@pytest.fixture
def mock_db_session():
    """Mock async database session"""
    return AsyncMock()

@pytest.mark.asyncio
async def test_get_or_generate_warm_message_new(mock_db_session, mocker):
    """
    Test Scene：no record in db，using Gemini to generate warm message
    """
    # 1. mock data
    journal_id = uuid4()
    test_journal = Journal(
        journal_id=journal_id,
        content="Feeling tired.",
        user_id=uuid4()
    )

    # mock gemini return result
    raw_text = """
        {
            "group_id": null,
            "alternatives": [
                {"warm_message": "It is okay to feel worn out after a long day. Rest your body now.", "tags": ["calm", "support"]},
                {"warm_message": "Recognizing your fatigue is the first step toward recovery. Try a gentle stretch.", "tags": ["empathy", "grounding"]},
                {"warm_message": "You have worked hard and deserve some quiet time. Breathe deeply.", "tags": ["encouragement", "calm"]}
            ],
            "generated_at": null
        }
        """
    mock_ai_response = AIWarmMessageLists.model_validate_json(raw_text)
    mock_ai_response.generated_at = datetime.now(timezone.utc)

    # 2. Mock GeminiClient
    mock_gemini = MagicMock()
    # using AsyncMock
    mock_gemini.generate_warm_message = AsyncMock(return_value=mock_ai_response)

    # 3. Mock db func
    #  mock load_warm_message_group return None，to generate
    mocker.patch("services.warm_msg_service.load_warm_message_group", return_value=None)
    mocker.patch("services.warm_msg_service.save_warm_message_lists", side_effect=lambda db, jid, ai: ai)

    # 4. execute func
    result = await get_or_generate_warm_message_for_journal(
        db=mock_db_session,
        journal=test_journal,
        gemini=mock_gemini
    )

    # 5. assertion
    assert len(result.alternatives) == 3
    assert result.alternatives[0].tags == ["calm", "support"]
    assert hasattr(result, "message_id")
    print(str(result.alternatives[0].warm_message))


@pytest.mark.asyncio
async def test_get_or_generate_warm_message_cached(mock_db_session, mocker):
    """
    test cache in db
    """
    journal_id = uuid4()
    test_journal = Journal(journal_id=journal_id, content="Test Content")

    # mock existing record in db
    mock_existing_group = MagicMock()
    mock_existing_group.group_id = uuid4()

    # Mock return existing record in db
    mocker.patch("services.warm_msg_service.load_warm_message_group", return_value=mock_existing_group)

    # Mock schema
    mock_result = AIWarmMessageLists(
        message_id=mock_existing_group.group_id,
        alternatives=[AIWarmMessage(warm_message="Test test test", tags=[])],
        generated_at=datetime.now(timezone.utc)
    )
    mocker.patch("services.warm_msg_service.build_ai_lists_from_group", return_value=mock_result)

    mock_gemini = MagicMock()
    mock_gemini.generate_warm_message = AsyncMock()

    result = await get_or_generate_warm_message_for_journal(
        db=mock_db_session,
        journal=test_journal,
        gemini=mock_gemini
    )

    assert result.message_id == mock_existing_group.group_id
    assert result.alternatives[0].warm_message == "Test test test"

    mock_gemini.generate_warm_message.assert_not_called()