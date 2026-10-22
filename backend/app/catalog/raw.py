"""Raw and semi-finished material: plates, sheets, bars, structural sections, wire, mesh, plastics."""
from app.catalog import noun
from app.catalog.data import fmt

G_PLATE, G_BAR, G_STRUCT, G_WIRE, G_PLASTIC = ("PLATES AND SHEETS", "BARS AND RODS", "STRUCTURAL STEEL", "WIRE AND MESH",
                                               "PLASTICS AND RUBBER")

PLATE = noun("PLATE", G_PLATE, "KG", ("TYPE", "MOC", "SPEC", "THICKNESS", "SIZE", "FINISH", "FEATURE"))
SHEET = noun("SHEET", G_PLATE, "KG", ("TYPE", "MOC", "SPEC", "THICKNESS", "SIZE", "FINISH", "COLOR"))
STRIP = noun("STRIP", G_PLATE, "KG", ("TYPE", "MOC", "SPEC", "SIZE", "FINISH"))
BAR = noun("BAR", G_BAR, "KG", ("TYPE", "CONDITION", "MOC", "SPEC", "SIZE", "LENGTH", "FINISH"))
ANGLE = noun("ANGLE", G_STRUCT, "KG", ("TYPE", "MOC", "SPEC", "SIZE", "FINISH", "STANDARD"))
CHANNEL = noun("CHANNEL", G_STRUCT, "KG", ("TYPE", "MOC", "SPEC", "SIZE", "FINISH", "STANDARD"))
BEAM = noun("BEAM", G_STRUCT, "KG", ("TYPE", "MOC", "SPEC", "SIZE", "FINISH", "STANDARD"))
HOLLOW = noun("HOLLOW SECTION", G_STRUCT, "KG", ("TYPE", "MOC", "SPEC", "SIZE", "THICKNESS", "FINISH", "STANDARD"))
GRATING = noun("GRATING", G_STRUCT, "SQM", ("TYPE", "MOC", "BEARING BAR", "PITCH", "FINISH", "STANDARD"))
# shared with welding filler wire (consumables)
WIRE = noun("WIRE", G_WIRE, "KG", ("TYPE", "MOC", "SPEC", "DIA", "FINISH", "PACK", "STANDARD", "MAKE"))
MESH = noun("MESH", G_WIRE, "SQM", ("TYPE", "MOC", "SIZE", "WIRE DIA", "FINISH"))

# ---------------------------------------------------------------- plates
CS_THK = [5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 36, 40, 45, 50, 56, 60, 63, 65, 70, 75, 80, 90, 100,
          110, 120, 125, 140, 150, 160, 180, 200]
