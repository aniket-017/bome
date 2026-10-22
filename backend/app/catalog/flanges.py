"""Flanges, spectacle blinds and gaskets."""
from app.catalog import noun
from app.catalog.data import FORGED_MATERIALS, B16_5_CLASSES, cl, dn, dn_range, family, schedules, specials

FLANGE = noun("FLANGE", "FLANGES", "NOS", ("TYPE", "FACE", "MOC", "SPEC", "SIZE", "RATING", "SCHEDULE", "STANDARD",
                                           "FEATURE"))
BLIND = noun("SPECTACLE BLIND", "FLANGES", "NOS", ("TYPE", "FACE", "MOC", "SPEC", "SIZE", "RATING", "STANDARD",
                                                   "FEATURE"))
GASKET = noun("GASKET", "GASKETS", "NOS", ("TYPE", "MATERIAL", "INNER RING", "OUTER RING", "SIZE", "RATING",
                                           "THICKNESS", "STANDARD", "FEATURE"))

B16_5_SIZES = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600]
B16_47_SIZES = [650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1300, 1400, 1500]

HIGH_YIELD = [("CS", "ASTM A694 F52"), ("CS", "ASTM A694 F60"), ("CS", "ASTM A694 F65")]


def b16_5_classes(d: int) -> list[int]:
    return [c for c in B16_5_CLASSES if c != 2500 or d <= 300]


# maximum size per (type, class) in ASME B16.5
TYPE_LIMITS = {
    "WN": {c: 600 for c in B16_5_CLASSES} | {2500: 300},
    "BL": {c: 600 for c in B16_5_CLASSES} | {2500: 300},
    "SO": {150: 600, 300: 600, 600: 600, 900: 600, 1500: 65},
    "LJ": {150: 600, 300: 600, 600: 600, 900: 600, 1500: 600, 2500: 300},
    "SW": {150: 80, 300: 80, 600: 80, 900: 65, 1500: 65, 2500: 50},
    "THRD": {150: 100, 300: 100, 600: 100, 900: 65, 1500: 65, 2500: 50},
}


def faces(c: int, moc: str, typ: str) -> list[str]:
    if typ == "LJ":
        return [""]
    if c == 150:
        return ["RF", "FF"] if moc in ("CS", "SS") else ["RF"]
    return ["RF", "RTJ"]


def wn_bores(moc: str, c: int, d: int) -> list[str]:
    fam = family(moc)
    if fam in ("CS", "LTCS", "AS"):
        names = (["SCH 10", "SCH 20", "SCH 30", "SCH STD", "SCH 40", "SCH XS", "SCH 80"] if c <= 300 else
                 ["SCH 40", "SCH XS", "SCH 80", "SCH 160"] if c == 600 else
                 ["SCH XS", "SCH 80", "SCH 160", "SCH XXS"])
    else:
        names = (["SCH 10S", "SCH 40S", "SCH 80S"] if c <= 300 else
                 ["SCH 40S", "SCH 80S", "SCH 160"] if c == 600 else ["SCH 80S", "SCH 160"])
    return schedules(names, d) or [""]


def sw_bores(moc: str, d: int) -> list[str]:
    names = ["SCH 40", "SCH 80", "SCH 160"] if family(moc) in ("CS", "LTCS", "AS") else ["SCH 40S", "SCH 80S", "SCH 160"]
    return schedules(names, d)


@FLANGE.generator
def b16_5_flanges():
    for moc, spec in FORGED_MATERIALS + HIGH_YIELD:
        high_yield = spec.startswith("ASTM A694")
        for typ, limits in TYPE_LIMITS.items():
            if high_yield and typ not in ("WN", "BL"):
                continue
            for c, top in limits.items():
                for d in dn_range(15, top, B16_5_SIZES):
                    bores = (wn_bores(moc, c, d) if typ == "WN" else sw_bores(moc, d) if typ == "SW" else [""])
                    for face in faces(c, moc, typ):
                        for bore in bores:
                            for sp in specials(moc):
                                yield {"TYPE": "THRD NPT" if typ == "THRD" else typ, "FACE": face, "MOC": moc,
                                       "SPEC": spec, "SIZE": dn(d), "RATING": cl(c), "SCHEDULE": bore,
                                       "STANDARD": "ASME B16.5", "FEATURE": sp}


