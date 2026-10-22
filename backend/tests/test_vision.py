"""Image BOM extraction with the vision providers mocked (no API key or network needed)."""
import json
from pathlib import Path

import httpx
import pytest

from app import vision
from app.config import Settings

LINES_JSON = json.dumps({"lines": [
    {"line_no": 1, "item_no": None, "description": "Conc Red. A403 WP304  6\" x 4\" BW Sch 40", "qty": 2, "uom": "NOS"},
    {"line_no": 2, "item_no": "301148", "description": "STUD FT IS 1367 Gr 8.8 M42 x 500 HDG", "qty": "16", "uom": "nos"},
    {"line_no": None, "item_no": None, "description": "  ", "qty": None, "uom": None},
    {"line_no": 0, "item_no": None, "description": "Lifting lug as per drawing", "qty": "1,200", "uom": None},
]})


def test_parse_lines_cleans_and_skips_empty():
    lines = vision.parse_lines(LINES_JSON)
    assert [l["raw_description"] for l in lines] == [
        "Conc Red. A403 WP304 6\" x 4\" BW Sch 40", "STUD FT IS 1367 Gr 8.8 M42 x 500 HDG", "Lifting lug as per drawing",
    ]
    assert [l["line_no"] for l in lines] == [1, 2, None]
    assert [l["qty"] for l in lines] == [2.0, 16.0, 1200.0]
    assert lines[1]["raw_item_no"] == "301148"
    assert lines[0]["extra"]["vision"]["uom"] == "NOS"


def test_parse_lines_merges_separate_size_and_material_columns():
    payload = json.dumps({"lines": [
        {"line_no": 1, "description": "PIPE SMLS BE SCH 40", "size": "3\"", "material": "A106 GR.B", "qty": 6, "uom": "M"},
        {"line_no": 2, "description": "ELBOW 90 LR 4\" BW", "size": "4 \"", "material": None, "qty": 2, "uom": "NOS"},
        {"line_no": 3, "description": None, "size": "M20 x 310", "material": "A193 B7", "qty": 8, "uom": None},
    ]})
    lines = vision.parse_lines(payload)
    assert [l["raw_description"] for l in lines] == [
        "PIPE SMLS BE SCH 40 A106 GR.B 3\"", "ELBOW 90 LR 4\" BW", "A193 B7 M20 x 310",
    ]
    assert lines[0]["extra"]["vision"]["size"] == "3\""


@pytest.mark.parametrize("payload", ["not json", "[]", '{"rows": []}'])
def test_parse_lines_rejects_bad_payload(payload):
    with pytest.raises(vision.VisionError):
        vision.parse_lines(payload)


def test_not_configured():
    with pytest.raises(vision.VisionNotConfigured):
        vision.extract_bom_lines(b"img", "image/png", Settings(vision_provider="openai", openai_api_key=""))


def test_pdf_requires_gemini():
    with pytest.raises(vision.VisionNotConfigured, match="gemini"):
        vision.extract_bom_lines(b"%PDF", "application/pdf", Settings(vision_provider="openai", openai_api_key="k"))


def test_openai_provider(monkeypatch):
    calls = []
    monkeypatch.setattr(vision, "_call_openai", lambda img, mime, s: calls.append((img, mime, s.openai_model)) or LINES_JSON)
    lines = vision.extract_bom_lines(b"img", "image/png", Settings(vision_provider="openai", openai_api_key="k"))
    assert len(lines) == 3 and calls == [(b"img", "image/png", "gpt-4o")]


def test_gemini_provider_request(monkeypatch):
    sent = {}

    def fake_post(url, params, json, timeout):
        sent.update(url=url, params=params, body=json)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": LINES_JSON}]}}]})

    monkeypatch.setattr(vision.httpx, "post", fake_post)
    s = Settings(vision_provider="gemini", gemini_api_key="g-key", gemini_model="gemini-test")
    lines = vision.extract_bom_lines(b"\x89PNG", "image/png", s)
    assert len(lines) == 3
    assert sent["url"].endswith("/models/gemini-test:generateContent")
    assert sent["params"] == {"key": "g-key"}
    assert sent["body"]["generationConfig"]["responseSchema"] == vision.GEMINI_SCHEMA
    assert sent["body"]["contents"][0]["parts"][1]["inlineData"]["mimeType"] == "image/png"


