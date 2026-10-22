"""Valves and piping specialties (strainers, steam traps, sight glasses, expansion joints, hoses)."""
from app.catalog import noun
from app.catalog.data import CAST_BODIES, DN_TO_NPS, FORGED_MATERIALS, cl, dn, dn_pair, dn_range, specials
from app.catalog.piping import COUPLING

VALVE = noun("VALVE", "VALVES", "NOS", ("TYPE", "DESIGN", "MOC", "BODY", "TRIM", "SEAT", "SIZE", "RATING", "END",
                                        "OPERATION", "STANDARD", "FEATURE"))
G_SPEC = "PIPING SPECIALTIES"
STRAINER = noun("STRAINER", G_SPEC, "NOS", ("TYPE", "MOC", "BODY", "SCREEN", "SIZE", "RATING", "END", "STANDARD"))
TRAP = noun("TRAP", G_SPEC, "NOS", ("TYPE", "MOC", "BODY", "SIZE", "RATING", "END", "FEATURE"))
SIGHT_GLASS = noun("SIGHT GLASS", G_SPEC, "NOS", ("TYPE", "MOC", "BODY", "GLASS", "SIZE", "RATING", "END"))
EXPANSION_JOINT = noun("EXPANSION JOINT", G_SPEC, "NOS", ("TYPE", "BELLOWS", "MOC", "SIZE", "RATING", "END",
                                                          "STANDARD"))
HOSE = noun("HOSE", G_SPEC, "MTR", ("TYPE", "MOC", "REINFORCEMENT", "SIZE", "RATING", "LENGTH", "END", "STANDARD"))

VALVE_SIZES = [15, 20, 25, 32, 40, 50, 65, 80, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 650, 700, 750, 800,
               900, 1000, 1050, 1200]
FORGED_SIZES = [15, 20, 25, 32, 40, 50]


def vsizes(lo: int, hi: int) -> list[int]:
    return dn_range(lo, hi, VALVE_SIZES)


TRIMS = {
    "CS": ["TRIM 8 13CR STELLITE", "TRIM 5 STELLITE", "TRIM 12 SS316 STELLITE"],
    "LTCS": ["TRIM 8 13CR STELLITE", "TRIM 12 SS316 STELLITE"],
    "AS": ["TRIM 5 STELLITE", "TRIM 8 13CR STELLITE"],
    "SS": ["TRIM 12 SS316 STELLITE", "TRIM 10 SS316"],
    "DSS": ["TRIM DUPLEX STELLITE"],
    "SDSS": ["TRIM SUPER DUPLEX STELLITE"],
}


def cast_ends(c: int) -> list[str]:
    return {150: ["FLGD RF"], 300: ["FLGD RF", "FLGD RTJ"], 2500: ["FLGD RTJ", "BW"]}.get(c, ["FLGD RF", "FLGD RTJ", "BW"])


HANDWHEEL_MAX = {150: 300, 300: 250, 600: 200, 900: 150, 1500: 100, 2500: 80}
GEAR_MIN = {150: 250, 300: 200, 600: 150, 900: 100, 1500: 80, 2500: 65}


def linear_ops(c: int, d: int) -> list[str]:
    ops = []
    if d <= HANDWHEEL_MAX[c]:
        ops.append("HANDWHEEL")
    if d >= GEAR_MIN[c]:
        ops.append("GEAR OPERATED")
    ops.append("ELECTRIC ACTUATED")
    return ops


CAST_LIMITS = {150: 900, 300: 900, 600: 600, 900: 600, 1500: 600, 2500: 300}


@VALVE.generator
def cast_gate_globe_check():
    for moc, body in CAST_BODIES:
        for c, top in CAST_LIMITS.items():
            bonnet = "BOLTED BONNET" if c <= 600 else "PRESSURE SEAL BONNET"
            cover = "BOLTED COVER" if c <= 600 else "PRESSURE SEAL COVER"
            for d in vsizes(50, top):
                for end in cast_ends(c):
                    for trim in TRIMS[moc]:
                        for sp in specials(moc):
                            for op in linear_ops(c, d):
                                yield {"TYPE": "GATE", "DESIGN": f"OS&Y {bonnet} FLEXIBLE WEDGE", "MOC": moc,
                                       "BODY": body, "TRIM": trim, "SIZE": dn(d), "RATING": cl(c), "END": end,
                                       "OPERATION": op, "STANDARD": "API 600", "FEATURE": sp}
                                if d <= (400 if c <= 600 else 300):
                                    yield {"TYPE": "GLOBE", "DESIGN": f"OS&Y {bonnet}", "MOC": moc, "BODY": body,
                                           "TRIM": trim, "SIZE": dn(d), "RATING": cl(c), "END": end, "OPERATION": op,
                                           "STANDARD": "BS 1873", "FEATURE": sp}
                            yield {"TYPE": "CHECK", "DESIGN": f"SWING {cover}", "MOC": moc, "BODY": body, "TRIM": trim,
                                   "SIZE": dn(d), "RATING": cl(c), "END": end, "STANDARD": "BS 1868", "FEATURE": sp}


