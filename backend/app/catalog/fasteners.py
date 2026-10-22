"""Fasteners and rigging hardware."""
from app.catalog import noun
from app.catalog.data import DN_TO_NPS, INCH_BOLTS, ISO_LENGTHS, fmt, inch_thread, lengths_between, m_dia, mm, stud_lengths

G = "FASTENERS"
G_RIG = "RIGGING AND LIFTING"
LEN_GLUE = {"LENGTH": " X "}

STUD = noun("STUD", G, "NOS", ("TYPE", "MOC", "SPEC", "DIA", "LENGTH", "NUTS", "FINISH", "STANDARD"), LEN_GLUE)
BOLT = noun("BOLT", G, "NOS", ("TYPE", "THREAD", "MOC", "SPEC", "DIA", "LENGTH", "FINISH", "STANDARD"), LEN_GLUE)
SCREW = noun("SCREW", G, "NOS", ("TYPE", "DRIVE", "MOC", "SPEC", "DIA", "LENGTH", "FINISH", "STANDARD"), LEN_GLUE)
NUT = noun("NUT", G, "NOS", ("TYPE", "MOC", "SPEC", "DIA", "FINISH", "STANDARD"))
WASHER = noun("WASHER", G, "NOS", ("TYPE", "MOC", "SPEC", "SIZE", "THICKNESS", "FINISH", "STANDARD"))
ANCHOR = noun("ANCHOR", G, "NOS", ("TYPE", "MOC", "DIA", "LENGTH", "FINISH", "STANDARD"), LEN_GLUE)
RIVET = noun("RIVET", G, "NOS", ("TYPE", "MOC", "DIA", "LENGTH", "STANDARD"), LEN_GLUE)
PIN = noun("PIN", G, "NOS", ("TYPE", "MOC", "DIA", "LENGTH", "FINISH", "STANDARD"), LEN_GLUE)
CIRCLIP = noun("RETAINING RING", G, "NOS", ("TYPE", "MOC", "SIZE", "FINISH", "STANDARD"))
KEY = noun("KEY", G, "NOS", ("TYPE", "MOC", "SIZE", "LENGTH", "STANDARD", "MAKE"), LEN_GLUE)
ROD = noun("ROD", G, "NOS", ("TYPE", "MOC", "SPEC", "DIA", "LENGTH", "FINISH", "STANDARD"), LEN_GLUE)
SHACKLE = noun("SHACKLE", G_RIG, "NOS", ("TYPE", "PIN", "MOC", "CAPACITY", "FINISH", "STANDARD"))
TURNBUCKLE = noun("TURNBUCKLE", G_RIG, "NOS", ("TYPE", "MOC", "DIA", "FINISH", "STANDARD"))
HOOK = noun("HOOK", G_RIG, "NOS", ("TYPE", "MOC", "CAPACITY", "FINISH", "STANDARD"))
WIRE_ROPE = noun("WIRE ROPE", G_RIG, "MTR", ("CONSTRUCTION", "CORE", "MOC", "DIA", "GRADE", "FINISH", "STANDARD"))
SLING = noun("SLING", G_RIG, "NOS", ("TYPE", "MOC", "CAPACITY", "LENGTH", "STANDARD"))
# shared with hose clamps / pipe clamps
CLAMP = noun("CLAMP", G, "NOS", ("TYPE", "MOC", "SIZE", "BOLT", "FINISH", "STANDARD"))
THIMBLE = noun("THIMBLE", G_RIG, "NOS", ("TYPE", "MOC", "SIZE", "FINISH", "STANDARD"))

METRIC_STUDS = ["M10", "M12", "M14", "M16", "M20", "M22", "M24", "M27", "M30", "M33", "M36", "M39", "M42", "M45",
                "M48", "M52", "M56", "M64"]
CARBON_FINISHES = ["PLAIN", "HDG", "ZINC PLATED", "PTFE COATED", "XYLAN COATED"]

# (moc, stud spec, matching heavy hex nut spec, finishes)
STUD_GRADES = [
    ("AS", "ASTM A193 B7", "ASTM A194 2H", CARBON_FINISHES),
    ("AS", "ASTM A193 B7M", "ASTM A194 2HM", CARBON_FINISHES),
    ("AS", "ASTM A193 B16", "ASTM A194 4", ["PLAIN", "PTFE COATED"]),
    ("AS", "ASTM A320 L7", "ASTM A194 7", ["PLAIN", "PTFE COATED", "XYLAN COATED"]),
    ("AS", "ASTM A320 L7M", "ASTM A194 7M", ["PLAIN", "PTFE COATED"]),
    ("SS", "ASTM A193 B8 CL1", "ASTM A194 8", ["PLAIN"]),
    ("SS", "ASTM A193 B8 CL2", "ASTM A194 8", ["PLAIN"]),
    ("SS", "ASTM A193 B8M CL1", "ASTM A194 8M", ["PLAIN"]),
    ("SS", "ASTM A193 B8M CL2", "ASTM A194 8M", ["PLAIN"]),
    ("SS", "ASTM A453 GR 660", "ASTM A453 GR 660", ["PLAIN"]),
    ("CS", "IS 1367 GR 8.8", "IS 1367 GR 8", ["PLAIN", "HDG", "ZINC PLATED"]),
    ("CS", "ASTM A307 GR B", "ASTM A563 GR A", ["PLAIN", "HDG"]),
]


def _stud_sizes():
    for m in METRIC_STUDS:
        yield m, m_dia(m)
    for label, d in INCH_BOLTS:
        yield inch_thread(label, d), d


