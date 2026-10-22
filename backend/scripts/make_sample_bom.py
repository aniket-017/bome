"""Create sample BOMs from the messy test set.

samples/sample_bom.xlsx: a realistic BOM sheet (title rows, no item numbers on most lines).
samples/sample_bom.png: a BOM table rendered as an image, for trying the image upload.
"""
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = Path(__file__).resolve().parent.parent / "tests" / "data" / "messy_bom.csv"
IMAGE_LINES = 12


def load_cases() -> list[dict]:
    with DATA.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))[:40]


def make_excel(cases: list[dict], out: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "BOM"
    ws.append(["PROJECT: HEAT EXCHANGER E-101"])
    ws.append(["Drawing No: HX-101-GA-001   Rev: 2"])
    ws.append([])
    ws.append(["Sr. No.", "Item Code", "Material Description", "Qty", "Unit", "Remarks"])
    for c in ws[4]:
        c.font = Font(bold=True)
    for i, case in enumerate(cases, start=1):
        item_code = case["expected_item_no"] if i % 10 == 0 else None
        ws.append([i, item_code, case["messy_description"], (i % 7) + 1, "NOS", None])
    ws.append([len(cases) + 1, None, "Lifting lug as per drawing", 4, "NOS", "Fabricated"])
    ws.column_dimensions["C"].width = 70
    wb.save(out)


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_image(cases: list[dict], out: Path) -> None:
    cols = [("Pos", 70), ("Description", 820), ("Qty", 80), ("Unit", 80)]
    row_h, pad, top = 40, 12, 110
    width = sum(w for _, w in cols) + 2 * pad
    height = top + row_h * (len(cases) + 1) + pad
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title, text = _font(26), _font(19)
    draw.text((pad, 20), "BILL OF MATERIAL - PUMP SKID P-201", fill="black", font=title)
    draw.text((pad, 60), "Dwg: P201-PIP-004  Rev 0", fill="#333", font=text)

    rows = [[c for c, _ in cols]] + [[str(i), case["messy_description"], str((i % 5) + 1), "NOS"]
                                     for i, case in enumerate(cases, start=1)]
    y = top
    for r, row in enumerate(rows):
        x = pad
        for (_, w), value in zip(cols, row):
            draw.rectangle([x, y, x + w, y + row_h], outline="black", width=1)
            draw.text((x + 8, y + 9), value, fill="black", font=text)
            x += w
        y += row_h
    img.save(out)


def main() -> None:
    cases = load_cases()
    out_dir = ROOT / "samples"
    out_dir.mkdir(exist_ok=True)
    make_excel(cases, out_dir / "sample_bom.xlsx")
    make_image(cases[:IMAGE_LINES], out_dir / "sample_bom.png")
    print(f"wrote {out_dir / 'sample_bom.xlsx'} and {out_dir / 'sample_bom.png'}")


if __name__ == "__main__":
    main()
