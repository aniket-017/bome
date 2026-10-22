"""Rolling bearings, bearing units and accessories, plain bushes."""
from app.catalog import noun
from app.catalog.data import BEARING_MAKES, TAPER_BEARING_MAKES, fmt
from app.catalog.fasteners import NUT, WASHER
from app.catalog.piping import BUSHING

G = "BEARINGS"
BEARING = noun("BEARING", G, "NOS", ("TYPE", "DESIGNATION", "SEALING", "CAGE", "CLEARANCE", "DIMENSIONS", "MAKE"))
SLEEVE = noun("SLEEVE", G, "NOS", ("TYPE", "DESIGNATION", "SIZE", "MOC", "MAKE"))
HOUSING = noun("BEARING HOUSING", G, "NOS", ("TYPE", "DESIGNATION", "MOC", "SEALING", "SIZE", "MAKE"))


def bore(code: int) -> int:
    return {0: 10, 1: 12, 2: 15, 3: 17}.get(code, code * 5)


# ISO dimension series: bore code -> (OD, width)
S60 = {0: (26, 8), 1: (28, 8), 2: (32, 9), 3: (35, 10), 4: (42, 12), 5: (47, 12), 6: (55, 13), 7: (62, 14), 8: (68, 15),
       9: (75, 16), 10: (80, 16), 11: (90, 18), 12: (95, 18), 13: (100, 18), 14: (110, 20), 15: (115, 20), 16: (125, 22),
       17: (130, 22), 18: (140, 24), 19: (145, 24), 20: (150, 24), 22: (170, 28), 24: (180, 28), 26: (200, 33),
       28: (210, 33), 30: (225, 35)}
S62 = {0: (30, 9), 1: (32, 10), 2: (35, 11), 3: (40, 12), 4: (47, 14), 5: (52, 15), 6: (62, 16), 7: (72, 17), 8: (80, 18),
       9: (85, 19), 10: (90, 20), 11: (100, 21), 12: (110, 22), 13: (120, 23), 14: (125, 24), 15: (130, 25), 16: (140, 26),
       17: (150, 28), 18: (160, 30), 19: (170, 32), 20: (180, 34), 22: (200, 38), 24: (215, 40), 26: (230, 40),
       28: (250, 42), 30: (270, 45)}
S63 = {0: (35, 11), 1: (37, 12), 2: (42, 13), 3: (47, 14), 4: (52, 15), 5: (62, 17), 6: (72, 19), 7: (80, 21), 8: (90, 23),
       9: (100, 25), 10: (110, 27), 11: (120, 29), 12: (130, 31), 13: (140, 33), 14: (150, 35), 15: (160, 37),
       16: (170, 39), 17: (180, 41), 18: (190, 43), 19: (200, 45), 20: (215, 47), 22: (240, 50), 24: (260, 55),
       26: (280, 58), 28: (300, 62), 30: (320, 65)}
S64 = {3: (62, 17), 4: (72, 19), 5: (80, 21), 6: (90, 23), 7: (100, 25), 8: (110, 27), 9: (120, 29), 10: (130, 31),
       11: (140, 33), 12: (150, 35), 13: (160, 37), 14: (180, 42), 15: (190, 45), 16: (200, 48), 18: (225, 54)}
S68 = {0: (19, 5), 1: (21, 5), 2: (24, 5), 3: (26, 5), 4: (32, 7), 5: (37, 7), 6: (42, 7), 7: (47, 7), 8: (52, 7),
       9: (58, 7), 10: (65, 7), 11: (72, 9), 12: (78, 10), 13: (85, 10), 14: (90, 10), 15: (95, 10), 16: (100, 10),
       17: (110, 13), 18: (115, 13), 19: (120, 13), 20: (125, 13)}