@STUD.generator
def stud_bolts():
    for moc, spec, nut_spec, finishes in STUD_GRADES:
        for dia, d in _stud_sizes():
            for L in stud_lengths(d):
                for nuts in ("", f"WITH 2 HEAVY HEX NUTS {nut_spec}"):
                    for finish in finishes:
                        yield {"TYPE": "FULL THRD", "MOC": moc, "SPEC": spec, "DIA": dia, "LENGTH": mm(L),
                               "NUTS": nuts, "FINISH": finish, "STANDARD": "ASME B18.31.2"}


@STUD.generator
def tap_end_studs():
    for moc, spec in (("CS", "GR 8.8"), ("AS", "ASTM A193 B7"), ("SS", "A2-70"), ("SS", "A4-70")):
        for m in ("M6", "M8", "M10", "M12", "M16", "M20", "M24", "M30"):
            d = m_dia(m)
            for L in lengths_between(2 * d + 10, 10 * d):
                for typ, std in (("TAP END", "DIN 938"), ("DOUBLE END", "DIN 976")):
                    yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "DIA": m, "LENGTH": mm(L), "FINISH": "PLAIN",
                           "STANDARD": std}


HEX_METRIC = ["M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24", "M27", "M30", "M33",
              "M36", "M42", "M48"]
PART_THREAD = {"M3": (20, 30), "M4": (25, 40), "M5": (25, 50), "M6": (30, 60), "M8": (40, 80), "M10": (45, 100),
               "M12": (50, 120), "M14": (60, 140), "M16": (65, 160), "M18": (70, 180), "M20": (80, 200),
               "M22": (90, 220), "M24": (90, 240), "M27": (100, 260), "M30": (110, 300), "M33": (130, 320),
               "M36": (140, 360), "M42": (160, 440), "M48": (180, 480)}
FULL_THREAD = {"M3": (6, 30), "M4": (8, 40), "M5": (10, 50), "M6": (12, 60), "M8": (16, 80), "M10": (20, 100),
               "M12": (25, 120), "M14": (30, 140), "M16": (30, 160), "M18": (35, 180), "M20": (40, 200),
               "M22": (45, 200), "M24": (50, 200), "M27": (55, 200), "M30": (60, 200), "M33": (65, 200),
               "M36": (70, 200), "M42": (80, 200), "M48": (100, 200)}
HEX_GRADES = [("CS", "GR 4.6", ["PLAIN", "ZINC PLATED", "HDG"]),
              ("CS", "GR 8.8", ["BLACK", "ZINC PLATED", "HDG", "ZINC FLAKE"]),
              ("CS", "GR 10.9", ["BLACK", "ZINC FLAKE"]),
              ("CS", "GR 12.9", ["BLACK"]),
              ("SS", "A2-70", ["PLAIN"]), ("SS", "A4-70", ["PLAIN"]), ("SS", "A4-80", ["PLAIN"])]


@BOLT.generator
def hex_bolts():
    for thread, table, std in (("PART THRD", PART_THREAD, "ISO 4014"), ("FULL THRD", FULL_THREAD, "ISO 4017")):
        for m in HEX_METRIC:
            lo, hi = table[m]
            for L in lengths_between(lo, hi):
                for moc, grade, finishes in HEX_GRADES:
                    for finish in finishes:
                        yield {"TYPE": "HEX HEAD", "THREAD": thread, "MOC": moc, "SPEC": grade, "DIA": m,
                               "LENGTH": mm(L), "FINISH": finish, "STANDARD": std}
    # metric fine thread
    for m, pitch in (("M8", "1"), ("M10", "1.25"), ("M12", "1.25"), ("M12", "1.5"), ("M14", "1.5"), ("M16", "1.5"),
                     ("M18", "1.5"), ("M20", "1.5"), ("M22", "1.5"), ("M24", "2"), ("M27", "2"), ("M30", "2")):
        lo, hi = FULL_THREAD[m]
        for L in lengths_between(lo, hi):
            for grade, finish in (("GR 8.8", "BLACK"), ("GR 8.8", "ZINC PLATED"), ("GR 10.9", "BLACK"),
                                  ("A2-70", "PLAIN")):
                yield {"TYPE": "HEX HEAD", "THREAD": "FULL THRD FINE", "MOC": "SS" if grade.startswith("A") else "CS",
                       "SPEC": grade, "DIA": f"{m} X {pitch}", "LENGTH": mm(L), "FINISH": finish, "STANDARD": "ISO 8676"}


IS_BOLT_GRADES = [("IS 1367 GR 4.6", ["BLACK", "HDG", "ZINC PLATED"]), ("IS 1367 GR 8.8", ["BLACK", "HDG", "ZINC PLATED"]),
                  ("IS 1367 GR 10.9", ["BLACK", "ZINC FLAKE"])]


@BOLT.generator
def is_hex_bolts():
    for thread, table, std in (("PART THRD", PART_THREAD, "IS 1364-1"), ("FULL THRD", FULL_THREAD, "IS 1364-2")):
        for m in HEX_METRIC:
            lo, hi = table[m]
            for L in lengths_between(lo, hi):
                for grade, finishes in IS_BOLT_GRADES:
                    for finish in finishes:
                        yield {"TYPE": "HEX HEAD", "THREAD": thread, "MOC": "CS", "SPEC": grade, "DIA": m,
                               "LENGTH": mm(L), "FINISH": finish, "STANDARD": std}
    # pressure-boundary hex bolts in ASTM grades, metric
    for thread, table, std in (("PART THRD", PART_THREAD, "ISO 4014"), ("FULL THRD", FULL_THREAD, "ISO 4017")):
        for m in HEX_METRIC[5:]:
            lo, hi = table[m]
            for L in lengths_between(lo, hi):
                for moc, spec, finishes in (("AS", "ASTM A193 B7", ("PLAIN", "HDG", "PTFE COATED")),
                                            ("SS", "ASTM A193 B8 CL1", ("PLAIN",)), ("SS", "ASTM A193 B8M CL1", ("PLAIN",))):
                    for finish in finishes:
                        yield {"TYPE": "HEX HEAD", "THREAD": thread, "MOC": moc, "SPEC": spec, "DIA": m,
                               "LENGTH": mm(L), "FINISH": finish, "STANDARD": std}
    # black bolts, product grade C
    for m in HEX_METRIC[3:]:
        lo, hi = PART_THREAD[m]
        for L in lengths_between(lo, hi):
            for finish in ("BLACK", "HDG"):
                yield {"TYPE": "HEX HEAD", "THREAD": "PART THRD", "MOC": "CS", "SPEC": "IS 1367 GR 4.6", "DIA": m,
                       "LENGTH": mm(L), "FINISH": finish, "STANDARD": "IS 1363-1"}


