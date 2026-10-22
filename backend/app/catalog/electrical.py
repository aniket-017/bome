"""Cables, wiring accessories, switchgear, control gear, lighting, cable management, power supply."""
from app.catalog import noun
from app.catalog.data import CABLE_MAKES, SWITCHGEAR_MAKES, fmt
from app.catalog.piping import PLUG
from app.catalog.raw import STRIP

G = "ELECTRICAL"
G_CAB = "CABLES AND WIRES"
G_SWG = "SWITCHGEAR AND CONTROLGEAR"
G_LT = "LIGHTING"
CABLE = noun("CABLE", G_CAB, "MTR", ("TYPE", "VOLTAGE", "CONDUCTOR", "CORES", "SIZE", "INSULATION", "SCREEN", "ARMOUR",
                                     "SHEATH", "COLOR", "STANDARD", "MAKE"))
GLAND = noun("CABLE GLAND", G, "NOS", ("TYPE", "MOC", "SIZE", "THREAD", "PROTECTION", "FEATURE", "MAKE"))
LUG = noun("CABLE LUG", G, "NOS", ("TYPE", "MOC", "SIZE", "STUD", "FINISH", "MAKE"))
TERMINAL = noun("TERMINAL", G, "NOS", ("TYPE", "SIZE", "MOUNTING", "COLOR", "MAKE"))
CONNECTOR = noun("CONNECTOR", G, "NOS", ("TYPE", "MOC", "SIZE", "POLES", "RATING", "PROTECTION", "MAKE"))
SOCKET = noun("SOCKET", G, "NOS", ("TYPE", "DRIVE", "SIZE", "POINTS", "POLES", "RATING", "VOLTAGE", "PROTECTION",
                                   "MOUNTING", "MOC", "MAKE"))
BREAKER = noun("CIRCUIT BREAKER", G_SWG, "NOS", ("TYPE", "POLES", "RATING", "CURVE", "BREAKING", "SENSITIVITY",
                                                  "RELEASE", "FEATURE", "MAKE"))
CONTACTOR = noun("CONTACTOR", G_SWG, "NOS", ("TYPE", "POLES", "RATING", "COIL", "AUX", "MAKE"))
RELAY = noun("RELAY", G_SWG, "NOS", ("TYPE", "RANGE", "CONTACTS", "COIL", "FUNCTION", "MOUNTING", "MAKE"))
FUSE = noun("FUSE", G_SWG, "NOS", ("TYPE", "SIZE", "RATING", "CLASS", "VOLTAGE", "MAKE"))
SWITCH = noun("SWITCH", G_SWG, "NOS", ("TYPE", "POLES", "RATING", "RANGE", "MOC", "CONNECTION", "PROTECTION",
                                       "FEATURE", "MAKE"))
PUSH_BUTTON = noun("PUSH BUTTON", G_SWG, "NOS", ("TYPE", "SIZE", "COLOR", "CONTACTS", "VOLTAGE", "MAKE"))
INDICATOR = noun("INDICATOR", G_SWG, "NOS", ("TYPE", "SIZE", "COLOR", "VOLTAGE", "MAKE"))
METER = noun("METER", G, "NOS", ("TYPE", "PRINCIPLE", "SIZE", "RANGE", "MOC", "LINER", "RATING", "END", "ACCURACY",
                                 "INPUT", "OUTPUT", "MAKE"))
TRANSFORMER = noun("TRANSFORMER", G, "NOS", ("TYPE", "RATING", "RATIO", "VOLTAGE", "CLASS", "BURDEN", "COOLING",
                                             "CONSTRUCTION", "MAKE"))
DRIVE = noun("DRIVE", G, "NOS", ("TYPE", "POWER", "VOLTAGE", "PROTECTION", "FEATURE", "MAKE"))
LIGHT = noun("LIGHT FITTING", G_LT, "NOS", ("TYPE", "POWER", "CCT", "LAMP", "MOUNTING", "PROTECTION", "FEATURE", "MAKE"))
LAMP = noun("LAMP", G_LT, "NOS", ("TYPE", "POWER", "CCT", "BASE", "MAKE"))
TRAY = noun("CABLE TRAY", G, "MTR", ("TYPE", "MOC", "WIDTH", "HEIGHT", "THICKNESS", "FINISH", "STANDARD"))
CONDUIT = noun("CONDUIT", G, "MTR", ("TYPE", "MOC", "SIZE", "CLASS", "FINISH", "STANDARD"))
JB = noun("JUNCTION BOX", G, "NOS", ("TYPE", "MOC", "SIZE", "ENTRIES", "TERMINALS", "PROTECTION", "MAKE"))
BATTERY = noun("BATTERY", G, "NOS", ("TYPE", "VOLTAGE", "CAPACITY", "MAKE"))
CHARGER = noun("CHARGER", G, "NOS", ("TYPE", "VOLTAGE", "CURRENT", "INPUT", "MAKE"))
BUSBAR = noun("BUSBAR", G, "KG", ("TYPE", "MOC", "SPEC", "SIZE", "FINISH"))
CAPACITOR = noun("CAPACITOR", G, "NOS", ("TYPE", "RATING", "VOLTAGE", "CONSTRUCTION", "MAKE"))
INSULATOR = noun("INSULATOR", G, "NOS", ("TYPE", "MOC", "SIZE", "VOLTAGE", "THREAD"))
RESISTOR = noun("RESISTOR", G, "NOS", ("TYPE", "RESISTANCE", "POWER", "CONSTRUCTION"))
CONTROLLER = noun("CONTROLLER", "INSTRUMENTATION", "NOS", ("TYPE", "SIZE", "INPUT", "OUTPUT", "SUPPLY", "FEATURE", "MAKE"))
PLC = noun("PLC MODULE", "AUTOMATION", "NOS", ("TYPE", "SERIES", "CHANNELS", "SIGNAL", "MAKE"))
ELECTRODE = noun("ELECTRODE", G, "NOS", ("TYPE", "MOC", "SPEC", "CLASS", "SIZE", "DIA", "LENGTH", "PACK", "MAKE"))

LT_SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]


def sqmm(s: float) -> str:
    return f"{fmt(s)} SQ MM"


@CABLE.generator
def lt_power_cables():
    for cond in ("CU", "AL"):
        for cores in ("1C", "2C", "3C", "3.5C", "4C"):
            for s in LT_SIZES:
                if cond == "AL" and s < 2.5:
                    continue
                if cores == "1C" and s < 4:
                    continue
                if cores == "3.5C" and not 25 <= s <= 400:
                    continue
                if cores in ("2C", "3C", "4C") and s > (400 if cond == "AL" else 300):
                    continue
                if cores == "2C" and s > 50:
                    continue
                armours = ["UNARMOURED", "AL WIRE ARMOURED"] if cores == "1C" else \
                    ["UNARMOURED", "GI WIRE ARMOURED" if s <= 16 else "GI STRIP ARMOURED"]
                for ins, std in (("XLPE", "IS 7098-1"), ("PVC", "IS 1554-1")):
                    for armour in armours:
                        for sheath in ("PVC ST2", "FRLS PVC"):
                            for make in CABLE_MAKES:
                                yield {"TYPE": "LT POWER", "VOLTAGE": "1.1 KV", "CONDUCTOR": cond, "CORES": cores,
                                       "SIZE": sqmm(s), "INSULATION": ins, "ARMOUR": armour, "SHEATH": sheath,
                                       "STANDARD": std, "MAKE": make}


