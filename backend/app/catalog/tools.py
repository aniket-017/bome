"""Cutting tools, inserts, abrasives, hand tools, measuring instruments, power tools."""
from app.catalog import noun
from app.catalog.data import ABRASIVE_MAKES, CUTTING_TOOL_MAKES, DRILL_MAKES, METRIC_COARSE, TOOL_MAKES, fmt, m_dia
from app.catalog.electrical import SOCKET

G_CUT = "CUTTING TOOLS"
G_ABR = "ABRASIVES"
G_HT = "HAND TOOLS"
G_MS = "MEASURING INSTRUMENTS"
G_PT = "POWER TOOLS"
DRILL = noun("DRILL", G_CUT, "NOS", ("TYPE", "MOC", "DIA", "LENGTH", "SHANK", "COATING", "STANDARD", "MAKE"))
TAP = noun("TAP", G_CUT, "NOS", ("TYPE", "MOC", "THREAD", "CLASS", "COATING", "STANDARD", "MAKE"))
DIE = noun("DIE", G_CUT, "NOS", ("TYPE", "MOC", "THREAD", "SIZE", "STANDARD", "MAKE"))
REAMER = noun("REAMER", G_CUT, "NOS", ("TYPE", "MOC", "DIA", "TOLERANCE", "SHANK", "STANDARD", "MAKE"))
END_MILL = noun("END MILL", G_CUT, "NOS", ("TYPE", "MOC", "DIA", "FLUTES", "LENGTH", "COATING", "MAKE"))
CUTTER = noun("CUTTER", G_CUT, "NOS", ("TYPE", "MOC", "SIZE", "TEETH", "BORE", "MAKE"))
INSERT = noun("INSERT", G_CUT, "NOS", ("TYPE", "DESIGNATION", "CHIPBREAKER", "GRADE", "APPLICATION", "MAKE"))
HOLDER = noun("TOOL HOLDER", G_CUT, "NOS", ("TYPE", "DESIGNATION", "SHANK", "HAND", "MAKE"))
BIT = noun("BIT", G_CUT, "NOS", ("TYPE", "MOC", "SIZE", "LENGTH", "SHANK", "MAKE"))
WHEEL = noun("WHEEL", G_ABR, "NOS", ("TYPE", "ABRASIVE", "SIZE", "GRIT", "GRADE", "BOND", "SPEED", "MOC", "CAPACITY",
                                     "MOUNTING", "MAKE"))
DISC = noun("DISC", G_ABR, "NOS", ("TYPE", "ABRASIVE", "SIZE", "GRIT", "APPLICATION", "MAKE"))
BLADE = noun("BLADE", G_CUT, "NOS", ("TYPE", "MOC", "SIZE", "TPI", "MAKE"))
ABRASIVE = noun("ABRASIVE", G_ABR, "NOS", ("TYPE", "ABRASIVE", "SIZE", "GRIT", "MAKE"))
BRUSH = noun("BRUSH", G_ABR, "NOS", ("TYPE", "MOC", "SIZE", "THREAD", "MAKE"))
SPANNER = noun("SPANNER", G_HT, "NOS", ("TYPE", "SIZE", "MOC", "FINISH", "STANDARD", "MAKE"))
WRENCH = noun("WRENCH", G_HT, "NOS", ("TYPE", "SIZE", "RANGE", "DRIVE", "MOC", "STANDARD", "MAKE"))
SCREWDRIVER = noun("SCREWDRIVER", G_HT, "NOS", ("TYPE", "TIP", "SIZE", "LENGTH", "FEATURE", "MAKE"))
PLIER = noun("PLIER", G_HT, "NOS", ("TYPE", "SIZE", "FEATURE", "MAKE"))
HAMMER = noun("HAMMER", G_HT, "NOS", ("TYPE", "WEIGHT", "HANDLE", "MAKE"))
FILE = noun("FILE", G_HT, "NOS", ("TYPE", "CUT", "SIZE", "MAKE"))
CHISEL = noun("CHISEL", G_HT, "NOS", ("TYPE", "SIZE", "LENGTH", "MAKE"))
PUNCH = noun("PUNCH", G_HT, "NOS", ("TYPE", "SIZE", "LENGTH", "MAKE"))
TOOL_KIT = noun("TOOL KIT", G_HT, "SET", ("TYPE", "PIECES", "MAKE"))
CALIPER = noun("CALIPER", G_MS, "NOS", ("TYPE", "RANGE", "RESOLUTION", "MAKE"))
MICROMETER = noun("MICROMETER", G_MS, "NOS", ("TYPE", "RANGE", "RESOLUTION", "MAKE"))
GAUGE_M = noun("MEASURING GAUGE", G_MS, "NOS", ("TYPE", "SIZE", "RANGE", "CLASS", "MAKE"))
TAPE = noun("MEASURING TAPE", G_MS, "NOS", ("TYPE", "LENGTH", "WIDTH", "MAKE"))
RULE = noun("RULE", G_MS, "NOS", ("TYPE", "LENGTH", "MAKE"))
LEVEL = noun("SPIRIT LEVEL", G_MS, "NOS", ("TYPE", "LENGTH", "ACCURACY", "MAKE"))
POWER_TOOL = noun("POWER TOOL", G_PT, "NOS", ("TYPE", "SIZE", "POWER", "VOLTAGE", "MAKE"))

POWER_MAKES = ("BOSCH", "MAKITA", "DEWALT", "HITACHI", "STANLEY")
METRIC_THREADS = [f"{m} X {fmt(p)}" for m, p in METRIC_COARSE.items() if m_dia(m) <= 36]
UNC_THREADS = ["1/4-20 UNC", "5/16-18 UNC", "3/8-16 UNC", "7/16-14 UNC", "1/2-13 UNC", "9/16-12 UNC", "5/8-11 UNC",
               "3/4-10 UNC", "7/8-9 UNC", "1-8 UNC"]


def _drill_dias():
    d = 1.0
    while d <= 13.0 + 1e-9:
        yield round(d, 1)
        d += 0.1
    d = 13.5
    while d <= 20 + 1e-9:
        yield d
        d += 0.5