S69 = {0: (22, 6), 1: (24, 6), 2: (28, 7), 3: (30, 7), 4: (37, 9), 5: (42, 9), 6: (47, 9), 7: (55, 10), 8: (62, 12),
       9: (68, 12), 10: (72, 12), 11: (80, 13), 12: (85, 13), 13: (90, 13), 14: (100, 16), 15: (105, 16), 16: (110, 16),
       17: (120, 18), 18: (125, 18), 19: (130, 18), 20: (140, 20)}
W22 = {4: 18, 5: 18, 6: 20, 7: 23, 8: 23, 9: 23, 10: 23, 11: 25, 12: 28, 13: 31, 14: 31, 15: 31, 16: 33, 17: 36, 18: 40,
       19: 43, 20: 46, 22: 53, 24: 58, 26: 64, 28: 68, 30: 73}
W23 = {4: 21, 5: 24, 6: 27, 7: 31, 8: 33, 9: 36, 10: 40, 11: 43, 12: 46, 13: 48, 14: 51, 15: 55, 16: 58, 17: 60, 18: 64,
       19: 67, 20: 73, 22: 80, 24: 86, 26: 93, 28: 102, 30: 108}
S22 = {c: (S62[c][0], w) for c, w in W22.items()}
S23 = {c: (S63[c][0], w) for c, w in W23.items()}
T302 = {3: 13.25, 4: 15.25, 5: 16.25, 6: 17.25, 7: 18.25, 8: 19.75, 9: 20.75, 10: 21.75, 11: 22.75, 12: 23.75, 13: 24.75,
        14: 26.25, 15: 27.25, 16: 28.25, 17: 30.5, 18: 32.5, 19: 34.5, 20: 37}
T303 = {2: 14.25, 3: 15.25, 4: 16.25, 5: 18.25, 6: 20.75, 7: 22.75, 8: 25.25, 9: 27.25, 10: 29.25, 11: 31.5, 12: 33.5,
        13: 36, 14: 38, 15: 40, 16: 42.5, 17: 44.5, 18: 46.5, 19: 49.5, 20: 51.5}
T322 = {5: 19.25, 6: 21.25, 7: 24.25, 8: 24.75, 9: 24.75, 10: 24.75, 11: 26.75, 12: 29.75, 13: 32.75, 14: 33.25,
        15: 33.25, 16: 35.25, 17: 38.5, 18: 42.5, 19: 45.5, 20: 49}
T323 = {5: 25.25, 6: 28.75, 7: 32.75, 8: 35.25, 9: 38.25, 10: 42.25, 11: 45.5, 12: 48.5, 13: 51, 14: 54, 15: 58,
        16: 61.5, 17: 63.5, 18: 67.5, 19: 71.5, 20: 77.5}
TH511 = {0: (24, 9), 1: (26, 9), 2: (28, 9), 3: (30, 9), 4: (35, 10), 5: (42, 11), 6: (47, 11), 7: (52, 12), 8: (60, 13),
         9: (65, 14), 10: (70, 14), 11: (78, 16), 12: (85, 17), 13: (90, 18), 14: (95, 18), 15: (100, 19), 16: (105, 19),
         17: (110, 19), 18: (120, 22), 20: (135, 25)}
TH512 = {0: (26, 11), 1: (28, 11), 2: (32, 12), 3: (35, 12), 4: (40, 14), 5: (47, 15), 6: (52, 16), 7: (62, 18),
         8: (68, 19), 9: (73, 20), 10: (78, 22), 11: (90, 25), 12: (95, 26), 13: (100, 27), 14: (105, 27), 15: (110, 27),
         16: (115, 28), 17: (125, 31), 18: (135, 35), 20: (150, 38)}
TH513 = {5: (52, 18), 6: (60, 21), 7: (68, 24), 8: (78, 26), 9: (85, 28), 10: (95, 31), 11: (105, 35), 12: (110, 35),
         13: (115, 36), 14: (125, 40), 15: (135, 44), 16: (140, 44), 17: (150, 49), 18: (155, 50), 20: (170, 55)}