@CABLE.generator
def control_cables():
    for s in (0.5, 0.75, 1, 1.5, 2.5, 4):
        for cores in (2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 19, 24, 27, 30, 37, 44, 52, 61):
            if s >= 4 and cores > 12:
                continue
            for ins in ("PVC", "XLPE"):
                for armour in ("UNARMOURED", "GI WIRE ARMOURED"):
                    for sheath in ("PVC ST2", "FRLS PVC"):
                        for make in CABLE_MAKES:
                            yield {"TYPE": "CONTROL", "VOLTAGE": "1.1 KV", "CONDUCTOR": "CU", "CORES": f"{cores}C",
                                   "SIZE": sqmm(s), "INSULATION": ins, "ARMOUR": armour, "SHEATH": sheath,
                                   "STANDARD": "IS 1554-1" if ins == "PVC" else "IS 7098-1", "MAKE": make}


@CABLE.generator
def instrumentation_cables():
    for unit in ("PAIR", "TRIAD"):
        for n in (1, 2, 4, 6, 8, 10, 12, 16, 20, 24):
            if unit == "TRIAD" and n > 12:
                continue
            for s in (0.5, 0.75, 1, 1.5):
                for screen in ("OVERALL SHIELDED", "INDIVIDUAL AND OVERALL SHIELDED"):
                    if n == 1 and screen.startswith("INDIVIDUAL"):
                        continue
                    for armour in ("UNARMOURED", "GI WIRE ARMOURED"):
                        for make in CABLE_MAKES:
                            yield {"TYPE": "INSTRUMENTATION", "VOLTAGE": "300/500 V", "CONDUCTOR": "ATC CU",
                                   "CORES": f"{n} {unit}", "SIZE": sqmm(s), "INSULATION": "PVC",
                                   "SCREEN": f"{screen} AL MYLAR", "ARMOUR": armour, "SHEATH": "FRLS PVC",
                                   "STANDARD": "BS EN 50288-7", "MAKE": make}
    for tc, color in (("K", "KX"), ("J", "JX"), ("T", "TX"), ("R/S", "SX COMPENSATING"), ("N", "NX")):
        for n in (1, 2, 4, 6, 8, 12, 16, 24):
            for s in (0.5, 1.5):
                for armour in ("UNARMOURED", "GI WIRE ARMOURED"):
                    yield {"TYPE": f"THERMOCOUPLE EXTENSION TYPE {tc}", "CONDUCTOR": color, "CORES": f"{n} PAIR",
                           "SIZE": sqmm(s), "INSULATION": "PVC", "SCREEN": "INDIVIDUAL AND OVERALL SHIELDED",
                           "ARMOUR": armour, "SHEATH": "FRLS PVC", "STANDARD": "IEC 60584-3", "MAKE": "POLYCAB"}


@CABLE.generator
def ht_cables():
    ranges = {"3.3 KV (E)": (25, 400), "6.6 KV (UE)": (35, 400), "11 KV (UE)": (35, 400), "22 KV (E)": (70, 400),
              "33 KV (E)": (95, 400)}
    for kv, (lo, hi) in ranges.items():
        for cond in ("AL", "CU"):
            for cores in ("1C", "3C"):
                for s in [s for s in LT_SIZES if lo <= s <= (630 if cores == "1C" else hi)] + ([800, 1000] if cores == "1C" else []):
                    armour = "AL WIRE ARMOURED" if cores == "1C" else "GI STRIP ARMOURED"
                    for make in CABLE_MAKES:
                        yield {"TYPE": "HT POWER", "VOLTAGE": kv, "CONDUCTOR": cond, "CORES": cores, "SIZE": sqmm(s),
                               "INSULATION": "XLPE", "SCREEN": "CU TAPE SCREENED", "ARMOUR": armour,
                               "SHEATH": "FRLS PVC", "STANDARD": "IS 7098-2", "MAKE": make}


@CABLE.generator
def flexible_cables():
    for s in (0.5, 0.75, 1, 1.5, 2.5, 4, 6):
        for cores in (1, 2, 3, 4, 5):
            colors = ("RED", "BLACK", "YELLOW", "BLUE", "GREEN", "GREY") if cores == 1 else ("",)
            for ins in ("FR PVC", "FRLS PVC", "HFFR", "ZHFR"):
                for color in colors:
                    for make in CABLE_MAKES:
                        yield {"TYPE": "FLEXIBLE" if cores > 1 else "BUILDING WIRE FLEXIBLE", "VOLTAGE": "1.1 KV",
                               "CONDUCTOR": "CU", "CORES": f"{cores}C", "SIZE": sqmm(s), "INSULATION": ins,
                               "COLOR": color, "STANDARD": "IS 694", "MAKE": make}
    for s in (16, 25, 35, 50, 70, 95, 120):
        yield {"TYPE": "WELDING", "CONDUCTOR": "FLEXIBLE CU", "CORES": "1C", "SIZE": sqmm(s), "INSULATION": "RUBBER",
               "SHEATH": "PCP", "STANDARD": "IS 9857"}
    for typ in ("LAN CAT6 UTP", "LAN CAT6 FTP", "LAN CAT6A SFTP", "COAXIAL RG6", "COAXIAL RG59", "TELEPHONE 2 PAIR",
                "TELEPHONE 10 PAIR", "OPTICAL FIBRE 6 CORE SM ARMOURED", "OPTICAL FIBRE 12 CORE SM ARMOURED",
                "OPTICAL FIBRE 24 CORE SM ARMOURED", "OPTICAL FIBRE 12 CORE MM OM3"):
        for make in ("D-LINK", "SCHNEIDER", "POLYCAB", "FINOLEX"):
            yield {"TYPE": typ, "MAKE": make}
    for typ, cores, sizes in (("TRAILING EPR CSP", (3, 4), (2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95)),
                              ("SUBMERSIBLE FLAT PVC", (3,), (1.5, 2.5, 4, 6, 10, 16, 25)),
                              ("SILICONE RUBBER HIGH TEMPERATURE", (1,), (0.5, 0.75, 1, 1.5, 2.5, 4, 6, 10)),
                              ("FIRE SURVIVAL", (2, 3, 4), (1.5, 2.5, 4))):
        for c in cores:
            for s in sizes:
                for make in CABLE_MAKES[:3]:
                    yield {"TYPE": typ, "VOLTAGE": "1.1 KV", "CONDUCTOR": "CU", "CORES": f"{c}C", "SIZE": sqmm(s),
                           "MAKE": make}


@STRIP.generator(group=G)
def earthing_strips():
    for moc, finish in (("GI", "HOT DIP GALVANISED"), ("CU", "BARE"), ("CU", "TINNED")):
        for w, t in ((20, 3), (25, 3), (25, 6), (32, 6), (40, 5), (40, 6), (50, 6), (50, 10), (75, 10)):
            yield {"TYPE": "EARTHING", "MOC": moc, "SIZE": f"{w} X {t} MM", "FINISH": finish}


@ELECTRODE.generator(group=G)
def earthing_electrodes():
    for typ, moc, dias in (("EARTHING PIPE", "GI", ("40 NB", "50 NB", "80 NB")),
                           ("EARTHING PLATE", "GI", ("600 X 600 X 6 MM",)), ("EARTHING PLATE", "CU", ("600 X 600 X 3 MM",)),
                           ("EARTHING ROD", "CU BONDED STEEL", ("14.2 MM", "17.2 MM")),
                           ("EARTHING CHEMICAL", "CU BONDED", ("50 MM", "80 MM"))):
        for d in dias:
            yield {"TYPE": typ, "MOC": moc, "SIZE": d, "LENGTH": "" if "PLATE" in typ else "L 3000 MM"}