@DRILL.generator
def drills():
    for d in _drill_dias():
        for moc, coat in (("HSS", "BRIGHT"), ("HSS", "TIN COATED"), ("HSS CO5", "BRONZE")):
            for make in DRILL_MAKES:
                yield {"TYPE": "TWIST JOBBER", "MOC": moc, "DIA": f"{fmt(d)} MM", "SHANK": "STRAIGHT SHANK",
                       "COATING": coat, "STANDARD": "DIN 338", "MAKE": make}
    d = 10.0
    while d <= 50:
        for moc in ("HSS", "HSS CO5"):
            for make in DRILL_MAKES:
                yield {"TYPE": "TWIST", "MOC": moc, "DIA": f"{fmt(d)} MM",
                       "SHANK": f"MT{1 if d <= 14 else 2 if d <= 23 else 3 if d <= 31.75 else 4} TAPER SHANK",
                       "COATING": "BRIGHT", "STANDARD": "DIN 345", "MAKE": make}
        d += 0.5
    for d in (3, 4, 5, 6, 6.8, 8, 8.5, 10, 10.2, 12, 14, 16, 18, 20):
        for L in ("3XD", "5XD", "8XD"):
            for make in CUTTING_TOOL_MAKES:
                yield {"TYPE": "SOLID CARBIDE COOLANT THROUGH" if L != "3XD" else "SOLID CARBIDE", "MOC": "CARBIDE",
                       "DIA": f"{fmt(d)} MM", "LENGTH": L, "SHANK": "DIN 6535 HA", "COATING": "TIALN", "MAKE": make}
    for d in (3, 4, 5, 6, 8, 10, 12):
        for make in DRILL_MAKES:
            yield {"TYPE": "CENTRE", "MOC": "HSS", "DIA": f"{d} MM PILOT", "COATING": "BRIGHT", "STANDARD": "DIN 333 A",
                   "MAKE": make}
    for d in (4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25):
        for L in (110, 160, 210, 310, 460):
            if d < 6 and L > 160:
                continue
            for make in ("BOSCH", "HILTI", "MAKITA"):
                yield {"TYPE": "MASONRY SDS PLUS" if d <= 20 else "MASONRY SDS MAX", "MOC": "CARBIDE TIPPED",
                       "DIA": f"{d} MM", "LENGTH": f"L {L} MM", "MAKE": make}


@TAP.generator
def taps():
    for thread in METRIC_THREADS:
        for typ in ("HAND SET OF 3", "MACHINE SPIRAL FLUTE", "MACHINE SPIRAL POINT"):
            for moc, coat in (("HSS", "BRIGHT"), ("HSS-E", "TIN COATED")):
                for make in DRILL_MAKES:
                    yield {"TYPE": typ, "MOC": moc, "THREAD": thread, "CLASS": "6H", "COATING": coat,
                           "STANDARD": "DIN 371/376" if typ.startswith("MACHINE") else "DIN 352", "MAKE": make}
    for thread in ("M8 X 1", "M10 X 1", "M10 X 1.25", "M12 X 1.25", "M12 X 1.5", "M14 X 1.5", "M16 X 1.5", "M18 X 1.5",
                   "M20 X 1.5", "M22 X 1.5", "M24 X 1.5", "M24 X 2", "M27 X 2", "M30 X 2"):
        for typ in ("HAND SET OF 3", "MACHINE SPIRAL POINT"):
            for make in DRILL_MAKES:
                yield {"TYPE": typ, "MOC": "HSS", "THREAD": thread, "CLASS": "6H", "STANDARD": "DIN 2181", "MAKE": make}
    for thread in UNC_THREADS:
        for typ in ("HAND SET OF 3", "MACHINE SPIRAL POINT"):
            for make in DRILL_MAKES:
                yield {"TYPE": typ, "MOC": "HSS", "THREAD": thread, "CLASS": "2B", "MAKE": make}
    for size in ("1/8", "1/4", "3/8", "1/2", "3/4", "1", "1-1/4", "1-1/2", "2"):
        for std in ("NPT", "BSPT", "BSP"):
            for make in DRILL_MAKES:
                yield {"TYPE": "PIPE", "MOC": "HSS", "THREAD": f"{size} {std}", "MAKE": make}


@DIE.generator
def dies():
    for thread in METRIC_THREADS + UNC_THREADS:
        for make in DRILL_MAKES:
            yield {"TYPE": "ROUND SPLIT", "MOC": "HSS", "THREAD": thread,
                   "STANDARD": "DIN 223", "MAKE": make}
    for size in ("1/8", "1/4", "3/8", "1/2", "3/4", "1", "1-1/4", "1-1/2", "2"):
        for std in ("NPT", "BSPT"):
            for make in DRILL_MAKES:
                yield {"TYPE": "PIPE ROUND", "MOC": "HSS", "THREAD": f"{size} {std}", "MAKE": make}


@REAMER.generator
def reamers():
    for d in (*range(3, 21), 22, 24, 25, 26, 28, 30, 32, 35, 38, 40, 45, 50):
        for typ, shank, std in (("MACHINE CHUCKING", "STRAIGHT SHANK" if d <= 20 else "MORSE TAPER SHANK", "DIN 212"),
                                ("HAND", "STRAIGHT SHANK", "DIN 206")):
            for moc in ("HSS", "CARBIDE TIPPED") if typ.startswith("MACHINE") else ("HSS",):
                for make in DRILL_MAKES:
                    yield {"TYPE": typ, "MOC": moc, "DIA": f"{d} MM", "TOLERANCE": "H7", "SHANK": shank,
                           "STANDARD": std, "MAKE": make}


@END_MILL.generator
def end_mills():
    for d in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 25, 32):
        for typ in ("SQUARE", "BALL NOSE", "CORNER RADIUS"):
            for flutes in (2, 3, 4):
                for length in ("STANDARD", "LONG"):
                    for moc, coat in (("SOLID CARBIDE", "TIALN"), ("SOLID CARBIDE", "ALTIN"), ("HSS CO8", "TIN")):
                        if moc.startswith("HSS") and d < 3:
                            continue
                        for make in [*CUTTING_TOOL_MAKES[:4], "YG-1"]:
                            yield {"TYPE": typ, "MOC": moc, "DIA": f"{fmt(d)} MM", "FLUTES": f"{flutes} FLUTE",
                                   "LENGTH": f"{length} LENGTH", "COATING": coat, "MAKE": make}