def dims(code: int, od: float, width: float) -> str:
    return f"{bore(code)} X {fmt(od)} X {fmt(width)} MM"


@BEARING.generator
def deep_groove():
    for series, table in (("60", S60), ("62", S62), ("63", S63), ("64", S64), ("68", S68), ("69", S69)):
        for code, (od, w) in table.items():
            seals = ("", "ZZ", "2RS") if code <= 20 else ("",)
            for sealing in seals:
                for clearance in ("", "C3"):
                    for make in BEARING_MAKES:
                        yield {"TYPE": "BALL DEEP GROOVE", "DESIGNATION": f"{series}{code:02d}", "SEALING": sealing,
                               "CLEARANCE": clearance, "DIMENSIONS": dims(code, od, w), "MAKE": make}


@BEARING.generator
def angular_contact():
    for series, table in (("72", S62), ("73", S63)):
        for code, (od, w) in table.items():
            if code > 20 or (series == "73" and code < 2):
                continue
            for cage in ("POLYAMIDE CAGE", "BRASS CAGE", "STEEL CAGE"):
                for make in BEARING_MAKES[:5]:
                    yield {"TYPE": "BALL ANGULAR CONTACT", "DESIGNATION": f"{series}{code:02d} B", "CAGE": cage,
                           "DIMENSIONS": dims(code, od, w), "MAKE": make}
    for series, table in (("32", S62), ("33", S63)):
        for code in range(4, 21):
            od = table[code][0]
            for sealing in ("", "2RS"):
                for make in BEARING_MAKES[:5]:
                    yield {"TYPE": "BALL ANGULAR CONTACT DOUBLE ROW", "DESIGNATION": f"{series}{code:02d} A",
                           "SEALING": sealing, "DIMENSIONS": f"{bore(code)} X {od} MM", "MAKE": make}


@BEARING.generator
def self_aligning_ball():
    for series, table in (("12", S62), ("13", S63), ("22", S22), ("23", S23)):
        for code, (od, w) in table.items():
            if not 4 <= code <= 20:
                continue
            for k in ("", " K"):
                for clearance in ("", "C3"):
                    for make in BEARING_MAKES[:5]:
                        yield {"TYPE": "BALL SELF ALIGNING", "DESIGNATION": f"{series}{code:02d}{k}",
                               "CLEARANCE": clearance, "DIMENSIONS": dims(code, od, w), "MAKE": make}


@BEARING.generator
def cylindrical_roller():
    for series, table in (("2", S62), ("3", S63), ("22", S22), ("23", S23)):
        for code, (od, w) in table.items():
            if code < 4:
                continue
            for prefix in ("NU", "NJ", "NUP", "N"):
                if prefix == "N" and series in ("22", "23"):
                    continue
                cages = ("POLYAMIDE CAGE", "STEEL CAGE", "BRASS CAGE") if code <= 20 else ("BRASS CAGE",)
                for cage in cages:
                    for clearance in ("", "C3"):
                        for make in BEARING_MAKES[:5]:
                            yield {"TYPE": "CYLINDRICAL ROLLER", "DESIGNATION": f"{prefix} {series}{code:02d} E",
                                   "CAGE": cage, "CLEARANCE": clearance, "DIMENSIONS": dims(code, od, w), "MAKE": make}


@BEARING.generator
def spherical_roller():
    for series, table, lo in (("222", S22, 5), ("223", S23, 8)):
        for code, (od, w) in table.items():
            if code < lo:
                continue
            for k in ("E", "EK"):
                for cage in ("STEEL CAGE", "BRASS CAGE"):
                    for clearance in ("", "C3"):
                        for make in ("SKF", "FAG", "NSK", "NTN", "TIMKEN"):
                            yield {"TYPE": "SPHERICAL ROLLER", "DESIGNATION": f"{series}{code:02d} {k}", "CAGE": cage,
                                   "CLEARANCE": clearance, "DIMENSIONS": dims(code, od, w), "MAKE": make}