SS_THK = [3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100]
AL_THK = [3, 4, 5, 6, 8, 10, 12, 15, 16, 20, 25, 30, 35, 40, 50, 60, 80, 100]
PLATE_SPECS = [
    # (moc, spec, thicknesses, sizes, finishes, features)
    *[("CS", s, CS_THK, ["2500 X 6300 MM", "2500 X 10000 MM", "2500 X 12500 MM"], [""], [""])
      for s in ("IS 2062 E250 BR", "IS 2062 E250 A", "IS 2062 E350 BR", "IS 2062 E410 C", "ASTM A36", "ASTM A283 GR C",
                "ASTM A572 GR 50", "EN 10025 S275JR", "EN 10025 S355J2")],
    *[("CS", s, CS_THK, ["2500 X 6300 MM", "2500 X 10000 MM", "2500 X 12500 MM"], [""],
       ["", "IBR", "NORMALISED", "HIC TESTED NACE MR0175"])
      for s in ("ASTM A516 GR 60", "ASTM A516 GR 70", "ASTM A515 GR 70", "ASTM A285 GR C", "ASTM A537 CL 1",
                "IS 2002 GR 2")],
    *[("AS", s, CS_THK[:28], ["2500 X 6300 MM", "2500 X 10000 MM"], [""], ["", "IBR"])
      for s in ("ASTM A387 GR 11 CL 2", "ASTM A387 GR 22 CL 2", "ASTM A387 GR 5 CL 2", "ASTM A387 GR 91 CL 2",
                "ASTM A204 GR B")],
    *[("SS", s, SS_THK, ["1250 X 2500 MM", "1500 X 6000 MM", "2000 X 6000 MM"], ["NO 1", "2B"], [""])
      for s in ("ASTM A240 TP304", "ASTM A240 TP304L", "ASTM A240 TP316", "ASTM A240 TP316L", "ASTM A240 TP321",
                "ASTM A240 TP347", "ASTM A240 TP310S", "ASTM A240 TP317L", "ASTM A240 TP904L", "ASTM A240 TP410S",
                "ASTM A240 TP430")],
    *[(m, s, SS_THK, ["1250 X 2500 MM", "2000 X 6000 MM"], ["NO 1"], [""])
      for m, s in (("DSS", "ASTM A240 S31803"), ("DSS", "ASTM A240 S32205"), ("SDSS", "ASTM A240 S32750"),
                   ("MONEL 400", "ASTM B127 N04400"), ("INCONEL 625", "ASTM B443 N06625"),
                   ("HASTELLOY C276", "ASTM B575 N10276"), ("TITANIUM", "ASTM B265 GR 2"))],
    *[("ALUMINIUM", s, AL_THK, ["1250 X 2500 MM", "1500 X 3000 MM"], [""], [""])
      for s in ("AA 1100 H14", "AA 5052 H32", "AA 5083 H111", "AA 6061 T6", "AA 6082 T6")],
    ("COPPER", "C11000 ETP", [3, 4, 5, 6, 8, 10, 12, 15, 20, 25], ["1000 X 2000 MM"], [""], [""]),
    ("BRASS", "C26000", [3, 4, 5, 6, 8, 10, 12, 15, 20], ["1000 X 2000 MM"], [""], [""]),
    *[("CS", s, [6, 8, 10, 12, 15, 16, 20, 25, 30, 40, 50], ["2000 X 6000 MM"], [""], [""])
      for s in ("WEAR RESISTANT 400 BHN", "WEAR RESISTANT 500 BHN")],
]


@PLATE.generator
def plates():
    for moc, spec, thicknesses, sizes, finishes, features in PLATE_SPECS:
        for t in thicknesses:
            for size in sizes:
                for finish in finishes:
                    if finish == "2B" and t > 6:
                        continue
                    for feat in features:
                        yield {"MOC": moc, "SPEC": spec, "THICKNESS": f"THK {fmt(t)} MM", "SIZE": size,
                               "FINISH": finish, "FEATURE": feat}
    for moc, spec, thicknesses in (("MS", "IS 3502", (4, 5, 6, 8, 10, 12)), ("SS", "SS304", (3, 4, 5, 6)),
                                   ("ALUMINIUM", "AA 5052 TREAD", (2, 3, 4, 5, 6))):
        for t in thicknesses:
            for size in ("1250 X 2500 MM", "1500 X 6000 MM"):
                yield {"TYPE": "CHEQUERED", "MOC": moc, "SPEC": spec, "THICKNESS": f"THK {t} MM", "SIZE": size}
    for moc in ("MS", "SS304", "SS316", "ALUMINIUM"):
        for t in (1, 1.5, 2, 3, 4, 5, 6):
            for hole, pitch in ((2, 4), (3, 5), (5, 8), (6, 9), (8, 12), (10, 15)):
                yield {"TYPE": "PERFORATED", "MOC": moc, "THICKNESS": f"THK {fmt(t)} MM",
                       "SIZE": f"HOLE {hole} MM PITCH {pitch} MM 1250 X 2500 MM"}