@CUTTER.generator
def cutters():
    for d, bores in ((63, (16, 22)), (80, (22, 27)), (100, (22, 27, 32)), (125, (27, 32)), (160, (32, 40)), (200, (40,))):
        for w in (4, 6, 8, 10, 12, 16, 20):
            for bore in bores:
                yield {"TYPE": "SIDE AND FACE STAGGERED TOOTH", "MOC": "HSS", "SIZE": f"{d} X {w} MM", "BORE": f"BORE {bore} MM"}
        for w in (0.5, 1, 1.6, 2, 3, 4):
            yield {"TYPE": "SLITTING SAW", "MOC": "HSS", "SIZE": f"{d} X {fmt(w)} MM", "BORE": f"BORE {bores[0]} MM"}
    for d in (40, 50, 63, 80, 100, 125, 160, 200, 250):
        for typ in ("FACE MILL 45 DEG", "FACE MILL 90 DEG SHOULDER"):
            for make in CUTTING_TOOL_MAKES:
                yield {"TYPE": f"{typ} INDEXABLE", "MOC": "STEEL BODY", "SIZE": f"DIA {d} MM",
                       "TEETH": f"{max(3, d // 16)} INSERTS", "MAKE": make}
    for m in (1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8):
        for n in range(1, 9):
            yield {"TYPE": "GEAR INVOLUTE", "MOC": "HSS", "SIZE": f"MODULE {fmt(m)} NO {n}"}
    for d in (12, 14, 16, 18, 20, 22, 24, 25, 26, 28, 30, 32, 35, 38, 40, 42, 45, 50, 55, 60, 65):
        for depth in (25, 50):
            for make in ("RUKO", "STAR", "EUROBOOR"):
                yield {"TYPE": f"ANNULAR CUTTER {depth} MM DEPTH", "MOC": "HSS", "SIZE": f"DIA {d} MM",
                       "BORE": "WELDON SHANK 19 MM", "MAKE": make}
    for d in (16, 19, 22, 25, 29, 32, 35, 38, 41, 44, 51, 57, 64, 76, 89, 102, 114, 127, 152):
        for make in ("BOSCH", "STARRETT", "MAKITA"):
            yield {"TYPE": "HOLE SAW BI METAL", "MOC": "HSS BI METAL", "SIZE": f"DIA {d} MM", "MAKE": make}


ISO_INSERTS = {
    "CNMG": ("090304", "090308", "120404", "120408", "120412", "160608", "160612", "190608", "190612"),
    "DNMG": ("110404", "110408", "150404", "150408", "150608", "150612"),
    "TNMG": ("160404", "160408", "160412", "220408", "220412"),
    "VNMG": ("160404", "160408", "160412"),
    "WNMG": ("060404", "060408", "080404", "080408", "080412"),
    "SNMG": ("120408", "120412", "150612", "190612", "250724"),
    "CCMT": ("060204", "060208", "09T304", "09T308", "120404", "120408"),
    "DCMT": ("070204", "070208", "11T304", "11T308"),
    "VCMT": ("110304", "160404", "160408"),
    "TCMT": ("110204", "110208", "16T304", "16T308"),
    "SCMT": ("09T304", "09T308", "120408"),
    "APMT": ("1135PDER", "1604PDER"),
    "SEKT": ("1204AFTN", "1204AFSN"),
    "RPMT": ("10T3MO", "1204MO"),
}
INSERT_GRADES = {"P": "STEEL", "M": "STAINLESS STEEL", "K": "CAST IRON"}


@INSERT.generator
def inserts():
    for shape, sizes in ISO_INSERTS.items():
        milling = shape in ("APMT", "SEKT", "RPMT")
        for size in sizes:
            for cb in ("FINISHING", "MEDIUM", "ROUGHING") if not milling else ("GENERAL",):
                for iso, app in INSERT_GRADES.items():
                    for make in CUTTING_TOOL_MAKES:
                        yield {"TYPE": "MILLING" if milling else "TURNING", "DESIGNATION": f"{shape} {size}",
                               "CHIPBREAKER": f"{cb} CHIPBREAKER", "GRADE": f"ISO {iso}25 CVD COATED",
                               "APPLICATION": f"FOR {app}", "MAKE": make}
    for w in (2, 3, 4, 5, 6):
        for make in CUTTING_TOOL_MAKES:
            yield {"TYPE": "GROOVING AND PARTING", "DESIGNATION": f"WIDTH {w} MM", "GRADE": "ISO P25 PVD COATED",
                   "MAKE": make}
    for pitch in ("1.0", "1.5", "2.0", "2.5", "3.0", "11 BSP", "14 NPT", "8 UN", "AG60"):
        for hand in ("EXTERNAL 16ER", "INTERNAL 16IR"):
            for make in CUTTING_TOOL_MAKES:
                yield {"TYPE": f"THREADING {hand}", "DESIGNATION": f"PITCH {pitch}", "GRADE": "ISO P25 PVD COATED",
                       "MAKE": make}


@HOLDER.generator
def tool_holders():
    for des in ("PCLNR", "PDJNR", "PTGNR", "PWLNR", "MVJNR", "PSBNR", "SCLCR", "SDJCR", "SVJCR"):
        for shank in ("16 X 16", "20 X 20", "25 X 25", "32 X 32"):
            for hand in ("RH", "LH"):
                for make in CUTTING_TOOL_MAKES[:4]:
                    yield {"TYPE": "TURNING EXTERNAL", "DESIGNATION": des[:-1] + hand[0], "SHANK": f"SHANK {shank} MM", "HAND": hand, "MAKE": make}
    for typ in ("ER COLLET CHUCK BT40", "ER COLLET CHUCK BT50", "SIDE LOCK HOLDER BT40", "SHRINK FIT HOLDER BT40",
                "HYDRAULIC CHUCK BT40"):
        for d in (6, 8, 10, 12, 16, 20, 25, 32):
            for make in ("BIG KAISER", "SANDVIK", "NIKKEN", "HAIMER"):
                yield {"TYPE": typ, "DESIGNATION": f"FOR DIA {d} MM", "MAKE": make}