GLAND_SIZES = {"20S/16": ("M20", "1/2 NPT"), "20S": ("M20", "1/2 NPT"), "20": ("M20", "1/2 NPT"),
               "25": ("M25", "3/4 NPT"), "32": ("M32", "1 NPT"), "40": ("M40", "1-1/4 NPT"),
               "50S": ("M50", "1-1/2 NPT"), "50": ("M50", "1-1/2 NPT"), "63S": ("M63", "2 NPT"), "63": ("M63", "2 NPT"),
               "75S": ("M75", "2-1/2 NPT"), "75": ("M75", "2-1/2 NPT"), "90": ("M90", "3 NPT")}


@GLAND.generator
def cable_glands():
    for typ, prot in (("DOUBLE COMPRESSION ARMOURED", "IP66"), ("SINGLE COMPRESSION UNARMOURED", "IP66"),
                      ("EX D DOUBLE COMPRESSION BARRIER", "EX D IIC IP66"), ("EX E DOUBLE COMPRESSION", "EX E II IP66")):
        for moc in ("BRASS", "NICKEL PLATED BRASS", "SS316", "AL"):
            for size, threads in GLAND_SIZES.items():
                for thread in threads:
                    for make in ("COMET", "HAWKE", "CCG", "BALIGA"):
                        yield {"TYPE": typ, "MOC": moc, "SIZE": size, "THREAD": thread, "PROTECTION": prot,
                               "MAKE": make}


LUG_STUDS = {1.5: ("M4", "M5"), 2.5: ("M4", "M5", "M6"), 4: ("M5", "M6"), 6: ("M5", "M6", "M8"), 10: ("M6", "M8"),
             16: ("M6", "M8", "M10"), 25: ("M8", "M10"), 35: ("M8", "M10", "M12"), 50: ("M10", "M12"),
             70: ("M10", "M12"), 95: ("M12",), 120: ("M12", "M16"), 150: ("M12", "M16"), 185: ("M16",),
             240: ("M16",), 300: ("M16",), 400: ("M16", "M20"), 500: ("M20",), 630: ("M20",)}


@LUG.generator
def cable_lugs():
    for s, studs in LUG_STUDS.items():
        for stud in studs:
            for typ, moc, finish in (("RING TUBULAR CRIMPING", "CU", "TINNED"), ("RING TUBULAR CRIMPING", "AL", ""),
                                     ("RING TUBULAR CRIMPING BIMETALLIC", "AL CU", ""),
                                     ("RING TUBULAR CRIMPING LONG BARREL", "CU", "TINNED")):
                if moc != "CU" and s < 10:
                    continue
                for make in ("DOWELLS", "JAINSON", "3D", "COMET"):
                    yield {"TYPE": typ, "MOC": moc, "SIZE": sqmm(s), "STUD": f"{stud} STUD", "FINISH": finish,
                           "MAKE": make}
    for s in (0.5, 1, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50):
        for typ in ("PIN INSULATED", "FORK INSULATED", "BOOTLACE FERRULE INSULATED", "PIN UNINSULATED"):
            for make in ("DOWELLS", "JAINSON", "3D"):
                yield {"TYPE": typ, "MOC": "CU", "SIZE": sqmm(s), "FINISH": "TINNED", "MAKE": make}


@TERMINAL.generator
def terminals():
    for typ, sizes in (("SCREW CLAMP", (2.5, 4, 6, 10, 16, 35, 50, 70, 95, 120, 150, 240)),
                       ("SPRING CLAMP", (1.5, 2.5, 4, 6, 10, 16, 35)), ("PUSH IN", (1.5, 2.5, 4, 6, 10)),
                       ("FUSE", (4, 6)), ("EARTH", (2.5, 4, 6, 10, 16, 35, 50, 95)), ("DISCONNECT KNIFE", (4, 6)),
                       ("DOUBLE DECK", (2.5, 4)), ("THERMOCOUPLE", (2.5,))):
        for s in sizes:
            colors = ("GREEN YELLOW",) if typ == "EARTH" else ("GREY", "BLUE") if typ in ("SCREW CLAMP", "SPRING CLAMP") else ("GREY",)
            for color in colors:
                for make in ("PHOENIX CONTACT", "WAGO", "CONNECTWELL", "ELMEX", "WEIDMULLER"):
                    yield {"TYPE": typ, "SIZE": sqmm(s), "MOUNTING": "DIN RAIL", "COLOR": color, "MAKE": make}


@CONNECTOR.generator
def connectors():
    for poles in (3, 4, 5, 7, 10, 16, 24, 32, 48):
        for rating in ("10A", "16A", "35A"):
            if poles > 24 and rating == "35A":
                continue
            for make in ("HARTING", "PHOENIX CONTACT", "ILME", "WEIDMULLER"):
                yield {"TYPE": "HEAVY DUTY RECTANGULAR", "POLES": f"{poles} PIN", "RATING": rating, "PROTECTION": "IP65",
                       "MAKE": make}
    for typ in ("M12 A CODED", "M12 D CODED", "M8"):
        for poles in (3, 4, 5, 8):
            if typ == "M8" and poles > 4:
                continue
            for cable in ("STRAIGHT FEMALE 5M CABLE", "90 DEG FEMALE 5M CABLE", "STRAIGHT MALE FIELD WIREABLE"):
                yield {"TYPE": f"{typ} {cable}", "POLES": f"{poles} PIN", "PROTECTION": "IP67", "MAKE": "PHOENIX CONTACT"}
    for s in (1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240):
        for typ, moc in (("BUTT CRIMPING", "CU TINNED"), ("BUTT CRIMPING", "AL"), ("PIERCING", "AL")):
            yield {"TYPE": typ, "MOC": moc, "SIZE": sqmm(s)}


@SOCKET.generator
def sockets():
    for rating in ("16A", "32A", "63A", "125A"):
        for poles, volt in (("3P", "230V"), ("4P", "415V"), ("5P", "415V")):
            for prot in ("IP44", "IP67"):
                for mounting in ("SURFACE", "PANEL"):
                    for make in ("LEGRAND", "SCHNEIDER", "MENNEKES", "ABB"):
                        yield {"TYPE": "INDUSTRIAL", "POLES": poles, "RATING": rating, "VOLTAGE": volt,
                               "PROTECTION": prot, "MOUNTING": mounting, "MAKE": make}
    for rating in ("6A", "16A"):
        for typ in ("MODULAR 3 PIN", "MODULAR 5 PIN", "METALCLAD 3 PIN WITH SWITCH"):
            for make in ("LEGRAND", "SCHNEIDER", "HAVELLS", "ANCHOR"):
                yield {"TYPE": typ, "RATING": rating, "VOLTAGE": "230V", "MAKE": make}
    for rating in ("16A", "32A", "63A", "125A"):
        for poles in ("3P", "4P", "5P"):
            for prot in ("IP44", "IP67"):
                for make in ("LEGRAND", "SCHNEIDER", "MENNEKES", "ABB"):
                    yield {"TYPE": "INDUSTRIAL", "POLES": poles, "RATING": rating, "PROTECTION": prot,
                           "MOUNTING": "INLINE CONNECTOR", "MAKE": make}


@PLUG.generator(group=G)
def industrial_plugs():
    for rating in ("16A", "32A", "63A", "125A"):
        for poles in ("3P", "4P", "5P"):
            for prot in ("IP44", "IP67"):
                for make in ("LEGRAND", "SCHNEIDER", "MENNEKES", "ABB"):
                    yield {"TYPE": "INDUSTRIAL", "RATING": rating, "POLES": poles, "PROTECTION": prot, "MAKE": make}


MCB_RATINGS = (0.5, 1, 2, 4, 6, 10, 16, 20, 25, 32, 40, 50, 63)


