"""Pipes, tubes, butt-weld (ASME B16.9) and forged (ASME B16.11) fittings, olets (MSS SP-97)."""
from app.catalog import noun
from app.catalog.data import (
    BW_MATERIALS, COMMON_FORGED, DN_SIZES, DN_TO_NPS, FITTING_SCH, FORGED_MATERIALS, PIPE_SCH, dn, dn_pair,
    dn_range, family, fmt, reducing_pairs, schedules, specials,
)

G_PIPE, G_FIT = "PIPES", "PIPE FITTINGS"

PIPE = noun("PIPE", G_PIPE, "MTR", ("TYPE", "MOC", "SPEC", "SIZE", "SCHEDULE", "THICKNESS", "RATING", "END",
                                    "STANDARD", "FINISH", "FEATURE"))
TUBE = noun("TUBE", G_PIPE, "MTR", ("TYPE", "MOC", "SPEC", "OD", "ID", "THICKNESS", "RATING", "STANDARD",
                                    "FINISH", "FEATURE", "COLOR", "MAKE"))
FIT_MODS = ("TYPE", "MOC", "SPEC", "SIZE", "SCHEDULE", "RATING", "END", "STANDARD", "FEATURE")
ELBOW = noun("ELBOW", G_FIT, "NOS", ("ANGLE", "RADIUS", "MOC", "SPEC", "SIZE", "SCHEDULE", "RATING", "END",
                                     "STANDARD", "FEATURE"))
TEE = noun("TEE", G_FIT, "NOS", FIT_MODS)
REDUCER = noun("REDUCER", G_FIT, "NOS", FIT_MODS)
CAP = noun("CAP", G_FIT, "NOS", FIT_MODS)
CROSS = noun("CROSS", G_FIT, "NOS", FIT_MODS)
STUB_END = noun("STUB END", G_FIT, "NOS", FIT_MODS)
BEND = noun("BEND", G_FIT, "NOS", ("ANGLE", "RADIUS", "MOC", "SPEC", "SIZE", "SCHEDULE", "END", "STANDARD",
                                   "FEATURE"))
# shared with shaft couplings / camlock couplings (transmission, valves modules)
COUPLING = noun("COUPLING", G_FIT, "NOS", ("TYPE", "MOC", "SPEC", "SIZE", "SCHEDULE", "RATING", "END",
                                           "ELEMENT", "BORE", "STANDARD", "FEATURE", "MAKE"))
UNION = noun("UNION", G_FIT, "NOS", FIT_MODS)
PLUG = noun("PLUG", G_FIT, "NOS", ("TYPE", "MOC", "SPEC", "SIZE", "RATING", "END", "POLES", "PROTECTION",
                                   "STANDARD", "FEATURE", "MAKE"))
BUSHING = noun("BUSHING", G_FIT, "NOS", ("TYPE", "MOC", "SPEC", "SIZE", "BORE", "RATING", "END", "STANDARD",
                                         "FEATURE", "MAKE"))
SWAGE = noun("SWAGE", G_FIT, "NOS", FIT_MODS)
NIPPLE = noun("NIPPLE", G_FIT, "NOS", ("TYPE", "MOC", "SPEC", "SIZE", "LENGTH", "SCHEDULE", "END", "STANDARD",
                                       "FEATURE"))
OLET = noun("OLET", G_FIT, "NOS", FIT_MODS)

BW_SIZES = [d for d in DN_SIZES if d >= 15]
FORGED_SIZES = [8, 10, 15, 20, 25, 32, 40, 50, 65, 80, 100]
FORGED_FITTING_MATERIALS = [m for m in FORGED_MATERIALS if m[1] not in {
    "ASTM A105N", "ASTM A350 LF3", "ASTM A182 F304H", "ASTM A182 F310", "ASTM A182 F60",
}]


def _bw_max(moc: str) -> int:
    return 1200 if moc in ("CS", "LTCS", "SS") else 600


def _std(moc: str) -> str:
    return "ASME B36.10M" if moc in ("CS", "LTCS", "AS") else "ASME B36.19M"


def _pipe_specials(moc: str, spec: str) -> list[str]:
    # IBR covers boiler/steam piping, never API 5L line pipe
    return ["", "NACE MR0175"] if spec.startswith("API 5L") else specials(moc)