B16_47_MATERIALS = [m for m in FORGED_MATERIALS if m[1] in {
    "ASTM A105", "ASTM A105N", "ASTM A350 LF2 CL1", "ASTM A182 F304", "ASTM A182 F304L", "ASTM A182 F316",
    "ASTM A182 F316L", "ASTM A182 F51"}] + HIGH_YIELD
B16_47_SERIES = {"SERIES A": {150: 1500, 300: 1500, 600: 1500, 900: 1200},
                 "SERIES B": {150: 1500, 300: 1500, 600: 1500, 900: 1000}}


@FLANGE.generator
def b16_47_flanges():
    for moc, spec in B16_47_MATERIALS:
        carbon = family(moc) in ("CS", "LTCS", "AS")
        for series, limits in B16_47_SERIES.items():
            for c, top in limits.items():
                for d in dn_range(650, top, B16_47_SIZES):
                    face_list = ["RF", "RTJ"] if series == "SERIES A" and c >= 300 else ["RF"]
                    bores = schedules(["SCH STD", "SCH XS"] if carbon else ["SCH 10S", "SCH 40S"], d) or [""]
                    for typ in ("WN", "BL"):
                        for face in face_list:
                            for bore in (bores if typ == "WN" else [""]):
                                for sp in specials(moc):
                                    yield {"TYPE": typ, "FACE": face, "MOC": moc, "SPEC": spec, "SIZE": dn(d),
                                           "RATING": cl(c), "SCHEDULE": bore, "STANDARD": f"ASME B16.47 {series}",
                                           "FEATURE": sp}


@FLANGE.generator
def orifice_flanges():
    mats = [m for m in FORGED_MATERIALS if m[1] in {
        "ASTM A105", "ASTM A350 LF2 CL1", "ASTM A182 F11", "ASTM A182 F22", "ASTM A182 F304", "ASTM A182 F304L",
        "ASTM A182 F316", "ASTM A182 F316L"}]
    for moc, spec in mats:
        for c in (300, 600, 900, 1500, 2500):
            for d in dn_range(25, 300 if c == 2500 else 600, B16_5_SIZES):
                for face in ("RF", "RTJ"):
                    for bore in wn_bores(moc, c, d):
                        yield {"TYPE": "ORIFICE WN", "FACE": face, "MOC": moc, "SPEC": spec, "SIZE": dn(d),
                               "RATING": cl(c), "SCHEDULE": bore, "STANDARD": "ASME B16.36"}


EN_SIZES = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000]
EN_MATERIALS = [("CS", "EN 10025 S235JR"), ("CS", "EN 10222-2 P245GH"), ("CS", "EN 10222-2 P250GH"),
                ("SS", "EN 10222-5 1.4301"), ("SS", "EN 10222-5 1.4404"), ("SS", "EN 10222-5 1.4571")]


@FLANGE.generator
def en_flanges():
    for moc, spec in EN_MATERIALS:
        for typ in ("TYPE 01 PLATE", "TYPE 05 BLIND", "TYPE 11 WN", "TYPE 12 HUBBED SO"):
            for pn in (6, 10, 16, 25, 40):
                if pn == 6 and typ != "TYPE 01 PLATE":
                    continue
                for d in dn_range(15, 600 if pn >= 25 else 1000, EN_SIZES):
                    for face in ("B1", "A"):
                        yield {"TYPE": typ, "FACE": face, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": f"PN {pn}",
                               "STANDARD": "EN 1092-1"}


@FLANGE.generator
def plate_flanges():
    mats = [("MS", "IS 2062 E250"), ("SS", "ASTM A240 TP304"), ("SS", "ASTM A240 TP316")]
    for moc, spec in mats:
        for typ in ("PLATE SO", "BL"):
            for pn in ("PN 6", "PN 10", "PN 16", "PN 25"):
                for d in dn_range(15, 1000, EN_SIZES):
                    yield {"TYPE": typ, "FACE": "FF", "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": pn,
                           "STANDARD": "IS 6392"}
            for table in ("TABLE D", "TABLE E", "TABLE F", "TABLE H"):
                for d in dn_range(15, 600, EN_SIZES):
                    yield {"TYPE": typ, "FACE": "FF", "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": table,
                           "STANDARD": "BS 10"}


