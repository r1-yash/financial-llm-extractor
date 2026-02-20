"""
PDF text extraction and Gemini-based financial data extraction.
API key is loaded from environment; never logged or printed.
"""

import json
from typing import Any

import requests
from pypdf import PdfReader
from io import BytesIO


EXTRACTION_PROMPT = """You are a financial data extraction assistant.
Extract:
- Revenue
- Net Income
- Total Debt
- Total Assets
- EPS

Return ONLY valid JSON in this exact format:
{
  "Revenue": "",
  "Net_Income": "",
  "Total_Debt": "",
  "Total_Assets": "",
  "EPS": ""
}

If a field is missing return null.
Do not add explanations."""

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
def get_api_key() -> str:
    """Load API key from environment. Raises if missing."""
    from dotenv import load_dotenv
    import os
    load_dotenv()
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key or key.upper() in ("YOUR_API_KEY_HERE", "PASTE_YOUR_KEY_HERE"):
        raise ValueError(
            "GEMINI_API_KEY is not set or is still a placeholder. "
            "Set it in .env with your actual API key."
        )
    return key


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes."""
    reader = PdfReader(BytesIO(pdf_bytes))
    parts = []
    for page in reader.pages:
        try:
            text = page.extract_text()
            if text:
                parts.append(text)
        except Exception:
            continue
    if not parts:
        raise ValueError("No text could be extracted from the PDF.")
    return "\n\n".join(parts)


def _extract_json_from_text(text: str) -> dict[str, Any]:
    """Find and parse a JSON object from model output (handles markdown code blocks)."""
    text = text.strip()
    # Remove optional markdown code block
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end == -1:
            end = len(text)
        text = text[start:end]
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end == -1:
            end = len(text)
        text = text[start:end]
    # Find first { and last }
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1 or last <= first:
        raise ValueError("No valid JSON object found in model response.")
    return json.loads(text[first : last + 1])


def _normalize_extraction(data: dict[str, Any]) -> dict[str, Any]:
    """Ensure keys match expected schema and nulls are used for missing values."""
    schema_keys = ["Revenue", "Net_Income", "Total_Debt", "Total_Assets", "EPS"]
    # Handle key variants (e.g. "Net Income" vs "Net_Income")
    key_map = {k.replace("_", " "): k for k in schema_keys}
    key_map.update({k: k for k in schema_keys})
    result = {}
    for raw_key, value in data.items():
        normalized_key = key_map.get(raw_key) or key_map.get(raw_key.replace(" ", "_"))
        if normalized_key:
            result[normalized_key] = value if value is not None and value != "" else None
    for k in schema_keys:
        result.setdefault(k, None)
    return result


def extract_financial_data_via_gemini(text: str, api_key: str) -> dict[str, Any]:
    """
    Send extracted PDF text to Gemini and return parsed financial JSON.
    Uses temperature=0. API key is never logged.
    """
    url = f"{GEMINI_BASE_URL}?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": EXTRACTION_PROMPT + "\n\n---\n\nDocument text:\n\n" + text}]}],
        "generationConfig": {"temperature": 0},
    }
    resp = requests.post(url, json=payload, timeout=60)
    if not resp.ok:
        # Do not include response body in errors (may contain key or sensitive info)
        raise ValueError(f"Gemini API error: HTTP {resp.status_code}")
    try:
        body = resp.json()
    except json.JSONDecodeError:
        raise ValueError("Gemini API returned invalid JSON")

    # Handle Gemini response structure
    candidates = body.get("candidates") or []
    if not candidates:
        prompt_feedback = body.get("promptFeedback", {})
        block_reason = prompt_feedback.get("blockReason", "UNKNOWN")
        raise ValueError(f"Gemini returned no candidates. Block reason: {block_reason}")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    if not parts:
        finish_reason = candidates[0].get("finishReason", "UNKNOWN")
        raise ValueError(f"Gemini returned empty content. Finish reason: {finish_reason}")

    raw_text = parts[0].get("text", "").strip()
    if not raw_text:
        raise ValueError("Gemini returned empty text.")

    parsed = _extract_json_from_text(raw_text)
    return _normalize_extraction(parsed)


def extract_financial_data_from_pdf(pdf_bytes: bytes) -> dict[str, Any]:
    """
    Full pipeline: extract text from PDF, call Gemini, return structured financial data.
    """
    api_key = get_api_key()
    text = extract_text_from_pdf(pdf_bytes)
    # Truncate if very long to stay within model limits (e.g. 1M tokens for 1.5-flash)
    max_chars = 900_000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Document truncated for length.]"
    return extract_financial_data_via_gemini(text, api_key)