# ======================================================================== PIPE
SMLS_PIPE = [
    ("CS", "ASTM A106 GR B"), ("CS", "ASTM A106 GR C"), ("CS", "ASTM A53 GR B"), ("CS", "API 5L GR B PSL1"),
    ("CS", "API 5L GR B PSL2"), ("CS", "API 5L X42 PSL2"), ("CS", "API 5L X52 PSL2"), ("CS", "API 5L X60 PSL2"),
    ("CS", "API 5L X65 PSL2"), ("CS", "API 5L X70 PSL2"),
    ("LTCS", "ASTM A333 GR 6"), ("LTCS", "ASTM A333 GR 3"),
    ("AS", "ASTM A335 P1"), ("AS", "ASTM A335 P5"), ("AS", "ASTM A335 P9"), ("AS", "ASTM A335 P11"),
    ("AS", "ASTM A335 P12"), ("AS", "ASTM A335 P22"), ("AS", "ASTM A335 P91"),
    ("SS", "ASTM A312 TP304"), ("SS", "ASTM A312 TP304L"), ("SS", "ASTM A312 TP304H"), ("SS", "ASTM A312 TP316"),
    ("SS", "ASTM A312 TP316L"), ("SS", "ASTM A312 TP316H"), ("SS", "ASTM A312 TP321"), ("SS", "ASTM A312 TP321H"),
    ("SS", "ASTM A312 TP347"), ("SS", "ASTM A312 TP310S"), ("SS", "ASTM A312 TP317L"), ("SS", "ASTM A312 TP904L"),
    ("DSS", "ASTM A790 S31803"), ("DSS", "ASTM A790 S32205"), ("SDSS", "ASTM A790 S32750"),
    ("SDSS", "ASTM A790 S32760"),
    ("MONEL 400", "ASTM B165 N04400"), ("INCONEL 600", "ASTM B167 N06600"), ("INCONEL 625", "ASTM B444 N06625"),
    ("INCOLOY 825", "ASTM B423 N08825"), ("HASTELLOY C276", "ASTM B622 N10276"),
]


def _pipe_ends(moc: str, d: int, sch: str) -> list[str]:
    ends = ["PE"]
    if d >= 50:
        ends.append("BE")
    if moc in ("CS", "SS") and d <= 100 and sch in ("SCH STD", "SCH 40", "SCH 40S", "SCH XS", "SCH 80", "SCH 80S"):
        ends.append("THRD NPT")
    return ends


@PIPE.generator
def seamless_pipes():
    for moc, spec in SMLS_PIPE:
        fam = family(moc)
        line_pipe = spec.startswith("API 5L X")
        top = 600 if fam in ("CS", "LTCS", "AS", "SS") else 300
        for d in dn_range(50 if line_pipe else 6, top):
            for sch in schedules(PIPE_SCH[fam], d):
                ends = ["BE"] if line_pipe else _pipe_ends(moc, d, sch)
                for end in ends:
                    for sp in _pipe_specials(moc, spec):
                        yield {"TYPE": "SMLS", "MOC": moc, "SPEC": spec, "SIZE": dn(d), "SCHEDULE": sch,
                               "END": end, "STANDARD": _std(moc), "FEATURE": sp}


