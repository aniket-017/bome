"""O-rings, oil seals, mechanical seals, gland packing, hydraulic seals."""
from app.catalog import noun
from app.catalog.data import fmt

G = "SEALS"
ORING = noun("O-RING", G, "NOS", ("MATERIAL", "HARDNESS", "SIZE", "STANDARD"))
CORD = noun("O-RING CORD", G, "MTR", ("MATERIAL", "HARDNESS", "SIZE"))
OIL_SEAL = noun("OIL SEAL", G, "NOS", ("TYPE", "MATERIAL", "SIZE", "STANDARD", "MAKE"))
MECH_SEAL = noun("MECHANICAL SEAL", G, "NOS", ("TYPE", "SIZE", "FACES", "ELASTOMER", "SPRING", "STANDARD", "MAKE"))
PACKING = noun("PACKING", G, "KG", ("TYPE", "MATERIAL", "SIZE", "FEATURE"))
SEAL = noun("SEAL", G, "NOS", ("TYPE", "MATERIAL", "SIZE", "STANDARD"))
V_RING = noun("V-RING", G, "NOS", ("TYPE", "MATERIAL", "SIZE", "MAKE"))

ELASTOMERS = [("NBR", "70 SHORE A"), ("NBR", "90 SHORE A"), ("FKM VITON", "75 SHORE A"), ("EPDM", "70 SHORE A"),
              ("SILICONE", "70 SHORE A"), ("HNBR", "80 SHORE A")]


def _id_steps(lo: int, hi: int):
    v = lo
    while v <= hi:
        yield v
        v += 1 if v < 50 else 2 if v < 100 else 5 if v < 300 else 10


METRIC_CS = {1.5: (2, 50), 1.78: (2, 60), 2: (3, 80), 2.5: (4, 100), 2.62: (5, 120), 3: (5, 200), 3.5: (10, 250),
             3.53: (10, 250), 4: (10, 300), 5: (20, 400), 5.33: (20, 400), 6: (30, 500), 7: (50, 600), 8: (50, 600)}
AS568 = [*range(1, 51), *range(102, 179), *range(201, 285), *range(309, 396), *range(425, 476)]


@ORING.generator
def orings():
    for cs, (lo, hi) in METRIC_CS.items():
        for i in _id_steps(lo, hi):
            for moc, hardness in ELASTOMERS:
                yield {"MATERIAL": moc, "HARDNESS": hardness, "SIZE": f"ID {i} X CS {fmt(cs)} MM", "STANDARD": "ISO 3601"}
    for dash in AS568:
        for moc, hardness in ELASTOMERS + [("FFKM KALREZ", "75 SHORE A"), ("PTFE", "")]:
            yield {"MATERIAL": moc, "HARDNESS": hardness, "SIZE": f"AS568-{dash:03d}", "STANDARD": "AS568"}


@CORD.generator
def oring_cords():
    for cs in (1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 12, 15, 20):
        for moc, hardness in ELASTOMERS:
            yield {"MATERIAL": moc, "HARDNESS": hardness, "SIZE": f"DIA {fmt(cs)} MM"}


SHAFTS = [10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55, 58, 60, 62, 65,
          68, 70, 72, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 140, 150, 160, 170, 180, 190, 200]


@OIL_SEAL.generator
def oil_seals():
    for d in SHAFTS:
        offs = (10, 12, 15, 20) if d < 30 else (12, 15, 20, 25) if d < 70 else (15, 20, 25, 30) if d < 120 else (20, 25, 30)
        widths = (7,) if d < 25 else (7, 8) if d < 50 else (10, 12) if d < 100 else (12, 15)
        for off in offs:
            for w in widths:
                for typ in ("TC DOUBLE LIP WITH SPRING", "SC SINGLE LIP WITH SPRING", "TB DOUBLE LIP METAL CASE",
                            "VC SINGLE LIP WITHOUT SPRING"):
                    for moc in ("NBR", "FKM VITON"):
                        yield {"TYPE": typ, "MATERIAL": moc, "SIZE": f"{d} X {d + off} X {w} MM", "STANDARD": "DIN 3760"}


SEAL_SHAFTS = [12, 14, 16, 18, 20, 22, 24, 25, 28, 30, 32, 33, 35, 38, 40, 43, 45, 48, 50, 53, 55, 58, 60, 65, 70, 75,
               80, 85, 90, 95, 100, 110, 120, 130, 140, 150]
SEAL_MAKES = ["JOHN CRANE", "EAGLEBURGMANN", "FLOWSERVE", "SEALMATIC", "LEAK-PROOF"]


