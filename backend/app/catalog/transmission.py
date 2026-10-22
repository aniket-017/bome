"""Belts, chains, sprockets, pulleys, taper bushes, shaft couplings, gears, gearboxes."""
from app.catalog import noun
from app.catalog.data import BELT_MAKES, fmt
from app.catalog.piping import BUSHING, COUPLING

G = "POWER TRANSMISSION"
BELT = noun("BELT", G, "NOS", ("TYPE", "SIZE", "CONSTRUCTION", "GRADE", "STANDARD", "MAKE"))
CHAIN = noun("CHAIN", G, "MTR", ("TYPE", "SIZE", "STRAND", "MOC", "STANDARD", "MAKE"))
SPROCKET = noun("SPROCKET", G, "NOS", ("TYPE", "CHAIN", "STRAND", "TEETH", "BORE", "MOC", "STANDARD"))
PULLEY = noun("PULLEY", G, "NOS", ("TYPE", "SECTION", "GROOVES", "PCD", "BORE", "MOC", "STANDARD"))
GEAR = noun("GEAR", G, "NOS", ("TYPE", "MODULE", "TEETH", "FACE WIDTH", "RATIO", "MOC", "FEATURE"))
RACK = noun("RACK", G, "NOS", ("TYPE", "MODULE", "SIZE", "LENGTH", "MOC", "FEATURE"))
GEARBOX = noun("GEARBOX", G, "NOS", ("TYPE", "SIZE", "RATIO", "POWER", "MOUNTING", "SHAFT", "MAKE"))

R40_MM = [500, 530, 560, 600, 630, 670, 710, 750, 800, 850, 900, 950, 1000, 1060, 1120, 1180, 1250, 1320, 1400, 1500,
          1600, 1700, 1800, 1900, 2000, 2120, 2240, 2360, 2500, 2650, 2800, 3000, 3150, 3350, 3550, 3750, 4000, 4250,
          4500, 4750, 5000, 5300, 5600, 6000, 6300, 6700, 7100, 7500, 8000, 8500, 9000, 9500, 10000, 10600, 11200,
          11800, 12500]


def _inch_lengths(lo: int, hi: int):
    v = lo
    while v <= hi:
        yield v
        v += 1 if v < 100 else 2 if v < 200 else 5 if v < 300 else 10


@BELT.generator
def v_belts():
    for sec, lo, hi in (("A", 20, 200), ("B", 25, 300), ("C", 50, 400), ("D", 100, 600), ("E", 150, 600)):
        for L in _inch_lengths(lo, hi):
            for cons, prefix in (("WRAPPED", ""), ("RAW EDGE COGGED", "X")):
                if prefix and sec in ("D", "E"):
                    continue
                for make in BELT_MAKES:
                    yield {"TYPE": "V CLASSICAL", "SIZE": f"{sec}{prefix} {L}",
                           "CONSTRUCTION": cons, "STANDARD": "IS 2494", "MAKE": make}
    for sec, lo, hi in (("SPZ", 487, 3550), ("SPA", 732, 4500), ("SPB", 1250, 8000), ("SPC", 2000, 12500)):
        for L in R40_MM:
            if not lo <= L <= hi:
                continue
            for cons, s in (("WRAPPED", sec), ("RAW EDGE COGGED", "XP" + sec[2:])):
                for make in BELT_MAKES:
                    yield {"TYPE": "V NARROW WEDGE", "SIZE": f"{s} {L}", "CONSTRUCTION": cons,
                           "STANDARD": "ISO 4184", "MAKE": make}
    for sec, lo, hi in (("3V", 250, 1400), ("5V", 500, 3550), ("8V", 1000, 6000)):
        for L in R40_MM + [250, 265, 280, 300, 315, 335, 355, 375, 400, 425, 450, 475]:
            if not lo <= L <= hi:
                continue
            for make in BELT_MAKES[:3]:
                yield {"TYPE": "V NARROW", "SIZE": f"{sec} {L}", "CONSTRUCTION": "WRAPPED",
                       "STANDARD": "RMA IP-22", "MAKE": make}