@BIT.generator
def bits():
    for size in ("1/4 X 2-1/2", "5/16 X 2-1/2", "3/8 X 3", "1/2 X 4", "5/8 X 6", "3/4 X 6", "1 X 8"):
        yield {"TYPE": "TOOL BIT SQUARE", "MOC": "HSS CO10", "SIZE": f"{size} IN"}
    for size in ("6 X 6", "8 X 8", "10 X 10", "12 X 12", "16 X 16", "20 X 20", "25 X 25"):
        for L in (100, 150, 200):
            yield {"TYPE": "TOOL BIT SQUARE", "MOC": "HSS CO10", "SIZE": f"{size} MM", "LENGTH": f"L {L} MM"}
    for tip in ("PH1", "PH2", "PH3", "PZ1", "PZ2", "PZ3", "SL 4", "SL 6", "HEX 3", "HEX 4", "HEX 5", "HEX 6", "T20", "T25",
                "T30", "T40"):
        for L in (25, 50, 90):
            for make in ("BOSCH", "WERA", "STANLEY"):
                yield {"TYPE": "SCREWDRIVER INSERT", "MOC": "S2 STEEL", "SIZE": tip, "LENGTH": f"L {L} MM",
                       "SHANK": "1/4 IN HEX", "MAKE": make}


@WHEEL.generator
def wheels():
    for d, bores in ((100, (16, 20)), (150, (25.4, 31.75)), (175, (25.4, 31.75)), (200, (31.75, 50.8)),
                     (250, (31.75, 76.2)), (300, (76.2, 127)), (350, (127,)), (400, (127, 203.2)), (500, (203.2, 304.8))):
        for t in (13, 20, 25, 40, 50):
            if t > d / 6:
                continue
            for bore in bores:
                for abr, grit, grade in (("A", 46, "K"), ("A", 60, "M"), ("WA", 46, "K"), ("WA", 60, "K"), ("WA", 80, "J"),
                                         ("GC", 60, "K"), ("GC", 80, "J"), ("A", 24, "Q"), ("A", 36, "P")):
                    for make in ABRASIVE_MAKES[:2]:
                        yield {"TYPE": "GRINDING STRAIGHT TYPE 1", "ABRASIVE": abr, "SIZE": f"{d} X {t} X {fmt(bore)} MM",
                               "GRIT": f"{grit} GRIT", "GRADE": f"GRADE {grade}", "BOND": "VITRIFIED", "MAKE": make}
    for d in (100, 125, 150, 200, 250):
        for typ in ("CUP FLARING TYPE 11", "DISH TYPE 12", "DIAMOND PLAIN TYPE 1A1"):
            yield {"TYPE": typ, "ABRASIVE": "D" if "DIAMOND" in typ else "WA", "SIZE": f"DIA {d} MM", "GRIT": "100 GRIT",
                   "BOND": "RESIN" if "DIAMOND" in typ else "VITRIFIED", "MAKE": "CUMI"}
    for d in (50, 65, 75, 100, 125, 150, 200, 250):
        for moc, cap in (("PU", 50), ("RUBBER", 40), ("NYLON", 80), ("CI", 150), ("PU ON CI CORE", 200)):
            cap = cap * d // 50
            for mounting in ("SWIVEL PLATE", "FIXED PLATE", "SWIVEL WITH BRAKE"):
                yield {"TYPE": "CASTOR", "SIZE": f"DIA {d} MM", "MOC": moc, "CAPACITY": f"{cap} KG",
                       "MOUNTING": mounting}


@DISC.generator
def discs():
    for d, thicknesses in ((105, (1, 1.2, 2.5)), (125, (1, 1.6, 3)), (180, (1.6, 3)), (230, (2, 3)), (355, (3, 3.2))):
        for t in thicknesses:
            for app in ("METAL", "STAINLESS STEEL INOX", "STONE"):
                for make in ABRASIVE_MAKES:
                    yield {"TYPE": "CUTTING OFF", "ABRASIVE": "A" if app != "STONE" else "C",
                           "SIZE": f"{d} X {fmt(t)} X {22.23 if d < 355 else 25.4} MM", "APPLICATION": f"FOR {app}",
                           "MAKE": make}
        if d <= 230:
            for app in ("METAL", "STAINLESS STEEL INOX"):
                for make in ABRASIVE_MAKES:
                    yield {"TYPE": "DEPRESSED CENTRE GRINDING", "ABRASIVE": "A", "SIZE": f"{d} X 6 X 22.23 MM",
                           "APPLICATION": f"FOR {app}", "MAKE": make}
            for grit in (40, 60, 80, 120):
                for abr in ("ZIRCONIA", "ALUMINIUM OXIDE", "CERAMIC"):
                    for make in ABRASIVE_MAKES:
                        yield {"TYPE": "FLAP", "ABRASIVE": abr, "SIZE": f"DIA {d} MM", "GRIT": f"{grit} GRIT", "MAKE": make}
            for grit in (16, 24, 36, 60, 80, 120):
                yield {"TYPE": "FIBRE SANDING", "ABRASIVE": "ALUMINIUM OXIDE", "SIZE": f"DIA {d} MM", "GRIT": f"{grit} GRIT",
                       "MAKE": "3M"}


@BLADE.generator
def blades():
    for L in (250, 300):
        for tpi in (18, 24, 32):
            for moc in ("HSS", "BI METAL HSS", "HCS"):
                for make in ("STARRETT", "BAHCO", "LENOX", "TOTEM"):
                    yield {"TYPE": "HACKSAW HAND", "MOC": moc, "SIZE": f"{L} X 12.7 MM", "TPI": f"{tpi} TPI", "MAKE": make}
    for L, w in ((300, 25), (350, 32), (400, 32), (450, 38), (500, 38), (600, 50)):
        for tpi in (4, 6, 8, 10):
            for make in ("STARRETT", "BAHCO", "LENOX"):
                yield {"TYPE": "HACKSAW POWER", "MOC": "BI METAL HSS M42", "SIZE": f"{L} X {w} X 1.6 MM", "TPI": f"{tpi} TPI",
                       "MAKE": make}
    for w, t in ((13, 0.65), (20, 0.9), (27, 0.9), (34, 1.1), (41, 1.3), (54, 1.6)):
        for tpi in ("3/4", "4/6", "5/8", "6/10", "8/12", "10/14"):
            for make in ("STARRETT", "BAHCO", "LENOX", "WIKUS"):
                yield {"TYPE": "BANDSAW BI METAL M42 COIL", "SIZE": f"{w} X {fmt(t)} MM", "TPI": f"{tpi} TPI", "MAKE": make}
    for d, bore in ((185, 20), (210, 30), (250, 30), (300, 30), (355, 25.4)):
        for teeth in (24, 40, 60, 80):
            yield {"TYPE": "CIRCULAR SAW TCT", "MOC": "CARBIDE TIPPED", "SIZE": f"{d} X {fmt(bore)} MM BORE",
                   "TPI": f"{teeth}T", "MAKE": "BOSCH"}
    for typ in ("UTILITY KNIFE SNAP OFF 18 MM", "UTILITY KNIFE TRAPEZOID", "SCRAPER 40 MM"):
        for make in ("STANLEY", "OLFA", "TAPARIA"):
            yield {"TYPE": typ, "SIZE": "PACK OF 10", "MAKE": make}


