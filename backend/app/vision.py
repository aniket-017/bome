"""Extract BOM lines from a drawing, photo or scan with a cloud vision model (OpenAI GPT-4o or Google Gemini).

Both providers are asked for the same strict JSON structure; the result is converted to the line
dicts that `bom_service.create_bom` takes, so image BOMs go through the normal matcher.
PDF drawings are sent to Gemini natively; OpenAI only gets raster images.
"""
from __future__ import annotations

import base64
import json

import httpx

from app.config import Settings, get_settings

IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
PDF_MIME_TYPE = "application/pdf"
DOCUMENT_MIME_TYPES = {**IMAGE_MIME_TYPES, ".pdf": PDF_MIME_TYPE}
REQUEST_TIMEOUT_SECONDS = 300

PROMPT = """You read Bills of Material (BOM) from engineering drawings and documents used in piping and
mechanical fabrication: GA / fabrication / assembly drawings, piping isometrics, skid and structural drawings,
and photos, scans or screenshots of BOM tables or handwritten material lists.

On a drawing the BOM is a table somewhere on the sheet (often above or beside the title block, or in a corner),
titled e.g. BILL OF MATERIAL, PARTS LIST, MATERIAL LIST, FABRICATION MATERIALS, ERECTION MATERIALS.
It may be split into several sections or side-by-side blocks, and continue on further pages. Read all of them.
Many drawings draw the BOM bottom-up (header row at the bottom, item 1 just above it); still return the lines
in item-number order.

Ignore everything that is not a material line: the drawing itself, dimensions, balloons, weld and surface symbols,
title block, revision table, notes, approvals, totals and cut-length / pipe-spool cut lists.

For each material line return:
- line_no: the item / position / mark number (ITEM, POS, PT NO, MARK, SR NO), or null if there is none
- item_no: the part / material / stock / commodity code or part drawing number, or null if there is none
- description: the description exactly as written (keep sizes, grades, standards, schedules, ratings, dimensions
  and units; join text that wraps onto several lines of the same item)
- size: the size when it is printed in its own column (SIZE, NPS, N.S., DN, DIA, dimensions), otherwise null
- material: the material / grade / specification when printed in its own column, otherwise null
- qty: the quantity as a number, or null if not readable
- uom: the unit (NOS, M, KG, SET ...), or null

When a value in a merged cell applies to several rows, repeat it on each of those rows.
Never invent lines or values; use null for anything you cannot read."""

LINE_FIELDS = ("line_no", "item_no", "description", "size", "material", "qty", "uom")

OPENAI_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["lines"],
    "properties": {
        "lines": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": list(LINE_FIELDS),
                "properties": {
                    "line_no": {"type": ["integer", "null"]},
                    "item_no": {"type": ["string", "null"]},
                    "description": {"type": "string"},
                    "size": {"type": ["string", "null"]},
                    "material": {"type": ["string", "null"]},
                    "qty": {"type": ["number", "null"]},
                    "uom": {"type": ["string", "null"]},
                },
            },
        }
    },
}

GEMINI_SCHEMA = {
    "type": "OBJECT",
    "required": ["lines"],
    "properties": {
        "lines": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": ["description"],
                "propertyOrdering": list(LINE_FIELDS),
                "properties": {
                    "line_no": {"type": "INTEGER", "nullable": True},
                    "item_no": {"type": "STRING", "nullable": True},
                    "description": {"type": "STRING"},
                    "size": {"type": "STRING", "nullable": True},
                    "material": {"type": "STRING", "nullable": True},
                    "qty": {"type": "NUMBER", "nullable": True},
                    "uom": {"type": "STRING", "nullable": True},
                },
            },
        }
    },
}


class VisionError(Exception):
    """The provider failed or returned something that is not a BOM."""


class VisionNotConfigured(VisionError):
    pass


def provider_status(settings: Settings | None = None) -> tuple[str, bool]:
    s = settings or get_settings()
    provider = s.vision_provider.lower()
    key = s.gemini_api_key if provider == "gemini" else s.openai_api_key
    return provider, bool(key)