SHEET_THK = [0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 1.6, 2.0, 2.5, 3.0]
SHEET_TYPES = [
    ("CRCA", "CS", "IS 513 CR4", SHEET_THK, ["1250 X 2500 MM", "1220 X 2440 MM"], [""]),
    ("HR", "CS", "IS 1079 HR2", [1.6, 2.0, 2.5, 3.0, 4.0, 5.0], ["1250 X 2500 MM", "1500 X 6000 MM"], [""]),
    ("GI", "CS", "IS 277 Z120", SHEET_THK, ["1220 X 2440 MM", "900 X 2500 MM"], [""]),
    ("GI", "CS", "IS 277 Z275", SHEET_THK, ["1220 X 2440 MM", "900 X 2500 MM"], [""]),
    ("GALVALUME", "CS", "AZ150", [0.35, 0.4, 0.45, 0.5, 0.6], ["1220 X 2440 MM"], [""]),
    *[("STAINLESS", "SS", s, SHEET_THK, ["1250 X 2500 MM", "1219 X 2438 MM"], ["2B", "BA", "NO 4", "HAIRLINE"])
      for s in ("ASTM A240 TP304", "ASTM A240 TP304L", "ASTM A240 TP316", "ASTM A240 TP316L", "ASTM A240 TP430",
                "ASTM A240 TP409")],
    *[("ALUMINIUM", "ALUMINIUM", s, SHEET_THK, ["1220 X 2440 MM", "1000 X 2000 MM"], ["MILL", "STUCCO"])
      for s in ("AA 1100 H14", "AA 3003 H14", "AA 5052 H32")],
    ("COPPER", "COPPER", "C11000 ETP", [0.5, 0.8, 1.0, 1.5, 2.0, 3.0], ["1000 X 2000 MM"], [""]),
    ("BRASS", "BRASS", "C26000", [0.5, 0.8, 1.0, 1.5, 2.0, 3.0], ["1000 X 2000 MM"], [""]),
]
RAL = ["RAL 9002 GREY WHITE", "RAL 5012 LIGHT BLUE", "RAL 6005 MOSS GREEN", "RAL 3009 OXIDE RED", "RAL 9006 SILVER",
       "RAL 1015 LIGHT IVORY"]


@SHEET.generator
def metal_sheets():
    for typ, moc, spec, thicknesses, sizes, finishes in SHEET_TYPES:
        for t in thicknesses:
            for size in sizes:
                for finish in finishes:
                    yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "THICKNESS": f"THK {fmt(t)} MM", "SIZE": size,
                           "FINISH": finish}
    for t in (0.35, 0.4, 0.45, 0.5, 0.6):
        for profile in ("PLAIN", "TRAPEZOIDAL PROFILE"):
            for color in RAL:
                yield {"TYPE": f"PPGI {profile}", "MOC": "CS", "SPEC": "IS 14246", "THICKNESS": f"THK {fmt(t)} MM",
                       "SIZE": "1220 MM WIDE", "COLOR": color}


PLASTIC_SHEETS = [
    ("PTFE VIRGIN", [1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50]),
    ("PTFE GLASS FILLED", [2, 3, 5, 6, 10, 15, 20, 25]),
    ("UHMWPE", [3, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50]),
    ("NYLON 6 CAST", [5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100]),
    ("ACETAL POM", [3, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50]),
    ("PP", [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25]),
    ("HDPE", [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25]),
    ("PVC RIGID", [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]),
    ("POLYCARBONATE CLEAR", [2, 3, 4, 5, 6, 8, 10, 12]),
    ("ACRYLIC CLEAR", [2, 3, 4, 5, 6, 8, 10, 12, 15, 20]),
    ("BAKELITE", [2, 3, 5, 6, 8, 10, 12, 15, 20, 25]),
    ("FRP", [2, 3, 4, 5, 6, 8, 10]),
    ("PEEK", [3, 5, 6, 8, 10, 12, 15, 20]),
]
RUBBER_SHEETS = ["NEOPRENE", "NITRILE", "EPDM", "NATURAL RUBBER", "SILICONE", "VITON", "SBR"]


@SHEET.generator(group=G_PLASTIC)
def plastic_and_rubber_sheets():
    for mat, thicknesses in PLASTIC_SHEETS:
        for t in thicknesses:
            yield {"TYPE": "ENGINEERING PLASTIC", "MOC": mat, "THICKNESS": f"THK {fmt(t)} MM", "SIZE": "1000 X 2000 MM"}
    for mat in RUBBER_SHEETS:
        for t in (1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25):
            for hardness in ("60 SHORE A", "70 SHORE A"):
                yield {"TYPE": "RUBBER", "MOC": mat, "SPEC": hardness, "THICKNESS": f"THK {fmt(t)} MM", "SIZE": "1000 MM WIDE ROLL"}
    for t in (1.5, 2, 3):
        for mat in ("CNAF", "EXPANDED GRAPHITE WITH SS316 INSERT", "EXPANDED PTFE"):
            yield {"TYPE": "GASKET", "MOC": mat, "THICKNESS": f"THK {fmt(t)} MM", "SIZE": "1500 X 1500 MM"}