WELDED_PIPE = [
    # (type, moc, spec, min DN, max DN, schedules)
    ("ERW", "CS", "ASTM A53 GR B", 15, 600, ["SCH 10", "SCH STD", "SCH 40", "SCH XS", "SCH 80"]),
    ("ERW", "CS", "API 5L GR B PSL1", 50, 600, ["SCH 10", "SCH 20", "SCH STD", "SCH 40", "SCH XS"]),
    ("ERW", "CS", "API 5L X42 PSL2", 50, 600, ["SCH 10", "SCH 20", "SCH STD", "SCH XS"]),
    ("ERW", "CS", "API 5L X52 PSL2", 50, 600, ["SCH 10", "SCH 20", "SCH STD", "SCH XS"]),
    ("ERW", "CS", "API 5L X60 PSL2", 100, 600, ["SCH 10", "SCH 20", "SCH STD", "SCH XS"]),
    ("LSAW", "CS", "API 5L X52 PSL2", 400, 1200, ["SCH 10", "SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("LSAW", "CS", "API 5L X60 PSL2", 400, 1200, ["SCH 10", "SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("LSAW", "CS", "API 5L X65 PSL2", 400, 1200, ["SCH 10", "SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("LSAW", "CS", "API 5L X70 PSL2", 400, 1200, ["SCH 10", "SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("SSAW", "CS", "API 5L GR B PSL1", 400, 1200, ["SCH 10", "SCH 20", "SCH STD"]),
    ("SSAW", "CS", "API 5L X52 PSL2", 400, 1200, ["SCH 10", "SCH 20", "SCH STD"]),
    ("EFW", "CS", "ASTM A671 CC60 CL22", 400, 1200, ["SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("EFW", "CS", "ASTM A671 CC65 CL22", 400, 1200, ["SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("EFW", "CS", "ASTM A671 CC70 CL22", 400, 1200, ["SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("EFW", "CS", "ASTM A672 C65 CL22", 400, 1200, ["SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("EFW", "CS", "ASTM A672 C70 CL22", 400, 1200, ["SCH 20", "SCH 30", "SCH STD", "SCH XS"]),
    ("EFW", "LTCS", "ASTM A671 CC60 CL32", 400, 1200, ["SCH 20", "SCH STD", "SCH XS"]),
    *[("WELDED", "SS", f"ASTM A312 {g}", 15, 600, ["SCH 5S", "SCH 10S", "SCH 40S", "SCH 80S"])
      for g in ("TP304", "TP304L", "TP316", "TP316L", "TP321", "TP317L")],
    *[("EFW", "SS", f"ASTM A358 {g} CL1", 200, 1200, ["SCH 5S", "SCH 10S", "SCH 40S"])
      for g in ("TP304", "TP304L", "TP316", "TP316L", "TP321", "TP347")],
    *[("WELDED", d, f"ASTM A790 {g}", 15, 600, ["SCH 5S", "SCH 10S", "SCH 40S"])
      for d, g in (("DSS", "S31803"), ("DSS", "S32205"), ("SDSS", "S32750"))],
]


@PIPE.generator
def welded_pipes():
    for typ, moc, spec, lo, hi, scheds in WELDED_PIPE:
        for d in dn_range(lo, hi):
            for sch in schedules(scheds, d):
                for end in (["BE"] if d >= 50 else ["PE"]):
                    for sp in _pipe_specials(moc, spec):
                        yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "SCHEDULE": sch, "END": end,
                               "STANDARD": _std(moc), "FEATURE": sp}


@PIPE.generator
def is_pipes():
    # IS 1239: light / medium / heavy, black or galvanised; plain end or screwed & socketed
    for d in dn_range(6, 150):
        for cls in ("LIGHT", "MEDIUM", "HEAVY"):
            if cls == "LIGHT" and d > 100:
                continue
            for finish in ("BLACK", "GALVANISED"):
                for end in ("PE", "SCREWED AND SOCKETED"):
                    yield {"TYPE": "ERW", "MOC": "MS", "SPEC": "IS 1239 PART 1", "SIZE": dn(d), "SCHEDULE": cls,
                           "END": end, "FINISH": finish}
    # IS 3589 large-bore ERW / SAW
    for d in dn_range(200, 1200):
        for grade in ("FE 330", "FE 410"):
            for thk in (5, 6, 7.1, 8, 10, 12):
                if thk < 6 and d > 500:
                    continue
                yield {"TYPE": "ERW" if d <= 500 else "SAW", "MOC": "MS", "SPEC": f"IS 3589 {grade}", "SIZE": dn(d),
                       "THICKNESS": f"THK {fmt(thk)} MM", "END": "BE", "FINISH": "BLACK"}


PLASTIC_PIPES = [
    # (moc, spec, sizes as labels, ratings, end)
    ("UPVC", "IS 4985", [f"OD {o} MM" for o in (20, 25, 32, 40, 50, 63, 75, 90, 110, 140, 160, 180, 200, 225, 250, 280, 315)],
     ["CLASS 2 (4 KGF/CM2)", "CLASS 3 (6 KGF/CM2)", "CLASS 4 (10 KGF/CM2)"], "PLAIN"),
    ("UPVC", "ASTM D1785", [dn(d) for d in dn_range(15, 300)], ["SCH 40", "SCH 80"], "PLAIN"),
    ("CPVC", "ASTM D2846", [DN_TO_NPS[d] for d in dn_range(15, 50)], ["SDR 11", "SDR 13.5"], "PLAIN"),
    ("CPVC", "ASTM F441", [dn(d) for d in dn_range(15, 200)], ["SCH 40", "SCH 80"], "PLAIN"),
    ("HDPE PE100", "IS 4984", [f"OD {o} MM" for o in (20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200,
                                                      225, 250, 280, 315, 355, 400, 450, 500, 560, 630)],
     ["PN 6", "PN 8", "PN 10", "PN 12.5", "PN 16"], "PLAIN"),
    ("PPR", "DIN 8077", [f"OD {o} MM" for o in (20, 25, 32, 40, 50, 63, 75, 90, 110)], ["PN 10", "PN 16", "PN 20", "PN 25"],
     "PLAIN"),
    ("GRP", "AWWA C950", [dn(d) for d in dn_range(100, 1200)], ["PN 6", "PN 10", "PN 16"], "SPIGOT SOCKET"),
]


@PIPE.generator
def plastic_pipes():
    for moc, spec, sizes, ratings, end in PLASTIC_PIPES:
        for size in sizes:
            for r in ratings:
                key = "SCHEDULE" if r.startswith("SCH") else "RATING"
                yield {"MOC": moc, "SPEC": spec, "SIZE": size, key: r, "END": end}


@PIPE.generator
def copper_pipes():
    for d in dn_range(8, 100):
        for typ in ("TYPE K", "TYPE L", "TYPE M"):
            for temper in ("HARD DRAWN", "ANNEALED"):
                if temper == "ANNEALED" and d > 25:
                    continue
                yield {"TYPE": "SMLS", "MOC": "COPPER", "SPEC": f"ASTM B88 {typ}", "SIZE": DN_TO_NPS[d],
                       "END": "PE", "FINISH": temper}
    for d in dn_range(15, 400):
        for spec in ("ASTM B466 C70600 (90/10)", "ASTM B466 C71500 (70/30)"):
            for rating in ("PN 16", "PN 20"):
                yield {"TYPE": "SMLS" if d <= 150 else "WELDED", "MOC": "CUNI", "SPEC": spec, "SIZE": dn(d),
                       "RATING": rating, "STANDARD": "EEMUA 144", "END": "PE"}


# ======================================================================== TUBE (boiler / heat exchanger)
BWG = {8: 4.19, 10: 3.40, 12: 2.77, 14: 2.11, 16: 1.65, 18: 1.24, 20: 0.89}
TUBE_OD_BWG = {
    12.7: (16, 18, 20), 15.88: (14, 16, 18, 20), 19.05: (12, 14, 16, 18), 25.4: (10, 12, 14, 16, 18),
    31.75: (10, 12, 14, 16), 38.1: (10, 12, 14, 16), 44.45: (10, 12, 14), 50.8: (8, 10, 12, 14),
    63.5: (8, 10, 12), 76.2: (8, 10, 12),
}
HX_TUBES = [
    ("SMLS", "CS", "ASTM A179"), ("SMLS", "CS", "ASTM A192"), ("SMLS", "CS", "ASTM A210 GR A1"),
    ("SMLS", "CS", "ASTM A210 GR C"), ("SMLS", "LTCS", "ASTM A334 GR 6"),
    ("SMLS", "AS", "ASTM A213 T5"), ("SMLS", "AS", "ASTM A213 T9"), ("SMLS", "AS", "ASTM A213 T11"),
    ("SMLS", "AS", "ASTM A213 T22"), ("SMLS", "AS", "ASTM A213 T91"),
    ("SMLS", "SS", "ASTM A213 TP304"), ("SMLS", "SS", "ASTM A213 TP304L"), ("SMLS", "SS", "ASTM A213 TP316"),
    ("SMLS", "SS", "ASTM A213 TP316L"), ("SMLS", "SS", "ASTM A213 TP321"), ("SMLS", "SS", "ASTM A213 TP347H"),
    ("SMLS", "SS", "ASTM A213 TP310S"),
    ("WELDED", "CS", "ASTM A214"), ("WELDED", "SS", "ASTM A249 TP304"), ("WELDED", "SS", "ASTM A249 TP304L"),
    ("WELDED", "SS", "ASTM A249 TP316"), ("WELDED", "SS", "ASTM A249 TP316L"), ("WELDED", "SS", "ASTM A688 TP304"),
    ("SMLS", "DSS", "ASTM A789 S31803"), ("SMLS", "DSS", "ASTM A789 S32205"), ("SMLS", "SDSS", "ASTM A789 S32750"),
    ("SMLS", "COPPER", "ASTM B111 C12200"), ("SMLS", "ADMIRALTY BRASS", "ASTM B111 C44300"),
    ("SMLS", "CUNI 90/10", "ASTM B111 C70600"), ("SMLS", "CUNI 70/30", "ASTM B111 C71500"),
    ("SMLS", "TITANIUM", "ASTM B338 GR 2"), ("SMLS", "INCOLOY 825", "ASTM B163 N08825"),
]


@TUBE.generator
def heat_exchanger_tubes():
    for typ, moc, spec in HX_TUBES:
        for od, gauges in TUBE_OD_BWG.items():
            for g in gauges:
                for sp in (["", "IBR"] if moc in ("CS", "AS") else [""]):
                    yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "OD": f"OD {fmt(od)} MM",
                           "THICKNESS": f"THK {fmt(BWG[g])} MM ({g} BWG)", "FEATURE": sp}


# ======================================================================== butt-weld fittings, ASME B16.9
def _bw_materials():
    for moc, spec in BW_MATERIALS:
        yield moc, spec, family(moc), _bw_max(moc)


ELBOW_TYPES = [("90 DEG", "LR", 15, 1200), ("90 DEG", "SR", 25, 600), ("45 DEG", "LR", 15, 1200),
               ("180 DEG", "LR", 15, 600), ("180 DEG", "SR", 25, 600)]


@ELBOW.generator
def bw_elbows():
    for moc, spec, fam, top in _bw_materials():
        for angle, radius, lo, hi in ELBOW_TYPES:
            for d in dn_range(lo, min(hi, top), BW_SIZES):
                for sch in schedules(FITTING_SCH[fam], d):
                    for sp in specials(moc):
                        yield {"ANGLE": angle, "RADIUS": radius, "MOC": moc, "SPEC": spec, "SIZE": dn(d),
                               "SCHEDULE": sch, "END": "BW", "STANDARD": "ASME B16.9", "FEATURE": sp}


def _bw_simple(types: list[str], top_limit: int = 1200):
    for moc, spec, fam, top in _bw_materials():
        for typ in types:
            for d in dn_range(15, min(top, top_limit), BW_SIZES):
                for sch in schedules(FITTING_SCH[fam], d):
                    for sp in specials(moc):
                        yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "SCHEDULE": sch, "END": "BW",
                               "STANDARD": "ASME B16.9", "FEATURE": sp}


def _bw_reducing(types: list[str], steps: int):
    for moc, spec, fam, top in _bw_materials():
        pairs = reducing_pairs(dn_range(15, top, BW_SIZES), steps=steps)
        for typ in types:
            for large, small in pairs:
                for sch in schedules(FITTING_SCH[fam], large):
                    if sch not in schedules(FITTING_SCH[fam], small):
                        continue
                    for sp in specials(moc):
                        yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn_pair(large, small), "SCHEDULE": sch,
                               "END": "BW", "STANDARD": "ASME B16.9", "FEATURE": sp}


TEE.generator(lambda: _bw_simple(["EQUAL"]))
TEE.generator(lambda: _bw_reducing(["REDUCING"], steps=5))
REDUCER.generator(lambda: _bw_reducing(["CONCENTRIC", "ECCENTRIC"], steps=4))
CAP.generator(lambda: _bw_simple([""]))
CROSS.generator(lambda: _bw_simple(["EQUAL"], top_limit=600))


@STUB_END.generator
def stub_ends():
    for moc, spec, fam, top in _bw_materials():
        for typ, std, hi in (("LONG", "ASME B16.9", 600), ("SHORT", "MSS SP-43", 600)):
            for d in dn_range(15, min(hi, top), BW_SIZES):
                for sch in schedules(FITTING_SCH[fam], d):
                    yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "SCHEDULE": sch, "END": "BW",
                           "STANDARD": std}


@BEND.generator
def induction_bends():
    specs = [("CS", "ASTM A106 GR B"), ("CS", "API 5L X52 PSL2"), ("CS", "API 5L X60 PSL2"),
             ("CS", "API 5L X65 PSL2"), ("LTCS", "ASTM A333 GR 6"), ("AS", "ASTM A335 P11"),
             ("AS", "ASTM A335 P22"), ("AS", "ASTM A335 P91"), ("SS", "ASTM A312 TP304L"), ("SS", "ASTM A312 TP316L")]
    for moc, spec in specs:
        for angle in ("22.5 DEG", "30 DEG", "45 DEG", "60 DEG", "90 DEG"):
            for radius in ("3D", "5D"):
                for d in dn_range(50, 600):
                    for sch in schedules(PIPE_SCH[family(moc)][:8] if moc == "CS" else PIPE_SCH[family(moc)], d):
                        yield {"ANGLE": angle, "RADIUS": radius, "MOC": moc, "SPEC": spec, "SIZE": dn(d),
                               "SCHEDULE": sch, "END": "BE", "STANDARD": "ASME B16.49"}


# ======================================================================== forged fittings, ASME B16.11
def forged_ratings(d: int, threaded: bool = True, socket: bool = True):
    if socket:
        yield "SW", "CL 3000"
        if d <= 50:
            yield "SW", "CL 6000"
        if 15 <= d <= 50:
            yield "SW", "CL 9000"
    if threaded:
        yield "THRD NPT", "CL 2000"
        yield "THRD NPT", "CL 3000"
        if d <= 50:
            yield "THRD NPT", "CL 6000"


def _forged(types: list[str], noun_key: str = "TYPE"):
    for moc, spec in FORGED_FITTING_MATERIALS:
        for typ in types:
            for d in FORGED_SIZES:
                for end, rating in forged_ratings(d):
                    for sp in specials(moc):
                        yield {noun_key: typ, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end,
                               "STANDARD": "ASME B16.11", "FEATURE": sp}


@ELBOW.generator
def forged_elbows():
    for item in _forged(["90 DEG", "45 DEG"], noun_key="ANGLE"):
        yield item


TEE.generator(lambda: _forged(["EQUAL"]))
CROSS.generator(lambda: _forged(["EQUAL"]))
CAP.generator(lambda: _forged([""]))
COUPLING.generator(lambda: _forged(["FULL", "HALF"]))


def _forged_pairs(types: list[str], steps: int, threaded=True, socket=True, std="ASME B16.11", rated=True):
    for moc, spec in FORGED_FITTING_MATERIALS:
        for typ in types:
            for large, small in reducing_pairs(FORGED_SIZES, steps=steps, min_small=8):
                for end, rating in forged_ratings(large, threaded, socket):
                    for sp in specials(moc):
                        yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn_pair(large, small),
                               "RATING": rating if rated else "", "END": end, "STANDARD": std, "FEATURE": sp}


TEE.generator(lambda: _forged_pairs(["REDUCING"], steps=3))
COUPLING.generator(lambda: _forged_pairs(["REDUCING"], steps=3))


@UNION.generator
def unions():
    for moc, spec in FORGED_FITTING_MATERIALS:
        for d in dn_range(8, 80, FORGED_SIZES):
            for end, rating in forged_ratings(d):
                if rating in ("CL 2000", "CL 9000"):
                    continue
                for sp in specials(moc):
                    yield {"MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end,
                           "STANDARD": "MSS SP-83", "FEATURE": sp}


@PLUG.generator
def pipe_plugs():
    for moc, spec in FORGED_FITTING_MATERIALS:
        for typ in ("HEX HEAD", "ROUND HEAD", "SQUARE HEAD"):
            for d in FORGED_SIZES:
                yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "END": "THRD NPT",
                       "STANDARD": "ASME B16.11"}


@BUSHING.generator
def pipe_bushings():
    for moc, spec in FORGED_FITTING_MATERIALS:
        for large, small in reducing_pairs(FORGED_SIZES, steps=4, min_small=8):
            for typ in ("HEX", "FLUSH"):
                yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn_pair(large, small), "END": "THRD NPT",
                       "STANDARD": "ASME B16.11"}


