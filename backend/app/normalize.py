"""Description normalization shared by the parts import, type-ahead search and BOM matching.

Stored descriptions and incoming text must go through exactly the same rules, otherwise
search and matching silently degrade. Change rules here only, then re-run the parts import
so `description_norm` / `search_text` / `attrs` are rebuilt.
"""
from __future__ import annotations

import re
from functools import lru_cache

NPS_TO_DN = {
    "1/8": 6, "1/4": 8, "3/8": 10, "1/2": 15, "3/4": 20, "1": 25, "1+1/4": 32, "1+1/2": 40,
    "2": 50, "2+1/2": 65, "3": 80, "3+1/2": 90, "4": 100, "5": 125, "6": 150, "8": 200,
    "10": 250, "12": 300, "14": 350, "16": 400, "18": 450, "20": 500, "22": 550, "24": 600,
    "26": 650, "28": 700, "30": 750, "32": 800, "34": 850, "36": 900, "40": 1000, "42": 1050, "48": 1200,
}

SYNONYMS = {
    "THREAD": "THRD", "THREADED": "THRD", "THRED": "THRD", "THD": "THRD",
    "GRAPHYTE": "GRAPHITE",
    "FASTNERS": "FASTENERS", "FASTNER": "FASTENER",
    "CONUMABLES": "CONSUMABLES",
    "ECC": "ECCENTRIC", "CONC": "CONCENTRIC",
    "REDUCERS": "REDUCER", "ELBOWS": "ELBOW", "ELL": "ELBOW", "TEES": "TEE",
    "EQ": "EQUAL", "UNEQ": "REDUCING", "UNEQL": "REDUCING", "UNEQUAL": "REDUCING",
    "FLANGED": "FLGD",
    "HEXAGON": "HEX", "HEXAGONAL": "HEX",
    "GASKETS": "GASKET", "FLANGES": "FLANGE", "PIPES": "PIPE", "BOLTS": "BOLT", "STUDS": "STUD",
    "NUTS": "NUT", "WASHERS": "WASHER", "PLATES": "PLATE", "CAPS": "CAP", "COUPLINGS": "COUPLING",
    "DEGREE": "DEG", "DEGREES": "DEG",
    "THICK": "THK", "THICKNESS": "THK",
    "SEAMLESS": "SMLS",
    "BLIND": "BL",
}

NOISE_TOKENS = {"GR", "GRADE", "TYPE", "TP", "OF", "THE", "AND", "WITH", "FOR", "&"}

# separators and BOM-only wording that the master never uses (seamless, bevelled/plain end):
# kept in the normalized text but never required to match
SOFT_TOKENS = {"X", "SMLS", "BE", "PE", "NOS"}