@STRIP.generator
def strips():
    for moc, spec in (("SS", "SS304"), ("SS", "SS316"), ("SS", "SS301 SPRING HARD"), ("COPPER", "C11000"),
                      ("BRASS", "C26000"), ("CS", "SPRING STEEL C75"), ("CS", "CRCA")):
        for t in (0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0):
            for w in (10, 12, 15, 20, 25, 30, 40, 50, 75, 100):
                yield {"MOC": moc, "SPEC": spec, "SIZE": f"{w} X {fmt(t)} MM"}
    for moc in ("GI", "COPPER"):
        for w, t in ((25, 3), (25, 6), (32, 6), (40, 6), (50, 6), (50, 10), (75, 10)):
            yield {"TYPE": "EARTHING", "MOC": moc, "SIZE": f"{w} X {t} MM", "FINISH": "HDG" if moc == "GI" else "TINNED"}


# ---------------------------------------------------------------- bars
ROUND_DIA = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 35, 36, 38, 40, 42, 45, 50, 55, 60, 63, 65, 70, 75, 80,
             85, 90, 95, 100, 110, 120, 125, 130, 140, 150, 160, 170, 180, 200, 220, 250, 280, 300]
BAR_STEELS = [
    ("CS", "EN8"), ("CS", "EN9"), ("CS", "C45"), ("CS", "AISI 1018"), ("CS", "IS 2062 E250"), ("CS", "EN1A FREE CUTTING"),
    ("AS", "EN19"), ("AS", "EN24"), ("AS", "EN31"), ("AS", "EN353"), ("AS", "EN36"), ("AS", "20MNCR5"), ("AS", "16MNCR5"),
    ("AS", "42CRMO4"), ("AS", "AISI 4140"), ("AS", "AISI 4340"),
    ("TOOL STEEL", "D2"), ("TOOL STEEL", "D3"), ("TOOL STEEL", "H13"), ("TOOL STEEL", "OHNS O1"), ("TOOL STEEL", "HSS M2"),
]
BAR_SS = [("SS", g) for g in ("SS304", "SS304L", "SS316", "SS316L", "SS303", "SS410", "SS420", "SS431", "17-4 PH",
                              "SS321", "SS310S", "DUPLEX 2205")]
BAR_NONFERROUS = [("BRASS", "CZ121"), ("ALUMINIUM", "AA 6061 T6"), ("ALUMINIUM", "AA 6082 T6"), ("ALUMINIUM", "AA 2014 T6"),
                  ("COPPER", "C11000 ETP"), ("PHOSPHOR BRONZE", "PB1"), ("GUN METAL", "LG2"), ("ALUMINIUM BRONZE", "AB2"),
                  ("MONEL", "MONEL 400"), ("INCONEL", "INCONEL 625"), ("TITANIUM", "GR 5")]


@BAR.generator
def round_bars():
    for moc, spec in BAR_STEELS:
        for d in ROUND_DIA:
            for cond in (("BRIGHT", "BLACK") if d <= 100 else ("BLACK", "PEELED")):
                yield {"TYPE": "ROUND", "CONDITION": cond, "MOC": moc, "SPEC": spec, "SIZE": f"DIA {d} MM"}
    for moc, spec in BAR_SS:
        for d in ROUND_DIA:
            for cond in (("BRIGHT", "BLACK") if d <= 100 else ("PEELED",)):
                yield {"TYPE": "ROUND", "CONDITION": cond, "MOC": moc, "SPEC": spec, "SIZE": f"DIA {d} MM"}
    for moc, spec in BAR_NONFERROUS:
        for d in ROUND_DIA[:40]:
            yield {"TYPE": "ROUND", "MOC": moc, "SPEC": spec, "SIZE": f"DIA {d} MM"}
    for d in (8, 10, 12, 16, 20, 25, 28, 32, 36, 40):
        for grade in ("FE 500", "FE 500D", "FE 550D"):
            yield {"TYPE": "TMT REBAR", "MOC": "CS", "SPEC": f"IS 1786 {grade}", "SIZE": f"DIA {d} MM", "LENGTH": "12 M"}


HEX_AF = [8, 10, 11, 13, 14, 17, 19, 22, 24, 27, 30, 32, 36, 41, 46, 50, 55, 60, 65, 70, 75]
SQUARE = [6, 8, 10, 12, 16, 20, 25, 30, 32, 40, 50, 60, 63, 75, 80, 100, 125, 150]
FLAT_W = [10, 12, 16, 20, 25, 30, 32, 40, 45, 50, 60, 65, 75, 80, 90, 100, 110, 125, 150, 200, 250, 300]
FLAT_T = [3, 5, 6, 8, 10, 12, 16, 20, 25, 32, 40, 50]