SWAGE_SIZES = [15, 20, 25, 32, 40, 50, 65, 80, 100, 150, 200]
SWAGE_ENDS = ["PBE", "BBE", "TBE", "BLE X PSE", "PLE X TSE"]
SWAGE_SCH = {"CS": ["SCH STD", "SCH XS", "SCH 160", "SCH XXS"], "LTCS": ["SCH XS", "SCH 160"],
             "AS": ["SCH XS", "SCH 160", "SCH XXS"], "SS": ["SCH 40S", "SCH 80S", "SCH 160"], "HA": ["SCH 40S", "SCH 80S"]}


@SWAGE.generator
def swage_nipples():
    for moc, spec in FORGED_FITTING_MATERIALS:
        fam = family(moc)
        for typ in ("CONCENTRIC", "ECCENTRIC"):
            for large, small in reducing_pairs(SWAGE_SIZES, steps=4):
                for sch in schedules(SWAGE_SCH[fam], large):
                    for end in SWAGE_ENDS:
                        if "T" in end and large > 100:
                            continue
                        for sp in specials(moc):
                            yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn_pair(large, small),
                                   "SCHEDULE": sch, "END": end, "STANDARD": "MSS SP-95", "FEATURE": sp}


NIPPLE_PIPES = [("CS", "ASTM A106 GR B"), ("LTCS", "ASTM A333 GR 6"), ("AS", "ASTM A335 P11"), ("AS", "ASTM A335 P22"),
                ("AS", "ASTM A335 P91"), ("SS", "ASTM A312 TP304"), ("SS", "ASTM A312 TP304L"),
                ("SS", "ASTM A312 TP316"), ("SS", "ASTM A312 TP316L"), ("SS", "ASTM A312 TP321"),
                ("DSS", "ASTM A790 S31803")]