# every noun of the parts catalog (app.catalog); parts descriptions always start with their noun
CATALOG_NOUNS = (
    "PIPE", "TUBE", "ELBOW", "TEE", "REDUCER", "CAP", "CROSS", "STUB END", "BEND", "COUPLING", "UNION", "PLUG",
    "BUSHING", "SWAGE", "NIPPLE", "OLET", "FLANGE", "SPECTACLE BLIND", "GASKET", "VALVE", "STRAINER", "TRAP",
    "SIGHT GLASS", "EXPANSION JOINT", "HOSE", "STUD", "BOLT", "SCREW", "NUT", "WASHER", "ANCHOR", "RIVET", "PIN",
    "RETAINING RING", "KEY", "ROD", "SHACKLE", "TURNBUCKLE", "HOOK", "WIRE ROPE", "SLING", "CLAMP", "THIMBLE",
    "PLATE", "SHEET", "STRIP", "BAR", "ANGLE", "CHANNEL", "BEAM", "HOLLOW SECTION", "GRATING", "WIRE", "MESH",
    "BEARING", "SLEEVE", "BEARING HOUSING", "O-RING", "O-RING CORD", "OIL SEAL", "MECHANICAL SEAL", "PACKING",
    "SEAL", "V-RING", "BELT", "CHAIN", "SPROCKET", "PULLEY", "GEAR", "RACK", "GEARBOX", "MOTOR", "PUMP",
    "COMPRESSOR", "FAN", "BLOWER", "SPRING", "CYLINDER", "FITTING", "FILTER", "CABLE", "CABLE GLAND", "CABLE LUG",
    "TERMINAL", "CONNECTOR", "SOCKET", "CIRCUIT BREAKER", "CONTACTOR", "RELAY", "FUSE", "SWITCH", "PUSH BUTTON",
    "INDICATOR", "METER", "TRANSFORMER", "DRIVE", "LIGHT FITTING", "LAMP", "CABLE TRAY", "CONDUIT", "JUNCTION BOX",
    "BATTERY", "CHARGER", "BUSBAR", "CAPACITOR", "INSULATOR", "RESISTOR", "CONTROLLER", "PLC MODULE", "ELECTRODE",
    "GAUGE", "THERMOWELL", "THERMOCOUPLE", "RTD", "TRANSMITTER", "SENSOR", "ACTUATOR", "POSITIONER", "DETECTOR",
    "ORIFICE PLATE", "DRILL", "TAP", "DIE", "REAMER", "END MILL", "CUTTER", "INSERT", "TOOL HOLDER", "BIT", "WHEEL",
    "DISC", "BLADE", "ABRASIVE", "BRUSH", "SPANNER", "WRENCH", "SCREWDRIVER", "PLIER", "HAMMER", "FILE", "CHISEL",
    "PUNCH", "TOOL KIT", "CALIPER", "MICROMETER", "MEASURING GAUGE", "MEASURING TAPE", "RULE", "SPIRIT LEVEL",
    "POWER TOOL", "FLUX", "GAS", "OIL", "GREASE", "COOLANT", "PAINT", "THINNER", "ADHESIVE", "SEALANT", "CHEMICAL",
    "TAPE", "SAFETY SHOE", "SAFETY HELMET", "GLOVES", "GOGGLES", "MASK", "PPE", "SAFETY HARNESS", "COVERALL",
    "INSULATION", "BRICK", "CASTABLE", "ANODE", "SHIM", "CLOTH", "LABEL", "MARKER", "CONTAINER",
)
# words BOMs use for a catalog noun
PTYPE_ALIASES = {
    "WELDOLET": "OLET", "SOCKOLET": "OLET", "THREDOLET": "OLET", "ELBOLET": "OLET", "NIPOLET": "OLET",
    "LATROLET": "OLET", "SWEEPOLET": "OLET", "FLAT": "BAR", "LATERAL": "LATERAL",
}
# in "SPRING WASHER", "GEAR PUMP", "PIPE CLAMP" the second noun is the part
HEAD_NOUNS = {
    "VALVE", "WASHER", "NUT", "PUMP", "CLAMP", "SCREW", "FLANGE", "GRATING", "BRUSH", "BEARING", "SEAL", "GASKET",
    "ELBOW", "TEE", "REDUCER", "CAP", "BEND", "NIPPLE", "COUPLING", "UNION", "SWITCH", "GAUGE", "TRANSMITTER",
    "MOTOR", "STRAINER", "FILTER", "OIL", "GREASE", "SPROCKET", "PULLEY",
}

SUBTYPES = {
    "ECCENTRIC", "CONCENTRIC", "EQUAL", "REDUCING", "WN", "SO", "BL", "LJ", "RF", "FF", "RTJ",
    "LR", "SR", "BW", "SW", "NPT", "BSPT", "BSP", "FULL", "HALF", "HEX", "ROUND", "SQ", "END", "SPW",
}

FLAGS = {"IBR", "NACE", "HDG", "THRD"}

# piping components are sized by nominal bore: an inch size on these means NPS, so it becomes DN
PIPING_TYPES = {
    "ELBOW", "TEE", "REDUCER", "FLANGE", "PIPE", "CAP", "COUPLING", "SOCKET", "PLUG", "UNION", "NIPPLE",
    "SWAGE", "GASKET", "CROSS", "OLET", "WELDOLET", "SOCKOLET", "THREDOLET", "VALVE", "STRAINER", "BUSHING",
    "BEND", "TRAP", "SPECTACLE",
}
_INCH_TOKEN_RE = re.compile(r'^(\d+\+\d/\d|\d/\d|\d+)"$')
FASTENER_WORDS = {"BOLT", "STUD", "NUT", "S+B+W", "N+B+W"}