@BREAKER.generator
def breakers():
    for poles in ("SP", "SPN", "DP", "TP", "TPN", "FP"):
        for a in MCB_RATINGS + (80, 100, 125):
            for curve in ("B CURVE", "C CURVE", "D CURVE"):
                for ka in ("6 KA", "10 KA"):
                    if a > 63 and ka == "6 KA":
                        continue
                    for make in SWITCHGEAR_MAKES:
                        yield {"TYPE": "MCB", "POLES": poles, "RATING": f"{fmt(a)}A", "CURVE": curve, "BREAKING": ka,
                               "MAKE": make}
    for poles in ("2P", "4P"):
        for a in (25, 40, 63, 80, 100):
            for ma in ("30 MA", "100 MA", "300 MA"):
                for typ in ("TYPE AC", "TYPE A"):
                    for make in SWITCHGEAR_MAKES:
                        yield {"TYPE": "RCCB", "POLES": poles, "RATING": f"{a}A", "CURVE": typ, "SENSITIVITY": ma,
                               "MAKE": make}
        for a in (6, 10, 16, 20, 25, 32, 40, 63):
            for ma in ("30 MA", "100 MA", "300 MA"):
                for make in SWITCHGEAR_MAKES:
                    yield {"TYPE": "RCBO", "POLES": poles, "RATING": f"{a}A", "CURVE": "C CURVE", "BREAKING": "10 KA",
                           "SENSITIVITY": ma, "MAKE": make}
    for poles in ("3P", "4P"):
        for a in (16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 320, 400, 500, 630, 800, 1000, 1250, 1600):
            for ka in ("25 KA", "36 KA", "50 KA", "70 KA"):
                for release in ("THERMAL MAGNETIC", "MICROPROCESSOR"):
                    if release == "MICROPROCESSOR" and a < 40:
                        continue
                    for make in SWITCHGEAR_MAKES:
                        yield {"TYPE": "MCCB", "POLES": poles, "RATING": f"{a}A", "BREAKING": ka, "RELEASE": release,
                               "MAKE": make}
        for a in (630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300):
            for ka in ("50 KA", "65 KA", "85 KA", "100 KA"):
                for feature in ("EDO ELECTRICALLY OPERATED DRAWOUT", "MDO MANUALLY OPERATED DRAWOUT",
                                "EF ELECTRICALLY OPERATED FIXED"):
                    for make in SWITCHGEAR_MAKES[:4]:
                        yield {"TYPE": "ACB", "POLES": poles, "RATING": f"{a}A", "BREAKING": ka,
                               "RELEASE": "MICROPROCESSOR LSIG", "FEATURE": feature, "MAKE": make}
    for lo, hi in ((0.1, 0.16), (0.16, 0.25), (0.25, 0.4), (0.4, 0.63), (0.63, 1), (1, 1.6), (1.6, 2.5), (2.5, 4),
                   (4, 6.3), (6, 10), (9, 14), (13, 18), (17, 23), (20, 25), (24, 32), (25, 40), (32, 50), (40, 63),
                   (56, 80), (70, 100)):
        for make in SWITCHGEAR_MAKES:
            yield {"TYPE": "MPCB MOTOR PROTECTION", "POLES": "3P", "RATING": f"{fmt(lo)}-{fmt(hi)}A", "MAKE": make}
    for kv in ("3.3 KV", "6.6 KV", "11 KV", "33 KV"):
        for a in (630, 800, 1250, 2000, 2500, 3150):
            for ka in ("25 KA", "31.5 KA", "40 KA"):
                for make in ("ABB", "SIEMENS", "SCHNEIDER", "L AND T"):
                    yield {"TYPE": f"VCB {kv} INDOOR", "POLES": "3P", "RATING": f"{a}A", "BREAKING": ka,
                           "FEATURE": "DRAWOUT", "MAKE": make}


AC3 = (9, 12, 18, 25, 32, 40, 50, 65, 80, 95, 115, 150, 185, 225, 265, 330, 400, 500, 630, 800)


@CONTACTOR.generator
def contactors():
    for a in AC3:
        for coil in ("24 VDC", "110 VAC", "230 VAC", "415 VAC"):
            for aux in ("1NO+1NC", "2NO+2NC"):
                for make in SWITCHGEAR_MAKES:
                    yield {"TYPE": "POWER AC3", "POLES": "3P", "RATING": f"{a}A", "COIL": f"{coil} COIL", "AUX": aux,
                           "MAKE": make}
    for kvar in (5, 7.5, 10, 12.5, 15, 20, 25, 30, 50, 60):
        for make in SWITCHGEAR_MAKES:
            yield {"TYPE": "CAPACITOR DUTY", "POLES": "3P", "RATING": f"{fmt(kvar)} KVAR", "COIL": "230 VAC COIL",
                   "MAKE": make}
    for aux in ("4NO", "3NO+1NC", "2NO+2NC"):
        for coil in ("24 VDC", "110 VAC", "230 VAC"):
            for make in SWITCHGEAR_MAKES:
                yield {"TYPE": "AUXILIARY CONTROL", "POLES": "4P", "RATING": "10A", "COIL": f"{coil} COIL", "AUX": aux,
                       "MAKE": make}


@RELAY.generator
def relays():
    for lo, hi in ((0.1, 0.16), (0.16, 0.25), (0.25, 0.4), (0.4, 0.63), (0.63, 1), (1, 1.6), (1.6, 2.5), (2.5, 4),
                   (4, 6), (5.5, 8), (7, 10), (9, 13), (12, 18), (17, 25), (23, 32), (30, 38), (37, 50), (48, 65),
                   (55, 70), (63, 80), (80, 104), (95, 120), (110, 150), (150, 200), (200, 330), (300, 500)):
        for typ in ("THERMAL OVERLOAD", "ELECTRONIC OVERLOAD"):
            for make in SWITCHGEAR_MAKES:
                yield {"TYPE": typ, "RANGE": f"{fmt(lo)}-{fmt(hi)}A", "CONTACTS": "1NO+1NC", "MAKE": make}
    for contacts in ("1CO", "2CO", "4CO"):
        for coil in ("12 VDC", "24 VDC", "24 VAC", "110 VAC", "230 VAC"):
            for typ in ("CONTROL PLUG IN WITH BASE", "INTERFACE SLIM DIN RAIL"):
                if typ.startswith("INTERFACE") and contacts == "4CO":
                    continue
                for make in ("OMRON", "PHOENIX CONTACT", "FINDER", "SCHNEIDER", "WEIDMULLER"):
                    yield {"TYPE": typ, "CONTACTS": contacts, "COIL": f"{coil} COIL", "MAKE": make}
    for fn in ("ON DELAY", "OFF DELAY", "STAR DELTA", "MULTIFUNCTION", "CYCLIC"):
        for supply in ("24-240 VAC/DC", "230 VAC"):
            for make in ("OMRON", "SCHNEIDER", "SIEMENS", "L AND T", "SELEC"):
                yield {"TYPE": "TIMER", "RANGE": "0.1 SEC-100 HR", "CONTACTS": "2CO", "COIL": supply, "FUNCTION": fn,
                       "MOUNTING": "DIN RAIL", "MAKE": make}
    for fn in ("NUMERICAL OVERCURRENT AND EARTH FAULT 50/51 50N/51N", "NUMERICAL MOTOR PROTECTION",
               "NUMERICAL FEEDER PROTECTION", "TRANSFORMER DIFFERENTIAL 87T", "UNDER OVER VOLTAGE 27/59",
               "MASTER TRIP 86", "TRIP CIRCUIT SUPERVISION 74", "EARTH LEAKAGE", "PHASE FAILURE PREVENTER"):
        for make in ("ABB", "SIEMENS", "SCHNEIDER", "GE", "L AND T", "MINILEC"):
            yield {"TYPE": "PROTECTION", "FUNCTION": fn, "MOUNTING": "FLUSH PANEL", "MAKE": make}