@BOLT.generator
def heavy_hex_and_structural_bolts():
    specs = [("AS", "ASTM A193 B7", ["PLAIN", "HDG", "PTFE COATED"]), ("CS", "ASTM A307 GR B", ["PLAIN", "HDG"]),
             ("CS", "ASTM A325 TYPE 1", ["PLAIN", "HDG"]), ("AS", "ASTM A490 TYPE 1", ["PLAIN"])]
    for moc, spec, finishes in specs:
        for label, d in INCH_BOLTS[:9]:
            for L in [L for L in ISO_LENGTHS if 2.5 * d <= L <= min(300, 12 * d)]:
                for finish in finishes:
                    yield {"TYPE": "HEAVY HEX", "THREAD": "PART THRD", "MOC": moc, "SPEC": spec,
                           "DIA": inch_thread(label, d), "LENGTH": mm(L), "FINISH": finish, "STANDARD": "ASME B18.2.1"}
    for m in ("M16", "M20", "M22", "M24", "M27", "M30", "M36"):
        d = m_dia(m)
        for L in lengths_between(2.5 * d, 10 * d):
            for grade in ("GR 8.8", "GR 10.9"):
                for finish in ("BLACK", "HDG"):
                    yield {"TYPE": "HSFG HEAVY HEX", "THREAD": "PART THRD", "MOC": "CS", "SPEC": grade, "DIA": m,
                           "LENGTH": mm(L), "FINISH": finish, "STANDARD": "IS 3757"}


@BOLT.generator
def special_bolts():
    for m in ("M6", "M8", "M10", "M12", "M16"):
        d = m_dia(m)
        for L in lengths_between(2 * d, 15 * d):
            for moc, grade, finish in (("CS", "GR 4.6", "ZINC PLATED"), ("CS", "GR 4.6", "HDG"), ("SS", "A2-70", "PLAIN")):
                yield {"TYPE": "CARRIAGE", "THREAD": "PART THRD", "MOC": moc, "SPEC": grade, "DIA": m, "LENGTH": mm(L),
                       "FINISH": finish, "STANDARD": "DIN 603"}
                yield {"TYPE": "HEX FLANGE", "THREAD": "FULL THRD", "MOC": moc, "SPEC": "GR 8.8" if moc == "CS" else grade,
                       "DIA": m, "LENGTH": mm(L), "FINISH": finish, "STANDARD": "DIN 6921"}
    for m in ("M6", "M8", "M10", "M12", "M16", "M20", "M24", "M30", "M36", "M42", "M48", "M56", "M64"):
        for moc, spec, finish in (("CS", "C15E FORGED", "ZINC PLATED"), ("CS", "C15E FORGED", "PLAIN"), ("SS", "SS304", "PLAIN"),
                                  ("SS", "SS316", "PLAIN")):
            yield {"TYPE": "EYE", "MOC": moc, "SPEC": spec, "DIA": m, "FINISH": finish, "STANDARD": "DIN 580"}
    # U-bolts for pipe supports: rod diameter by pipe size
    for d, rod in ((15, "M10"), (20, "M10"), (25, "M10"), (32, "M10"), (40, "M12"), (50, "M12"), (65, "M12"),
                   (80, "M12"), (100, "M16"), (125, "M16"), (150, "M16"), (200, "M20"), (250, "M20"), (300, "M20"),
                   (350, "M24"), (400, "M24"), (450, "M24"), (500, "M24"), (600, "M24")):
        for moc, finish in (("CS", "HDG"), ("CS", "PLAIN"), ("SS", "SS304"), ("SS", "SS316")):
            yield {"TYPE": "U", "MOC": moc, "SPEC": finish if moc == "SS" else "IS 2062 E250",
                   "DIA": f"FOR {DN_TO_NPS[d]} PIPE {rod}", "FINISH": "PLAIN" if moc == "SS" else finish,
                   "STANDARD": "MSS SP-58"}
    for m in ("M12", "M16", "M20", "M24", "M30", "M36", "M42", "M48"):
        d = m_dia(m)
        for L in range(300, 2100, 100):
            if L < 15 * d or L > 50 * d:
                continue
            for typ in ("FOUNDATION L TYPE", "FOUNDATION J TYPE"):
                for grade in ("GR 4.6", "GR 8.8"):
                    for finish in ("PLAIN", "HDG"):
                        yield {"TYPE": typ, "THREAD": "PART THRD", "MOC": "CS", "SPEC": grade, "DIA": m,
                               "LENGTH": mm(L), "FINISH": finish, "STANDARD": "IS 5624"}


SHCS = {"M2": (4, 20), "M2.5": (5, 25), "M3": (5, 30), "M4": (6, 40), "M5": (8, 50), "M6": (8, 60), "M8": (10, 80),
        "M10": (12, 100), "M12": (16, 120), "M14": (20, 140), "M16": (20, 160), "M20": (25, 200), "M24": (30, 200),
        "M30": (40, 200), "M36": (50, 200)}