_STAINLESS_RE = re.compile(r"^3\d\d[LH]?$")
_FLANGE_FACE_RE = re.compile(r"^(WN|SO|BL|LJ|SW|TH)(RF|FF|RTJ)$")
_SPEC_TOKEN_RE = re.compile(r"^(SA\d+|IS\d+)$")
_PROPERTY_CLASS = {"4.6", "4.8", "5.6", "8.8", "10.9", "12.9"}


def _nps_sub(match: re.Match) -> str:
    size = match.group(1).replace("-", "+").replace(" ", "+")
    dn = NPS_TO_DN.get(size)
    return f" DN{dn} " if dn else match.group(0)


_RULES: list[tuple[re.Pattern, object]] = [
    (re.compile(r"[’‘`´]"), "'"),
    (re.compile(r"[”“″]"), '"'),
    (re.compile(r"''"), '"'),
    (re.compile(r"[×]"), "X"),
    (re.compile(r"[–—]"), "-"),
    (re.compile(r"°"), " DEG "),
    (re.compile(r"[^\x20-\x7E]"), " "),
    # standards bodies carry no information once the spec number is canonical
    (re.compile(r"\b(?:ASTM|ASME|ANSI)\b\s*"), " "),
    # SA-403 / SA - 403 / SA--234 / A 105 / A105 -> SA403 (trailing space splits SA-403WP317)
    (re.compile(r"\bS?A\s*[-:.]*\s*(\d{2,3})(?![\d.])"), r" SA\1 "),
    (re.compile(r"\bIS\s*[-:.]*\s*(\d{3,5})\b"), r" IS\1 "),
    (re.compile(r"\bB\s*16\s*\.\s*(\d{1,2})\b"), r" B16.\1 "),
    # GR. / GR- / GRADE / Gr.8 are dropped; the grade value itself remains
    (re.compile(r"\bGR(?:ADE)?(?:\s*[.\-:]\s*|\s+|(?=\d))"), " "),
    (re.compile(r"\bTYPE\b\s*[.\-:]?"), " "),
    (re.compile(r"\bTP\s*[-.]?\s*(?=\d)"), " "),
    # WP304 / F-316L / F316 (stainless family) -> bare grade
    (re.compile(r"\b(?:WP|F)\s*[-.]?\s*(3\d\d[LH]?)\b"), r" \1 "),
    (re.compile(r"\bSS\s*-?\s*(3\d\d[LH]?)\b"), r" SS \1 "),
    # sizes
    (re.compile(r"\bNPS\s*(\d+(?:[-+ ]\d/\d)?|\d/\d)\s*(?:\"|INCH(?:ES)?\b)?"), _nps_sub),
    (re.compile(r"\b(\d+)\s*NB\b"), r" DN\1 "),
    (re.compile(r"\bDN\s*[-.:]?\s*(\d+)"), r" DN\1 "),
    (re.compile(r"\bSCH(?:EDULE)?\s*[-.:]?\s*(\d{1,3}S?|XXS|XS|STD)\b"), r" SCH\1 "),
    (re.compile(r"\b(NPT|BSPT|BSP)\s*CL"), r" \1 CL"),
    (re.compile(r"\b(?:CLASS|CL)\s*[-.:#]?\s*(\d{3,4})\b"), r" CL\1 "),
    (re.compile(r"#\s*(\d{3,4})\b"), r" CL\1 "),
    (re.compile(r"\b(\d{3,4})\s*(?:#|LBS?\b)"), r" CL\1 "),
    (re.compile(r"\b(\d{2,3})\s*-?\s*DEG(?:REE)?S?\b"), r" \1DEG "),
    # phrases
    (re.compile(r"\bSPIRAL(?:LY)?\s*WOUND\b"), " SPW "),
    (re.compile(r"\bI\.?R\.?\s*(?:[/&+]|AND)\s*O\.?R\b\.?"), " INNER RING OUTER RING "),
    (re.compile(r"\bGEAR\s+BOX\b"), " GEARBOX "),
    (re.compile(r"\b(CONC|ECC|CONCENTRIC|ECCENTRIC)\.?\s*RED\b\.?"), r" \1 REDUCER "),
    (re.compile(r"\bLONG\s+RADIUS\b"), " LR "),
    (re.compile(r"\bSHORT\s+RADIUS\b"), " SR "),
    (re.compile(r"\bWELD\s*NECK\b"), " WN "),
    (re.compile(r"\bSLIP\s*-?\s*ON\b"), " SO "),
    (re.compile(r"\bSOCKET\s*WELD(?:ED|ING)?\b"), " SW "),
    (re.compile(r"\bBUTT\s*WELD(?:ED|ING)?\b"), " BW "),
    (re.compile(r"\bRAISED\s*FACE\b"), " RF "),
    (re.compile(r"\bFLAT\s*FACE\b"), " FF "),
    (re.compile(r"\b(WN|SO|BL|LJ|SW|TH)\s*[-/]\s*(RF|FF|RTJ)\b"), r" \1 \2 "),
    # dimensions
    (re.compile(r"(\d)\s*IN\b"), r'\1"'),
    (re.compile(r"(?<=[\d\"])\s*[X*]\s*(?=\d|DN|M\d)"), " X "),
    (re.compile(r"\b(\d)(?:[-+]| )(\d/\d{1,2})\s*(?=\"|INCH)"), r"\1+\2"),
    (re.compile(r"(\d)\s*(?:\"|INCH(?:ES)?\b)"), r'\1"'),
    (re.compile(r"(\d)\s*SQ\.?\s*MM\b"), r"\1SQMM"),
    (re.compile(r"(\d)\s*(KW|HP|KVA|KV|HZ|RPM)\b"), r"\1\2"),
    (re.compile(r"(\d)\s*MM\b"), r"\1MM"),
    # IS 2062 E250 A / E250A / E 250 BR
    (re.compile(r"\bE\s*(250|275|300|350|410|450|550|600|650)\s*-?\s*(A|BR|B0|C)\b"), r" E\1\2 "),
    (re.compile(r"\bM\s*-?\s*(\d{1,2})\b(?!\.)"), r" M\1 "),
    # punctuation: keep '.' and '/' only inside numbers, keep '+' (S+B+W, 1+1/8)
    (re.compile(r"(?<!\d)\.|\.(?!\d)"), " "),
    (re.compile(r"(?<!\d)/|/(?!\d)"), " "),
    (re.compile(r"[,;()\[\]{}'#&=_!?|\\-]"), " "),
]