@MECH_SEAL.generator
def mechanical_seals():
    types = [("SINGLE SPRING ELASTOMER BELLOWS", "SS316", ""), ("SINGLE SPRING CONICAL", "SS316", ""),
             ("MULTI SPRING BALANCED", "HASTELLOY C", ""), ("MULTI SPRING UNBALANCED", "HASTELLOY C", ""),
             ("METAL BELLOWS", "ALLOY 718", ""), ("CARTRIDGE SINGLE", "HASTELLOY C", "API 682"),
             ("CARTRIDGE DOUBLE", "HASTELLOY C", "API 682")]
    faces = ["CARBON VS SIC", "SIC VS SIC", "TC VS TC", "CARBON VS CERAMIC", "CARBON VS TC"]
    for typ, spring, std in types:
        for d in SEAL_SHAFTS:
            if typ.startswith("CARTRIDGE") and d < 25:
                continue
            for face in faces:
                if typ.startswith(("CARTRIDGE", "METAL")) and face == "CARBON VS CERAMIC":
                    continue
                for elast in ("FKM VITON", "EPDM", "FFKM"):
                    if elast == "FFKM" and not typ.startswith(("CARTRIDGE", "METAL")):
                        continue
                    for make in SEAL_MAKES:
                        yield {"TYPE": typ, "SIZE": f"SHAFT {d} MM", "FACES": face, "ELASTOMER": elast,
                               "SPRING": f"{spring} SPRING", "STANDARD": std, "MAKE": make}


@PACKING.generator
def gland_packing():
    mats = ["PTFE", "GRAPHITE", "GFO PTFE GRAPHITE", "ARAMID", "ARAMID PTFE", "CERAMIC FIBRE", "EXPANDED GRAPHITE INCONEL WIRE",
            "CARBON FIBRE", "RAMIE PTFE", "GLASS FIBRE"]
    for moc in mats:
        for s in (3, 4, 5, 6, 8, 10, 12, 13, 14, 16, 19, 20, 22, 25):
            yield {"TYPE": "BRAIDED GLAND", "MATERIAL": moc, "SIZE": f"{s} X {s} MM SQUARE"}
    for d in SEAL_SHAFTS:
        for s in (6, 8, 10, 12):
            if s > d / 3:
                continue
            for h in (s, s + 2):
                yield {"TYPE": "DIE FORMED RING", "MATERIAL": "EXPANDED GRAPHITE 98 PCT", "SIZE": f"{d} X {d + 2 * s} X {h} MM",
                       "FEATURE": "SET OF 5"}


@SEAL.generator
def hydraulic_seals():
    rods = [10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 35, 36, 40, 45, 50, 55, 56, 60, 63, 65, 70, 75, 80, 85, 90, 100,
            110, 120, 125, 140, 160, 180, 200]
    for d in rods:
        for x, h in ((5, 6), (8, 8), (10, 10), (12.5, 12)):
            if x > d / 2:
                continue
            for typ, moc in (("ROD U-CUP", "PU 93 SHORE A"), ("ROD U-CUP", "NBR 85 SHORE A"),
                             ("ROD BUFFER STEP", "PTFE BRONZE"), ("WIPER SNAP-IN", "PU 93 SHORE A")):
                yield {"TYPE": typ, "MATERIAL": moc, "SIZE": f"{d} X {fmt(d + 2 * x)} X {h} MM", "STANDARD": "ISO 5597"}
    for bore in (25, 32, 40, 50, 63, 80, 100, 125, 140, 160, 180, 200, 220, 250, 280, 320):
        for typ, moc in (("PISTON COMPACT", "NBR PU POM"), ("PISTON STEP", "PTFE BRONZE"), ("PISTON U-CUP", "PU 93 SHORE A")):
            for x in (5, 7.5, 10):
                yield {"TYPE": typ, "MATERIAL": moc, "SIZE": f"{bore} X {fmt(bore - 2 * x)} MM", "STANDARD": "ISO 6020"}
        for w in (9.7, 15, 20, 25):
            yield {"TYPE": "WEAR RING", "MATERIAL": "PTFE BRONZE", "SIZE": f"BORE {bore} X {fmt(w)} X 2.5 MM", "STANDARD": "ISO 10766"}


@V_RING.generator
def v_rings():
    for d in [*range(5, 30, 1), *range(30, 100, 5), *range(100, 205, 10)]:
        for typ in ("VA", "VS"):
            for moc in ("NBR", "FKM"):
                for make in ("SKF", "FORSHEDA"):
                    yield {"TYPE": typ, "MATERIAL": moc, "SIZE": f"SHAFT {d} MM", "MAKE": make}
