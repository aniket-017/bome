"""Engineering reference tables shared by the catalog generators."""
from __future__ import annotations

from collections.abc import Iterable

# ---------------------------------------------------------------- nominal pipe sizes
DN_SIZES = [6, 8, 10, 15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500,
            550, 600, 650, 700, 750, 800, 850, 900, 1000, 1050, 1200]

DN_TO_NPS = {
    6: '1/8"', 8: '1/4"', 10: '3/8"', 15: '1/2"', 20: '3/4"', 25: '1"', 32: '1-1/4"', 40: '1-1/2"',
    50: '2"', 65: '2-1/2"', 80: '3"', 100: '4"', 125: '5"', 150: '6"', 200: '8"', 250: '10"', 300: '12"',
    350: '14"', 400: '16"', 450: '18"', 500: '20"', 550: '22"', 600: '24"', 650: '26"', 700: '28"',
    750: '30"', 800: '32"', 850: '34"', 900: '36"', 950: '38"', 1000: '40"', 1050: '42"', 1100: '44"',
    1150: '46"', 1200: '48"', 1300: '52"', 1400: '56"', 1500: '60"',
}


def dn(d: int) -> str:
    return f"DN {d}"


def dn_pair(a: int, b: int) -> str:
    return f"DN {a} X DN {b}"


def dn_range(lo: int, hi: int, sizes: Iterable[int] = DN_SIZES) -> list[int]:
    return [d for d in sizes if lo <= d <= hi]


def reducing_pairs(sizes: list[int], steps: int = 4, min_small: int = 15) -> list[tuple[int, int]]:
    """(large, small) combinations as listed in ASME B16.9: each size reduces to the next few smaller sizes."""
    out = []
    for i, large in enumerate(sizes):
        for small in reversed(sizes[max(0, i - steps):i]):
            if small >= min_small:
                out.append((large, small))
    return out


# ---------------------------------------------------------------- wall schedules (ASME B36.10M / B36.19M)
SCHEDULE_RANGE = {
    "SCH 5S": (15, 750), "SCH 10S": (6, 750), "SCH 40S": (6, 600), "SCH 80S": (6, 600),
    "SCH 10": (15, 900), "SCH 20": (200, 900), "SCH 30": (200, 900), "SCH STD": (6, 1200),
    "SCH 40": (6, 600), "SCH 60": (200, 600), "SCH XS": (6, 1200), "SCH 80": (6, 600),
    "SCH 100": (200, 600), "SCH 120": (100, 600), "SCH 140": (200, 600), "SCH 160": (15, 600),
    "SCH XXS": (15, 300),
}


def schedules(names: Iterable[str], d: int) -> list[str]:
    return [s for s in names if SCHEDULE_RANGE[s][0] <= d <= SCHEDULE_RANGE[s][1]]


# ---------------------------------------------------------------- material families
CARBON_FAMILIES = {"CS", "LTCS", "AS"}

PIPE_SCH = {
    "CS": ["SCH 10", "SCH 20", "SCH 30", "SCH STD", "SCH 40", "SCH 60", "SCH XS", "SCH 80", "SCH 100",
           "SCH 120", "SCH 140", "SCH 160", "SCH XXS"],
    "LTCS": ["SCH STD", "SCH 40", "SCH XS", "SCH 80", "SCH 160", "SCH XXS"],
    "AS": ["SCH STD", "SCH 40", "SCH XS", "SCH 80", "SCH 120", "SCH 160", "SCH XXS"],
    "SS": ["SCH 5S", "SCH 10S", "SCH 40S", "SCH 80S", "SCH 160", "SCH XXS"],
    "HA": ["SCH 5S", "SCH 10S", "SCH 40S", "SCH 80S", "SCH 160"],
}
FITTING_SCH = {
    "CS": ["SCH 10", "SCH 20", "SCH STD", "SCH 40", "SCH XS", "SCH 80", "SCH 120", "SCH 160", "SCH XXS"],
    "LTCS": ["SCH STD", "SCH 40", "SCH XS", "SCH 80", "SCH 160"],
    "AS": ["SCH STD", "SCH 40", "SCH XS", "SCH 80", "SCH 160", "SCH XXS"],
    "SS": ["SCH 5S", "SCH 10S", "SCH 40S", "SCH 80S", "SCH 160", "SCH XXS"],
    "HA": ["SCH 10S", "SCH 40S", "SCH 80S"],
}


def family(moc: str) -> str:
    """Schedule family: carbon/alloy steels use B36.10 schedules, everything else B36.19."""
    if moc in ("CS", "LTCS", "AS", "SS"):
        return moc
    return "HA"  # duplex, super duplex and nickel alloys


# special requirements that create separate catalogue items (certification / sour service)
SPECIALS = {
    "CS": ["", "IBR", "NACE MR0175"],
    "LTCS": ["", "NACE MR0175"],
    "AS": ["", "IBR"],
    "SS": ["", "IBR"],
}