_REDUCER_DN_RE = re.compile(r"\b(DN\d+) X (\d+)\b(?!MM|\"|\.|\+|/)")
# bolt lengths and plate thicknesses are always millimetres, even when the unit is omitted
_BARE_LENGTH_RES = [
    re.compile(r"(\bM\d{1,2} X |\" X )(\d+(?:\.\d+)?)(?![\d.+/]|MM|\")"),
    re.compile(r"(\bTHK )(\d+(?:\.\d+)?)(?![\d.]|MM|\"| X)"),
]


@lru_cache(maxsize=200_000)
def normalize(text: str | None) -> str:
    if not text:
        return ""
    s = f" {str(text).upper()} "
    for pattern, repl in _RULES:
        s = pattern.sub(repl, s)
    s = _REDUCER_DN_RE.sub(r"\1 X DN\2", s)
    s = " ".join(s.split())
    for pattern in _BARE_LENGTH_RES:
        s = pattern.sub(r"\1\2MM", s)

    tokens: list[str] = []
    for raw in s.split():
        tok = SYNONYMS.get(raw, raw)
        if tok in NOISE_TOKENS:
            continue
        face = _FLANGE_FACE_RE.match(tok)
        parts = [face.group(1), face.group(2)] if face else [tok]
        for p in parts:
            if not tokens or tokens[-1] != p:
                tokens.append(p)

    if "FT" in tokens and FASTENER_WORDS.intersection(tokens):
        i = tokens.index("FT")
        tokens[i:i + 1] = ["FULL", "THRD"]

    if PIPING_TYPES.intersection(tokens):
        for i, t in enumerate(tokens):
            m = _INCH_TOKEN_RE.match(t)
            if m and m.group(1) in NPS_TO_DN:
                tokens[i] = f"DN{NPS_TO_DN[m.group(1)]}"
    return " ".join(tokens)


