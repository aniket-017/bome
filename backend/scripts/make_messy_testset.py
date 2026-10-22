"""Build the matching accuracy test set: master parts rewritten the way BOMs typically write them.

Writes tests/data/messy_bom.csv (messy_description, expected_item_no, source_description).
Deterministic (fixed seed) so results are comparable between runs.

Usage: python scripts/make_messy_testset.py [--per-group 6]
"""
import argparse
import csv
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.db import SessionLocal  # noqa: E402
from app.normalize import NPS_TO_DN  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "tests" / "data" / "messy_bom.csv"
DN_TO_NPS = {v: k.replace("+", "-") for k, v in NPS_TO_DN.items()}
GROUPS = ["PIPE FITTINGS", "FASTENERS", "FLANGES", "GASKETS", "PIPES", "STRUCTURAL STEEL", "PLATES AND SHEETS",
          "VALVES", "BEARINGS", "SEALS"]
PIPING_PTYPES = {"ELBOW", "TEE", "REDUCER", "FLANGE", "PIPE", "CAP", "COUPLING", "PLUG", "GASKET", "SWAGE", "OLET",
                 "CROSS", "UNION", "NIPPLE", "VALVE", "STRAINER", "SPECTACLE BL"}

# hand-written BOM lines -> exact master description they should resolve to
HANDWRITTEN = [
    ('90 Deg LR Elbow, ASTM A403 WP316L, BW, 4" Sch 40', "ELBOW 90 DEG LR SS ASTM A403 WP316L DN 100 SCH 40S BW ASME B16.9"),
    ("Weld Neck Flange RF A182 F304L 300# Sch 80S 16\" B16.5",
     "FLANGE WN RF SS ASTM A182 F304L DN 400 CL 300 SCH 80S ASME B16.5"),
    ('Conc Red. A403 WP304 6" x 4" BW Sch 40',
     "REDUCER CONCENTRIC SS ASTM A403 WP304 DN 150 X DN 100 SCH 40S BW ASME B16.9"),
    ('PIPE SMLS A106 GR.B 3" SCH 40 BE IBR', "PIPE SMLS CS ASTM A106 GR B DN 80 SCH 40 BE ASME B36.10M IBR"),
    ("Hex bolt IS 1367 Gr 8.8 M24 x 100 HDG full thread",
     "BOLT HEX HEAD FULL THRD CS IS 1367 GR 8.8 M24 X 100 MM HDG IS 1364-2"),
    ('Spiral wound gasket graphite filler 6" cl 300 4.5 thk SS316L IR/OR',
     "GASKET SPIRAL WOUND SS316L WINDING GRAPHITE FILLER SS316L INNER RING CS OUTER RING DN 150 CL 300 THK 4.5 MM "
     "ASME B16.20"),
    ("plate sa516 gr70 12mm thk 2500 x 6300", "PLATE CS ASTM A516 GR 70 THK 12 MM 2500 X 6300 MM"),
    ("Slip on flange RF A105 150# 2\" B16.5", "FLANGE SO RF CS ASTM A105 DN 50 CL 150 ASME B16.5"),
    ("Stud full thread A193 B7 M20 x 300 plain", "STUD FULL THRD AS ASTM A193 B7 M20 X 300 MM PLAIN ASME B18.31.2"),
    ("SS angle 304 100x100x10", "ANGLE EQUAL SS SS304 100 X 100 X 10 MM IS 808"),
    ("Hex nut IS 1367 Gr 8 M20 HDG", "NUT HEX CS IS 1367 GR 8 M20 HDG IS 1364-3"),
    ("Plain washer M18 HDG IS 2016", "WASHER PLAIN CS IS 2062 FOR M18 HDG IS 2016"),
    ("Channel ISMC 100 IS 2062 E250 A", "CHANNEL CS IS 2062 E250 A ISMC 100 X 50 X 5 MM IS 808"),
    ("ISMB 200 beam IS2062 E250A", "BEAM CS IS 2062 E250 A ISMB 200 X 100 X 5.7 MM IS 808"),
    ("Ball bearing 6205 SKF", "BEARING BALL DEEP GROOVE 6205 25 X 52 X 15 MM SKF"),
    ("Oil seal 65x80x12 TC NBR", "OIL SEAL TC DOUBLE LIP WITH SPRING NBR 65 X 80 X 12 MM DIN 3760"),
    ("Motor 7.5kW 4 pole 415V IE3 foot mounted ABB",
     "MOTOR INDUCTION SQUIRREL CAGE 7.5 KW 4 POLE FRAME 132M FOOT B3 415V 3PH 50HZ IE3 TEFC IP55 ABB"),
    ('Pressure gauge 100 mm dial 0-10 bar SS316 wetted 1/2" NPT back WIKA',
     "GAUGE PRESSURE BOURDON 100 MM DIAL 0-10 BAR SS304 CASE SS316 WETTED 1/2 NPT(M) BACK DRY CLASS 1.0 EN 837-1 WIKA"),
    ("Electrode E7018 3.15mm ESAB", "ELECTRODE WELDING LOW HYDROGEN AWS A5.1 E7018 3.15 MM L 350 MM ESAB"),
]