@BELT.generator
def timing_belts():
    for pitch, p, widths, lo, hi, step in (("3M", 3, (6, 9, 15), 50, 400, 10), ("5M", 5, (9, 15, 25), 50, 400, 5),
                                           ("8M", 8, (20, 30, 50, 85), 60, 450, 5),
                                           ("14M", 14, (40, 55, 85, 115, 170), 60, 400, 5)):
        for teeth in range(lo, hi + 1, step):
            for w in widths:
                for make in ("GATES", "OPTIBELT", "CONTINENTAL", "FENNER"):
                    yield {"TYPE": "TIMING HTD", "SIZE": f"{teeth * p}-{pitch}-{w}",
                           "CONSTRUCTION": "NEOPRENE GLASS CORD", "MAKE": make}
    for pitch, p, widths in (("XL", 5.08, ("025", "037")), ("L", 9.525, ("050", "075", "100")),
                             ("H", 12.7, ("075", "100", "150", "200", "300"))):
        for teeth in range(30, 250, 5):
            for w in widths:
                yield {"TYPE": "TIMING CLASSICAL",
                       "SIZE": f"{round(teeth * p / 2.54)}{pitch} {w}", "CONSTRUCTION": "NEOPRENE GLASS CORD",
                       "MAKE": "GATES"}


@BELT.generator(group="CONVEYOR SPARES", uom="MTR")
def conveyor_belts():
    for width in (400, 500, 650, 800, 1000, 1200, 1400, 1600, 1800, 2000):
        for rating in ("EP 400/3", "EP 500/4", "EP 630/4", "EP 800/4", "EP 1000/5", "EP 1250/5", "EP 1600/6"):
            for cover in ("4+2", "5+2", "6+3", "8+3"):
                for grade in ("M24", "N17", "HR T2", "FR K"):
                    yield {"TYPE": "CONVEYOR", "SIZE": f"{width} MM WIDE", "CONSTRUCTION": f"{rating} COVER {cover} MM",
                           "GRADE": f"GRADE {grade}", "STANDARD": "IS 1891"}


CHAINS = [("06B", "3/8 IN"), ("08B", "1/2 IN"), ("10B", "5/8 IN"), ("12B", "3/4 IN"), ("16B", "1 IN"),
          ("20B", "1-1/4 IN"), ("24B", "1-1/2 IN"), ("28B", "1-3/4 IN"), ("32B", "2 IN"),
          ("ANSI 40", "1/2 IN"), ("ANSI 50", "5/8 IN"), ("ANSI 60", "3/4 IN"), ("ANSI 80", "1 IN"),
          ("ANSI 100", "1-1/4 IN"), ("ANSI 120", "1-1/2 IN"), ("ANSI 140", "1-3/4 IN"), ("ANSI 160", "2 IN")]
STRANDS = ("SIMPLEX", "DUPLEX", "TRIPLEX")


@CHAIN.generator
def roller_chains():
    for code, pitch in CHAINS:
        std = "ANSI B29.1" if code.startswith("ANSI") else "ISO 606"
        for strand in STRANDS:
            for moc in ("CS", "SS304", "NICKEL PLATED CS"):
                for make in ("RENOLD", "ROLCON", "TSUBAKI", "DIAMOND"):
                    yield {"TYPE": "ROLLER", "SIZE": f"{code} {pitch} PITCH", "STRAND": strand, "MOC": moc,
                           "STANDARD": std, "MAKE": make}


@CHAIN.generator(uom="NOS")
def chain_links():
    for code, pitch in CHAINS:
        std = "ANSI B29.1" if code.startswith("ANSI") else "ISO 606"
        for typ in ("CONNECTING LINK", "CRANKED LINK OFFSET"):
            for strand in STRANDS:
                yield {"TYPE": typ, "SIZE": f"{code} {pitch} PITCH", "STRAND": strand, "MOC": "CS", "STANDARD": std}


TEETH = [*range(9, 31), 32, 35, 36, 38, 40, 42, 45, 48, 50, 54, 57, 60, 64, 70, 76]


@SPROCKET.generator
def sprockets():
    for code, pitch in CHAINS:
        if code.startswith("ANSI"):
            continue
        for strand, max_t in (("SIMPLEX", 76), ("DUPLEX", 57), ("TRIPLEX", 45)):
            for t in TEETH:
                if t > max_t:
                    continue
                for bore in ("PILOT BORE", "TAPER LOCK BORE"):
                    if bore == "TAPER LOCK BORE" and t < 15:
                        continue
                    for moc in ("C45", "CI"):
                        if moc == "CI" and t < 25:
                            continue
                        yield {"TYPE": "PLATE WHEEL WITH HUB", "CHAIN": f"{code} {pitch}", "STRAND": strand,
                               "TEETH": f"{t}T", "BORE": bore, "MOC": moc, "STANDARD": "ISO 606"}