def tokens(norm: str) -> list[str]:
    return norm.split() if norm else []


def extract_attrs(norm: str) -> dict:
    """Critical attributes used by the matcher to reject candidates with the wrong size/material."""
    toks = tokens(norm)
    attrs: dict[str, list[str] | str] = {}

    def put(key: str, values: list[str]) -> None:
        if values:
            attrs[key] = sorted(values)

    put("dn", re.findall(r"\bDN(\d+)\b", norm))
    put("sch", re.findall(r"\bSCH(\w+)\b", norm))
    put("cl", re.findall(r"\bCL(\d+)\b", norm))
    put("m", re.findall(r"\bM(\d{1,2})\b", norm))
    put("inch", re.findall(r'(?<![\w/+.])(\d+\+\d+/\d+|\d+/\d+|\d+)"', norm))
    # lengths: explicit "230MM", or a bare number after a bolt size ("M24 X 230", '1" X 370')
    lengths = set(re.findall(r"\b(\d+(?:\.\d+)?)MM\b", norm))
    lengths.update(re.findall(r'(?:\bM\d{1,2}|")\s+X\s+(\d+(?:\.\d+)?)(?:MM)?\b', norm))
    lengths.update(re.findall(r"\b(?:THK|OD|ID)\s+(\d+(?:\.\d+)?)(?:MM)?\b(?!\s+X)", norm))
    put("mm", list(lengths))
    put("deg", re.findall(r"\b(\d+)DEG\b", norm))
    put("spec", [t for t in toks if _SPEC_TOKEN_RE.match(t)])

    grades: set[str] = set()
    for i, t in enumerate(toks):
        if i > 0 and toks[i - 1] == "X":
            continue
        if _STAINLESS_RE.match(t) or t in _PROPERTY_CLASS:
            grades.add(t)
        elif i > 0 and _SPEC_TOKEN_RE.match(toks[i - 1]) and not _SPEC_TOKEN_RE.match(t):
            if not re.match(r"^(DN|SCH|CL|M)\d", t) and t not in SUBTYPES and t not in FLAGS:
                grades.add(t)
    put("grade", list(grades))

    ptype = product_type(toks)
    if ptype == "SOCKET" and ("dn" in attrs or "inch" in attrs or "cl" in attrs or {"SW", "THRD"} & set(toks)):
        ptype = "COUPLING"
    if ptype:
        attrs["ptype"] = ptype
    put("subtype", sorted({t for t in toks if t in SUBTYPES}))
    put("flags", sorted({t for t in toks if t in FLAGS}))
    return attrs


# normalized noun phrase (as tokens) -> product type; the product type of a catalog noun is its normalized name
_TYPE_PHRASES: dict[tuple[str, ...], str] = {tuple(normalize(n).split()): normalize(n) for n in CATALOG_NOUNS}
_TYPE_PHRASES.update({(w,): t for w, t in PTYPE_ALIASES.items()})
_MAX_PHRASE = max(len(k) for k in _TYPE_PHRASES)
NOUN_BY_PTYPE = {normalize(n): n for n in CATALOG_NOUNS}


def _type_at(toks: list[str], i: int) -> tuple[str, int] | None:
    for size in range(min(_MAX_PHRASE, len(toks) - i), 0, -1):
        ptype = _TYPE_PHRASES.get(tuple(toks[i:i + size]))
        if ptype:
            return ptype, size
    return None


def product_type(toks: list[str]) -> str | None:
    """First noun of the text; for an English compound ("SPRING WASHER") the head noun that follows it."""
    for i, t in enumerate(toks):
        hit = _type_at(toks, i)
        if hit:
            ptype, size = hit
            following = _type_at(toks, i + size)
            if following and following[0] in HEAD_NOUNS:
                return following[0]
            return ptype
        if "+" in t and not t[0].isdigit():
            return t
    return None


def infer_noun(attrs: dict) -> str | None:
    ptype = attrs.get("ptype")
    if not ptype:
        return None
    if "+" in ptype:
        return "STUD"
    return NOUN_BY_PTYPE.get(ptype)