@FUSE.generator
def fuses():
    nh = {"000": (2, 160), "00": (6, 160), "1": (80, 250), "2": (125, 400), "3": (315, 630), "4": (500, 1250)}
    ratings = (2, 4, 6, 10, 16, 20, 25, 32, 35, 40, 50, 63, 80, 100, 125, 160, 200, 224, 250, 315, 355, 400, 500, 630,
               800, 1000, 1250)
    for size, (lo, hi) in nh.items():
        for a in ratings:
            if lo <= a <= hi:
                for cls in ("GG", "AM", "AR SEMICONDUCTOR"):
                    for make in ("SIEMENS", "L AND T", "ABB", "BUSSMANN", "HAVELLS"):
                        yield {"TYPE": "HRC LINK DIN NH", "SIZE": f"SIZE {size}", "RATING": f"{a}A", "CLASS": cls,
                               "VOLTAGE": "500 VAC", "MAKE": make}
    for size in ("5 X 20 MM", "6.3 X 32 MM", "10 X 38 MM", "14 X 51 MM", "22 X 58 MM"):
        for a in (0.5, 1, 2, 4, 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125):
            limit = {"5 X 20 MM": 10, "6.3 X 32 MM": 20, "10 X 38 MM": 32, "14 X 51 MM": 63}.get(size, 125)
            if a <= limit:
                yield {"TYPE": "CARTRIDGE GLASS" if size in ("5 X 20 MM", "6.3 X 32 MM") else "CARTRIDGE CERAMIC",
                       "SIZE": size, "RATING": f"{fmt(a)}A", "CLASS": "GG", "VOLTAGE": "500 VAC"}
    for a in (2, 4, 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400):
        yield {"TYPE": "HRC LINK BS88 BOLTED", "RATING": f"{a}A", "CLASS": "GG", "VOLTAGE": "415 VAC", "MAKE": "L AND T"}


@SWITCH.generator
def switches():
    for a in (32, 63, 100, 125, 160, 200, 250, 315, 400, 630, 800):
        for poles in ("TP", "TPN", "FP"):
            for typ in ("DISCONNECTOR FUSE SDF", "ON LOAD CHANGEOVER", "LOAD BREAK ISOLATOR", "OFF LOAD CHANGEOVER"):
                for make in SWITCHGEAR_MAKES:
                    yield {"TYPE": typ, "POLES": poles, "RATING": f"{a}A", "MAKE": make}
    for a in (10, 16, 20, 25, 32, 40, 63):
        for typ in ("ROTARY CAM 2 WAY", "ROTARY CAM ON OFF", "AMMETER SELECTOR 4 POSITION", "VOLTMETER SELECTOR 7 POSITION"):
            for poles in ("1P", "2P", "3P", "4P"):
                if "SELECTOR" in typ and poles != "3P":
                    continue
                for make in ("KAYCEE", "SALZER", "L AND T", "SIEMENS"):
                    yield {"TYPE": typ, "POLES": poles, "RATING": f"{a}A", "MAKE": make}
    for typ in ("LIMIT ROLLER LEVER", "LIMIT ADJUSTABLE ROD LEVER", "LIMIT PLUNGER", "LIMIT ROLLER PLUNGER", "LIMIT FORK"):
        for moc in ("METAL BODY", "PLASTIC BODY"):
            for make in ("TELEMECANIQUE", "SIEMENS", "OMRON", "HONEYWELL", "PIZZATO"):
                yield {"TYPE": typ, "MOC": moc, "RATING": "10A", "FEATURE": "1NO+1NC", "PROTECTION": "IP65", "MAKE": make}
    for typ in ("PRESSURE", "DIFFERENTIAL PRESSURE", "TEMPERATURE", "LEVEL FLOAT", "LEVEL VIBRATING FORK", "FLOW PADDLE"):
        for rng in {"PRESSURE": ("0.2-2 BAR", "0.5-6 BAR", "1-10 BAR", "2-20 BAR", "5-50 BAR", "10-100 BAR", "20-250 BAR"),
                    "DIFFERENTIAL PRESSURE": ("0-100 MMWC", "0-500 MMWC", "0.1-1 BAR", "0.5-5 BAR"),
                    "TEMPERATURE": ("0-100 DEG C", "0-200 DEG C", "50-300 DEG C"),
                    "LEVEL FLOAT": ("SIDE MOUNTED", "TOP MOUNTED"),
                    "LEVEL VIBRATING FORK": ("SHORT INSERTION", "EXTENDED 500 MM"),
                    "FLOW PADDLE": ("DN 25-200",)}[typ]:
            conns = ("FLANGED 2 IN CL150",) if typ.startswith("LEVEL") else \
                ("1 NPT", "FLANGED 2 IN CL150") if typ.startswith("FLOW") else ("1/4 NPT", "1/2 NPT")
            for conn in conns:
                for prot in ("WEATHERPROOF IP66", "EX D IIC T6"):
                    for make in ("SWITZER", "INDFOS", "DANFOSS", "ENDRESS HAUSER", "ASHCROFT"):
                        yield {"TYPE": typ, "RANGE": rng, "MOC": "SS316 WETTED PARTS", "CONNECTION": conn,
                               "PROTECTION": prot, "FEATURE": "SPDT", "MAKE": make}
    for a in ("6A", "16A"):
        for typ in ("MODULAR 1 WAY", "MODULAR 2 WAY", "MODULAR BELL PUSH", "DP WITH INDICATOR"):
            for make in ("LEGRAND", "SCHNEIDER", "HAVELLS", "ANCHOR"):
                yield {"TYPE": typ, "RATING": a, "MAKE": make}
    for typ in ("EMERGENCY STOP PULL CORD", "BELT SWAY", "ZERO SPEED"):
        for make in ("JAYASHREE", "SIEMENS", "TECHNOCRAT"):
            yield {"TYPE": typ, "MOC": "CAST AL BODY", "PROTECTION": "IP65", "FEATURE": "2NO+2NC", "MAKE": make}


PB_COLORS = ("RED", "GREEN", "YELLOW", "BLUE", "BLACK", "WHITE")
CONTROL_MAKES = ("SCHNEIDER", "SIEMENS", "L AND T", "TEKNIC", "ABB", "SALZER")


@PUSH_BUTTON.generator
def push_buttons():
    for typ in ("FLUSH", "EXTENDED", "MUSHROOM 40 MM", "ILLUMINATED FLUSH", "EMERGENCY STOP TWIST RELEASE",
                "SELECTOR 2 POSITION", "SELECTOR 3 POSITION", "KEY SELECTOR 2 POSITION"):
        colors = ("RED",) if "EMERGENCY" in typ else ("BLACK",) if "SELECTOR" in typ else PB_COLORS
        for color in colors:
            for contacts in ("1NO", "1NC", "1NO+1NC"):
                volts = ("24 VDC", "110 VAC", "230 VAC") if "ILLUMINATED" in typ else ("",)
                for v in volts:
                    for make in CONTROL_MAKES:
                        yield {"TYPE": typ, "SIZE": "22 MM", "COLOR": color, "CONTACTS": contacts, "VOLTAGE": v,
                               "MAKE": make}