SOCKET_GRADES = [("AS", "GR 12.9", "BLACK"), ("AS", "GR 12.9", "ZINC FLAKE"), ("CS", "GR 8.8", "ZINC PLATED"),
                 ("SS", "A2-70", "PLAIN"), ("SS", "A4-70", "PLAIN"), ("SS", "A4-80", "PLAIN")]
SCREW_LENGTHS = [2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90,
                 100, 110, 120, 130, 140, 150, 160, 180, 200]


@SCREW.generator
def socket_screws():
    for typ, std, max_m, max_ratio in (("SOCKET HEAD CAP", "ISO 4762", 36, 99), ("CSK SOCKET HEAD", "ISO 10642", 20, 10),
                                       ("BUTTON HEAD SOCKET", "ISO 7380", 16, 6), ("LOW HEAD SOCKET CAP", "DIN 7984", 24, 8)):
        for m, (lo, hi) in SHCS.items():
            if m_dia(m) > max_m:
                continue
            for L in lengths_between(lo, min(hi, max_ratio * m_dia(m)), SCREW_LENGTHS):
                for moc, grade, finish in SOCKET_GRADES:
                    if typ == "BUTTON HEAD SOCKET" and grade == "GR 12.9" and finish == "ZINC FLAKE":
                        continue
                    yield {"TYPE": typ, "DRIVE": "HEX SOCKET", "MOC": moc, "SPEC": grade, "DIA": m, "LENGTH": mm(L),
                           "FINISH": finish, "STANDARD": std}
    for typ, std in (("SET FLAT POINT", "ISO 4026"), ("SET CONE POINT", "ISO 4027"), ("SET DOG POINT", "ISO 4028"),
                     ("SET CUP POINT", "ISO 4029")):
        for m in ("M3", "M4", "M5", "M6", "M8", "M10", "M12", "M16", "M20", "M24"):
            d = m_dia(m)
            for L in lengths_between(max(3, d * 0.8), 6 * d, SCREW_LENGTHS):
                for moc, grade, finish in (("AS", "GR 45H", "BLACK"), ("SS", "A2-70", "PLAIN"), ("SS", "A4-70", "PLAIN")):
                    yield {"TYPE": typ, "DRIVE": "HEX SOCKET", "MOC": moc, "SPEC": grade, "DIA": m, "LENGTH": mm(L),
                           "FINISH": finish, "STANDARD": std}


@SCREW.generator
def machine_and_tapping_screws():
    for typ, drive, std in (("PAN HEAD", "PHILLIPS", "ISO 7045"), ("CSK HEAD", "PHILLIPS", "ISO 7046"),
                            ("CHEESE HEAD", "SLOTTED", "ISO 1207"), ("PAN HEAD", "SLOTTED", "ISO 1580"),
                            ("CSK HEAD", "SLOTTED", "ISO 2009"), ("PAN HEAD", "TORX", "ISO 14583")):
        for m in ("M2", "M2.5", "M3", "M4", "M5", "M6", "M8", "M10"):
            d = m_dia(m)
            for L in lengths_between(max(3, d), min(60, 10 * d), SCREW_LENGTHS):
                for moc, grade, finish in (("CS", "GR 4.8", "ZINC PLATED"), ("SS", "A2-70", "PLAIN"),
                                           ("SS", "A4-70", "PLAIN"), ("BRASS", "CUZN39PB3", "PLAIN")):
                    yield {"TYPE": typ, "DRIVE": drive, "MOC": moc, "SPEC": grade, "DIA": m, "LENGTH": mm(L),
                           "FINISH": finish, "STANDARD": std}
    for typ, drive, std in (("SELF TAPPING PAN HEAD", "PHILLIPS", "ISO 7049"), ("SELF TAPPING CSK HEAD", "PHILLIPS", "ISO 7050"),
                            ("SELF DRILLING HEX WASHER HEAD", "HEX", "DIN 7504 K"),
                            ("SELF DRILLING CSK HEAD", "PHILLIPS", "DIN 7504 P")):
        for st in ("ST2.9", "ST3.5", "ST3.9", "ST4.2", "ST4.8", "ST5.5", "ST6.3"):
            d = float(st[2:])
            for L in (6.5, 9.5, 13, 16, 19, 22, 25, 32, 38, 45, 50, 63, 75):
                if L < 2 * d or L > 15 * d:
                    continue
                for moc, finish in (("CS", "ZINC PLATED"), ("SS", "SS304"), ("SS", "SS410")):
                    yield {"TYPE": typ, "DRIVE": drive, "MOC": moc, "SPEC": finish if moc == "SS" else "CASE HARDENED",
                           "DIA": st, "LENGTH": mm(L), "FINISH": "PLAIN" if moc == "SS" else finish, "STANDARD": std}
    for d in (6, 8, 10, 12, 16):
        for L in (25, 40, 50, 65, 75, 100, 125, 150):
            if L < 4 * d:
                continue
            for finish in ("ZINC PLATED", "HDG"):
                yield {"TYPE": "HEX LAG", "DRIVE": "HEX", "MOC": "CS", "SPEC": "GR 4.6", "DIA": f"{d} MM",
                       "LENGTH": mm(L), "FINISH": finish, "STANDARD": "DIN 571"}


NUT_METRIC = ["M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24", "M27", "M30", "M33",
              "M36", "M39", "M42", "M45", "M48", "M52", "M56", "M64"]