@VALVE.generator
def dual_plate_checks():
    bodies = [("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("SS", "ASTM A351 CF8M"), ("SS", "ASTM A351 CF8"),
              ("DSS", "ASTM A995 4A"), ("DI", "IS 1865 SG 500/7")]
    for moc, body in bodies:
        plates = ["PLATE AL BRONZE", "PLATE CF8M"] if moc == "DI" else ["PLATE CF8M"] if moc != "DSS" else ["PLATE 4A"]
        for c in ((150,) if moc == "DI" else (150, 300, 600, 900)):
            for end in (("WAFER", "LUG", "DOUBLE FLANGED") if c <= 600 else ("DOUBLE FLANGED",)):
                for d in vsizes(50, 1200 if end != "LUG" else 600):
                    for plate in plates:
                        for seat in ("METAL SEATED", "EPDM SEAT", "VITON SEAT"):
                            if moc == "DI" and seat == "METAL SEATED":
                                continue
                            yield {"TYPE": "CHECK", "DESIGN": "DUAL PLATE", "MOC": moc, "BODY": body, "TRIM": plate,
                                   "SEAT": seat, "SIZE": dn(d), "RATING": cl(c), "END": end, "STANDARD": "API 594"}


FORGED_VALVE_BODIES = [m for m in FORGED_MATERIALS if m[1] in {
    "ASTM A105", "ASTM A350 LF2 CL1", "ASTM A182 F5", "ASTM A182 F11", "ASTM A182 F22", "ASTM A182 F91",
    "ASTM A182 F304", "ASTM A182 F304L", "ASTM A182 F316", "ASTM A182 F316L", "ASTM A182 F321", "ASTM A182 F51"}]
FORGED_ENDS = {800: ["SW", "THRD NPT"], 1500: ["SW", "THRD NPT", "BW"], 2500: ["SW", "BW"]}


@VALVE.generator
def forged_valves():
    designs = [
        ("GATE", "BOLTED BONNET", (800, 1500), "HANDWHEEL"), ("GATE", "WELDED BONNET", (800, 1500, 2500), "HANDWHEEL"),
        ("GLOBE", "BOLTED BONNET", (800, 1500), "HANDWHEEL"), ("GLOBE", "WELDED BONNET", (800, 1500, 2500), "HANDWHEEL"),
        ("CHECK", "PISTON BOLTED COVER", (800, 1500), ""), ("CHECK", "BALL BOLTED COVER", (800, 1500), ""),
        ("CHECK", "SWING BOLTED COVER", (800,), ""), ("CHECK", "PISTON WELDED COVER", (1500, 2500), ""),
    ]
    for moc, body in FORGED_VALVE_BODIES:
        for typ, design, classes, op in designs:
            for d in FORGED_SIZES:
                for trim in TRIMS[moc]:
                    for sp in specials(moc):
                        for c in classes:
                            for end in FORGED_ENDS[c]:
                                yield {"TYPE": typ, "DESIGN": design, "MOC": moc, "BODY": body, "TRIM": trim,
                                       "SIZE": dn(d), "RATING": cl(c), "END": end, "OPERATION": op,
                                       "STANDARD": "API 602", "FEATURE": sp}
                        if design.startswith(("BOLTED", "PISTON BOLTED")):
                            for c in (150, 300, 600, 900, 1500):
                                for end in (["FLGD RF"] if c == 150 else ["FLGD RF", "FLGD RTJ"]):
                                    yield {"TYPE": typ, "DESIGN": f"{design} INTEGRAL FLANGED", "MOC": moc,
                                           "BODY": body, "TRIM": trim, "SIZE": dn(d), "RATING": cl(c), "END": end,
                                           "OPERATION": op, "STANDARD": "API 602", "FEATURE": sp}


def ball_features(moc: str) -> list[str]:
    feats = ["", "FIRE SAFE API 607"]
    if moc in ("CS", "LTCS"):
        feats.append("FIRE SAFE API 607 NACE MR0175")
    return feats


def quarter_turn_ops(d: int, lever_max: int = 100, gear_min: int = 150) -> list[str]:
    ops = []
    if d <= lever_max:
        ops.append("LEVER")
    if d >= gear_min:
        ops.append("GEAR OPERATED")
    return ops + ["PNEUMATIC ACTUATED", "ELECTRIC ACTUATED"]


BALL_CAST = [("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("SS", "ASTM A351 CF8M"), ("SS", "ASTM A351 CF8"),
             ("SS", "ASTM A351 CF3M")]
BALL_FORGED = [("CS", "ASTM A105"), ("LTCS", "ASTM A350 LF2 CL1"), ("SS", "ASTM A182 F316"), ("SS", "ASTM A182 F304"),
               ("SS", "ASTM A182 F316L"), ("DSS", "ASTM A182 F51")]
SEATS = {"RPTFE SEAT": 300, "PEEK SEAT": 2500, "DEVLON SEAT": 900, "METAL SEATED": 2500}


@VALVE.generator
def floating_ball_valves():
    for moc, body in BALL_CAST + BALL_FORGED:
        forged = (moc, body) in BALL_FORGED
        for bore in ("FULL BORE", "REDUCED BORE"):
            for c, top in ((150, 200), (300, 200), (600, 100)):
                for d in vsizes(15, 50 if forged else top):
                    for end in (["FLGD RF"] if c == 150 else ["FLGD RF", "FLGD RTJ"]):
                        for seat, max_c in SEATS.items():
                            if c > max_c:
                                continue
                            for op in quarter_turn_ops(d):
                                for feat in ball_features(moc):
                                    yield {"TYPE": "BALL", "DESIGN": f"FLOATING {bore} 2 PIECE", "MOC": moc,
                                           "BODY": body, "SEAT": seat, "SIZE": dn(d), "RATING": cl(c), "END": end,
                                           "OPERATION": op, "STANDARD": "API 608", "FEATURE": feat}
        for d in vsizes(15, 50):
            for c in (800, 1500):
                for end in FORGED_ENDS[c]:
                    for seat in ("RPTFE SEAT", "PEEK SEAT", "METAL SEATED"):
                        for op in ("LEVER", "PNEUMATIC ACTUATED", "ELECTRIC ACTUATED"):
                            for feat in ball_features(moc):
                                yield {"TYPE": "BALL", "DESIGN": "FLOATING FULL BORE 3 PIECE", "MOC": moc, "BODY": body,
                                       "SEAT": seat, "SIZE": dn(d), "RATING": cl(c), "END": end, "OPERATION": op,
                                       "STANDARD": "ASME B16.34", "FEATURE": feat}


TRUNNION_LIMITS = {150: 1200, 300: 1200, 600: 1200, 900: 900, 1500: 600, 2500: 300}
TRUNNION_BODIES = [("CS", "ASTM A105"), ("LTCS", "ASTM A350 LF2 CL1"), ("SS", "ASTM A182 F316"), ("DSS", "ASTM A182 F51"),
                   ("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("SS", "ASTM A351 CF8M")]


@VALVE.generator
def trunnion_ball_valves():
    for moc, body in TRUNNION_BODIES:
        for bore in ("FULL BORE", "REDUCED BORE"):
            for c, top in TRUNNION_LIMITS.items():
                ends = {150: ["FLGD RF"], 2500: ["FLGD RTJ", "BW"]}.get(c, ["FLGD RF", "FLGD RTJ", "BW"])
                for d in vsizes(50, top):
                    for end in ends:
                        for seat, max_c in SEATS.items():
                            if c > max_c:
                                continue
                            for op in quarter_turn_ops(d, lever_max=100 if c <= 300 else 0, gear_min=50):
                                for feat in ball_features(moc)[1:]:
                                    yield {"TYPE": "BALL", "DESIGN": f"TRUNNION MOUNTED {bore}", "MOC": moc,
                                           "BODY": body, "SEAT": seat, "SIZE": dn(d), "RATING": cl(c), "END": end,
                                           "OPERATION": op, "STANDARD": "API 6D", "FEATURE": feat}


@VALVE.generator
def butterfly_valves():
    # resilient seated, concentric
    bodies = [("CI", "IS 210 FG 260", ["DISC DI EPOXY COATED", "DISC CF8M", "DISC AL BRONZE"]),
              ("DI", "IS 1865 SG 500/7", ["DISC DI EPOXY COATED", "DISC CF8M", "DISC AL BRONZE"]),
              ("CS", "ASTM A216 WCB", ["DISC CF8M", "DISC CF8"]),
              ("SS", "ASTM A351 CF8M", ["DISC CF8M"])]
    for moc, body, discs in bodies:
        for disc in discs:
            for liner in ("EPDM LINER", "NITRILE LINER", "VITON LINER", "PTFE LINER"):
                for rating in ("PN 10", "PN 16", "CL 150"):
                    for end in ("WAFER", "LUG", "DOUBLE FLANGED"):
                        for d in vsizes(50, 600 if end != "DOUBLE FLANGED" else 1200):
                            for op in quarter_turn_ops(d, lever_max=200, gear_min=150):
                                yield {"TYPE": "BUTTERFLY", "DESIGN": "CONCENTRIC", "MOC": moc, "BODY": body,
                                       "TRIM": disc, "SEAT": liner, "SIZE": dn(d), "RATING": rating, "END": end,
                                       "OPERATION": op, "STANDARD": "API 609 CAT A"}
    # high performance: double / triple offset
    hp_bodies = [("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("SS", "ASTM A351 CF8M"), ("SS", "ASTM A351 CF8"),
                 ("DSS", "ASTM A995 4A")]
    for moc, body in hp_bodies:
        for design, seats in (("DOUBLE OFFSET", ("RPTFE SEAT", "METAL SEATED")),
                              ("TRIPLE OFFSET", ("LAMINATED SS GRAPHITE SEAL", "SOLID METAL SEAT"))):
            for seat in seats:
                for c in (150, 300, 600):
                    for end in ("WAFER", "LUG", "DOUBLE FLANGED"):
                        for d in vsizes(80, 1200 if end == "DOUBLE FLANGED" else 600):
                            for op in quarter_turn_ops(d, lever_max=150 if c == 150 else 0, gear_min=80):
                                for feat in ("", "FIRE SAFE API 607"):
                                    yield {"TYPE": "BUTTERFLY", "DESIGN": design, "MOC": moc, "BODY": body,
                                           "SEAT": seat, "SIZE": dn(d), "RATING": cl(c), "END": end, "OPERATION": op,
                                           "STANDARD": "API 609 CAT B", "FEATURE": feat}


@VALVE.generator
def plug_valves():
    for moc, body in (("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("SS", "ASTM A351 CF8M"), ("CI", "IS 210 FG 260")):
        for design in ("LUBRICATED", "SLEEVED NON LUBRICATED", "PTFE LINED"):
            if moc == "CI" and design != "LUBRICATED":
                continue
            for c, top in ((150, 600), (300, 600), (600, 300)):
                if moc == "CI" and c > 150:
                    continue
                for d in vsizes(15, top):
                    for end in (["FLGD RF", "THRD NPT"] if d <= 50 else ["FLGD RF"]):
                        for op in (["WRENCH OPERATED"] if d <= 100 else []) + (["GEAR OPERATED"] if d >= 150 else []) + \
                                  ["PNEUMATIC ACTUATED"]:
                            yield {"TYPE": "PLUG", "DESIGN": design, "MOC": moc, "BODY": body, "SIZE": dn(d),
                                   "RATING": cl(c), "END": end, "OPERATION": op, "STANDARD": "API 599"}


@VALVE.generator
def diaphragm_valves():
    for moc, body in (("CI", "IS 210 FG 260"), ("DI", "ASTM A536 65-45-12"), ("CS", "ASTM A216 WCB"),
                      ("SS", "ASTM A351 CF8M")):
        for design in ("WEIR TYPE", "STRAIGHT THROUGH"):
            for lining in ("UNLINED", "RUBBER LINED", "PTFE LINED", "PFA LINED"):
                if moc == "SS" and lining != "UNLINED":
                    continue
                for dia in ("DIAPHRAGM EPDM", "DIAPHRAGM PTFE BACKED EPDM", "DIAPHRAGM NEOPRENE"):
                    for d in vsizes(15, 300):
                        for op in ("HANDWHEEL", "PNEUMATIC ACTUATED"):
                            yield {"TYPE": "DIAPHRAGM", "DESIGN": design, "MOC": moc, "BODY": body, "TRIM": dia,
                                   "SEAT": lining, "SIZE": dn(d), "RATING": "PN 10", "END": "FLGD", "OPERATION": op,
                                   "STANDARD": "BS EN 13397"}


@VALVE.generator
def knife_gate_valves():
    for moc, body in (("CI", "IS 210 FG 260"), ("DI", "IS 1865 SG 500/7"), ("CS", "ASTM A216 WCB"),
                      ("SS", "ASTM A351 CF8M")):
        for design in ("UNIDIRECTIONAL", "BIDIRECTIONAL"):
            for gate in ("GATE SS304", "GATE SS316"):
                for seat in ("METAL SEATED", "EPDM SEAT", "NITRILE SEAT"):
                    for end in ("WAFER", "LUG"):
                        for d in vsizes(50, 1200):
                            ops = (["HANDWHEEL"] if d <= 300 else ["BEVEL GEAR OPERATED"]) + ["PNEUMATIC ACTUATED",
                                                                                               "ELECTRIC ACTUATED"]
                            for op in ops:
                                yield {"TYPE": "KNIFE GATE", "DESIGN": design, "MOC": moc, "BODY": body, "TRIM": gate,
                                       "SEAT": seat, "SIZE": dn(d), "RATING": "PN 10", "END": end, "OPERATION": op,
                                       "STANDARD": "MSS SP-81"}


@VALVE.generator
def low_pressure_valves():
    for typ, design in (("GATE", "SCREWED BONNET"), ("GLOBE", "SCREWED BONNET"), ("CHECK", "HORIZONTAL LIFT"),
                        ("CHECK", "SWING")):
        for cls in ("CLASS 1", "CLASS 2"):
            for d in vsizes(15, 80):
                yield {"TYPE": typ, "DESIGN": design, "MOC": "BRONZE", "BODY": "IS 318 LTB 2", "SIZE": dn(d),
                       "RATING": cls, "END": "THRD BSP", "OPERATION": "HANDWHEEL" if typ != "CHECK" else "",
                       "STANDARD": "IS 778"}
    for d in vsizes(50, 1200):
        for pn in ("PN 1.0", "PN 1.6"):
            yield {"TYPE": "GATE", "DESIGN": "SLUICE NON RISING SPINDLE", "MOC": "CI", "BODY": "IS 210 FG 200",
                   "SIZE": dn(d), "RATING": pn, "END": "FLGD", "OPERATION": "CAP TOP" if d > 300 else "HANDWHEEL",
                   "STANDARD": "IS 14846"}
            yield {"TYPE": "CHECK", "DESIGN": "SWING REFLUX", "MOC": "CI", "BODY": "IS 210 FG 200", "SIZE": dn(d),
                   "RATING": pn, "END": "FLGD", "STANDARD": "IS 5312"}
    for d in vsizes(25, 300):
        yield {"TYPE": "FOOT", "DESIGN": "WITH STRAINER", "MOC": "CI", "BODY": "IS 210 FG 200", "SIZE": dn(d),
               "END": "FLGD" if d > 80 else "THRD BSP", "STANDARD": "IS 4038"}
    for d in vsizes(15, 100):
        for body in (("BRASS", "FORGED BRASS CW617N"), ("SS", "ASTM A351 CF8M"), ("CS", "ASTM A216 WCB")):
            for design in ("1 PIECE REDUCED BORE", "2 PIECE FULL BORE", "3 PIECE FULL BORE"):
                for end in ("THRD BSP", "THRD NPT"):
                    yield {"TYPE": "BALL", "DESIGN": design, "MOC": body[0], "BODY": body[1], "SEAT": "PTFE SEAT",
                           "SIZE": dn(d), "RATING": "PN 25" if body[0] == "BRASS" else "1000 WOG", "END": end,
                           "OPERATION": "LEVER"}


PSV_ORIFICES = {"D": [(25, 50), (40, 50)], "E": [(25, 50), (40, 50)], "F": [(40, 50), (40, 80)], "G": [(40, 80), (50, 80)],
                "H": [(40, 80), (50, 80)], "J": [(50, 80), (65, 100), (80, 100)], "K": [(80, 100), (80, 150)],
                "L": [(80, 100), (100, 150)], "M": [(100, 150)], "N": [(100, 150)], "P": [(100, 150)],
                "Q": [(150, 200)], "R": [(150, 200), (150, 250)], "T": [(200, 250)]}


@VALVE.generator
def safety_relief_valves():
    for moc, body in (("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("AS", "ASTM A217 WC6"),
                      ("SS", "ASTM A351 CF8M")):
        for design in ("SPRING LOADED CONVENTIONAL", "SPRING LOADED BALANCED BELLOWS", "PILOT OPERATED"):
            for orifice, pairs in PSV_ORIFICES.items():
                for inlet, outlet in pairs:
                    for c in (150, 300, 600, 900, 1500):
                        if c >= 900 and inlet > 100:
                            continue
                        for end in (["FLGD RF"] if c <= 300 else ["FLGD RF", "FLGD RTJ"]):
                            yield {"TYPE": "SAFETY RELIEF", "DESIGN": f"{design} ORIFICE {orifice}", "MOC": moc,
                                   "BODY": body, "TRIM": "NOZZLE AND DISC SS316", "SIZE": dn_pair(inlet, outlet),
                                   "RATING": f"{cl(c)} X CL 150", "END": end, "STANDARD": "API 526"}
    for body in (("CS", "ASTM A105"), ("SS", "ASTM A182 F316")):
        for inlet, outlet in ((15, 20), (20, 25), (25, 25), (25, 40)):
            for end in ("THRD NPT", "SW"):
                for design in ("THERMAL RELIEF", "SAFETY RELIEF OPEN BONNET", "SAFETY RELIEF CLOSED BONNET"):
                    yield {"TYPE": "SAFETY RELIEF", "DESIGN": design, "MOC": body[0], "BODY": body[1],
                           "TRIM": "SS316", "SIZE": dn_pair(inlet, outlet), "END": end, "STANDARD": "ASME SEC VIII"}


@VALVE.generator
def solenoid_valves():
    designs = ["2/2 WAY NC", "2/2 WAY NO", "3/2 WAY NC", "3/2 WAY NO", "5/2 WAY SINGLE SOLENOID",
               "5/2 WAY DOUBLE SOLENOID", "5/3 WAY CLOSED CENTRE"]
    ports = ['1/8"', '1/4"', '3/8"', '1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"']
    for design in designs:
        pneumatic = design.startswith("5/")
        bodies = [("AL", "ALUMINIUM")] if pneumatic else [("BRASS", "FORGED BRASS"), ("SS", "SS316")]
        for moc, body in bodies:
            for seat in (("NBR SEAT",) if pneumatic else ("NBR SEAT", "VITON SEAT", "EPDM SEAT", "PTFE SEAT")):
                for port in (ports[:5] if pneumatic else ports):
                    for coil in ("COIL 24 V DC", "COIL 110 V AC", "COIL 230 V AC"):
                        for feat in ("WEATHERPROOF IP65", "FLAMEPROOF EX D IIC T4"):
                            yield {"TYPE": "SOLENOID", "DESIGN": design, "MOC": moc, "BODY": body, "SEAT": seat,
                                   "SIZE": port, "END": "THRD BSP" if pneumatic else "THRD NPT", "OPERATION": coil,
                                   "FEATURE": feat}


@VALVE.generator
def control_valves():
    designs = [("GLOBE SINGLE SEATED", 15, 300), ("GLOBE CAGE GUIDED", 25, 300), ("ROTARY BALL V PORT", 25, 400),
               ("ROTARY BUTTERFLY", 80, 600)]
    for design, lo, hi in designs:
        for moc, body in (("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("AS", "ASTM A217 WC6"),
                          ("SS", "ASTM A351 CF8M")):
            for char in ("EQUAL PERCENTAGE", "LINEAR"):
                for c in (150, 300, 600, 900):
                    for d in vsizes(lo, hi):
                        for end in (["FLGD RF"] if c == 150 else ["FLGD RF", "FLGD RTJ"]):
                            for op in ("PNEUMATIC DIAPHRAGM ACTUATOR FAIL CLOSE", "PNEUMATIC DIAPHRAGM ACTUATOR FAIL OPEN"):
                                yield {"TYPE": "CONTROL", "DESIGN": design, "MOC": moc, "BODY": body,
                                       "TRIM": f"{char} SS316 STELLITE", "SIZE": dn(d), "RATING": cl(c), "END": end,
                                       "OPERATION": op, "STANDARD": "IEC 60534", "FEATURE": "WITH SMART POSITIONER"}


# ======================================================================== strainers
SCREENS = ["SCREEN SS304 20 MESH", "SCREEN SS304 40 MESH", "SCREEN SS316 40 MESH", "SCREEN SS316 60 MESH",
           "SCREEN SS316 100 MESH", "PERFORATED SS316 3 MM"]


@STRAINER.generator
def strainers():
    for moc, body in (("CS", "ASTM A216 WCB"), ("LTCS", "ASTM A352 LCC"), ("AS", "ASTM A217 WC6"), ("SS", "ASTM A351 CF8M")):
        for c, top in ((150, 400), (300, 400), (600, 300), (900, 200), (1500, 150)):
            for d in vsizes(15, top):
                for end in (["FLGD RF"] if c == 150 else ["FLGD RF", "FLGD RTJ", "BW"]):
                    for screen in SCREENS:
                        yield {"TYPE": "Y", "MOC": moc, "BODY": body, "SCREEN": screen, "SIZE": dn(d), "RATING": cl(c),
                               "END": end, "STANDARD": "ASME B16.34"}
    for moc, body in (("CS", "ASTM A105"), ("LTCS", "ASTM A350 LF2 CL1"), ("SS", "ASTM A182 F316"), ("SS", "ASTM A182 F304")):
        for d in FORGED_SIZES:
            for c in (800, 1500):
                for end in ("SW", "THRD NPT"):
                    for screen in SCREENS:
                        yield {"TYPE": "Y", "MOC": moc, "BODY": body, "SCREEN": screen, "SIZE": dn(d), "RATING": cl(c),
                               "END": end, "STANDARD": "ASME B16.11"}
    for typ in ("BASKET SIMPLEX", "BASKET DUPLEX", "T TYPE"):
        for moc, body in (("CS", "FABRICATED ASTM A106 GR B/A516 GR 70"), ("SS", "FABRICATED ASTM A312 TP316")):
            for c in (150, 300, 600):
                for d in vsizes(50, 600):
                    for screen in SCREENS:
                        yield {"TYPE": typ, "MOC": moc, "BODY": body, "SCREEN": screen, "SIZE": dn(d), "RATING": cl(c),
                               "END": "FLGD RF"}
        for d in vsizes(50, 300):
            for screen in SCREENS[:3]:
                yield {"TYPE": typ, "MOC": "CI", "BODY": "IS 210 FG 260", "SCREEN": screen, "SIZE": dn(d),
                       "RATING": "PN 16", "END": "FLGD"}
    for typ in ("TEMPORARY CONE", "TEMPORARY FLAT"):
        for moc in ("SS304", "SS316"):
            for c in (150, 300, 600, 900):
                for d in vsizes(50, 600):
                    for mesh in ("40 MESH", "60 MESH", "PERFORATED 3 MM"):
                        yield {"TYPE": typ, "MOC": moc, "SCREEN": mesh, "SIZE": dn(d), "RATING": cl(c)}


@TRAP.generator
def steam_traps():
    for typ in ("THERMODYNAMIC", "BALL FLOAT", "INVERTED BUCKET", "THERMOSTATIC", "BIMETALLIC"):
        for moc, body in (("CS", "ASTM A105"), ("SS", "ASTM A182 F316"), ("CS", "ASTM A216 WCB"), ("CI", "IS 210 FG 260")):
            for d in vsizes(15, 50):
                ends = ["FLGD"] if moc == "CI" else ["SW", "THRD NPT", "FLGD RF"]
                for end in ends:
                    for rating in (("PN 16",) if moc == "CI" else ("CL 300", "CL 600")):
                        for feat in ("", "WITH INTEGRAL STRAINER"):
                            yield {"TYPE": typ, "MOC": moc, "BODY": body, "SIZE": dn(d), "RATING": rating, "END": end,
                                   "FEATURE": feat}


@SIGHT_GLASS.generator
def sight_glasses():
    for typ in ("FULL VIEW DOUBLE WINDOW", "SINGLE WINDOW", "FLOW INDICATOR ROTARY", "FLOW INDICATOR FLAPPER"):
        for moc, body in (("CS", "ASTM A216 WCB"), ("SS", "ASTM A351 CF8M"), ("CS", "ASTM A105"), ("CI", "IS 210 FG 260")):
            for d in vsizes(15, 300):
                forged = body == "ASTM A105"
                if forged and d > 50:
                    continue
                for rating, ends in ((("PN 16", ["FLGD"]),) if moc == "CI" else
                                     (("CL 150", ["FLGD RF"]), ("CL 300", ["FLGD RF"])) if not forged else
                                     (("CL 800", ["SW", "THRD NPT"]),)):
                    for end in ends:
                        yield {"TYPE": typ, "MOC": moc, "BODY": body, "GLASS": "TOUGHENED BOROSILICATE",
                               "SIZE": dn(d), "RATING": rating, "END": end}


@EXPANSION_JOINT.generator
def expansion_joints():
    for typ in ("METALLIC SINGLE BELLOWS", "METALLIC UNIVERSAL", "METALLIC HINGED", "METALLIC GIMBAL"):
        for bellows in ("SS321 BELLOWS", "SS316L BELLOWS", "INCONEL 625 BELLOWS"):
            for moc in ("CS", "SS"):
                for c in (150, 300):
                    for d in vsizes(50, 1200):
                        for end in ("FLGD RF", "BW"):
                            yield {"TYPE": typ, "BELLOWS": bellows, "MOC": moc, "SIZE": dn(d), "RATING": cl(c),
                                   "END": end, "STANDARD": "EJMA"}
    for typ in ("RUBBER SINGLE SPHERE", "RUBBER TWIN SPHERE"):
        for bellows in ("EPDM", "NEOPRENE", "NITRILE"):
            for d in vsizes(25, 600):
                for rating in ("PN 10", "PN 16"):
                    yield {"TYPE": typ, "BELLOWS": bellows, "MOC": "MS ZINC PLATED FLANGES", "SIZE": dn(d),
                           "RATING": rating, "END": "FLGD"}
    for d in vsizes(25, 300):
        yield {"TYPE": "PTFE BELLOWS 3 CONVOLUTION", "BELLOWS": "PTFE", "MOC": "MS FLANGES", "SIZE": dn(d),
               "RATING": "CL 150", "END": "FLGD RF"}


@HOSE.generator
def hoses():
    hyd = ["SAE 100 R1AT", "SAE 100 R2AT", "EN 856 4SP", "EN 856 4SH", "SAE 100 R12", "SAE 100 R13"]
    dash = {"-4": '1/4"', "-5": '5/16"', "-6": '3/8"', "-8": '1/2"', "-10": '5/8"', "-12": '3/4"', "-16": '1"',
            "-20": '1-1/4"', "-24": '1-1/2"', "-32": '2"'}
    for std in hyd:
        for code, inch in dash.items():
            if std in ("EN 856 4SH", "SAE 100 R13") and code in ("-4", "-5", "-6", "-8", "-10"):
                continue
            yield {"TYPE": "HYDRAULIC", "MOC": "SYNTHETIC RUBBER", "REINFORCEMENT":
                   "STEEL WIRE BRAID" if "R1" in std or "R2" in std else "STEEL WIRE SPIRAL", "SIZE": f"{inch} ({code})",
                   "STANDARD": std}
    for typ, mat, sizes in (("AIR", "RUBBER", (6, 8, 10, 12, 16, 19, 25, 32, 38, 50)),
                            ("WATER", "RUBBER", (12, 19, 25, 32, 38, 50, 65, 75, 100)),
                            ("STEAM", "EPDM", (12, 19, 25, 32, 38, 50)),
                            ("CHEMICAL", "UHMWPE LINED", (19, 25, 32, 38, 50, 75, 100)),
                            ("SUCTION AND DELIVERY", "PVC", (25, 32, 38, 50, 65, 75, 100, 150)),
                            ("FIRE LAY FLAT", "RRL", (38, 63)),
                            ("WELDING TWIN", "RUBBER", (6, 8, 10))):
        for s in sizes:
            for rating in ("10 BAR", "20 BAR"):
                if typ == "SUCTION AND DELIVERY" and rating == "20 BAR":
                    continue
                yield {"TYPE": typ, "MOC": mat, "REINFORCEMENT": "TEXTILE BRAID", "SIZE": f"ID {s} MM",
                       "RATING": rating}
    for braid in ("SS304 SINGLE BRAID", "SS304 DOUBLE BRAID"):
        for d in vsizes(15, 150):
            yield {"TYPE": "FLEXIBLE CORRUGATED", "MOC": "SS316L", "REINFORCEMENT": braid, "SIZE": dn(d),
                   "STANDARD": "ISO 10380"}
            for length in (500, 1000, 1500, 2000):
                for end in ("FLGD CL 150 RF BOTH ENDS", "MALE NPT BOTH ENDS", "FLGD X UNION"):
                    if d > 50 and end != "FLGD CL 150 RF BOTH ENDS":
                        continue
                    yield {"TYPE": "FLEXIBLE CORRUGATED ASSEMBLY", "MOC": "SS316L", "REINFORCEMENT": braid,
                           "SIZE": dn(d), "LENGTH": f"L {length} MM", "END": end, "STANDARD": "ISO 10380"}
    for d in vsizes(15, 50):
        yield {"TYPE": "PTFE LINED", "MOC": "PTFE", "REINFORCEMENT": "SS304 BRAID", "SIZE": dn(d)}


CAMLOCK_TYPES = ["TYPE A", "TYPE B", "TYPE C", "TYPE D", "TYPE E", "TYPE F", "TYPE DC", "TYPE DP"]


@COUPLING.generator(group=G_SPEC)
def camlock_couplings():
    for typ in CAMLOCK_TYPES:
        for moc in ("ALUMINIUM", "SS316", "BRASS", "POLYPROPYLENE"):
            for d in vsizes(15, 150):
                yield {"TYPE": f"CAMLOCK {typ}", "MOC": moc, "SIZE": DN_TO_NPS[d], "STANDARD": "EN 14420-7"}