BLIND_MATERIALS = [("CS", "ASTM A516 GR 70"), ("CS", "ASTM A105"), ("LTCS", "ASTM A350 LF2 CL1"),
                   ("AS", "ASTM A387 GR 11 CL 2"), ("AS", "ASTM A387 GR 22 CL 2"), ("SS", "ASTM A240 TP304"),
                   ("SS", "ASTM A240 TP304L"), ("SS", "ASTM A240 TP316"), ("SS", "ASTM A240 TP316L"),
                   ("DSS", "ASTM A240 S31803")]


@BLIND.generator
def spectacle_blinds():
    for moc, spec in BLIND_MATERIALS:
        for c in B16_5_CLASSES:
            for typ, top in (("FIGURE 8", 300), ("SPADE", 600), ("SPACER", 600)):
                if c == 2500:
                    top = min(top, 300)
                for d in dn_range(15, top, B16_5_SIZES):
                    for face in (["RF"] if c == 150 else ["RF", "RTJ"]):
                        for sp in specials(moc):
                            yield {"TYPE": typ, "FACE": face, "MOC": moc, "SPEC": spec, "SIZE": dn(d), "RATING": cl(c),
                                   "STANDARD": "ASME B16.48", "FEATURE": sp}


# ======================================================================== gaskets
def flange_size_classes(include_b16_47: bool = True, classes=B16_5_CLASSES):
    for d in B16_5_SIZES:
        for c in b16_5_classes(d):
            if c in classes:
                yield d, c, "ASME B16.5"
    if include_b16_47:
        for series, limits in B16_47_SERIES.items():
            for c, top in limits.items():
                if c in classes:
                    for d in dn_range(650, top, B16_47_SIZES):
                        yield d, c, f"ASME B16.47 {series}"


def _gasket_std(gasket_std: str, flange_std: str) -> str:
    if flange_std == "ASME B16.5":
        return gasket_std
    return f"{gasket_std} FOR {flange_std.removeprefix('ASME ')}"


SPW_CONSTRUCTIONS = [
    ("SS304", "GRAPHITE"), ("SS316", "GRAPHITE"), ("SS316L", "GRAPHITE"), ("SS321", "GRAPHITE"), ("SS347", "GRAPHITE"),
    ("SS304", "PTFE"), ("SS316L", "PTFE"), ("SS316", "MICA"), ("DUPLEX S31803", "GRAPHITE"),
    ("INCONEL 625", "GRAPHITE"), ("MONEL 400", "PTFE"), ("HASTELLOY C276", "PTFE"),
]


@GASKET.generator
def spiral_wound():
    for winding, filler in SPW_CONSTRUCTIONS:
        outers = ["CS OUTER RING", "SS304 OUTER RING"] if winding.startswith("SS") else ["CS OUTER RING"]
        for inner in ("", f"{winding} INNER RING"):
            for outer in outers:
                for d, c, std in flange_size_classes():
                    for thk in ("THK 4.5 MM", "THK 3.2 MM"):
                        if thk == "THK 3.2 MM" and (std != "ASME B16.5" or c > 600):
                            continue
                        yield {"TYPE": "SPIRAL WOUND", "MATERIAL": f"{winding} WINDING {filler} FILLER",
                               "INNER RING": inner, "OUTER RING": outer, "SIZE": dn(d), "RATING": cl(c),
                               "THICKNESS": thk, "STANDARD": _gasket_std("ASME B16.20", std)}


RING_NUMBERS = [n for n in range(11, 106) if n != 83]
RTJ_MATERIALS = ["SOFT IRON 90 BHN", "LOW CARBON STEEL 120 BHN", "F5 130 BHN", "SS304 160 BHN", "SS316 160 BHN",
                 "SS347 160 BHN", "SS410 170 BHN", "INCONEL 625"]