@NUT.generator
def nuts():
    for m in NUT_METRIC:
        d = m_dia(m)
        for moc, grade, finishes in (("CS", "GR 8", ["BLACK", "ZINC PLATED", "HDG"]), ("CS", "GR 10", ["BLACK", "ZINC FLAKE"]),
                                     ("SS", "A2-70", ["PLAIN"]), ("SS", "A4-70", ["PLAIN"]), ("SS", "A4-80", ["PLAIN"])):
            for finish in finishes:
                yield {"TYPE": "HEX", "MOC": moc, "SPEC": grade, "DIA": m, "FINISH": finish, "STANDARD": "ISO 4032"}
                if moc == "CS":
                    yield {"TYPE": "HEX", "MOC": moc, "SPEC": f"IS 1367 {grade}", "DIA": m, "FINISH": finish,
                           "STANDARD": "IS 1364-3"}
                if d <= 36:
                    yield {"TYPE": "HEX THIN", "MOC": moc, "SPEC": grade.replace("GR 8", "GR 04").replace("GR 10", "GR 05"),
                           "DIA": m, "FINISH": finish, "STANDARD": "ISO 4035"}
                if d <= 36 and grade != "A4-80":
                    yield {"TYPE": "NYLON INSERT LOCK", "MOC": moc, "SPEC": grade, "DIA": m, "FINISH": finish,
                           "STANDARD": "ISO 7040"}
        if d >= 12:
            for moc, spec, finishes in (("AS", "ASTM A194 2H", ["PLAIN", "HDG", "ZINC PLATED", "PTFE COATED", "XYLAN COATED"]),
                                        ("AS", "ASTM A194 2HM", ["PLAIN", "PTFE COATED"]),
                                        ("AS", "ASTM A194 4", ["PLAIN"]), ("AS", "ASTM A194 7", ["PLAIN", "PTFE COATED"]),
                                        ("SS", "ASTM A194 8", ["PLAIN"]), ("SS", "ASTM A194 8M", ["PLAIN"])):
                for finish in finishes:
                    yield {"TYPE": "HEAVY HEX", "MOC": moc, "SPEC": spec, "DIA": m, "FINISH": finish,
                           "STANDARD": "ASME B18.2.2"}
        if d <= 24:
            for typ, std in (("HEX FLANGE", "DIN 6923"), ("DOME CAP", "DIN 1587"), ("SQUARE", "DIN 557"),
                             ("CASTLE", "DIN 935"), ("COUPLING", "DIN 6334"), ("WELD HEX", "DIN 929")):
                for moc, grade, finish in (("CS", "GR 8", "ZINC PLATED"), ("SS", "A2-70", "PLAIN"), ("SS", "A4-70", "PLAIN")):
                    yield {"TYPE": typ, "MOC": moc, "SPEC": grade, "DIA": m, "FINISH": finish, "STANDARD": std}
        if d <= 16:
            for moc, finish in (("CS", "ZINC PLATED"), ("SS", "PLAIN")):
                yield {"TYPE": "WING", "MOC": moc, "DIA": m, "FINISH": finish, "STANDARD": "DIN 315"}
        if d <= 64 and d >= 8:
            for moc, finish in (("CS", "ZINC PLATED"), ("SS", "PLAIN")):
                yield {"TYPE": "EYE", "MOC": moc, "SPEC": "C15E FORGED" if moc == "CS" else "SS304", "DIA": m,
                       "FINISH": finish, "STANDARD": "DIN 582"}
    for label, d in INCH_BOLTS:
        for spec, finishes in (("ASTM A194 2H", ["PLAIN", "HDG", "PTFE COATED", "XYLAN COATED"]), ("ASTM A194 2HM", ["PLAIN"]),
                               ("ASTM A194 4", ["PLAIN"]), ("ASTM A194 7", ["PLAIN"]), ("ASTM A194 8", ["PLAIN"]),
                               ("ASTM A194 8M", ["PLAIN"]), ("ASTM A563 GR A", ["PLAIN", "HDG"])):
            for finish in finishes:
                yield {"TYPE": "HEAVY HEX", "MOC": "SS" if spec.endswith(("8", "8M")) else "AS", "SPEC": spec,
                       "DIA": inch_thread(label, d), "FINISH": finish, "STANDARD": "ASME B18.2.2"}