@BAR.generator
def shaped_bars():
    shaped = BAR_STEELS[:10] + BAR_SS[:8] + [("BRASS", "CZ121"), ("ALUMINIUM", "AA 6061 T6")]
    for moc, spec in shaped:
        for af in HEX_AF:
            yield {"TYPE": "HEX", "CONDITION": "BRIGHT", "MOC": moc, "SPEC": spec, "SIZE": f"AF {af} MM"}
        for s in SQUARE:
            yield {"TYPE": "SQUARE", "CONDITION": "BRIGHT" if s <= 75 else "BLACK", "MOC": moc, "SPEC": spec,
                   "SIZE": f"{s} X {s} MM"}
    for moc, spec in (("CS", "IS 2062 E250"), ("CS", "EN8"), ("SS", "SS304"), ("SS", "SS316"), ("ALUMINIUM", "AA 6063 T6"),
                      ("COPPER", "C11000 ETP")):
        for w in FLAT_W:
            for t in FLAT_T:
                if t >= w or t < w / 25:
                    continue
                yield {"TYPE": "FLAT", "CONDITION": "BRIGHT" if moc != "CS" or spec == "EN8" else "HOT ROLLED", "MOC": moc,
                       "SPEC": spec, "SIZE": f"{w} X {t} MM"}


PLASTIC_RODS = ["PTFE VIRGIN", "PTFE GLASS FILLED", "PTFE CARBON FILLED", "NYLON 6 CAST", "NYLON 66", "ACETAL POM",
                "UHMWPE", "PEEK", "PP", "HDPE", "BAKELITE"]


@BAR.generator(group=G_PLASTIC)
def plastic_rods():
    for mat in PLASTIC_RODS:
        for d in (6, 8, 10, 12, 16, 20, 25, 30, 32, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120, 150, 200, 250, 300):
            if mat == "PEEK" and d > 100:
                continue
            yield {"TYPE": "ROUND", "MOC": mat, "SIZE": f"DIA {d} MM", "LENGTH": "1 M"}


# ---------------------------------------------------------------- rolled sections
EQUAL_ANGLES = {20: (3, 4), 25: (3, 4, 5), 30: (3, 4, 5), 35: (3, 4, 5, 6), 40: (3, 4, 5, 6), 45: (3, 4, 5, 6),
                50: (3, 4, 5, 6), 55: (5, 6, 8), 60: (5, 6, 8), 65: (5, 6, 8, 10), 70: (5, 6, 8, 10), 75: (5, 6, 8, 10),
                80: (6, 8, 10, 12), 90: (6, 8, 10, 12), 100: (6, 8, 10, 12), 110: (8, 10, 12, 16), 130: (8, 10, 12, 16),
                150: (10, 12, 16, 20), 200: (12, 16, 20, 25)}
UNEQUAL_ANGLES = {(30, 20): (3, 4, 5), (40, 25): (3, 4, 5, 6), (45, 30): (3, 4, 5, 6), (50, 30): (3, 4, 5, 6),
                  (60, 40): (5, 6, 8), (65, 45): (5, 6, 8), (70, 45): (5, 6, 8), (75, 50): (5, 6, 8, 10),
                  (80, 50): (5, 6, 8, 10), (90, 60): (6, 8, 10, 12), (100, 65): (6, 8, 10), (100, 75): (6, 8, 10, 12),
                  (125, 75): (6, 8, 10), (125, 95): (6, 8, 10, 12), (150, 75): (8, 10, 12), (150, 115): (8, 10, 12, 16),
                  (200, 100): (10, 12, 16), (200, 150): (10, 12, 16, 18)}
SECTION_STEELS = [("CS", "IS 2062 E250 A"), ("CS", "IS 2062 E250 BR"), ("CS", "IS 2062 E350 BR"), ("CS", "ASTM A36"),
                  ("CS", "EN 10025 S275JR"), ("CS", "EN 10025 S355J2")]