@GASKET.generator
def ring_joints():
    for n in RING_NUMBERS:
        for shape in ("OVAL", "OCTAGONAL"):
            for mat in RTJ_MATERIALS:
                yield {"TYPE": f"RING JOINT {shape}", "MATERIAL": mat, "SIZE": f"R-{n}", "STANDARD": "ASME B16.20"}
    for prefix, numbers, std in (("RX", [20, 23, 24, 25, 26, 27, 31, 35, 37, 39, 41, 44, 45, 46, 47, 49, 50, 53, 54,
                                         57, 63, 65, 66, 69, 70, 73, 74, 82, 84, 85, 86, 87, 88, 89, 90, 91], "API 6A"),
                                 ("BX", [150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 162, 163, 164, 165, 166,
                                         167, 168, 169, 170], "API 6A")):
        for n in numbers:
            for mat in ("LOW CARBON STEEL 120 BHN", "SS304 160 BHN", "SS316 160 BHN", "INCONEL 625"):
                yield {"TYPE": f"RING JOINT {prefix}", "MATERIAL": mat, "SIZE": f"{prefix}-{n}", "STANDARD": std}


SOFT_MATERIALS = {
    "CNAF": ("THK 1.5 MM", "THK 2 MM", "THK 3 MM"),
    "PTFE VIRGIN": ("THK 1.5 MM", "THK 3 MM"),
    "PTFE GLASS FILLED": ("THK 1.5 MM", "THK 3 MM"),
    "EXPANDED PTFE": ("THK 1.5 MM", "THK 3 MM"),
    "FLEXIBLE GRAPHITE WITH SS316 TANGED INSERT": ("THK 1.5 MM", "THK 2 MM", "THK 3 MM"),
    "EPDM": ("THK 3 MM", "THK 5 MM"),
    "NEOPRENE": ("THK 3 MM", "THK 5 MM"),
    "NITRILE": ("THK 3 MM", "THK 5 MM"),
    "VITON": ("THK 3 MM",),
    "RED RUBBER": ("THK 3 MM", "THK 5 MM"),
}


@GASKET.generator
def soft_cut():
    for mat, thicknesses in SOFT_MATERIALS.items():
        rubber = mat in ("EPDM", "NEOPRENE", "NITRILE", "VITON", "RED RUBBER")
        classes = (150,) if rubber else (150, 300) if mat.startswith(("PTFE", "EXPANDED")) else (150, 300, 600)
        for d, c, std in flange_size_classes(classes=classes):
            for typ in (("RING", "FULL FACE") if c == 150 else ("RING",)):
                for thk in thicknesses:
                    yield {"TYPE": typ, "MATERIAL": mat, "SIZE": dn(d), "RATING": cl(c), "THICKNESS": thk,
                           "STANDARD": _gasket_std("ASME B16.21", std)}
        for pn in (6, 10, 16, 25, 40):
            for d in dn_range(15, 600 if pn >= 25 else 1000, EN_SIZES):
                for thk in thicknesses[:2]:
                    yield {"TYPE": "RING", "MATERIAL": mat, "SIZE": dn(d), "RATING": f"PN {pn}", "THICKNESS": thk,
                           "STANDARD": "EN 1514-1"}


@GASKET.generator
def kammprofile():
    for core in ("SS316L", "SS304", "SS321"):
        for facing in ("GRAPHITE", "PTFE"):
            for outer in ("", "INTEGRAL OUTER RING", "LOOSE OUTER RING"):
                for d, c, _ in flange_size_classes(include_b16_47=False):
                    if c == 2500:
                        continue
                    yield {"TYPE": "KAMMPROFILE", "MATERIAL": f"{core} CORE {facing} FACING", "OUTER RING": outer,
                           "SIZE": dn(d), "RATING": cl(c), "THICKNESS": "THK 4 MM"}


@GASKET.generator
def insulation_kits():
    for typ in ("TYPE E", "TYPE F", "TYPE D"):
        for mat in ("G10 GRE RETAINER WITH PTFE SEAL", "PHENOLIC WITH NITRILE FACING", "G10 GRE WITH VITON SEAL"):
            for d, c, _ in flange_size_classes(include_b16_47=False, classes=(150, 300, 600, 900, 1500)):
                yield {"TYPE": f"INSULATION KIT {typ}", "MATERIAL": mat, "SIZE": dn(d), "RATING": cl(c),
                       "FEATURE": "WITH SLEEVES AND WASHERS"}