@WASHER.generator
def washers():
    for m in NUT_METRIC:
        d = m_dia(m)
        for moc, spec, finish in (("CS", "HV 200", "BLACK"), ("CS", "HV 200", "ZINC PLATED"), ("CS", "HV 200", "HDG"),
                                  ("CS", "HV 300", "BLACK"), ("SS", "SS304", "PLAIN"), ("SS", "SS316", "PLAIN")):
            yield {"TYPE": "FLAT", "MOC": moc, "SPEC": spec, "SIZE": f"FOR {m}", "FINISH": finish, "STANDARD": "ISO 7089"}
            if d <= 24 and spec != "HV 300":
                yield {"TYPE": "FENDER", "MOC": moc, "SPEC": spec, "SIZE": f"FOR {m}", "FINISH": finish,
                       "STANDARD": "DIN 9021"}
        for moc, spec, finish in (("CS", "IS 2062", "BLACK"), ("CS", "IS 2062", "HDG"), ("CS", "IS 2062", "ZINC PLATED"),
                                  ("SS", "SS304", "PLAIN")):
            yield {"TYPE": "PLAIN", "MOC": moc, "SPEC": spec, "SIZE": f"FOR {m}", "FINISH": finish, "STANDARD": "IS 2016"}
        if d <= 36:
            for moc, spec, finish in (("CS", "SPRING STEEL", "BLACK"), ("CS", "SPRING STEEL", "ZINC PLATED"),
                                      ("CS", "SPRING STEEL", "HDG"), ("SS", "SS304", "PLAIN"), ("SS", "SS316", "PLAIN")):
                yield {"TYPE": "SPRING", "MOC": moc, "SPEC": spec, "SIZE": f"FOR {m}", "FINISH": finish,
                       "STANDARD": "DIN 127 B"}
            for finish in ("BLACK", "HDG", "ZINC PLATED"):
                yield {"TYPE": "SPRING", "MOC": "CS", "SPEC": "SPRING STEEL", "SIZE": f"FOR {m}", "FINISH": finish,
                       "STANDARD": "IS 3063 TYPE B"}
        if 6 <= d <= 36:
            for moc, finish in (("CS", "ZINC FLAKE"), ("SS", "SS316")):
                yield {"TYPE": "WEDGE LOCK PAIR", "MOC": moc, "SIZE": f"FOR {m}", "FINISH": finish, "STANDARD": "DIN 25201"}
            for typ, std in (("TAPER FOR CHANNEL", "IS 5372"), ("TAPER FOR I BEAM", "IS 5374")):
                for finish in ("BLACK", "HDG"):
                    yield {"TYPE": typ, "MOC": "CS", "SPEC": "IS 2062", "SIZE": f"FOR {m}", "FINISH": finish,
                           "STANDARD": std}
    for label, d in INCH_BOLTS:
        for finish in ("PLAIN", "HDG", "PTFE COATED"):
            yield {"TYPE": "HARDENED FLAT", "MOC": "CS", "SPEC": "ASTM F436", "SIZE": f'FOR {label}', "FINISH": finish,
                   "STANDARD": "ASTM F436"}
    for od, id_, thk in ((8, 4.2, 0.4), (10, 5.2, 0.5), (12.5, 6.2, 0.7), (16, 8.2, 0.9), (20, 10.2, 1.1),
                         (25, 12.2, 1.5), (31.5, 16.3, 1.75), (40, 20.4, 2.25), (50, 25.4, 3), (63, 31, 3.5),
                         (71, 36, 4), (80, 41, 5), (100, 51, 6), (125, 64, 8)):
        for moc in ("50CRV4", "SS301"):
            yield {"TYPE": "DISC SPRING", "MOC": moc, "SIZE": f"OD {fmt(od)} X ID {fmt(id_)} MM", "THICKNESS": f"THK {fmt(thk)} MM",
                   "STANDARD": "DIN 2093"}
    for m in ("M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24", "M27", "M30", "M33", "M36", "M42", "M48"):
        for typ in ("BONDED SEAL", "COPPER SEALING"):
            yield {"TYPE": typ, "MOC": "CS NITRILE" if typ == "BONDED SEAL" else "COPPER", "SIZE": f"FOR {m}",
                   "STANDARD": "DIN 7603" if typ == "COPPER SEALING" else ""}


@ANCHOR.generator
def anchors():
    for typ, sizes, std in (("WEDGE", ("M8", "M10", "M12", "M16", "M20", "M24"), "ETA OPTION 1"),
                            ("SLEEVE", ("M6", "M8", "M10", "M12", "M16"), ""),
                            ("DROP IN", ("M6", "M8", "M10", "M12", "M16", "M20"), ""),
                            ("CHEMICAL STUD", ("M8", "M10", "M12", "M16", "M20", "M24", "M30"), "ETA")):
        for m in sizes:
            d = m_dia(m)
            for L in [L for L in (25, 30, 40, 50, 60, 65, 75, 80, 95, 100, 110, 120, 125, 140, 150, 160, 170, 180, 200,
                                  220, 250, 300, 350, 380) if (typ == "DROP IN" and L <= 4 * d) or (typ != "DROP IN" and 6 * d <= L <= 15 * d)]:
                for moc, finish in (("CS", "ZINC PLATED"), ("CS", "HDG"), ("SS", "SS316")):
                    yield {"TYPE": typ, "MOC": moc, "DIA": m, "LENGTH": mm(L), "FINISH": finish if moc == "CS" else "",
                           "STANDARD": std}


@RIVET.generator
def rivets():
    for d in (3.2, 4.0, 4.8, 6.4):
        for L in (6, 8, 10, 12, 14, 16, 18, 20, 25, 30):
            if L < 1.5 * d:
                continue
            for moc in ("ALUMINIUM/STEEL", "ALUMINIUM/ALUMINIUM", "SS304/SS304", "STEEL/STEEL"):
                for typ in ("BLIND DOME HEAD", "BLIND CSK HEAD"):
                    yield {"TYPE": typ, "MOC": moc, "DIA": mm(d), "LENGTH": mm(L), "STANDARD": "ISO 15977"}
    for d in (3, 4, 5, 6, 8, 10, 12, 16, 20):
        for L in (6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 50, 60, 80):
            if not 1.5 * d <= L <= 6 * d:
                continue
            for moc in ("MS", "COPPER", "ALUMINIUM"):
                for typ, std in (("SOLID ROUND HEAD", "IS 2155"), ("SOLID CSK HEAD", "IS 2155")):
                    yield {"TYPE": typ, "MOC": moc, "DIA": mm(d), "LENGTH": mm(L), "STANDARD": std}


@PIN.generator
def pins():
    for d in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20):
        for L in (4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100,
                  120, 140, 160, 180, 200):
            if not 2 * d <= L <= 10 * d:
                continue
            for typ, std, mats in (("DOWEL HARDENED M6", "ISO 8734", (("AS", "HARDENED"), ("SS", "SS420"))),
                                   ("DOWEL H8", "ISO 2338", (("CS", "BRIGHT"), ("SS", "SS304"))),
                                   ("SPRING SLOTTED HEAVY", "ISO 8752", (("CS", "PLAIN"), ("SS", "SS420"))),
                                   ("SPRING COILED", "ISO 8750", (("CS", "PLAIN"), ("SS", "SS420"))),
                                   ("TAPER", "ISO 2339", (("CS", "BRIGHT"),))):
                for moc, finish in mats:
                    yield {"TYPE": typ, "MOC": moc, "DIA": mm(d), "LENGTH": mm(L), "FINISH": finish, "STANDARD": std}
    for d in (1, 1.6, 2, 2.5, 3.2, 4, 5, 6.3, 8, 10):
        for L in (10, 12, 16, 20, 25, 32, 40, 50, 63, 71, 80, 100, 125):
            if not 4 * d <= L <= 16 * d:
                continue
            for moc, finish in (("CS", "ZINC PLATED"), ("SS", "SS304")):
                yield {"TYPE": "COTTER SPLIT", "MOC": moc, "DIA": mm(d), "LENGTH": mm(L), "FINISH": finish,
                       "STANDARD": "ISO 1234"}
    for d in (4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 30):
        for L in (10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120):
            if not 2 * d <= L <= 6 * d:
                continue
            for moc, finish in (("CS", "ZINC PLATED"), ("SS", "SS304")):
                yield {"TYPE": "CLEVIS WITH HEAD", "MOC": moc, "DIA": mm(d), "LENGTH": mm(L), "FINISH": finish,
                       "STANDARD": "ISO 2341 B"}