R20_PCD = [56, 63, 71, 75, 80, 85, 90, 95, 100, 106, 112, 118, 125, 132, 140, 150, 160, 170, 180, 190, 200, 212, 224,
           236, 250, 265, 280, 300, 315, 335, 355, 375, 400, 425, 450, 475, 500, 530, 560, 600, 630, 710, 750, 800, 900,
           1000, 1120, 1250]


@PULLEY.generator
def pulleys():
    for sec, lo, hi, grooves in (("SPZ", 56, 630, range(1, 7)), ("SPA", 80, 800, range(1, 7)),
                                 ("SPB", 112, 1250, range(1, 9)), ("SPC", 200, 1250, range(2, 11)),
                                 ("A", 63, 630, range(1, 7)), ("B", 100, 1000, range(1, 9)), ("C", 160, 1250, range(2, 11))):
        std = "ISO 4183" if sec.startswith("SP") else "IS 3142"
        for pcd in R20_PCD:
            if not lo <= pcd <= hi:
                continue
            for g in grooves:
                for bore in ("PILOT BORE", "TAPER LOCK BORE"):
                    yield {"TYPE": "V BELT", "SECTION": sec, "GROOVES": f"{g} GROOVE", "PCD": f"PCD {pcd} MM",
                           "BORE": bore, "MOC": "CI GG20", "STANDARD": std}
    for pitch, widths in (("5M", (15, 25)), ("8M", (20, 30, 50, 85)), ("14M", (40, 55, 85, 115, 170))):
        for t in (18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 44, 48, 56, 64, 72, 80, 90, 112, 144):
            for w in widths:
                yield {"TYPE": "TIMING HTD", "SECTION": f"{pitch} {w} MM BELT", "GROOVES": f"{t}T",
                       "BORE": "TAPER LOCK BORE", "MOC": "CI GG20" if t > 30 else "AL"}


TAPER_BUSH = {"1008": (9, 25), "1108": (9, 28), "1210": (11, 32), "1610": (14, 42), "1615": (14, 42), "2012": (14, 50),
              "2517": (16, 65), "3020": (25, 75), "3030": (35, 75), "3525": (35, 90), "3535": (35, 90),
              "4030": (40, 100), "4040": (40, 100), "4535": (55, 110), "4545": (55, 110), "5040": (70, 125),
              "5050": (70, 125)}
BORES = [9, 10, 11, 12, 14, 15, 16, 18, 19, 20, 22, 24, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 55, 60, 65, 70, 75,
         80, 85, 90, 95, 100, 105, 110, 115, 120, 125]


@BUSHING.generator(group=G)
def taper_bushes():
    for size, (lo, hi) in TAPER_BUSH.items():
        for b in BORES:
            if lo <= b <= hi:
                for make in ("FENNER", "TB WOODS", "NATRAJ"):
                    yield {"TYPE": "TAPER LOCK", "MOC": "CI GG25", "SIZE": size, "BORE": f"BORE {b} MM WITH KEYWAY",
                           "MAKE": make}


@COUPLING.generator(group=G)
def shaft_couplings():
    families = [
        ("JAW", ["L035", "L050", "L070", "L075", "L090", "L095", "L099", "L100", "L110", "L150", "L190", "L225"],
         "NBR SPIDER", ["LOVEJOY", "FENNER", "KTR"]),
        ("TYRE", [f"F{n}" for n in (40, 50, 60, 70, 80, 90, 100, 110, 120, 140, 160, 180, 200, 220, 250)],
         "RUBBER TYRE", ["FENNER", "ROTEX", "RATHI"]),
        ("PIN BUSH", [f"SIZE {n}" for n in range(1, 16)], "RUBBER BUSH", ["RATHI", "FLEXIBLE COUPLING CO", "NATRAJ"]),
        ("GEAR", [f"SIZE {n}" for n in (1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7)], "", ["FALK", "ELECON", "NATRAJ"]),
        ("GRID", [f"{n}T10" for n in range(1020, 1110, 10)], "", ["FALK", "REXNORD"]),
        ("CHAIN", ["4012", "4014", "4016", "5014", "5016", "5018", "6018", "6020", "6022", "8018", "8020", "8022",
                   "10020"], "DUPLEX CHAIN", ["KATSU", "TSUBAKI", "RENOLD"]),
        ("DISC", [f"SIZE {n}" for n in (101, 126, 151, 176, 201, 226, 261, 301)], "SS DISC PACK", ["REXNORD", "EAGLEBURGMANN"]),
        ("FLUID", [f"SIZE {n}" for n in (7, 8, 9, 11, 12, 13, 15, 17, 19, 21, 24, 27)], "", ["FLUIDOMAT", "VOITH", "ELECON"]),
    ]
    for typ, sizes, element, makes in families:
        for size in sizes:
            for bore in ("PILOT BORE", "FINISH BORE WITH KEYWAY"):
                for make in makes:
                    yield {"TYPE": f"{typ} FLEXIBLE", "SIZE": size, "ELEMENT": element, "BORE": bore, "MAKE": make}
            if element:
                for make in makes:
                    yield {"TYPE": f"{typ} ELEMENT", "SIZE": size, "ELEMENT": element, "MAKE": make}


