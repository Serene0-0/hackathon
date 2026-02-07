"""
Gemini AI Client for generating warm messages
"""
import asyncio
import random
from datetime import datetime, timezone
import json
from google import genai
from google.genai import types
from typing import List, Dict, Any

from core.config import settings
from .prompt import WARM_MESSAGE_SYSTEM_PROMPT, build_user_prompt
from schemas.warm_messages import AIWarmMessageLists, AIWarmMessage, WarmMessageTags

class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError (
                "GEMINI_API_KEY not configured. "
                "Please set it in .env file."
            )

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL.replace("models/", "")

    def _is_retryable(self, e: Exception) -> bool:
        # SDK/HTTP errors often include code/message in str(e)
        msg = str(e).lower()
        return (
            "503" in msg or "unavailable" in msg or "overloaded" in msg or
            "429" in msg or "rate" in msg or
            "500" in msg or "internal" in msg
        )

    async def generate_warm_message(self, journal_content: str, *, max_retries: int = 5, debug: bool = False):
        if not journal_content or not journal_content.strip():
            raise ValueError("journal_content cannot be empty")

        user_prompt = build_user_prompt(journal_content)

        last_err: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                # run blocking SDK call in a thread so we don't block the event loop
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=WARM_MESSAGE_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=AIWarmMessageLists,
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=2048
                    )
                )

                raw_text = getattr(response, "text", None)
                usage = getattr(response, "usage_metadata", None) or getattr(response, "usage", None)

                result = AIWarmMessageLists.model_validate_json(raw_text)
                result.generated_at = datetime.now(timezone.utc)

                if debug:
                    return result, {
                        "model": self.model_name,
                        "raw_text": raw_text,
                        "usage": usage,
                        "has_raw_text": bool(raw_text and raw_text.strip()),
                    }

                return result

            except Exception as e:
                last_err = e
                if attempt >= max_retries or not self._is_retryable(e):
                    raise RuntimeError(f"AI generation failed: {e}") from e

                # exponential backoff + jitter
                base = 0.5 * (2 ** attempt)          # 0.5,1,2,4,8...
                jitter = random.uniform(0, 0.25)     # small jitter
                await asyncio.sleep(base + jitter)

        # should never reach
        raise RuntimeError(f"AI generation failed: {last_err}")