@ANGLE.generator
def angles():
    for moc, spec in SECTION_STEELS + [("SS", "SS304"), ("SS", "SS316"), ("ALUMINIUM", "AA 6063 T6")]:
        for leg, thks in EQUAL_ANGLES.items():
            for t in thks:
                for finish in (("", "GALVANISED") if moc == "CS" else ("",)):
                    yield {"TYPE": "EQUAL", "MOC": moc, "SPEC": spec, "SIZE": f"{leg} X {leg} X {t} MM", "FINISH": finish,
                           "STANDARD": "IS 808"}
        for (a, b), thks in UNEQUAL_ANGLES.items():
            for t in thks:
                for finish in (("", "GALVANISED") if moc == "CS" else ("",)):
                    yield {"TYPE": "UNEQUAL", "MOC": moc, "SPEC": spec, "SIZE": f"{a} X {b} X {t} MM", "FINISH": finish,
                           "STANDARD": "IS 808"}


CHANNELS = {"ISMC": (75, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400), "ISJC": (100, 125, 150, 175, 200),
            "ISLC": (75, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400),
            "UPN": (80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 350, 380, 400)}
BEAMS = {"ISMB": (100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 550, 600),
         "ISLB": (75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 400, 450, 500, 550, 600),
         "ISWB": (150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 550, 600),
         "ISHB": (150, 200, 225, 250, 300, 350, 400, 450),
         "NPB IPE": (80, 100, 120, 140, 160, 180, 200, 220, 240, 270, 300, 330, 360, 400, 450, 500, 550, 600),
         "HEA": (100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 400, 450, 500, 550, 600, 650,
                 700, 800, 900, 1000),
         "HEB": (100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 400, 450, 500, 550, 600, 650,
                 700, 800, 900, 1000),
         "HEM": (100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 400, 450, 500)}
# IS 808 depth -> (flange width, web thickness) in mm, written into the size as BOMs quote them ("ISMC 100 X 50 X 5")
IS808_DIMENSIONS = {
    "ISMC": {75: (40, 4.8), 100: (50, 5), 125: (65, 5.3), 150: (75, 5.7), 175: (75, 6), 200: (75, 6.2), 225: (80, 6.5),
             250: (80, 7.2), 300: (90, 7.8), 350: (100, 8.3), 400: (100, 8.8)},
    "ISMB": {100: (75, 4), 125: (75, 4.4), 150: (80, 4.8), 175: (90, 5.5), 200: (100, 5.7), 225: (110, 6.5),
             250: (125, 6.9), 300: (140, 7.5), 350: (140, 8.1), 400: (140, 8.9), 450: (150, 9.4), 500: (180, 10.2),
             550: (190, 11.2), 600: (210, 12)},
}


def _section_size(series: str, depth: int) -> str:
    dims = IS808_DIMENSIONS.get(series, {}).get(depth)
    if not dims:
        return f"{series} {depth}"
    return f"{series} {depth} X {dims[0]} X {fmt(dims[1])} MM"


W_SHAPES = ["W6X9", "W6X12", "W6X15", "W8X10", "W8X13", "W8X18", "W8X24", "W8X31", "W10X12", "W10X19", "W10X26",
            "W10X33", "W10X49", "W12X14", "W12X19", "W12X26", "W12X35", "W12X50", "W12X65", "W14X22", "W14X30",
            "W14X43", "W14X61", "W14X90", "W16X26", "W16X36", "W16X50", "W18X35", "W18X50", "W18X76", "W21X44",
            "W21X62", "W24X55", "W24X76", "W24X104", "W27X84", "W30X99", "W33X118", "W36X135"]


@CHANNEL.generator
def channels():
    for series, depths in CHANNELS.items():
        std = "EN 10279" if series == "UPN" else "IS 808"
        for depth in depths:
            for moc, spec in SECTION_STEELS:
                for finish in ("", "GALVANISED"):
                    yield {"MOC": moc, "SPEC": spec, "SIZE": _section_size(series, depth), "FINISH": finish,
                           "STANDARD": std}
    for d, w, t in ((41, 41, 2.5), (41, 21, 2.5), (41, 41, 2), (41, 62, 2.5), (41, 82, 2.5)):
        for moc, finish in (("CS", "HDG"), ("CS", "PRE GALVANISED"), ("SS", "SS304"), ("SS", "SS316")):
            yield {"TYPE": "STRUT SLOTTED", "MOC": moc, "SIZE": f"{d} X {w} X {t} MM", "FINISH": finish}


@BEAM.generator
def beams():
    for series, depths in BEAMS.items():
        std = "IS 808" if series.startswith("IS") else "EN 10365"
        for depth in depths:
            for moc, spec in SECTION_STEELS:
                for finish in ("", "GALVANISED"):
                    yield {"MOC": moc, "SPEC": spec, "SIZE": _section_size(series, depth), "FINISH": finish,
                           "STANDARD": std}
    for shape in W_SHAPES:
        for spec in ("ASTM A992", "ASTM A572 GR 50", "ASTM A36"):
            yield {"MOC": "CS", "SPEC": spec, "SIZE": shape, "STANDARD": "ASTM A6"}