@CIRCLIP.generator
def retaining_rings():
    shafts = list(range(3, 41)) + list(range(42, 101, 2)) + list(range(105, 201, 5))
    for d in shafts:
        for moc, finish in (("SPRING STEEL", "PHOSPHATED"), ("SS", "SS420")):
            yield {"TYPE": "EXTERNAL", "MOC": moc, "SIZE": f"FOR SHAFT {d} MM", "FINISH": finish, "STANDARD": "DIN 471"}
            if d >= 8:
                yield {"TYPE": "INTERNAL", "MOC": moc, "SIZE": f"FOR BORE {d} MM", "FINISH": finish, "STANDARD": "DIN 472"}
    for d in (1.2, 1.5, 1.9, 2.3, 3.2, 4, 5, 6, 7, 8, 9, 10, 12, 15, 19, 24):
        yield {"TYPE": "E CLIP", "MOC": "SPRING STEEL", "SIZE": f"{fmt(d)} MM", "FINISH": "PHOSPHATED", "STANDARD": "DIN 6799"}


# DIN 6885 A parallel keys: section b x h and the standard length range
PARALLEL_KEYS = [((2, 2), 6, 20), ((3, 3), 6, 36), ((4, 4), 8, 45), ((5, 5), 10, 56), ((6, 6), 14, 70), ((8, 7), 18, 90),
                 ((10, 8), 22, 110), ((12, 8), 28, 140), ((14, 9), 36, 160), ((16, 10), 45, 180), ((18, 11), 50, 200),
                 ((20, 12), 56, 220), ((22, 14), 63, 250), ((25, 14), 70, 280), ((28, 16), 80, 320), ((32, 18), 90, 360),
                 ((36, 20), 100, 400), ((40, 22), 110, 400), ((45, 25), 125, 400), ((50, 28), 140, 400)]
KEY_LENGTHS = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56, 63, 70, 80, 90, 100, 110, 125, 140, 160,
               180, 200, 220, 250, 280, 320, 360, 400]


@KEY.generator
def keys():
    for (b, h), lo, hi in PARALLEL_KEYS:
        for L in lengths_between(lo, hi, KEY_LENGTHS):
            for moc in ("C45 BRIGHT", "SS304", "SS316"):
                yield {"TYPE": "PARALLEL TYPE A", "MOC": moc, "SIZE": f"{b} X {h} MM", "LENGTH": mm(L), "STANDARD": "DIN 6885"}
            if b >= 4:
                yield {"TYPE": "GIB HEAD TAPER", "MOC": "C45 BRIGHT", "SIZE": f"{b} X {h} MM", "LENGTH": mm(L),
                       "STANDARD": "DIN 6887"}
    for b, h, dia in ((2, 2.6, 7), (2, 3.7, 10), (3, 3.7, 10), (3, 5, 13), (3, 6.5, 16), (4, 5, 13), (4, 6.5, 16),
                      (4, 7.5, 19), (5, 6.5, 16), (5, 7.5, 19), (5, 9, 22), (6, 7.5, 19), (6, 9, 22), (6, 10, 25),
                      (6, 11, 28), (8, 9, 22), (8, 11, 28), (8, 13, 32), (10, 13, 32), (10, 15, 38), (10, 16, 45)):
        for moc in ("C45 BRIGHT", "SS304"):
            yield {"TYPE": "WOODRUFF", "MOC": moc, "SIZE": f"{b} X {fmt(h)} X DIA {dia} MM", "STANDARD": "DIN 6888"}


@ROD.generator
def threaded_rods():
    for m in ("M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24", "M27", "M30", "M33", "M36",
              "M42", "M48"):
        for moc, spec, finish in (("CS", "GR 4.8", "ZINC PLATED"), ("CS", "GR 4.8", "HDG"), ("CS", "GR 8.8", "BLACK"),
                                  ("CS", "GR 10.9", "BLACK"), ("SS", "A2-70", "PLAIN"), ("SS", "A4-70", "PLAIN"),
                                  ("AS", "ASTM A193 B7", "PLAIN"), ("SS", "ASTM A193 B8M CL1", "PLAIN")):
            for L in (1000, 2000, 3000):
                yield {"TYPE": "THREADED", "MOC": moc, "SPEC": spec, "DIA": m, "LENGTH": mm(L), "FINISH": finish,
                       "STANDARD": "DIN 975"}


# ======================================================================== rigging
WLL = [0.33, 0.5, 0.75, 1, 1.5, 2, 3.25, 4.75, 6.5, 8.5, 9.5, 12, 13.5, 17, 25, 35, 55, 85]


@SHACKLE.generator
def shackles():
    for typ in ("BOW", "DEE"):
        for pin in ("SCREW PIN", "SAFETY BOLT"):
            for wll in WLL:
                for moc, finish in (("CS", "HDG"), ("AS", "HDG"), ("SS", "SS316")):
                    if moc == "SS" and wll > 8.5:
                        continue
                    yield {"TYPE": typ, "PIN": pin, "MOC": moc, "CAPACITY": f"WLL {fmt(wll)} T",
                           "FINISH": finish if moc != "SS" else "", "STANDARD": "US FED RR-C-271"}


