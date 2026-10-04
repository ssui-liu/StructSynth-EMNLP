"""Parse finite JSON model content without changing its values."""
from __future__ import annotations

import json

from ..artifacts import canonical_json
from .contracts import LLMResponseError


def parse_json_content(content):
    if isinstance(content, (dict, list)):
        canonical_json(content)  # Reject non-finite numbers, including in scripted responses.
        return content
    if not isinstance(content, str):
        raise LLMResponseError("Expected a JSON string/object from the model")
    text = content.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1])
    try:
        return json.loads(text, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (ValueError, TypeError) as exc:
        raise LLMResponseError("Model response is not valid finite JSON") from exc