def specials(moc: str) -> list[str]:
    return SPECIALS.get(moc, [""])


# (MOC, specification) for wrought butt-weld fittings, ASME B16.9
BW_MATERIALS = [
    ("CS", "ASTM A234 WPB"), ("CS", "ASTM A234 WPC"),
    ("LTCS", "ASTM A420 WPL6"), ("LTCS", "ASTM A420 WPL3"),
    ("AS", "ASTM A234 WP5"), ("AS", "ASTM A234 WP9"), ("AS", "ASTM A234 WP11"), ("AS", "ASTM A234 WP22"),
    ("AS", "ASTM A234 WP91"),
    ("SS", "ASTM A403 WP304"), ("SS", "ASTM A403 WP304L"), ("SS", "ASTM A403 WP304H"),
    ("SS", "ASTM A403 WP316"), ("SS", "ASTM A403 WP316L"), ("SS", "ASTM A403 WP321"),
    ("SS", "ASTM A403 WP347"), ("SS", "ASTM A403 WP310S"), ("SS", "ASTM A403 WP317L"),
    ("SS", "ASTM A403 WP904L"),
    ("DSS", "ASTM A815 WPS31803"), ("DSS", "ASTM A815 WPS32205"),
    ("SDSS", "ASTM A815 WPS32750"), ("SDSS", "ASTM A815 WPS32760"),
    ("MONEL 400", "ASTM B366 WPNC"), ("INCONEL 600", "ASTM B366 WPNCI"), ("INCONEL 625", "ASTM B366 WPNCMC"),
    ("INCOLOY 825", "ASTM B366 WPNICMC"), ("HASTELLOY C276", "ASTM B366 WPHC276"),
]

# (MOC, specification) for forgings: B16.11 fittings, B16.5 flanges, olets, forged valves
FORGED_MATERIALS = [
    ("CS", "ASTM A105"), ("CS", "ASTM A105N"),
    ("LTCS", "ASTM A350 LF2 CL1"), ("LTCS", "ASTM A350 LF3"),
    ("AS", "ASTM A182 F5"), ("AS", "ASTM A182 F9"), ("AS", "ASTM A182 F11"), ("AS", "ASTM A182 F22"),
    ("AS", "ASTM A182 F91"),
    ("SS", "ASTM A182 F304"), ("SS", "ASTM A182 F304L"), ("SS", "ASTM A182 F304H"), ("SS", "ASTM A182 F316"),
    ("SS", "ASTM A182 F316L"), ("SS", "ASTM A182 F321"), ("SS", "ASTM A182 F347"), ("SS", "ASTM A182 F310"),
    ("SS", "ASTM A182 F317L"),
    ("DSS", "ASTM A182 F51"), ("DSS", "ASTM A182 F60"), ("SDSS", "ASTM A182 F53"), ("SDSS", "ASTM A182 F55"),
    ("MONEL 400", "ASTM B564 N04400"), ("INCONEL 600", "ASTM B564 N06600"), ("INCONEL 625", "ASTM B564 N06625"),
    ("INCOLOY 825", "ASTM B564 N08825"), ("HASTELLOY C276", "ASTM B564 N10276"),
]

COMMON_FORGED = [m for m in FORGED_MATERIALS if m[1] in {
    "ASTM A105", "ASTM A350 LF2 CL1", "ASTM A182 F11", "ASTM A182 F22", "ASTM A182 F91", "ASTM A182 F304",
    "ASTM A182 F304L", "ASTM A182 F316", "ASTM A182 F316L", "ASTM A182 F321", "ASTM A182 F51", "ASTM A182 F53",
}]

# cast valve bodies
CAST_BODIES = [
    ("CS", "ASTM A216 WCB"), ("CS", "ASTM A216 WCC"), ("LTCS", "ASTM A352 LCB"), ("LTCS", "ASTM A352 LCC"),
    ("AS", "ASTM A217 WC6"), ("AS", "ASTM A217 WC9"), ("AS", "ASTM A217 C5"), ("AS", "ASTM A217 C12A"),
    ("SS", "ASTM A351 CF8"), ("SS", "ASTM A351 CF8M"), ("SS", "ASTM A351 CF3"), ("SS", "ASTM A351 CF3M"),
    ("DSS", "ASTM A995 4A"), ("SDSS", "ASTM A995 5A"),
]

# ---------------------------------------------------------------- pressure classes
B16_5_CLASSES = [150, 300, 600, 900, 1500, 2500]


def cl(c: int | str) -> str:
    return f"CL {c}"