@NIPPLE.generator
def pipe_nipples():
    for moc, spec in NIPPLE_PIPES:
        fam = family(moc)
        for d in dn_range(8, 50):
            for length in (75, 100, 150, 200):
                for sch in schedules(SWAGE_SCH[fam], d):
                    for end in ("PBE", "TBE", "POE X TOE", "BBE"):
                        for sp in specials(moc):
                            yield {"TYPE": "BARREL", "MOC": moc, "SPEC": spec, "SIZE": dn(d),
                                   "LENGTH": f"L {length} MM", "SCHEDULE": sch, "END": end, "FEATURE": sp}


# ======================================================================== olets, MSS SP-97
OLET_RUNS = dn_range(50, 600, BW_SIZES)
OLET_SCH = {"CS": ["SCH STD", "SCH XS", "SCH 160", "SCH XXS"], "LTCS": ["SCH STD", "SCH XS", "SCH 160"],
            "AS": ["SCH STD", "SCH XS", "SCH 160"], "SS": ["SCH 10S", "SCH 40S", "SCH 80S", "SCH 160"],
            "HA": ["SCH 10S", "SCH 40S", "SCH 80S"]}


@OLET.generator
def olets():
    for moc, spec in COMMON_FORGED:
        fam = family(moc)
        sp_list = specials(moc)
        for i, run in enumerate(OLET_RUNS):
            smaller = [d for d in BW_SIZES if d < run]
            # weldolet: branch down to DN 15, up to two sizes below the run
            for branch in [d for d in smaller[:-1] if d <= 300] if len(smaller) > 1 else []:
                for sch in schedules(OLET_SCH[fam], branch):
                    for sp in sp_list:
                        yield {"TYPE": "WELDOLET", "MOC": moc, "SPEC": spec, "SIZE": dn_pair(run, branch),
                               "SCHEDULE": sch, "END": "BW", "STANDARD": "MSS SP-97", "FEATURE": sp}
            for branch in [d for d in (15, 20, 25, 32, 40, 50, 65, 80, 100) if d < run]:
                for typ, end in (("SOCKOLET", "SW"), ("THREDOLET", "THRD NPT")):
                    for rating in ("CL 3000", "CL 6000"):
                        if rating == "CL 6000" and branch > 50:
                            continue
                        for sp in sp_list:
                            yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn_pair(run, branch),
                                   "RATING": rating, "END": end, "STANDARD": "MSS SP-97", "FEATURE": sp}
                if branch <= 50:
                    for typ in ("ELBOLET", "LATROLET"):
                        for end, rating in (("SW", "CL 3000"), ("SW", "CL 6000"), ("THRD NPT", "CL 3000")):
                            yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn_pair(run, branch),
                                   "RATING": rating, "END": end, "STANDARD": "MSS SP-97"}
                    for sch in schedules(OLET_SCH[fam][:2], branch):
                        yield {"TYPE": "NIPOLET", "MOC": moc, "SPEC": spec, "SIZE": dn_pair(run, branch),
                               "SCHEDULE": sch, "END": "PE", "STANDARD": "MSS SP-97"}