@ABRASIVE.generator
def abrasives():
    for grit in (36, 40, 60, 80, 100, 120, 150, 180, 220, 320, 400, 600, 800, 1000):
        for typ, size in (("PAPER SHEET", "230 X 280 MM"), ("CLOTH ROLL", "50 MM X 50 M"), ("CLOTH ROLL", "100 MM X 50 M")):
            for make in ABRASIVE_MAKES:
                yield {"TYPE": typ, "ABRASIVE": "SILICON CARBIDE" if typ == "PAPER SHEET" else "ALUMINIUM OXIDE",
                       "SIZE": size, "GRIT": f"{grit} GRIT", "MAKE": make}
        for w, L in ((6, 610), (10, 330), (13, 610), (25, 762), (50, 2000), (75, 2000), (100, 915), (150, 2000)):
            if grit <= 400:
                yield {"TYPE": "SANDING BELT", "ABRASIVE": "ZIRCONIA" if grit <= 60 else "ALUMINIUM OXIDE",
                       "SIZE": f"{w} X {L} MM", "GRIT": f"{grit} GRIT", "MAKE": "3M"}
    for size in ("6 X 25 MM", "10 X 20 MM", "16 X 25 MM", "20 X 25 MM", "25 X 25 MM", "32 X 32 MM"):
        for shape in ("CYLINDRICAL", "BALL", "CONE", "TREE"):
            for typ in ("MOUNTED POINT", "TUNGSTEN CARBIDE ROTARY BURR"):
                yield {"TYPE": f"{typ} {shape}", "SIZE": size, "ABRASIVE": "WA" if typ.startswith("MOUNTED") else "",
                       "MAKE": "CUMI" if typ.startswith("MOUNTED") else "OSBORN"}
    for size in ("100 X 25 X 12 MM", "150 X 50 X 25 MM", "200 X 50 X 25 MM"):
        for grit in ("COARSE FINE COMBINATION", "FINE"):
            yield {"TYPE": "SHARPENING STONE", "ABRASIVE": "SILICON CARBIDE", "SIZE": size, "GRIT": grit, "MAKE": "CUMI"}


@BRUSH.generator
def brushes():
    for d in (75, 100, 115, 125, 150, 200):
        for typ in ("WIRE CUP CRIMPED", "WIRE CUP TWISTED KNOT", "WIRE WHEEL CRIMPED", "WIRE WHEEL TWISTED KNOT"):
            if "CUP" in typ and d > 150:
                continue
            for moc in ("STEEL", "SS"):
                for thread in ("M14 X 2", "5/8-11 UNC"):
                    yield {"TYPE": typ, "MOC": f"{moc} WIRE", "SIZE": f"DIA {d} MM", "THREAD": thread, "MAKE": "OSBORN"}
    for rows in (2, 3, 4, 5, 6):
        for moc in ("STEEL", "SS", "BRASS"):
            yield {"TYPE": f"WIRE HAND {rows} ROW", "MOC": f"{moc} WIRE", "MAKE": "OSBORN"}
    for w in (25, 38, 50, 63, 75, 100, 150):
        yield {"TYPE": "PAINT FLAT", "MOC": "BRISTLE", "SIZE": f"{w} MM", "MAKE": "ASIAN PAINTS"}


SPANNER_PAIRS = [(6, 7), (8, 9), (8, 10), (10, 11), (12, 13), (13, 15), (14, 15), (16, 17), (17, 19), (18, 19),
                 (19, 22), (20, 22), (21, 23), (22, 24), (24, 27), (25, 28), (27, 30), (30, 32), (32, 36), (36, 41),
                 (41, 46), (46, 50)]
SPANNER_SIZES = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32,
                 34, 36, 38, 41, 46, 50, 55, 60, 65, 70, 75]


@SPANNER.generator
def spanners():
    for a, b in SPANNER_PAIRS:
        for typ, std in (("DOUBLE OPEN END", "DIN 3110"), ("DOUBLE RING OFFSET", "DIN 838")):
            for make in TOOL_MAKES:
                yield {"TYPE": typ, "SIZE": f"{a} X {b} MM", "MOC": "CR-V", "FINISH": "CHROME PLATED", "STANDARD": std,
                       "MAKE": make}
    for s in SPANNER_SIZES:
        if s <= 50:
            for make in TOOL_MAKES:
                yield {"TYPE": "COMBINATION", "SIZE": f"{s} MM", "MOC": "CR-V", "FINISH": "CHROME PLATED",
                       "STANDARD": "DIN 3113", "MAKE": make}
        if s >= 17:
            for typ in ("SLOGGING RING", "SLOGGING OPEN END"):
                for make in TOOL_MAKES[:3]:
                    yield {"TYPE": typ, "SIZE": f"{s} MM", "MOC": "CR-V", "FINISH": "BLACK", "STANDARD": "DIN 7444",
                           "MAKE": make}
    for s in (19, 24, 27, 30, 32, 36, 41, 46, 50, 55, 60, 65, 70, 75, 80):
        yield {"TYPE": "SLOGGING RING", "SIZE": f"{s} MM", "MOC": "BERYLLIUM COPPER", "FINISH": "NON SPARKING",
               "MAKE": "AMPCO"}