@BEARING.generator
def taper_roller():
    for series, widths, ods in (("302", T302, S62), ("303", T303, S63), ("322", T322, S62), ("323", T323, S63)):
        for code, t in widths.items():
            for make in TAPER_BEARING_MAKES:
                yield {"TYPE": "TAPER ROLLER", "DESIGNATION": f"{series}{code:02d}",
                       "DIMENSIONS": dims(code, ods[code][0], t), "MAKE": make}


@BEARING.generator
def thrust_ball():
    for series, table in (("511", TH511), ("512", TH512), ("513", TH513)):
        for code, (od, h) in table.items():
            for make in BEARING_MAKES[:5]:
                yield {"TYPE": "THRUST BALL", "DESIGNATION": f"{series}{code:02d}", "DIMENSIONS": dims(code, od, h),
                       "MAKE": make}


NA49 = {0: (22, 13), 1: (24, 13), 2: (28, 13), 3: (30, 13), 4: (37, 17), 5: (42, 17), 6: (47, 17), 7: (55, 20),
        8: (62, 22), 9: (68, 22), 10: (72, 22), 11: (80, 25), 12: (85, 25), 13: (90, 25), 14: (100, 30)}
HK = [(8, 12, 8), (10, 14, 10), (12, 18, 10), (14, 20, 12), (15, 21, 12), (16, 22, 12), (17, 23, 12), (20, 26, 10),
      (20, 26, 16), (20, 26, 20), (25, 32, 16), (25, 32, 20), (30, 37, 16), (30, 37, 20), (35, 42, 20), (40, 47, 20)]


@BEARING.generator
def needle_roller():
    for code, (od, w) in NA49.items():
        for make in ("INA", "SKF", "NTN", "IKO"):
            yield {"TYPE": "NEEDLE ROLLER WITH INNER RING", "DESIGNATION": f"NA49{code:02d}",
                   "DIMENSIONS": dims(code, od, w), "MAKE": make}
    for fw, od, w in HK:
        for make in ("INA", "SKF", "NTN", "IKO"):
            yield {"TYPE": "NEEDLE ROLLER DRAWN CUP", "DESIGNATION": f"HK{fw:02d}{w:02d}",
                   "DIMENSIONS": f"{fw} X {od} X {w} MM", "MAKE": make}


UC_BORES = {1: 12, 2: 15, 3: 17, 4: 20, 5: 25, 6: 30, 7: 35, 8: 40, 9: 45, 10: 50, 11: 55, 12: 60, 13: 65, 14: 70,
            15: 75, 16: 80, 17: 85, 18: 90}
UNIT_MAKES = ["SKF", "FAG", "NTN", "ASAHI", "FYH", "NBC"]


@BEARING.generator
def bearing_units():
    for housing, name in (("UCP", "PILLOW BLOCK UNIT"), ("UCF", "SQUARE FLANGE UNIT 4 BOLT"), ("UCFL", "OVAL FLANGE UNIT 2 BOLT"),
                          ("UCT", "TAKE UP UNIT"), ("UCFC", "ROUND FLANGE UNIT"), ("UCPA", "TAPPED BASE PILLOW BLOCK UNIT")):
        for code, b in UC_BORES.items():
            if housing in ("UCPA",) and code > 10:
                continue
            for make in UNIT_MAKES:
                yield {"TYPE": name, "DESIGNATION": f"{housing} 2{code:02d}", "DIMENSIONS": f"BORE {b} MM",
                       "MAKE": make}
    for code, b in UC_BORES.items():
        for make in UNIT_MAKES:
            yield {"TYPE": "INSERT", "DESIGNATION": f"UC 2{code:02d}", "DIMENSIONS": f"BORE {b} MM", "MAKE": make}