# ======================================================================== plastic fittings
PLASTIC_FITTINGS = [
    ("UPVC", "ASTM D2466 SCH 40", [dn(d) for d in dn_range(15, 200)], "SOLVENT WELD"),
    ("UPVC", "ASTM D2467 SCH 80", [dn(d) for d in dn_range(15, 200)], "SOLVENT WELD"),
    ("CPVC", "ASTM D2846 SDR 11", [DN_TO_NPS[d] for d in dn_range(15, 50)], "SOLVENT WELD"),
    ("CPVC", "ASTM F439 SCH 80", [dn(d) for d in dn_range(15, 150)], "SOLVENT WELD"),
    ("HDPE PE100", "PN 10", [f"OD {o} MM" for o in (63, 75, 90, 110, 125, 160, 200, 250, 315, 400, 500, 630)],
     "BUTT FUSION"),
    ("HDPE PE100", "PN 16", [f"OD {o} MM" for o in (20, 25, 32, 40, 50, 63, 75, 90, 110, 160)], "ELECTROFUSION"),
    ("PPR", "PN 20", [f"OD {o} MM" for o in (20, 25, 32, 40, 50, 63, 75, 90, 110)], "SOCKET FUSION"),
]


@ELBOW.generator
def plastic_elbows():
    for moc, spec, sizes, end in PLASTIC_FITTINGS:
        for angle in ("90 DEG", "45 DEG"):
            for s in sizes:
                yield {"ANGLE": angle, "MOC": moc, "SPEC": spec, "SIZE": s, "END": end}