def mess(desc: str, rng: random.Random, ptype_piping: bool) -> str:
    s = desc

    def maybe(p: float) -> bool:
        return rng.random() < p

    s = re.sub(r"\b(?:ASTM A|SA\s*-*\s*)(\d{2,3})", lambda m: rng.choice(
        [f"A{m.group(1)}", f"ASTM A{m.group(1)}", f"SA {m.group(1)}", f"A-{m.group(1)}", f"SA-{m.group(1)}"]), s)
    s = re.sub(r"\bGR\s+", lambda m: rng.choice(["GR.", "Gr ", "GR ", "", "Grade "]), s)
    s = re.sub(r"\bDN\s*(\d+)", lambda m: (
        rng.choice([f'{DN_TO_NPS[int(m.group(1))]}"', f"{m.group(1)}NB", f"DN{m.group(1)}", f"{m.group(1)} NB"])
        if ptype_piping and int(m.group(1)) in DN_TO_NPS else rng.choice([f"DN{m.group(1)}", f"DN {m.group(1)}"])), s)
    s = re.sub(r"\bSCH\s*(\w+)", lambda m: rng.choice([f"Sch{m.group(1)}", f"SCH-{m.group(1)}", f"Sch. {m.group(1)}",
                                                        f"SCHEDULE {m.group(1)}"]), s)
    s = re.sub(r"\b(?:CL|CLASS)\s*(\d{3,4})", lambda m: rng.choice([f"{m.group(1)}#", f"CLASS {m.group(1)}",
                                                                     f"{m.group(1)} LB", f"CL.{m.group(1)}"]), s)
    s = re.sub(r"\bWN RF\b", lambda m: rng.choice(["WN RF", "Weld Neck RF", "WN-RF", "WNRF"]), s)
    s = re.sub(r"\bSO RF\b", lambda m: rng.choice(["SO RF", "Slip On RF", "SO-RF", "SORF"]), s)
    s = re.sub(r"\b(\d+) DEG (LR|SR)\b", lambda m: rng.choice([f"{m.group(1)} deg {m.group(2)}",
                                                                f"{m.group(1)}° {'Long' if m.group(2) == 'LR' else 'Short'} Radius",
                                                                f"{m.group(2)} {m.group(1)}DEG"]), s)
    s = re.sub(r"\bFULL THRD\b", lambda m: rng.choice(["full thread", "FULL THREADED", "FT"]), s)
    s = re.sub(r"\bSPIRAL WOUND\b", lambda m: rng.choice(["SPW", "Spiral Wound", "SPIRAL WOUND"]), s)
    s = re.sub(r"\bREDUCER ECCENTRIC\b", lambda m: rng.choice(["Ecc. Reducer", "Eccentric Reducer", "ECC RED"]), s)
    s = re.sub(r"\bREDUCER CONCENTRIC\b", lambda m: rng.choice(["Conc. Reducer", "Concentric Reducer", "CONC RED"]), s)
    s = re.sub(r"(\d) MM\b", lambda m: rng.choice([f"{m.group(1)}mm", f"{m.group(1)} MM", f"{m.group(1)}"]), s)
    # BOMs rarely repeat the material class or the dimensional standard
    if maybe(0.6):
        s = re.sub(r"\b(?:CS|SS|AS|LTCS) (?=(?:ASTM |SA|A-?)?\d|IS )", "", s)
    if maybe(0.5):
        s = re.sub(r"\s+(?:ASME B\d+(?:\.\d+)+M?|IS \d+(?:-\d)?|ISO \d+|DIN \d+|EN \d+(?:-\d)?)(?![\w.])", "", s)
    if maybe(0.3):
        s = re.sub(r"\bWITH\b\s*", "", s)
    if maybe(0.25):
        s += rng.choice([" SMLS", " BE", " ASME", " (as per spec)"])
    if maybe(0.4):
        s = s.lower()
    elif maybe(0.3):
        s = s.title()
    return " ".join(s.split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-group", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    db = SessionLocal()

    rows = []
    for messy, canonical in HANDWRITTEN:
        item = db.execute(text("SELECT item_no FROM parts WHERE description = :d ORDER BY item_no LIMIT 1"),
                          {"d": canonical}).scalar()
        if item is None:
            print(f"!! handwritten target not in master: {canonical}")
            continue
        rows.append((messy, item, canonical, "handwritten"))

    for group in GROUPS:
        picked = db.execute(text("""
            SELECT item_no, description, attrs->>'ptype' AS ptype FROM parts p
            WHERE item_group = :g AND is_active
              AND (SELECT count(*) FROM parts q WHERE q.description_norm = p.description_norm) = 1
            ORDER BY md5(item_no || :seed) LIMIT :n"""), {"g": group, "n": args.per_group, "seed": str(args.seed)})
        for item_no, desc, ptype in picked:
            rows.append((mess(desc, rng, ptype in PIPING_PTYPES), item_no, desc, "generated"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["messy_description", "expected_item_no", "source_description", "kind"])
        w.writerows(rows)
    print(f"wrote {len(rows)} lines to {OUT}")


if __name__ == "__main__":
    main()