SHS = {20: (2, 2.6), 25: (2, 2.6, 3.2), 30: (2, 2.6, 3.2), 40: (2, 2.6, 3.2, 4), 50: (2.6, 3.2, 4, 4.8),
       60: (2.6, 3.2, 4, 4.8), 72: (3.2, 4, 4.8), 80: (3.2, 4, 4.8), 91.5: (3.6, 4.5, 5.4), 100: (4, 5, 6),
       113.5: (4.5, 5.4), 132: (4.8, 5.4, 6), 150: (5, 6, 8), 180: (6, 8, 10), 200: (6, 8, 10), 250: (8, 10, 12),
       300: (10, 12)}
RHS = {(40, 20): (2, 2.6, 3.2), (50, 25): (2.6, 3.2), (60, 40): (2.6, 3.2, 4), (66, 33): (2.6, 3.2, 4),
       (80, 40): (3.2, 4, 4.8), (96, 48): (3.2, 4, 4.8), (100, 50): (3.2, 4, 5), (122, 61): (3.6, 4.5, 5.4),
       (145, 82): (4.8, 5.4), (150, 100): (5, 6), (172, 92): (4.8, 5.4), (200, 100): (5, 6, 8), (250, 150): (6, 8),
       (300, 200): (8, 10), (400, 200): (8, 10, 12)}
CHS_OD = {21.3: (2, 2.6, 3.2), 26.9: (2.3, 2.6, 3.2), 33.7: (2.6, 3.2, 4), 42.4: (2.6, 3.2, 4), 48.3: (2.9, 3.2, 4),
          60.3: (2.9, 3.6, 4.5), 76.1: (3.2, 3.6, 4.5), 88.9: (3.2, 4, 4.8), 114.3: (3.6, 4.5, 5.4),
          139.7: (4.5, 4.8, 5.4), 165.1: (4.5, 4.8, 5.4), 168.3: (4.5, 4.8, 6.3), 219.1: (4.8, 5.6, 6.3),
          273: (5.6, 6.3, 8), 323.9: (6.3, 8, 10), 355.6: (8, 10), 406.4: (8, 10, 12)}


@HOLLOW.generator
def hollow_sections():
    specs = [("CS", "IS 4923 YST 210"), ("CS", "IS 4923 YST 310"), ("CS", "IS 4923 YST 355"), ("CS", "EN 10219 S355J2H")]
    for moc, spec in specs:
        for a, thks in SHS.items():
            for t in thks:
                for finish in ("", "GALVANISED"):
                    yield {"TYPE": "SHS", "MOC": moc, "SPEC": spec, "SIZE": f"{fmt(a)} X {fmt(a)} MM", "THICKNESS": f"THK {fmt(t)} MM",
                           "FINISH": finish, "STANDARD": "IS 4923"}
        for (a, b), thks in RHS.items():
            for t in thks:
                for finish in ("", "GALVANISED"):
                    yield {"TYPE": "RHS", "MOC": moc, "SPEC": spec, "SIZE": f"{a} X {b} MM", "THICKNESS": f"THK {fmt(t)} MM",
                           "FINISH": finish, "STANDARD": "IS 4923"}
    for spec in ("IS 1161 YST 210", "IS 1161 YST 240", "IS 1161 YST 310"):
        for od, thks in CHS_OD.items():
            for t in thks:
                yield {"TYPE": "CHS", "MOC": "CS", "SPEC": spec, "SIZE": f"OD {fmt(od)} MM", "THICKNESS": f"THK {fmt(t)} MM",
                       "STANDARD": "IS 1161"}
    for spec in ("ASTM A554 SS304", "ASTM A554 SS316"):
        for a in (20, 25, 30, 40, 50, 60, 80, 100):
            for t in (1.2, 1.5, 2, 3):
                for finish in ("MIRROR POLISHED", "HAIRLINE"):
                    yield {"TYPE": "SHS", "MOC": "SS", "SPEC": spec, "SIZE": f"{a} X {a} MM", "THICKNESS": f"THK {fmt(t)} MM",
                           "FINISH": finish}


