import json
import os
from typing import Any, Optional

from openai import OpenAI


# Returns True when an OpenAI API key is available for server-side use.
def llm_is_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


# Returns the text model used for enrichment, with an overridable default.
def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


# Creates the OpenAI client for server-side API calls.
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Calls the OpenAI Responses API and tries to parse a JSON object from the result.
def request_json_response(system_prompt: str, user_prompt: str) -> Optional[dict[str, Any]]:
    if not llm_is_configured():
        return None

    try:
        client = get_openai_client()
        response = client.responses.create(
            model=get_openai_model(),
            input=(
                f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
                f"USER INPUT:\n{user_prompt}\n\n"
                "Return only valid JSON."
            ),
        )

        text = getattr(response, "output_text", "") or ""
        if not text:
            return None

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            return None

        return json.loads(text[start : end + 1])
    except Exception:
        # Graceful fallback: deterministic backend response still returns.
        return None