# ---------------------------------------------------------------- threads / fastener sizes
METRIC_COARSE = {
    "M2": 0.4, "M2.5": 0.45, "M3": 0.5, "M4": 0.7, "M5": 0.8, "M6": 1.0, "M8": 1.25, "M10": 1.5, "M12": 1.75,
    "M14": 2.0, "M16": 2.0, "M18": 2.5, "M20": 2.5, "M22": 2.5, "M24": 3.0, "M27": 3.0, "M30": 3.5,
    "M33": 3.5, "M36": 4.0, "M39": 4.0, "M42": 4.5, "M45": 4.5, "M48": 5.0, "M52": 5.0, "M56": 5.5,
    "M60": 5.5, "M64": 6.0, "M72": 6.0, "M80": 6.0, "M90": 6.0, "M100": 6.0,
}


def m_dia(m: str) -> float:
    return float(m[1:])


# inch stud/bolt sizes: (label, nominal mm) - UNC up to 1", 8UN above
INCH_BOLTS = [
    ('1/2"', 12.7), ('5/8"', 15.9), ('3/4"', 19.1), ('7/8"', 22.2), ('1"', 25.4), ('1-1/8"', 28.6),
    ('1-1/4"', 31.8), ('1-3/8"', 34.9), ('1-1/2"', 38.1), ('1-5/8"', 41.3), ('1-3/4"', 44.5),
    ('1-7/8"', 47.6), ('2"', 50.8), ('2-1/4"', 57.2), ('2-1/2"', 63.5), ('2-3/4"', 69.9), ('3"', 76.2),
    ('3-1/4"', 82.6), ('3-1/2"', 88.9), ('3-3/4"', 95.3), ('4"', 101.6),
]


def inch_thread(label: str, mm: float) -> str:
    return f"{label} {'UNC' if mm <= 25.4 else '8UN'}"


ISO_LENGTHS = [3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100,
               110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 220, 240, 260, 280, 300, 320, 340, 360,
               380, 400, 420, 440, 460, 480, 500]


def lengths_between(lo: float, hi: float, series: list[int] = ISO_LENGTHS) -> list[int]:
    return [L for L in series if lo <= L <= hi]


def stud_lengths(d_mm: float) -> list[int]:
    """Stock stud-bolt lengths: about 4.5d up to 20d, 5 mm steps to 100, 10 mm to 300, 25 mm beyond."""
    lo = max(40, int(round(4.5 * d_mm / 5.0)) * 5)
    hi = min(800, int(20 * d_mm))
    out, L = [], lo
    while L <= hi:
        out.append(L)
        L += 5 if L < 100 else 10 if L < 300 else 25
    return out


def mm(v: float | int) -> str:
    return f"{fmt(v)} MM"


def fmt(v: float | int) -> str:
    """12.0 -> '12', 2.5 -> '2.5'."""
    f = float(v)
    return str(int(f)) if f.is_integer() else f"{f:g}"


# ---------------------------------------------------------------- brands (manufacturer modifier)
BEARING_MAKES = ["SKF", "FAG", "NSK", "NTN", "KOYO", "NBC"]
TAPER_BEARING_MAKES = ["TIMKEN", "SKF", "FAG", "KOYO", "NBC"]
BELT_MAKES = ["FENNER", "GATES", "OPTIBELT", "CONTINENTAL", "BANDO", "PIX"]
MOTOR_MAKES = ["ABB", "SIEMENS", "CROMPTON GREAVES", "KIRLOSKAR", "BHARAT BIJLEE", "WEG"]
SWITCHGEAR_MAKES = ["SCHNEIDER", "ABB", "SIEMENS", "L AND T", "LEGRAND", "HAVELLS"]
CABLE_MAKES = ["POLYCAB", "KEI", "HAVELLS", "FINOLEX", "RR KABEL"]
INSTRUMENT_MAKES = ["EMERSON", "YOKOGAWA", "ENDRESS HAUSER", "HONEYWELL", "ABB", "SIEMENS"]
GAUGE_MAKES = ["WIKA", "BAUMER", "GENERAL INSTRUMENTS", "H GURU", "FIEBIG"]
TUBE_FITTING_MAKES = ["SWAGELOK", "PARKER", "HAM-LET", "FITOK"]
PNEUMATIC_MAKES = ["FESTO", "SMC", "JANATICS", "NORGREN", "CAMOZZI"]
WELDING_MAKES = ["ESAB", "L AND T", "D AND H SECHERON", "ADOR", "LINCOLN"]
LUBE_MAKES = ["SERVO", "CASTROL", "SHELL", "MOBIL", "HP LUBRICANTS"]
PAINT_MAKES = ["ASIAN PAINTS", "BERGER", "JOTUN", "HEMPEL", "AKZO NOBEL", "KANSAI NEROLAC"]
TOOL_MAKES = ["TAPARIA", "STANLEY", "GEDORE", "JHALANI", "BAHCO"]
CUTTING_TOOL_MAKES = ["SANDVIK", "KENNAMETAL", "ISCAR", "MITSUBISHI", "TAEGUTEC", "WALTER"]
DRILL_MAKES = ["ADDISON", "TOTEM", "DORMER", "GUHRING", "YG-1"]
ABRASIVE_MAKES = ["CUMI", "NORTON", "BOSCH", "3M"]