@GRATING.generator
def gratings():
    for typ in ("ELECTROFORGED", "PRESS LOCKED"):
        for moc, finishes in (("MS IS 2062", ("HDG", "PAINTED", "PLAIN")), ("SS304", ("PICKLED",)), ("SS316", ("PICKLED",))):
            for bar in ("25 X 3 MM", "25 X 5 MM", "32 X 5 MM", "40 X 5 MM", "50 X 5 MM", "65 X 5 MM"):
                for pitch in ("30 X 100 MM", "40 X 100 MM", "30 X 50 MM"):
                    for finish in finishes:
                        yield {"TYPE": typ, "MOC": moc, "BEARING BAR": f"BEARING BAR {bar}", "PITCH": f"PITCH {pitch}",
                               "FINISH": finish, "STANDARD": "IS 8147"}
    for depth in (25, 38, 50):
        for mesh in ("38 X 38 MM", "50 X 50 MM"):
            yield {"TYPE": "FRP MOULDED", "MOC": "FRP ISOPHTHALIC", "BEARING BAR": f"DEPTH {depth} MM", "PITCH": f"MESH {mesh}"}


@WIRE.generator
def wires():
    swg = {8: 4.06, 10: 3.25, 12: 2.64, 14: 2.03, 16: 1.63, 18: 1.22, 20: 0.91, 22: 0.71, 24: 0.56}
    for g, d in swg.items():
        yield {"TYPE": "BINDING", "MOC": "MS", "DIA": f"{g} SWG ({fmt(d)} MM)", "FINISH": "ANNEALED BLACK"}
        yield {"TYPE": "GI", "MOC": "MS", "DIA": f"{g} SWG ({fmt(d)} MM)", "FINISH": "GALVANISED", "STANDARD": "IS 280"}
    for d in (0.2, 0.3, 0.5, 0.8, 1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6):
        for g in ("SS304", "SS316", "SS302 SPRING"):
            yield {"TYPE": "STAINLESS", "MOC": "SS", "SPEC": g, "DIA": f"DIA {fmt(d)} MM"}
        yield {"TYPE": "COPPER BARE", "MOC": "COPPER", "SPEC": "ETP", "DIA": f"DIA {fmt(d)} MM"}
    for d in (0.5, 0.8, 1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12):
        for g in ("GRADE 1", "GRADE 2", "GRADE 3"):
            yield {"TYPE": "SPRING STEEL", "MOC": "CS", "SPEC": f"IS 4454 {g}", "DIA": f"DIA {fmt(d)} MM"}
    for d in (0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.71, 0.8, 0.9, 1, 1.2, 1.5, 2):
        yield {"TYPE": "ENAMELLED COPPER", "MOC": "COPPER", "SPEC": "CLASS H", "DIA": f"DIA {fmt(d)} MM", "STANDARD": "IS 13730"}
    for g in (12, 14):
        yield {"TYPE": "BARBED", "MOC": "MS", "DIA": f"{g} SWG", "FINISH": "GALVANISED", "STANDARD": "IS 278"}


@MESH.generator
def meshes():
    for count, wire in ((4, 1.2), (8, 0.8), (10, 0.6), (20, 0.4), (30, 0.3), (40, 0.25), (60, 0.18), (80, 0.14),
                        (100, 0.1), (150, 0.06), (200, 0.05), (325, 0.035)):
        for moc in ("SS304", "SS316"):
            yield {"TYPE": "WOVEN", "MOC": moc, "SIZE": f"{count} MESH", "WIRE DIA": f"WIRE {fmt(wire)} MM"}
    for opening in ("25 X 25 MM", "50 X 50 MM", "75 X 75 MM", "100 X 100 MM", "150 X 150 MM"):
        for wire in (2, 2.5, 3, 4, 5, 6):
            yield {"TYPE": "WELDED", "MOC": "MS", "SIZE": opening, "WIRE DIA": f"WIRE {wire} MM", "FINISH": "GALVANISED"}
    for lwd, swd, strand in ((25, 12, 2), (50, 25, 3), (62, 25, 4), (75, 40, 5), (100, 40, 6)):
        for moc in ("MS", "SS304", "ALUMINIUM"):
            yield {"TYPE": "EXPANDED METAL", "MOC": moc, "SIZE": f"LWD {lwd} X SWD {swd} MM", "WIRE DIA": f"STRAND {strand} MM"}