@WRENCH.generator
def wrenches():
    for size in (150, 200, 250, 300, 375, 450, 600):
        for make in TOOL_MAKES:
            yield {"TYPE": "ADJUSTABLE", "SIZE": f"{size} MM", "MOC": "CR-V", "MAKE": make}
    for size in (200, 250, 300, 350, 450, 600, 900, 1200):
        for moc in ("CI", "AL"):
            for make in ("RIDGID", "TAPARIA", "STANLEY", "BAHCO"):
                yield {"TYPE": "PIPE STILLSON", "SIZE": f"{size} MM", "MOC": moc, "MAKE": make}
    for drive, ranges in (("1/4 IN DRIVE", ("2-10 NM", "5-25 NM")), ("3/8 IN DRIVE", ("10-50 NM", "20-100 NM")),
                          ("1/2 IN DRIVE", ("40-200 NM", "60-340 NM")), ("3/4 IN DRIVE", ("100-500 NM", "200-800 NM")),
                          ("1 IN DRIVE", ("300-1000 NM", "500-1500 NM"))):
        for r in ranges:
            for make in ("NORBAR", "GEDORE", "STAHLWILLE", "TAPARIA"):
                yield {"TYPE": "TORQUE CLICK", "RANGE": r, "DRIVE": drive, "STANDARD": "ISO 6789", "MAKE": make}
    for drive, nms in (("3/4 IN DRIVE", (1000, 2000)), ("1 IN DRIVE", (3000, 5000, 8000)), ("1-1/2 IN DRIVE", (10000, 20000))):
        for nm in nms:
            for make in ("HYTORC", "ENERPAC", "PLARAD"):
                yield {"TYPE": "HYDRAULIC TORQUE SQUARE DRIVE", "RANGE": f"MAX {nm} NM", "DRIVE": drive, "MAKE": make}
    for s in (1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 14, 17, 19, 22, 24):
        for make in TOOL_MAKES:
            yield {"TYPE": "HEX KEY L TYPE", "SIZE": f"{fmt(s)} MM", "MOC": "CR-V", "STANDARD": "ISO 2936", "MAKE": make}
    for typ in ("CHAIN PIPE", "STRAP", "FILTER BAND", "RATCHET HANDLE", "T HANDLE", "SPEED BRACE"):
        for make in TOOL_MAKES[:3]:
            yield {"TYPE": typ, "MAKE": make}


@SOCKET.generator(group=G_HT)
def tool_sockets():
    for drive, sizes in (("1/4 IN DRIVE", range(4, 15)), ("3/8 IN DRIVE", range(8, 23)), ("1/2 IN DRIVE", range(8, 33)),
                         ("3/4 IN DRIVE", range(19, 51)), ("1 IN DRIVE", range(27, 81))):
        for s in sizes:
            if s > 50 and s % 5:
                continue
            if s > 36 and s % 2 and s not in (41, 46):
                continue
            for typ, moc in (("HAND", "CR-V"), ("IMPACT", "CR-MO")):
                if typ == "IMPACT" and drive.startswith("1/4"):
                    continue
                for points in ("6 POINT", "12 POINT") if typ == "HAND" else ("6 POINT",):
                    for make in TOOL_MAKES[:4]:
                        yield {"TYPE": typ, "DRIVE": drive, "SIZE": f"{s} MM", "POINTS": points, "MOC": moc, "MAKE": make}


@SCREWDRIVER.generator
def screwdrivers():
    for tip, sizes in (("FLAT", ("3 X 75", "4 X 100", "5 X 125", "6 X 150", "8 X 200", "10 X 250")),
                       ("PHILLIPS", ("PH0 X 60", "PH1 X 80", "PH2 X 100", "PH3 X 150")),
                       ("POZIDRIV", ("PZ1 X 80", "PZ2 X 100", "PZ3 X 150"))):
        for size in sizes:
            for feature in ("", "VDE INSULATED 1000V"):
                for make in TOOL_MAKES:
                    yield {"TYPE": "STANDARD", "TIP": tip, "SIZE": f"{size} MM", "FEATURE": feature, "MAKE": make}
    for v in ("100-500V", "125-250V"):
        for make in TOOL_MAKES[:3]:
            yield {"TYPE": "LINE TESTER", "TIP": "FLAT", "SIZE": "3.5 MM", "FEATURE": v, "MAKE": make}


@PLIER.generator
def pliers():
    for typ, sizes in (("COMBINATION", (160, 180, 200, 250)), ("LONG NOSE", (150, 160, 200)),
                       ("DIAGONAL CUTTING", (125, 160, 180, 200)), ("CIRCLIP EXTERNAL STRAIGHT", (125, 180, 225, 300)),
                       ("CIRCLIP INTERNAL STRAIGHT", (125, 180, 225, 300)), ("CIRCLIP EXTERNAL BENT", (125, 180, 225)),
                       ("CIRCLIP INTERNAL BENT", (125, 180, 225)), ("WATER PUMP SLIP JOINT", (180, 250, 300, 400)),
                       ("LOCKING GRIP", (180, 250, 300)), ("WIRE STRIPPER", (160, 180)),
                       ("CABLE CUTTER", (210, 250, 500, 600))):
        for s in sizes:
            for feature in ("", "VDE INSULATED 1000V") if typ in ("COMBINATION", "LONG NOSE", "DIAGONAL CUTTING") else ("",):
                for make in TOOL_MAKES:
                    yield {"TYPE": typ, "SIZE": f"{s} MM", "FEATURE": feature, "MAKE": make}
    for lo, hi in ((1.5, 10), (6, 50), (16, 95), (10, 120), (16, 240), (50, 400), (120, 630)):
        for typ in ("CRIMPING HAND HEXAGONAL", "CRIMPING HYDRAULIC") if hi > 50 else ("CRIMPING HAND RATCHET",):
            for make in ("DOWELLS", "JAINSON", "KLAUKE"):
                yield {"TYPE": typ, "SIZE": f"{fmt(lo)}-{hi} SQ MM", "MAKE": make}


