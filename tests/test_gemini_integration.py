import os
import pytest
from ai.gemini_client import GeminiClient
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_minimal_token_usage():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")

    client = GeminiClient()
    test_input = "Feeling tired."

    result, dbg = await client.generate_warm_message(test_input, debug=True)

    print("\n--- Gemini debug ---")
    print("model:", dbg["model"])
    print("usage:", dbg["usage"])
    print("raw_text:", dbg["raw_text"])

    assert dbg["has_raw_text"] is True
    assert isinstance(dbg["raw_text"], str)
    assert len(dbg["raw_text"]) > 20

    assert result.message_id is None
    assert len(result.alternatives) == 3
    assert result.generated_at is not None
    assert all(a.warm_message and a.warm_message.strip() for a in result.alternatives)

    if dbg["usage"] is not None:

        d = dbg["usage"]

        maybe_total = getattr(d, "total_token_count", None) or (d.get("total_token_count") if isinstance(d, dict) else None)
        if maybe_total is not None:
            assert maybe_total > 0
