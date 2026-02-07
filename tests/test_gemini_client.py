import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from schemas.warm_messages import AIWarmMessageLists
from ai.gemini_client import GeminiClient


@pytest.mark.asyncio
async def test_generate_warm_message_success():
    # 1. Mock Gemini return response structure
    mock_response = MagicMock()
    # mock JSON string
    mock_response.text = """
    {
        "group_id": null,
        "alternatives": [
            {
                "warm_message": "That sounds peaceful. Take a deep breath.",
                "tags": ["calm", "grounding"]
            }
        ]
    }
    """

    # 2. using patch mock genai.Client to generate_content
    with patch("google.genai.Client") as mock_genai_client:
        # 预设 mock 行为
        instance = mock_genai_client.return_value
        instance.models.generate_content.return_value = mock_response

        # initialization
        client = GeminiClient()

        # 3. execute generate method
        journal_text = "I went for a walk in the park today."
        result = await client.generate_warm_message(journal_text)

        # 4. verification
        assert isinstance(result, AIWarmMessageLists)
        assert len(result.alternatives) == 1
        assert result.alternatives[0].tags == ["calm", "grounding"]
        assert result.message_id is None
        assert result.generated_at is not None
        assert result.generated_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_generate_warm_message_empty_input():
    client = GeminiClient()
    with pytest.raises(ValueError, match="journal_content cannot be empty"):
        await client.generate_warm_message("")