MODULES = (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10)
GEAR_TEETH = [*range(12, 31), 32, 35, 36, 38, 40, 42, 45, 48, 50, 55, 60, 65, 70, 75, 80, 90, 100, 110, 120]


@GEAR.generator
def gears():
    for m in MODULES:
        for t in GEAR_TEETH:
            for moc, feature in (("C45", ""), ("EN8", ""), ("EN24", "HARDENED AND TEMPERED"),
                                 ("EN353", "CASE CARBURISED AND GROUND"), ("NYLON 66", "")):
                if moc == "NYLON 66" and m > 3:
                    continue
                yield {"TYPE": "SPUR", "MODULE": f"MODULE {fmt(m)}", "TEETH": f"{t}T", "FACE WIDTH": f"FW {fmt(10 * m)} MM",
                       "MOC": moc, "FEATURE": feature}
            if t >= 15:
                for hand in ("RH", "LH"):
                    yield {"TYPE": f"HELICAL {hand} 15 DEG", "MODULE": f"MODULE {fmt(m)}", "TEETH": f"{t}T",
                           "FACE WIDTH": f"FW {fmt(12 * m)} MM", "MOC": "EN24", "FEATURE": "HARDENED AND TEMPERED"}
        for ratio in ("1:1", "1.5:1", "2:1", "3:1", "4:1"):
            yield {"TYPE": "BEVEL STRAIGHT SET", "MODULE": f"MODULE {fmt(m)}", "RATIO": ratio, "MOC": "EN353",
                   "FEATURE": "CASE CARBURISED"}
    for cd in (40, 50, 63, 75, 90, 110, 130, 150):
        for ratio in (5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60):
            yield {"TYPE": "WORM AND WHEEL SET", "MODULE": f"CENTRE DISTANCE {cd} MM", "RATIO": f"{fmt(ratio)}:1",
                   "MOC": "EN353 WORM PB2 WHEEL"}


@RACK.generator
def racks():
    for m in MODULES:
        for L in (500, 1000, 1500, 2000):
            for moc, feature in (("C45", ""), ("EN24", "INDUCTION HARDENED")):
                yield {"TYPE": "SPUR STRAIGHT", "MODULE": f"MODULE {fmt(m)}", "SIZE": f"{fmt(10 * m)} X {fmt(10 * m)} MM",
                       "LENGTH": f"L {L} MM", "MOC": moc, "FEATURE": feature}


GB_MAKES = ["ELECON", "BONFIGLIOLI", "PREMIUM", "SEW", "NORD"]
GB_POWERS = (0.18, 0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.7, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110)


@GEARBOX.generator
def gearboxes():
    for cd in (40, 50, 63, 75, 90, 110, 130, 150, 185, 225):
        for ratio in (5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100):
            for mounting in ("FOOT MOUNTED", "FLANGE MOUNTED"):
                for shaft in ("SOLID OUTPUT SHAFT", "HOLLOW OUTPUT SHAFT"):
                    for make in GB_MAKES:
                        yield {"TYPE": "WORM REDUCTION", "SIZE": f"CENTRE DISTANCE {cd} MM", "RATIO": f"{fmt(ratio)}:1",
                               "MOUNTING": mounting, "SHAFT": shaft, "MAKE": make}
    for typ, ratios in (("HELICAL INLINE", (5, 10, 16, 20, 25, 31.5, 40, 50, 63, 80, 100)),
                        ("BEVEL HELICAL RIGHT ANGLE", (8, 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100)),
                        ("PARALLEL SHAFT HELICAL", (6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40, 50)),
                        ("PLANETARY", (10, 20, 31.5, 50, 80, 100, 160, 200))):
        for kw in GB_POWERS:
            for ratio in ratios:
                for mounting in ("FOOT MOUNTED", "FLANGE MOUNTED"):
                    for make in GB_MAKES:
                        yield {"TYPE": typ, "RATIO": f"{fmt(ratio)}:1", "POWER": f"{fmt(kw)} KW",
                               "MOUNTING": mounting, "MAKE": make}