def extract_bom_lines(image: bytes, mime_type: str, settings: Settings | None = None) -> list[dict]:
    s = settings or get_settings()
    provider, configured = provider_status(s)
    if not configured:
        raise VisionNotConfigured(
            f"Image extraction is not configured: set {'GEMINI' if provider == 'gemini' else 'OPENAI'}_API_KEY "
            "in backend/.env"
        )
    if mime_type == PDF_MIME_TYPE and provider != "gemini":
        raise VisionNotConfigured("PDF drawings need VISION_PROVIDER=gemini; upload a PNG/JPG image instead")
    if provider == "gemini":
        payload = _call_gemini(image, mime_type, s)
    elif provider == "openai":
        payload = _call_openai(image, mime_type, s)
    else:
        raise VisionNotConfigured(f"Unknown VISION_PROVIDER {s.vision_provider!r} (use openai or gemini)")
    return parse_lines(payload)


def _call_openai(image: bytes, mime_type: str, s: Settings) -> str:
    from openai import OpenAI, OpenAIError

    client = OpenAI(api_key=s.openai_api_key, timeout=REQUEST_TIMEOUT_SECONDS)
    data_url = f"data:{mime_type};base64,{base64.b64encode(image).decode()}"
    try:
        resp = client.chat.completions.create(
            model=s.openai_model,
            temperature=0,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract the BOM lines from this image."},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                ]},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "bom_lines", "strict": True, "schema": OPENAI_SCHEMA},
            },
        )
    except OpenAIError as exc:
        raise VisionError(f"OpenAI request failed: {exc}") from exc
    message = resp.choices[0].message
    if getattr(message, "refusal", None):
        raise VisionError(f"The model refused to read the image: {message.refusal}")
    return message.content or ""


def _call_gemini(image: bytes, mime_type: str, s: Settings) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{s.gemini_model}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": PROMPT}]},
        "contents": [{"role": "user", "parts": [
            {"text": "Extract the BOM lines from this drawing / document."},
            {"inlineData": {"mimeType": mime_type, "data": base64.b64encode(image).decode()}},
        ]}],
        "generationConfig": {
            "temperature": 0,
            # BOM text on a full drawing sheet is small; the default resolution misreads it
            "mediaResolution": "MEDIA_RESOLUTION_HIGH",
            "responseMimeType": "application/json",
            "responseSchema": GEMINI_SCHEMA,
        },
    }
    try:
        resp = httpx.post(url, params={"key": s.gemini_api_key}, json=body, timeout=REQUEST_TIMEOUT_SECONDS)
    except httpx.HTTPError as exc:
        raise VisionError(f"Gemini request failed: {exc}") from exc
    if resp.status_code != 200:
        raise VisionError(f"Gemini request failed ({resp.status_code}): {resp.text[:300]}")
    try:
        parts = resp.json()["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    except (KeyError, IndexError, ValueError, AttributeError) as exc:
        raise VisionError(f"Unexpected Gemini response: {resp.text[:300]}") from exc
    if not text:
        raise VisionError(f"Gemini returned no text: {resp.text[:300]}")
    return text


def _clean_str(value) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def _clean_number(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def _squash(text: str) -> str:
    return "".join(text.upper().split())


def merge_description(desc: str | None, *columns: str | None) -> str | None:
    """Append size / material columns the description does not already contain, so the matcher sees them."""
    out = desc
    for col in columns:
        if col and (not out or _squash(col) not in _squash(out)):
            out = f"{out} {col}" if out else col
    return out


def parse_lines(payload: str) -> list[dict]:
    try:
        data = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise VisionError("The model did not return valid JSON") from exc
    raw_lines = data.get("lines") if isinstance(data, dict) else None
    if not isinstance(raw_lines, list):
        raise VisionError("The model response has no 'lines' list")

    lines = []
    for raw in raw_lines:
        if not isinstance(raw, dict):
            continue
        desc = merge_description(
            _clean_str(raw.get("description")), _clean_str(raw.get("material")), _clean_str(raw.get("size"))
        )
        item_no = _clean_str(raw.get("item_no"))
        if not desc and not item_no:
            continue
        line_no = _clean_number(raw.get("line_no"))
        lines.append({
            "line_no": int(line_no) if line_no is not None and line_no.is_integer() and line_no > 0 else None,
            "raw_item_no": item_no,
            "raw_description": desc,
            "qty": _clean_number(raw.get("qty")),
            "uom": _clean_str(raw.get("uom")),
            "extra": {"vision": {k: raw.get(k) for k in LINE_FIELDS}},
        })
    return lines