@INDICATOR.generator
def indicators():
    for color in PB_COLORS[:5] + ("AMBER",):
        for v in ("24 VDC", "110 VAC", "230 VAC", "415 VAC"):
            for size in ("22 MM", "30 MM"):
                for make in CONTROL_MAKES:
                    yield {"TYPE": "LED PILOT LAMP", "SIZE": size, "COLOR": color, "VOLTAGE": v, "MAKE": make}
    for v in ("24 VDC", "230 VAC"):
        yield {"TYPE": "TOWER LAMP 3 STAGE WITH BUZZER", "COLOR": "RED AMBER GREEN", "VOLTAGE": v, "MAKE": "SCHNEIDER"}
        yield {"TYPE": "HOOTER 100 DB", "VOLTAGE": v, "MAKE": "SCHNEIDER"}
        for color in ("RED", "AMBER", "GREEN", "BLUE"):
            yield {"TYPE": "FLASHER BEACON", "COLOR": color, "VOLTAGE": v, "MAKE": "SCHNEIDER"}


@METER.generator
def panel_meters():
    for typ, ranges in (("AMMETER", [f"0-{a}A" for a in (5, 10, 20, 50, 100, 200, 400, 600, 800, 1000, 1600, 2000, 3200)]),
                        ("VOLTMETER", ["0-300V", "0-500V", "0-600V"]),
                        ("FREQUENCY METER", ["45-55 HZ"]), ("POWER FACTOR METER", ["0.5 LAG-1-0.5 LEAD"])):
        for principle in ("ANALOG MOVING IRON", "DIGITAL LED"):
            for size in ("72 X 72 MM", "96 X 96 MM"):
                for r in ranges:
                    for make in ("AE", "RISHABH", "SECURE", "L AND T", "SELEC"):
                        yield {"TYPE": typ, "PRINCIPLE": principle, "SIZE": size, "RANGE": r,
                               "ACCURACY": "CLASS 1.5" if principle.startswith("ANALOG") else "CLASS 0.5",
                               "INPUT": "CT /5A" if typ == "AMMETER" and r not in ("0-5A", "0-10A", "0-20A") else "",
                               "MAKE": make}
    for typ in ("MULTIFUNCTION METER", "ENERGY METER 3 PHASE 4 WIRE", "POWER ANALYSER WITH HARMONICS"):
        for acc in ("CLASS 0.5S", "CLASS 1"):
            for out in ("", "RS485 MODBUS"):
                for inp in ("CT /1A", "CT /5A"):
                    for make in ("SCHNEIDER", "SECURE", "L AND T", "SELEC", "RISHABH", "ABB"):
                        yield {"TYPE": typ, "PRINCIPLE": "DIGITAL LCD", "SIZE": "96 X 96 MM", "ACCURACY": acc,
                               "INPUT": inp, "OUTPUT": out, "MAKE": make}


CT_PRIMARY = (5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500,
              1600, 2000, 2500, 3000, 3200, 4000)


@TRANSFORMER.generator
def transformers():
    for p in CT_PRIMARY:
        for sec in ("5A", "1A"):
            for cls, burden in (("CLASS 0.5", "5 VA"), ("CLASS 1", "5 VA"), ("CLASS 0.5", "15 VA"), ("5P10", "15 VA"),
                                ("5P20", "10 VA"), ("PS", "")):
                for cons in ("RESIN CAST", "TAPE WOUND RING"):
                    yield {"TYPE": "CURRENT CT", "RATIO": f"{p}/{sec}", "VOLTAGE": "0.66 KV", "CLASS": cls,
                           "BURDEN": burden, "CONSTRUCTION": cons}
    for kv in ("415V", "3.3 KV", "6.6 KV", "11 KV", "33 KV"):
        for sec in ("110V", "63.5V"):
            for cls in ("CLASS 0.5", "3P"):
                yield {"TYPE": "POTENTIAL PT", "RATIO": f"{kv}/{sec}", "CLASS": cls, "BURDEN": "50 VA",
                       "CONSTRUCTION": "RESIN CAST"}
    for va in (50, 100, 150, 250, 500, 750, 1000, 1500, 2000, 3000, 5000):
        for ratio in ("415V/230V", "415V/110V", "415V/24V", "230V/24V", "230V/110V", "415V/230V/110V"):
            yield {"TYPE": "CONTROL", "RATING": f"{va} VA", "RATIO": ratio, "CONSTRUCTION": "DRY TYPE OPEN FRAME"}
    for kva in (25, 63, 100, 160, 200, 250, 315, 400, 500, 630, 750, 800, 1000, 1250, 1600, 2000, 2500, 3150, 5000):
        for ratio in ("11 KV/433V", "22 KV/433V", "33 KV/433V", "33 KV/11 KV"):
            if ratio == "33 KV/11 KV" and kva < 1000:
                continue
            for cooling, cons in (("ONAN", "OIL FILLED"), ("AN", "DRY TYPE CAST RESIN")):
                for make in ("ABB", "SIEMENS", "CROMPTON GREAVES", "KIRLOSKAR ELECTRIC", "VOLTAMP"):
                    yield {"TYPE": "DISTRIBUTION", "RATING": f"{kva} KVA", "RATIO": ratio, "VOLTAGE": "DYN11",
                           "COOLING": cooling, "CONSTRUCTION": cons, "MAKE": make}


DRIVE_MAKES = ("ABB", "SIEMENS", "DANFOSS", "SCHNEIDER", "YASKAWA", "DELTA")


@DRIVE.generator
def drives():
    kws = (0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.7, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160,
           200, 250, 315)
    for kw in kws:
        for volt in ("415V 3PH", "230V 1PH"):
            if volt == "230V 1PH" and kw > 2.2:
                continue
            for prot in ("IP20", "IP55"):
                for make in DRIVE_MAKES:
                    yield {"TYPE": "VARIABLE FREQUENCY VFD", "POWER": f"{fmt(kw)} KW", "VOLTAGE": volt,
                           "PROTECTION": prot, "MAKE": make}
        if kw >= 5.5:
            for make in DRIVE_MAKES:
                yield {"TYPE": "SOFT STARTER", "POWER": f"{fmt(kw)} KW", "VOLTAGE": "415V 3PH",
                       "FEATURE": "WITH INBUILT BYPASS", "MAKE": make}
    for kw in (0.4, 0.75, 1, 1.5, 2, 3, 5, 7):
        for make in ("YASKAWA", "SIEMENS", "DELTA", "MITSUBISHI"):
            yield {"TYPE": "SERVO WITH MOTOR", "POWER": f"{fmt(kw)} KW", "VOLTAGE": "230V 1PH", "MAKE": make}


LT_MAKES = ("PHILIPS", "CROMPTON GREAVES", "BAJAJ", "HAVELLS", "WIPRO", "SYSKA")