@HOUSING.generator
def plummer_blocks():
    for code in range(5, 33):
        if code in (25, 27, 29, 31):
            continue
        for typ in ("SN", "SNL"):
            for sealing in ("WITH DOUBLE LIP SEALS", "WITH LABYRINTH SEALS", "WITH TACONITE SEALS"):
                for make in ("SKF", "FAG", "NTN"):
                    yield {"TYPE": "PLUMMER BLOCK SPLIT", "DESIGNATION": f"{typ} 5{code:02d}", "MOC": "CI GG20",
                           "SEALING": sealing, "SIZE": f"FOR BEARING 12{code:02d} K/22{code:02d} K", "MAKE": make}


@SLEEVE.generator
def adapter_sleeves():
    for series, lo in (("H 2", 4), ("H 3", 4), ("H 23", 5)):
        for code in range(lo, 31):
            if code in (21, 23, 25, 27, 29):
                continue
            shaft = bore(code) - (5 if code >= 4 else 0)
            for make in ("SKF", "FAG", "NTN", "NBC"):
                yield {"TYPE": "ADAPTER WITH NUT AND LOCKWASHER", "DESIGNATION": f"{series}{code:02d}",
                       "SIZE": f"SHAFT {shaft} MM", "MAKE": make}


KM_THREADS = {0: "M10 X 0.75", 1: "M12 X 1", 2: "M15 X 1", 3: "M17 X 1", 4: "M20 X 1", 5: "M25 X 1.5", 6: "M30 X 1.5",
              7: "M35 X 1.5", 8: "M40 X 1.5", 9: "M45 X 1.5", 10: "M50 X 1.5", 11: "M55 X 2", 12: "M60 X 2",
              13: "M65 X 2", 14: "M70 X 2", 15: "M75 X 2", 16: "M80 X 2", 17: "M85 X 2", 18: "M90 X 2", 19: "M95 X 2",
              20: "M100 X 2", 22: "M110 X 2", 24: "M120 X 2", 26: "M130 X 2", 28: "M140 X 2", 30: "M150 X 2"}


@NUT.generator(group=G)
def bearing_lock_nuts():
    for n, thread in KM_THREADS.items():
        yield {"TYPE": f"BEARING LOCK KM{n}", "MOC": "CS", "DIA": thread, "FINISH": "PHOSPHATED", "STANDARD": "DIN 981"}


@WASHER.generator(group=G)
def bearing_lock_washers():
    for n, thread in KM_THREADS.items():
        yield {"TYPE": f"BEARING LOCK MB{n}", "MOC": "CS", "SIZE": f"FOR {thread.split(' X ')[0]}", "STANDARD": "DIN 5406"}


@BUSHING.generator(group=G)
def plain_bushes():
    lengths = (5, 6, 8, 10, 12, 15, 16, 20, 25, 30, 40, 50, 60)
    for i in (6, 8, 10, 12, 14, 15, 16, 18, 20, 22, 25, 28, 30, 32, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100):
        wall = 1 if i <= 16 else 1.5 if i <= 40 else 2.5
        for L in [L for L in lengths if 0.5 * i <= L <= 1.5 * i]:
            for typ, moc in (("PLAIN BEARING DU", "STEEL BACKED PTFE"), ("PLAIN BEARING DX", "STEEL BACKED POM"),
                             ("PLAIN BEARING OILITE", "SINTERED BRONZE")):
                yield {"TYPE": typ, "MOC": moc, "SIZE": f"ID {i} X OD {fmt(i + 2 * wall)} X L {L} MM"}
    for i in (10, 12, 15, 16, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120, 150):
        for L in (20, 25, 30, 40, 50, 60, 80, 100):
            if not 0.6 * i <= L <= 2 * i:
                continue
            for moc in ("GUN METAL LG2", "PHOSPHOR BRONZE PB1"):
                yield {"TYPE": "PLAIN BEARING SOLID", "MOC": moc, "SIZE": f"ID {i} X OD {i + 10 if i < 50 else i + 20} X L {L} MM"}