@TEE.generator
def plastic_tees():
    for moc, spec, sizes, end in PLASTIC_FITTINGS:
        for s in sizes:
            yield {"TYPE": "EQUAL", "MOC": moc, "SPEC": spec, "SIZE": s, "END": end}
        for i in range(1, len(sizes)):
            for j in range(max(0, i - 3), i):
                yield {"TYPE": "REDUCING", "MOC": moc, "SPEC": spec, "SIZE": f"{sizes[i]} X {sizes[j]}", "END": end}


@REDUCER.generator
def plastic_reducers():
    for moc, spec, sizes, end in PLASTIC_FITTINGS:
        for i in range(1, len(sizes)):
            for j in range(max(0, i - 3), i):
                yield {"TYPE": "CONCENTRIC", "MOC": moc, "SPEC": spec, "SIZE": f"{sizes[i]} X {sizes[j]}", "END": end}


@COUPLING.generator
def plastic_couplings():
    for moc, spec, sizes, end in PLASTIC_FITTINGS:
        for s in sizes:
            yield {"TYPE": "FULL", "MOC": moc, "SPEC": spec, "SIZE": s, "END": end}


@CAP.generator
def plastic_caps():
    for moc, spec, sizes, end in PLASTIC_FITTINGS:
        for s in sizes:
            yield {"MOC": moc, "SPEC": spec, "SIZE": s, "END": end}