@LIGHT.generator
def light_fittings():
    groups = [
        ("LED STREET LIGHT", (30, 45, 60, 90, 120, 150, 200, 250), "POLE MOUNTED", "IP66"),
        ("LED FLOOD LIGHT", (10, 20, 30, 50, 70, 100, 150, 200, 300, 400, 500), "BRACKET", "IP66"),
        ("LED HIGH BAY", (50, 70, 100, 120, 150, 200, 250, 300), "HOOK SUSPENDED", "IP65"),
        ("LED WELL GLASS", (20, 30, 40, 50, 60, 80, 100, 150), "PENDANT", "IP66"),
        ("LED BATTEN", (10, 18, 20, 22, 36, 40), "SURFACE", "IP20"),
        ("LED PANEL 2 X 2", (30, 36, 40, 45), "RECESSED", "IP20"),
        ("LED DOWNLIGHT", (6, 9, 12, 15, 18, 24), "RECESSED", "IP20"),
        ("LED BULKHEAD", (8, 12, 18, 24), "SURFACE", "IP65"),
    ]
    for typ, watts, mounting, prot in groups:
        for w in watts:
            for cct in ("3000K", "4000K", "5700K", "6500K"):
                for make in LT_MAKES:
                    yield {"TYPE": typ, "POWER": f"{w}W", "CCT": cct, "MOUNTING": mounting, "PROTECTION": prot,
                           "MAKE": make}
    for typ, watts in (("FLAMEPROOF LED WELL GLASS", (20, 40, 60, 80, 100, 150)), ("FLAMEPROOF LED FLOOD", (50, 100, 150, 200)),
                       ("FLAMEPROOF LED TUBE FITTING", (20, 2 * 20))):
        for w in watts:
            for zone in ("EX D IIB T4", "EX D IIC T6"):
                for make in ("BALIGA", "FCG", "SUDHIR", "CROMPTON GREAVES"):
                    yield {"TYPE": typ, "POWER": f"{w}W", "CCT": "5700K", "PROTECTION": "IP66", "FEATURE": zone,
                           "MAKE": make}
    for hrs in ("1.5 HR", "3 HR"):
        for typ in ("EMERGENCY LIGHT LED TWIN SPOT", "EXIT SIGN LED"):
            for make in LT_MAKES[:3]:
                yield {"TYPE": typ, "FEATURE": f"{hrs} BACKUP", "MAKE": make}


@LAMP.generator
def lamps():
    for typ, watts, bases in (("LED BULB", (5, 7, 9, 12, 15, 20, 30, 40, 50), ("B22", "E27")),
                              ("LED TUBE T8", (10, 18, 20, 22), ("G13",)), ("METAL HALIDE", (70, 150, 250, 400), ("E40",)),
                              ("HPSV", (70, 150, 250, 400), ("E40",)), ("HALOGEN", (500, 1000), ("R7S",))):
        for w in watts:
            for base in bases:
                ccts = ("3000K", "6500K") if typ.startswith("LED") else ("",)
                for cct in ccts:
                    for make in LT_MAKES:
                        yield {"TYPE": typ, "POWER": f"{w}W", "CCT": cct, "BASE": base, "MAKE": make}


@TRAY.generator
def cable_trays():
    for typ in ("LADDER", "PERFORATED", "RACEWAY"):
        for w in (50, 75, 100, 150, 200, 300, 450, 600, 750, 900, 1000, 1200):
            if typ == "RACEWAY" and w > 300:
                continue
            if typ == "LADDER" and w < 150:
                continue
            for h in (25, 50, 75, 100, 150):
                if (typ == "LADDER" and h < 50) or (typ != "LADDER" and h > 100) or h > w:
                    continue
                for t in (1.6, 2, 2.5):
                    for moc, finish in (("MS", "HOT DIP GALVANISED"), ("MS", "PRE GALVANISED"), ("AL", ""),
                                        ("SS316", ""), ("FRP", "")):
                        if moc == "FRP" and t != 2.5:
                            continue
                        yield {"TYPE": typ, "MOC": moc, "WIDTH": f"{w} MM WIDE", "HEIGHT": f"{h} MM HIGH",
                               "THICKNESS": f"{fmt(t)} MM THK", "FINISH": finish, "STANDARD": "NEMA VE 1"}


@TRAY.generator(uom="NOS")
def tray_accessories():
    for typ in ("LADDER 90 DEG HORIZONTAL BEND", "LADDER HORIZONTAL TEE", "LADDER HORIZONTAL CROSS",
                "LADDER VERTICAL INSIDE BEND", "LADDER VERTICAL OUTSIDE BEND", "LADDER STRAIGHT REDUCER",
                "PERFORATED 90 DEG HORIZONTAL BEND", "PERFORATED HORIZONTAL TEE", "PERFORATED COVER"):
        for w in (150, 200, 300, 450, 600, 750, 900):
            for h in ((50, 75, 100) if "LADDER" in typ else (25, 50)):
                yield {"TYPE": typ, "MOC": "MS", "WIDTH": f"{w} MM WIDE", "HEIGHT": f"{h} MM HIGH",
                       "THICKNESS": "2 MM THK", "FINISH": "HOT DIP GALVANISED"}


@CONDUIT.generator
def conduits():
    for size in (16, 20, 25, 32, 40, 50):
        for cls in ("LIGHT", "MEDIUM", "HEAVY"):
            yield {"TYPE": "RIGID", "MOC": "PVC", "SIZE": f"{size} MM", "CLASS": cls, "STANDARD": "IS 9537-3"}
        for cls in ("16 SWG", "14 SWG"):
            yield {"TYPE": "RIGID", "MOC": "GI", "SIZE": f"{size} MM", "CLASS": cls, "FINISH": "HOT DIP GALVANISED",
                   "STANDARD": "IS 9537-2"}
        for moc in ("GI", "PVC COATED GI", "PVC"):
            yield {"TYPE": "FLEXIBLE", "MOC": moc, "SIZE": f"{size} MM"}


@JB.generator
def junction_boxes():
    for moc in ("CAST AL", "SS316", "GRP", "PVC", "CRCA POWDER COATED"):
        for size in ("100 X 100 X 75 MM", "150 X 150 X 100 MM", "200 X 200 X 120 MM", "250 X 200 X 120 MM",
                     "300 X 300 X 150 MM", "400 X 300 X 200 MM", "500 X 400 X 200 MM", "600 X 600 X 250 MM"):
            for terminals in ("6 WAY", "12 WAY", "24 WAY", "48 WAY"):
                for prot in ("IP65", "IP66", "EX E IIC IP66", "EX D IIC IP66"):
                    if prot.startswith("EX D") and moc not in ("CAST AL", "SS316"):
                        continue
                    if prot.startswith("EX") and moc in ("PVC", "CRCA POWDER COATED"):
                        continue
                    yield {"TYPE": "TERMINAL", "MOC": moc, "SIZE": size, "TERMINALS": terminals, "PROTECTION": prot}


@BATTERY.generator
def batteries():
    for ah in (7, 12, 17, 26, 42, 65, 75, 100, 120, 150, 200):
        for make in ("EXIDE", "AMARA RAJA", "QUANTA", "LUMINOUS"):
            yield {"TYPE": "VRLA SMF", "VOLTAGE": "12V", "CAPACITY": f"{ah} AH", "MAKE": make}
    for ah in (100, 150, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 2500, 3000):
        for typ in ("TUBULAR FLOODED LEAD ACID CELL", "VRLA CELL", "NI-CD POCKET PLATE CELL"):
            for make in ("EXIDE", "AMARA RAJA", "HBL"):
                yield {"TYPE": typ, "VOLTAGE": "1.2V" if "NI-CD" in typ else "2V", "CAPACITY": f"{ah} AH", "MAKE": make}
    for size, v in (("AA", "1.5V"), ("AAA", "1.5V"), ("C", "1.5V"), ("D", "1.5V"), ("9V PP3", "9V"),
                    ("CR2032 COIN", "3V"), ("CR123A", "3V")):
        for chem in ("ALKALINE", "LITHIUM") if not size.startswith("CR") else ("LITHIUM",):
            for make in ("DURACELL", "EVEREADY", "PANASONIC"):
                yield {"TYPE": f"{chem} {size}", "VOLTAGE": v, "MAKE": make}