@TURNBUCKLE.generator
def turnbuckles():
    for typ in ("HOOK AND EYE", "EYE AND EYE", "JAW AND JAW", "HOOK AND HOOK"):
        for m in ("M6", "M8", "M10", "M12", "M16", "M20", "M24", "M30", "M36"):
            for moc, finish in (("CS", "HDG"), ("SS", "SS316")):
                yield {"TYPE": typ, "MOC": moc, "DIA": m, "FINISH": finish if moc == "CS" else "", "STANDARD": "DIN 1480"}


@HOOK.generator
def hooks():
    for typ in ("EYE SLING WITH LATCH", "CLEVIS SLING WITH LATCH", "EYE SELF LOCKING", "SWIVEL WITH LATCH"):
        for wll in (1, 1.5, 2, 3, 5, 8, 10, 12.5, 15, 20, 25):
            yield {"TYPE": typ, "MOC": "ALLOY STEEL GRADE 80", "CAPACITY": f"WLL {fmt(wll)} T", "FINISH": "PAINTED",
                   "STANDARD": "EN 1677"}


@WIRE_ROPE.generator
def wire_ropes():
    for construction in ("6X19", "6X36", "6X37", "8X36", "19X7 NON ROTATING", "35X7 NON ROTATING"):
        for core in ("FC", "IWRC"):
            for d in (6, 8, 10, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 32, 36, 40, 44, 48, 52):
                for grade, finish in (("1770 GRADE", "UNGALVANISED"), ("1770 GRADE", "GALVANISED"), ("1960 GRADE", "UNGALVANISED")):
                    if construction.endswith("NON ROTATING") and core == "FC":
                        continue
                    yield {"CONSTRUCTION": construction, "CORE": core, "MOC": "STEEL", "DIA": f"DIA {d} MM",
                           "GRADE": grade, "FINISH": finish, "STANDARD": "IS 2266"}
    for construction in ("7X7", "7X19", "1X19"):
        for d in (1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12):
            yield {"CONSTRUCTION": construction, "MOC": "SS316", "DIA": f"DIA {fmt(d)} MM"}


@SLING.generator
def slings():
    for wll in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20):
        for L in (1, 1.5, 2, 3, 4, 5, 6, 8, 10):
            yield {"TYPE": "WEBBING ENDLESS ROUND", "MOC": "POLYESTER", "CAPACITY": f"WLL {wll} T", "LENGTH": f"{fmt(L)} M",
                   "STANDARD": "EN 1492-2"}
            yield {"TYPE": "WEBBING FLAT EYE AND EYE", "MOC": "POLYESTER", "CAPACITY": f"WLL {wll} T",
                   "LENGTH": f"{fmt(L)} M", "STANDARD": "EN 1492-1"}
    for legs in ("1 LEG", "2 LEG", "4 LEG"):
        for wll in (1.12, 2, 3.15, 5.3, 8, 11.2, 15, 22.4):
            for L in (1, 1.5, 2, 3, 4, 5):
                yield {"TYPE": f"CHAIN {legs}", "MOC": "ALLOY STEEL GRADE 80", "CAPACITY": f"WLL {fmt(wll)} T",
                       "LENGTH": f"{fmt(L)} M", "STANDARD": "EN 818-4"}
                yield {"TYPE": f"WIRE ROPE {legs}", "MOC": "STEEL", "CAPACITY": f"WLL {fmt(wll)} T",
                       "LENGTH": f"{fmt(L)} M", "STANDARD": "EN 13414-1"}


@CLAMP.generator
def clamps():
    for d in (3, 5, 6, 8, 10, 13, 16, 19, 22, 26, 30, 34, 40):
        for moc, finish in (("CS", "GALVANISED"), ("SS", "SS316")):
            yield {"TYPE": "WIRE ROPE CLIP", "MOC": moc, "SIZE": f"FOR {d} MM ROPE", "FINISH": finish, "STANDARD": "DIN 741"}
    for lo, hi in ((8, 12), (10, 16), (12, 20), (16, 25), (20, 32), (25, 40), (32, 50), (40, 60), (50, 70), (60, 80),
                   (70, 90), (80, 100), (90, 110), (100, 120), (110, 130), (120, 140), (130, 150), (150, 170), (170, 190),
                   (190, 210)):
        for moc, finish in (("SS304", "W4"), ("SS316", "W5"), ("CS", "W1 ZINC PLATED")):
            for width in ("9 MM", "12 MM"):
                yield {"TYPE": "HOSE WORM DRIVE", "MOC": moc, "SIZE": f"RANGE {lo}-{hi} MM BAND {width}", "FINISH": finish,
                       "STANDARD": "DIN 3017"}
    for d in (15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600):
        for typ in ("PIPE U TYPE", "PIPE 2 BOLT", "PIPE 3 BOLT HEAVY", "PIPE RISER"):
            for moc, finish in (("CS", "HDG"), ("CS", "PAINTED"), ("SS", "SS304")):
                yield {"TYPE": typ, "MOC": moc, "SIZE": f"FOR {DN_TO_NPS[d]} PIPE", "FINISH": finish, "STANDARD": "MSS SP-58"}


@THIMBLE.generator
def thimbles():
    for d in (6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 32, 36, 40):
        for moc, finish in (("CS", "GALVANISED"), ("SS", "SS316")):
            for typ in ("STANDARD", "HEAVY DUTY"):
                yield {"TYPE": typ, "MOC": moc, "SIZE": f"FOR {d} MM ROPE", "FINISH": finish, "STANDARD": "DIN 6899"}