def test_gemini_pdf_skips_thought_parts(monkeypatch):
    sent = {}

    def fake_post(url, params, json, timeout):
        sent.update(body=json)
        parts = [{"text": "thinking...", "thought": True}, {"text": LINES_JSON}]
        return httpx.Response(200, json={"candidates": [{"content": {"parts": parts}}]})

    monkeypatch.setattr(vision.httpx, "post", fake_post)
    lines = vision.extract_bom_lines(b"%PDF", "application/pdf", Settings(vision_provider="gemini", gemini_api_key="g"))
    assert len(lines) == 3
    assert sent["body"]["contents"][0]["parts"][1]["inlineData"]["mimeType"] == "application/pdf"


def test_gemini_http_error(monkeypatch):
    monkeypatch.setattr(vision.httpx, "post", lambda *a, **k: httpx.Response(429, text="quota exceeded"))
    with pytest.raises(vision.VisionError, match="429"):
        vision.extract_bom_lines(b"x", "image/png", Settings(vision_provider="gemini", gemini_api_key="g"))


try:
    from fastapi.testclient import TestClient
    from sqlalchemy import text

    from app.db import engine
    from app.main import app

    with engine.connect() as conn:
        HAS_PARTS = conn.execute(text("SELECT count(*) FROM parts")).scalar() > 0
except Exception:  # pragma: no cover - environment without DB
    HAS_PARTS = False

needs_db = pytest.mark.skipif(not HAS_PARTS, reason="database with parts master required")


@needs_db
def test_upload_image_flow(monkeypatch):
    from app.routers import boms

    with engine.connect() as conn:
        stud_item_no = conn.execute(text("SELECT item_no FROM parts WHERE description = :d"), {
            "d": "STUD FULL THRD CS IS 1367 GR 8.8 M42 X 500 MM HDG ASME B18.31.2"}).scalar_one()
        reducer_item_no = conn.execute(text("SELECT item_no FROM parts WHERE description = :d"), {
            "d": "REDUCER CONCENTRIC SS ASTM A403 WP304 DN 150 X DN 100 SCH 40S BW ASME B16.9"}).scalar_one()
    payload = LINES_JSON.replace('"301148"', f'"{stud_item_no}"')
    monkeypatch.setattr(boms, "extract_bom_lines", lambda data, mime: vision.parse_lines(payload))
    client = TestClient(app)
    image = b"\x89PNG\r\n\x1a\nfake image bytes"
    r = client.post("/api/boms/upload-image", files={"file": ("bom photo.png", image, "image/png")},
                    data={"name": "pytest image"})
    assert r.status_code == 201, r.text
    bom = r.json()
    try:
        assert bom["source_type"] == "image" and bom["source_file"] == "bom photo.png"
        statuses = [l["match_status"] for l in bom["lines"]]
        assert statuses[0] == "auto" and statuses[1] == "exact_item_no"
        assert bom["lines"][0]["matched_part"]["item_no"] == reducer_item_no
        assert statuses[2] == "unmatched"
        img = client.get(f"/api/boms/{bom['id']}/image")
        assert img.status_code == 200 and img.content == image
    finally:
        client.delete(f"/api/boms/{bom['id']}")
    assert not Path(bom["image_path"]).exists()


@needs_db
def test_upload_image_errors(monkeypatch):
    from app.routers import boms

    client = TestClient(app)
    r = client.post("/api/boms/upload-image", files={"file": ("bom.dwg", b"AC1032", "application/octet-stream")},
                    data={"name": "x"})
    assert r.status_code == 415

    def not_configured(data, mime):
        raise vision.VisionNotConfigured("set OPENAI_API_KEY")

    monkeypatch.setattr(boms, "extract_bom_lines", not_configured)
    r = client.post("/api/boms/upload-image", files={"file": ("bom.jpg", b"jpg", "image/jpeg")}, data={"name": "x"})
    assert r.status_code == 503 and "OPENAI_API_KEY" in r.json()["detail"]

    monkeypatch.setattr(boms, "extract_bom_lines", lambda data, mime: [])
    r = client.post("/api/boms/upload-image", files={"file": ("bom.jpg", b"jpg", "image/jpeg")}, data={"name": "x"})
    assert r.status_code == 422