@HAMMER.generator
def hammers():
    for typ, weights in (("BALL PEIN", ("100 G", "200 G", "300 G", "450 G", "700 G", "900 G", "1 KG")),
                         ("SLEDGE DOUBLE FACE", ("2 KG", "3 KG", "4 KG", "5 KG", "6 KG", "8 KG", "10 KG")),
                         ("CROSS PEIN", ("200 G", "300 G", "500 G", "800 G")), ("CLAW", ("450 G", "570 G", "680 G")),
                         ("SOFT FACE NYLON", ("300 G", "500 G", "1 KG")), ("RUBBER MALLET", ("450 G", "700 G", "900 G")),
                         ("DEAD BLOW", ("500 G", "1 KG", "1.5 KG"))):
        for w in weights:
            for handle in ("WOODEN HANDLE", "FIBREGLASS HANDLE"):
                for make in TOOL_MAKES:
                    yield {"TYPE": typ, "WEIGHT": w, "HANDLE": handle, "MAKE": make}
    for w in ("450 G", "900 G", "2 KG", "4 KG"):
        yield {"TYPE": "BALL PEIN NON SPARKING BERYLLIUM COPPER", "WEIGHT": w, "HANDLE": "WOODEN HANDLE", "MAKE": "AMPCO"}


@FILE.generator
def files():
    for typ in ("FLAT", "HALF ROUND", "ROUND", "SQUARE", "TRIANGULAR", "KNIFE"):
        for size in (150, 200, 250, 300, 350):
            for cut in ("BASTARD", "SECOND CUT", "SMOOTH"):
                for make in ("JK", "BAHCO", "NICHOLSON", "PFERD"):
                    yield {"TYPE": typ, "CUT": cut, "SIZE": f"{size} MM", "MAKE": make}
    for typ in ("NEEDLE SET OF 6", "NEEDLE SET OF 12"):
        for make in ("JK", "BAHCO", "PFERD"):
            yield {"TYPE": typ, "SIZE": "160 MM", "MAKE": make}


@CHISEL.generator
def chisels():
    for typ, sizes in (("COLD FLAT", (12, 16, 19, 22, 25)), ("CAPE", (6, 8, 10)), ("WOOD", (6, 12, 18, 25, 32))):
        for s in sizes:
            for L in (150, 200, 250, 300):
                if typ == "WOOD" and L > 200:
                    continue
                for make in TOOL_MAKES[:3]:
                    yield {"TYPE": typ, "SIZE": f"{s} MM", "LENGTH": f"L {L} MM", "MAKE": make}


@PUNCH.generator
def punches():
    for typ, sizes in (("CENTRE", (3, 4, 5, 6, 8, 10)), ("PIN", (2, 3, 4, 5, 6, 8)), ("TAPER", (3, 4, 5, 6, 8)),
                       ("HOLLOW", (6, 8, 10, 12, 16, 20, 25, 32, 40, 50))):
        for s in sizes:
            for make in TOOL_MAKES[:3]:
                yield {"TYPE": typ, "SIZE": f"{s} MM", "MAKE": make}
    for typ in ("LETTER SET A-Z", "NUMBER SET 0-9"):
        for s in (3, 4, 5, 6, 8, 10, 12):
            yield {"TYPE": typ, "SIZE": f"{s} MM", "MAKE": "TAPARIA"}


@TOOL_KIT.generator
def tool_kits():
    for typ, pieces in (("SOCKET SET 1/2 IN DRIVE", (12, 24, 32)), ("SOCKET SET 3/8 IN DRIVE", (12, 20)),
                        ("COMBINATION SPANNER SET", (8, 12, 16, 25)), ("DOUBLE OPEN END SPANNER SET", (8, 12)),
                        ("HEX KEY SET", (7, 9, 10)), ("SCREWDRIVER SET", (6, 8, 12)),
                        ("MECHANIC TOOL KIT WITH BOX", (65, 94, 120, 150)), ("ELECTRICIAN TOOL KIT VDE", (9, 14, 22))):
        for n in pieces:
            for make in TOOL_MAKES:
                yield {"TYPE": typ, "PIECES": f"{n} PCS", "MAKE": make}


MEAS_MAKES = ("MITUTOYO", "INSIZE", "BAKER", "AEROSPACE", "STARRETT")


@CALIPER.generator
def calipers():
    for rng in (150, 200, 300, 450, 600, 1000):
        for typ, res in (("VERNIER", "0.02 MM"), ("DIAL", "0.02 MM"), ("DIGITAL", "0.01 MM")):
            if typ == "DIAL" and rng > 300:
                continue
            for make in MEAS_MAKES:
                yield {"TYPE": typ, "RANGE": f"0-{rng} MM", "RESOLUTION": res, "MAKE": make}
    for rng in (150, 200, 300):
        for typ in ("VERNIER DEPTH", "DIGITAL DEPTH", "VERNIER HEIGHT", "DIGITAL HEIGHT"):
            for make in MEAS_MAKES:
                yield {"TYPE": typ, "RANGE": f"0-{rng} MM", "RESOLUTION": "0.02 MM" if "VERNIER" in typ else "0.01 MM",
                       "MAKE": make}


@MICROMETER.generator
def micrometers():
    for lo in range(0, 300, 25):
        for typ, res in (("OUTSIDE MECHANICAL", "0.01 MM"), ("OUTSIDE DIGITAL", "0.001 MM")):
            for make in MEAS_MAKES:
                yield {"TYPE": typ, "RANGE": f"{lo}-{lo + 25} MM", "RESOLUTION": res, "MAKE": make}
    for rng in ("5-30 MM", "25-50 MM", "50-75 MM", "50-300 MM"):
        for typ in ("INSIDE TUBULAR", "INSIDE 3 POINT BORE"):
            for make in MEAS_MAKES[:3]:
                yield {"TYPE": typ, "RANGE": rng, "RESOLUTION": "0.005 MM", "MAKE": make}
    for rng in ("0-25 MM", "0-150 MM", "0-300 MM"):
        yield {"TYPE": "DEPTH", "RANGE": rng, "RESOLUTION": "0.01 MM", "MAKE": "MITUTOYO"}