# ======================================================================== screwed cast fittings
# (MOC, SPEC, finish, sizes, end, rating, standard)
SCREWED = [
    ("MI", "IS 1879", "GALVANISED", dn_range(15, 150), "THRD BSP", "", "IS 1879"),
    ("MI", "IS 1879", "BLACK", dn_range(15, 150), "THRD BSP", "", "IS 1879"),
    ("MI", "ASTM A197", "GALVANISED", dn_range(8, 100), "THRD NPT", "CL 150", "ASME B16.3"),
    ("MI", "ASTM A197", "BLACK", dn_range(8, 100), "THRD NPT", "CL 300", "ASME B16.3"),
    ("SS", "ASTM A351 CF8", "", dn_range(8, 100), "THRD BSP", "CL 150", "MSS SP-114"),
    ("SS", "ASTM A351 CF8M", "", dn_range(8, 100), "THRD BSP", "CL 150", "MSS SP-114"),
    ("SS", "ASTM A351 CF8M", "", dn_range(8, 100), "THRD NPT", "CL 150", "MSS SP-114"),
]


def _screwed_pairs(sizes: list[int]):
    for i in range(1, len(sizes)):
        for j in range(max(0, i - 3), i):
            yield sizes[i], sizes[j]


@ELBOW.generator
def screwed_elbows():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for angle in ("90 DEG", "45 DEG", "90 DEG STREET"):
            for d in sizes:
                yield {"ANGLE": angle, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end,
                       "STANDARD": std, "FEATURE": finish}


@TEE.generator
def screwed_tees():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for d in sizes:
            yield {"TYPE": "EQUAL", "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end,
                   "STANDARD": std, "FEATURE": finish}
        for a, b in _screwed_pairs(sizes):
            yield {"TYPE": "REDUCING", "MOC": moc, "SPEC": spec, "SIZE": dn_pair(a, b), "RATING": rating, "END": end,
                   "STANDARD": std, "FEATURE": finish}


@CROSS.generator
def screwed_crosses():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for d in sizes:
            yield {"TYPE": "EQUAL", "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end,
                   "STANDARD": std, "FEATURE": finish}


@COUPLING.generator
def screwed_sockets():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for d in sizes:
            yield {"TYPE": "SOCKET", "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end,
                   "STANDARD": std, "FEATURE": finish}
        for a, b in _screwed_pairs(sizes):
            yield {"TYPE": "REDUCING SOCKET", "MOC": moc, "SPEC": spec, "SIZE": dn_pair(a, b), "RATING": rating,
                   "END": end, "STANDARD": std, "FEATURE": finish}


@UNION.generator
def screwed_unions():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for d in sizes:
            for typ in ("FLAT SEAT", "CONICAL SEAT"):
                yield {"TYPE": typ, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end,
                       "STANDARD": std, "FEATURE": finish}


@CAP.generator
def screwed_caps():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for d in sizes:
            yield {"MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": rating, "END": end, "STANDARD": std,
                   "FEATURE": finish}


@PLUG.generator
def screwed_plugs():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for d in sizes:
            yield {"TYPE": "SQUARE HEAD" if moc == "MI" else "HEX HEAD", "MOC": moc, "SPEC": spec, "SIZE": dn(d),
                   "RATING": rating, "END": end, "STANDARD": std, "FEATURE": finish}


@BUSHING.generator
def screwed_bushes():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for a, b in _screwed_pairs(sizes):
            yield {"TYPE": "HEX", "MOC": moc, "SPEC": spec, "SIZE": dn_pair(a, b), "RATING": rating, "END": end,
                   "STANDARD": std, "FEATURE": finish}


@NIPPLE.generator
def screwed_nipples():
    for moc, spec, finish, sizes, end, rating, std in SCREWED:
        for d in sizes:
            yield {"TYPE": "HEX", "MOC": moc, "SPEC": spec, "SIZE": dn(d), "END": end, "STANDARD": std,
                   "FEATURE": finish}