@CHARGER.generator
def chargers():
    for v in ("24 VDC", "48 VDC", "110 VDC", "220 VDC"):
        for a in (10, 15, 20, 30, 50, 75, 100, 150, 200):
            for typ in ("FLOAT CUM BOOST FCBC", "FLOAT CUM BOOST FCBC DUAL"):
                yield {"TYPE": f"BATTERY {typ}", "VOLTAGE": v, "CURRENT": f"{a}A", "INPUT": "415V 3PH", "MAKE": "CHHABI"}
    for v, amps in (("24 VDC", (2.5, 5, 10, 20, 40)), ("12 VDC", (5, 10))):
        for a in amps:
            for make in ("PHOENIX CONTACT", "MEAN WELL", "SIEMENS", "OMRON"):
                yield {"TYPE": "SMPS POWER SUPPLY DIN RAIL", "VOLTAGE": v, "CURRENT": f"{fmt(a)}A",
                       "INPUT": "85-264 VAC", "MAKE": make}
    for kva in (1, 2, 3, 5, 6, 10, 15, 20, 30, 40, 60, 80, 100, 120, 160, 200):
        for make in ("APC", "EMERSON VERTIV", "EATON", "NUMERIC"):
            yield {"TYPE": "UPS ONLINE DOUBLE CONVERSION", "VOLTAGE": f"{kva} KVA", "INPUT": "415V 3PH" if kva >= 10 else "230V 1PH",
                   "MAKE": make}


@BUSBAR.generator
def busbars():
    for moc, spec, finish in (("CU", "ETP IS 613", "BARE"), ("CU", "ETP IS 613", "TINNED"), ("AL", "E91E IS 5082", "BARE")):
        for w in (12, 15, 20, 25, 30, 40, 50, 60, 75, 80, 100, 120, 150, 160, 200):
            for t in (3, 5, 6, 8, 10, 12):
                if t * 4 > w:
                    continue
                yield {"TYPE": "FLAT", "MOC": moc, "SPEC": spec, "SIZE": f"{w} X {t} MM", "FINISH": finish}


@CAPACITOR.generator
def capacitors():
    for kvar in (1, 2, 2.5, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 50):
        for v in ("440V", "480V", "525V"):
            for cons in ("MPP HEAVY DUTY CYLINDRICAL", "MPP BOX TYPE", "APP GAS FILLED"):
                for make in ("EPCOS", "SCHNEIDER", "L AND T", "ABB"):
                    yield {"TYPE": "POWER FACTOR CORRECTION 3 PHASE", "RATING": f"{fmt(kvar)} KVAR", "VOLTAGE": v,
                           "CONSTRUCTION": cons, "MAKE": make}
    for uf in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 36, 40, 50, 60, 72, 100):
        yield {"TYPE": "MOTOR RUN", "RATING": f"{fmt(uf)} MFD", "VOLTAGE": "440 VAC", "CONSTRUCTION": "PP CAN"}
    for uf in (100, 150, 200, 250, 300, 400, 500):
        yield {"TYPE": "MOTOR START", "RATING": f"{uf} MFD", "VOLTAGE": "230 VAC", "CONSTRUCTION": "ELECTROLYTIC"}


@INSULATOR.generator
def insulators():
    for h in (25, 30, 35, 40, 51, 60, 76, 100, 130):
        for thread in ("M6", "M8", "M10", "M12", "M16"):
            if (h < 40 and thread in ("M12", "M16")) or (h > 60 and thread in ("M6",)):
                continue
            yield {"TYPE": "BUSBAR SUPPORT SM", "MOC": "EPOXY DMC", "SIZE": f"SM {h} MM HIGH", "VOLTAGE": "1.1 KV",
                   "THREAD": f"{thread} INSERT"}
    for kv in ("11 KV", "22 KV", "33 KV"):
        for typ in ("PIN", "POST", "DISC 70 KN", "DISC 120 KN", "SHACKLE", "STAY"):
            if typ in ("SHACKLE", "STAY") and kv != "11 KV":
                continue
            yield {"TYPE": typ, "MOC": "PORCELAIN", "VOLTAGE": kv}
            yield {"TYPE": typ, "MOC": "POLYMER SILICONE", "VOLTAGE": kv}


@RESISTOR.generator
def resistors():
    for ohm in (10, 15, 20, 30, 40, 50, 75, 100, 150, 200):
        for w in (200, 500, 1000, 2000, 5000, 10000):
            yield {"TYPE": "BRAKING", "RESISTANCE": f"{ohm} OHM", "POWER": f"{w}W", "CONSTRUCTION": "AL HOUSED WIREWOUND"}
    for kv in ("3.3 KV", "6.6 KV", "11 KV"):
        for a in (50, 100, 200, 300, 400, 500):
            yield {"TYPE": f"NEUTRAL GROUNDING NGR {kv}", "RESISTANCE": f"{a}A 10 SEC", "CONSTRUCTION": "SS GRID"}


@CONTROLLER.generator
def controllers():
    for typ in ("PID TEMPERATURE", "ON OFF TEMPERATURE", "PROCESS INDICATOR", "PROCESS INDICATOR CONTROLLER WITH ALARM"):
        for size in ("48 X 48 MM", "72 X 72 MM", "96 X 96 MM", "48 X 96 MM"):
            for inp in ("UNIVERSAL TC RTD MA", "J K TC", "PT100 RTD", "4-20 MA"):
                for out in ("RELAY", "SSR", "4-20 MA") if "INDICATOR" not in typ else ("RELAY",):
                    for make in ("SELEC", "MULTISPAN", "YOKOGAWA", "OMRON", "HONEYWELL"):
                        yield {"TYPE": typ, "SIZE": size, "INPUT": inp, "OUTPUT": out, "SUPPLY": "85-265 VAC",
                               "MAKE": make}
    for typ in ("APFC RELAY 8 STAGE", "APFC RELAY 12 STAGE", "LEVEL CONTROLLER 2 PROBE", "DG SYNCHRONISING",
                "AMF CONTROLLER"):
        for make in ("SELEC", "EPCOS", "MINILEC", "DEEP SEA"):
            yield {"TYPE": typ, "SUPPLY": "230 VAC", "MAKE": make}


PLC_SERIES = {"SIEMENS": ("S7-1200", "S7-1500", "ET 200SP"), "ALLEN BRADLEY": ("MICRO850", "COMPACTLOGIX 5380"),
              "SCHNEIDER": ("M221", "M580"), "MITSUBISHI": ("FX5U", "IQ-R"), "DELTA": ("DVP-SS2", "AS300"),
              "OMRON": ("CP2E", "NX1P")}


@PLC.generator
def plc_modules():
    mods = [("CPU", "", ""), ("POWER SUPPLY", "", "24 VDC 5A"), ("DIGITAL INPUT", "16 CH", "24 VDC"),
            ("DIGITAL INPUT", "32 CH", "24 VDC"), ("DIGITAL OUTPUT", "16 CH", "24 VDC TRANSISTOR"),
            ("DIGITAL OUTPUT", "16 CH", "RELAY"), ("ANALOG INPUT", "4 CH", "4-20 MA"), ("ANALOG INPUT", "8 CH", "4-20 MA HART"),
            ("ANALOG INPUT", "8 CH", "RTD TC"), ("ANALOG OUTPUT", "4 CH", "4-20 MA"), ("ANALOG OUTPUT", "8 CH", "4-20 MA"),
            ("COMMUNICATION", "", "PROFINET"), ("COMMUNICATION", "", "MODBUS RTU RS485"), ("COMMUNICATION", "", "ETHERNET IP"),
            ("HMI 7 IN TOUCH", "", ""), ("HMI 10 IN TOUCH", "", ""), ("HMI 15 IN TOUCH", "", "")]
    for make, series in PLC_SERIES.items():
        for s in series:
            for typ, ch, sig in mods:
                yield {"TYPE": typ, "SERIES": s, "CHANNELS": ch, "SIGNAL": sig, "MAKE": make}