@GAUGE_M.generator
def measuring_gauges():
    for typ, ranges in (("DIAL INDICATOR PLUNGER", ("0-10 MM 0.01 MM", "0-1 MM 0.001 MM", "0-25 MM 0.01 MM")),
                        ("DIAL TEST INDICATOR LEVER", ("0-0.8 MM 0.01 MM", "0-0.2 MM 0.002 MM")),
                        ("BORE GAUGE DIAL", ("18-35 MM", "35-60 MM", "50-160 MM", "160-250 MM")),
                        ("FEELER GAUGE SET", ("0.05-1 MM 20 BLADES", "0.03-1 MM 32 BLADES")),
                        ("THREAD PITCH GAUGE", ("METRIC 0.4-7 MM", "WHITWORTH 4-62 TPI")),
                        ("RADIUS GAUGE SET", ("1-7 MM", "7.5-15 MM", "15.5-25 MM")),
                        ("WELDING GAUGE", ("BRIDGE CAM", "FILLET")), ("COATING THICKNESS DFT", ("0-1500 MICRON", "0-5000 MICRON")),
                        ("ULTRASONIC THICKNESS", ("1-200 MM",)), ("VACUUM", ("0-760 MMHG",)),
                        ("MAGNETIC BASE STAND", ("60 KG PULL", "80 KG PULL"))):
        for r in ranges:
            for make in MEAS_MAKES[:3]:
                yield {"TYPE": typ, "RANGE": r, "MAKE": make}
    for d in (3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 28, 30, 32, 35, 40, 45, 50):
        yield {"TYPE": "PLUG GO NOGO", "SIZE": f"DIA {d} MM", "CLASS": "H7", "MAKE": "MITUTOYO"}
    for thread in METRIC_THREADS:
        yield {"TYPE": "THREAD PLUG GO NOGO", "SIZE": thread, "CLASS": "6H"}
        yield {"TYPE": "THREAD RING GO NOGO", "SIZE": thread, "CLASS": "6G"}
    for n in (32, 47, 56, 81, 87, 103, 112):
        for cls in ("GRADE 0", "GRADE 1", "GRADE 2"):
            yield {"TYPE": "SLIP GAUGE BLOCK SET", "SIZE": f"{n} PCS", "CLASS": cls, "MAKE": "MITUTOYO"}


@TAPE.generator
def tapes():
    for L in (3, 5, 7.5, 8, 10):
        for w in ("19 MM", "25 MM"):
            for make in ("STANLEY", "FREEMANS", "TAPARIA", "KOMELON"):
                yield {"TYPE": "POCKET STEEL", "LENGTH": f"{fmt(L)} M", "WIDTH": w, "MAKE": make}
    for L in (15, 20, 30, 50, 100):
        for typ in ("STEEL LONG", "FIBREGLASS LONG"):
            for make in ("STANLEY", "FREEMANS", "KOMELON"):
                yield {"TYPE": typ, "LENGTH": f"{L} M", "WIDTH": "13 MM", "MAKE": make}
    for rng in ("40 M", "60 M", "100 M"):
        yield {"TYPE": "LASER DISTANCE METER", "LENGTH": rng, "MAKE": "BOSCH"}


@RULE.generator
def rules():
    for L in (150, 300, 600, 1000, 1500, 2000):
        for typ in ("STEEL", "STEEL FLEXIBLE"):
            for make in ("MITUTOYO", "INSIZE", "FREEMANS"):
                yield {"TYPE": typ, "LENGTH": f"{L} MM", "MAKE": make}
    for L in (100, 150, 200, 300, 500):
        yield {"TYPE": "TRY SQUARE", "LENGTH": f"{L} MM", "MAKE": "INSIZE"}
    for L in (150, 300):
        yield {"TYPE": "COMBINATION SET", "LENGTH": f"{L} MM", "MAKE": "STARRETT"}


@LEVEL.generator
def levels():
    for L in (150, 200, 250, 300):
        for acc in ("0.02 MM/M", "0.05 MM/M"):
            yield {"TYPE": "PRECISION MACHINIST", "LENGTH": f"{L} MM", "ACCURACY": acc, "MAKE": "MITUTOYO"}
    for L in (300, 600, 1000, 1200, 1800):
        for make in ("STANLEY", "STABILA"):
            yield {"TYPE": "ALUMINIUM BOX", "LENGTH": f"{L} MM", "ACCURACY": "0.5 MM/M", "MAKE": make}
    for make in ("BOSCH", "STANLEY", "LEICA"):
        yield {"TYPE": "LASER CROSS LINE", "ACCURACY": "0.3 MM/M", "MAKE": make}


@POWER_TOOL.generator
def power_tools():
    groups = [("ANGLE GRINDER", (("100 MM", "750W"), ("125 MM", "1100W"), ("180 MM", "2000W"), ("230 MM", "2400W"))),
              ("DRILL MACHINE", (("10 MM", "500W"), ("13 MM", "650W"), ("13 MM IMPACT", "750W"))),
              ("ROTARY HAMMER SDS PLUS", (("26 MM", "800W"), ("28 MM", "900W"))),
              ("ROTARY HAMMER SDS MAX", (("40 MM", "1100W"), ("45 MM", "1500W"))),
              ("MAGNETIC DRILL", (("32 MM", "1100W"), ("50 MM", "1200W"), ("75 MM", "1600W"))),
              ("CHOP SAW", (("355 MM", "2200W"),)), ("JIGSAW", (("65 MM", "650W"),)),
              ("CIRCULAR SAW", (("185 MM", "1400W"), ("235 MM", "2000W"))),
              ("DIE GRINDER", (("6 MM COLLET", "500W"),)), ("HEAT GUN", (("", "2000W"),)),
              ("IMPACT WRENCH 1/2 IN", (("", "500W"),)), ("BLOWER", (("", "650W"),)),
              ("POLISHER", (("180 MM", "1300W"),)), ("DEMOLITION HAMMER", (("HEX 30 MM", "1700W"),))]
    for typ, variants in groups:
        for size, w in variants:
            for make in POWER_MAKES:
                yield {"TYPE": typ, "SIZE": size, "POWER": w, "VOLTAGE": "230V", "MAKE": make}
    for typ in ("DRILL DRIVER", "IMPACT DRIVER", "IMPACT WRENCH 1/2 IN", "ANGLE GRINDER 125 MM"):
        for v in ("12V", "18V"):
            for make in POWER_MAKES:
                yield {"TYPE": f"CORDLESS {typ}", "VOLTAGE": f"{v} LI-ION", "MAKE": make}
    for drive, nm in (("1/2 IN", 800), ("3/4 IN", 1500), ("1 IN", 3000)):
        for make in ("INGERSOLL RAND", "CHICAGO PNEUMATIC", "ATLAS COPCO"):
            yield {"TYPE": f"PNEUMATIC IMPACT WRENCH {drive}", "POWER": f"{nm} NM", "MAKE": make}
