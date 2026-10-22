"""Welding consumables, gases, lubricants, paints, adhesives, tapes, PPE, insulation, refractories, misc."""
from app.catalog import noun
from app.catalog.data import LUBE_MAKES, PAINT_MAKES, WELDING_MAKES, fmt
from app.catalog.electrical import ELECTRODE
from app.catalog.raw import WIRE
from app.catalog.rotating import FILTER

G_WLD = "WELDING CONSUMABLES"
G_LUB = "LUBRICANTS"
G_PNT = "PAINTS AND COATINGS"
G_CHM = "CHEMICALS AND ADHESIVES"
G_PPE = "SAFETY AND PPE"
G_INS = "INSULATION AND REFRACTORY"
G_GEN = "GENERAL CONSUMABLES"
FLUX = noun("FLUX", G_WLD, "KG", ("TYPE", "CLASS", "PACK", "MAKE"))
GAS = noun("GAS", G_WLD, "NOS", ("TYPE", "PURITY", "CAPACITY", "PACK"))
OIL = noun("OIL", G_LUB, "LTR", ("TYPE", "GRADE", "SPEC", "PACK", "MAKE"))
GREASE = noun("GREASE", G_LUB, "KG", ("TYPE", "GRADE", "PACK", "MAKE"))
COOLANT = noun("COOLANT", G_LUB, "LTR", ("TYPE", "GRADE", "PACK", "MAKE"))
PAINT = noun("PAINT", G_PNT, "LTR", ("TYPE", "SYSTEM", "SHADE", "FINISH", "PACK", "MAKE"))
THINNER = noun("THINNER", G_PNT, "LTR", ("TYPE", "PACK", "MAKE"))
ADHESIVE = noun("ADHESIVE", G_CHM, "NOS", ("TYPE", "GRADE", "STRENGTH", "PACK", "MAKE"))
SEALANT = noun("SEALANT", G_CHM, "NOS", ("TYPE", "GRADE", "COLOR", "PACK", "MAKE"))
CHEMICAL = noun("CHEMICAL", G_CHM, "KG", ("NAME", "CONCENTRATION", "GRADE", "PACK"))
TAPE = noun("TAPE", G_GEN, "NOS", ("TYPE", "MOC", "SIZE", "COLOR", "MAKE"))
SHOE = noun("SAFETY SHOE", G_PPE, "PAIR", ("TYPE", "TOE", "SOLE", "SIZE", "STANDARD", "MAKE"))
HELMET = noun("SAFETY HELMET", G_PPE, "NOS", ("TYPE", "COLOR", "SUSPENSION", "STANDARD", "MAKE"))
GLOVES = noun("GLOVES", G_PPE, "PAIR", ("TYPE", "MOC", "SIZE", "STANDARD", "MAKE"))
GOGGLES = noun("GOGGLES", G_PPE, "NOS", ("TYPE", "LENS", "STANDARD", "MAKE"))
MASK = noun("MASK", G_PPE, "NOS", ("TYPE", "FILTER", "STANDARD", "MAKE"))
PPE = noun("PPE", G_PPE, "NOS", ("TYPE", "SIZE", "COLOR", "STANDARD", "MAKE"))
HARNESS = noun("SAFETY HARNESS", G_PPE, "NOS", ("TYPE", "LANYARD", "STANDARD", "MAKE"))
COVERALL = noun("COVERALL", G_PPE, "NOS", ("TYPE", "MOC", "COLOR", "SIZE", "STANDARD"))
INSULATION = noun("INSULATION", G_INS, "NOS", ("TYPE", "MOC", "DENSITY", "SIZE", "THICKNESS", "FACING", "STANDARD"))
BRICK = noun("BRICK", G_INS, "NOS", ("TYPE", "MOC", "GRADE", "SHAPE", "SIZE", "STANDARD"))
CASTABLE = noun("CASTABLE", G_INS, "KG", ("TYPE", "MOC", "TEMPERATURE", "DENSITY", "PACK"))
ANODE = noun("ANODE", G_GEN, "NOS", ("TYPE", "MOC", "SIZE", "WEIGHT", "STANDARD"))
SHIM = noun("SHIM", G_GEN, "NOS", ("TYPE", "MOC", "SIZE", "THICKNESS"))
CLOTH = noun("CLOTH", G_GEN, "KG", ("TYPE", "MOC", "SIZE"))
LABEL = noun("LABEL", G_GEN, "NOS", ("TYPE", "MOC", "SIZE", "COLOR"))
MARKER = noun("MARKER", G_GEN, "NOS", ("TYPE", "TIP", "COLOR", "MAKE"))
CONTAINER = noun("CONTAINER", G_GEN, "NOS", ("TYPE", "MOC", "CAPACITY", "COLOR"))

SMAW = [
    ("E6013", "AWS A5.1", "RUTILE"), ("E7018", "AWS A5.1", "LOW HYDROGEN"), ("E7018-1", "AWS A5.1", "LOW HYDROGEN"),
    ("E7016", "AWS A5.1", "LOW HYDROGEN"), ("E6010", "AWS A5.1", "CELLULOSIC"), ("E7010-P1", "AWS A5.5", "CELLULOSIC"),
    ("E8018-B2", "AWS A5.5", "LOW HYDROGEN"), ("E9018-B3", "AWS A5.5", "LOW HYDROGEN"), ("E8018-C1", "AWS A5.5", "LOW HYDROGEN"),
    ("E8018-C3", "AWS A5.5", "LOW HYDROGEN"), ("E9015-B91", "AWS A5.5", "LOW HYDROGEN"), ("E8018-G", "AWS A5.5", "LOW HYDROGEN"),
    ("E308L-16", "AWS A5.4", "STAINLESS"), ("E309L-16", "AWS A5.4", "STAINLESS"), ("E316L-16", "AWS A5.4", "STAINLESS"),
    ("E347-16", "AWS A5.4", "STAINLESS"), ("E310-16", "AWS A5.4", "STAINLESS"), ("E2209-16", "AWS A5.4", "DUPLEX"),
    ("E2594-16", "AWS A5.4", "SUPER DUPLEX"), ("ENICRFE-3", "AWS A5.11", "NICKEL"), ("ENICRMO-3", "AWS A5.11", "NICKEL"),
    ("ENI-CI", "AWS A5.15", "CAST IRON"), ("ENIFE-CI", "AWS A5.15", "CAST IRON"), ("EFECR-A1 HARDFACING", "AWS A5.13", "HARDFACING"),
]
SMAW_DIAS = (2.0, 2.5, 3.15, 4.0, 5.0)
GTAW = ["ER70S-2", "ER70S-6", "ER80S-B2", "ER90S-B3", "ER80S-NI1", "ER90S-B9", "ER308L", "ER309L", "ER316L", "ER347",
        "ER2209", "ER2594", "ERNICR-3", "ERNICRMO-3", "ERCUNI", "ER4043", "ER5356", "ERTI-2"]


@ELECTRODE.generator(group=G_WLD, uom="KG")
def welding_electrodes():
    for cls, spec, typ in SMAW:
        for d in SMAW_DIAS:
            if typ in ("STAINLESS", "DUPLEX", "SUPER DUPLEX", "NICKEL", "CAST IRON") and d > 4:
                continue
            if typ == "CELLULOSIC" and d < 2.5:
                continue
            L = 300 if d <= 2.0 else 350 if d <= 3.15 else 450
            for make in WELDING_MAKES:
                yield {"TYPE": f"WELDING {typ}", "SPEC": spec, "CLASS": cls, "DIA": f"{fmt(d)} MM", "LENGTH": f"L {L} MM",
                       "MAKE": make}
    for d in (6.35, 9.5, 12.7):
        yield {"TYPE": "GOUGING CARBON", "MOC": "COPPER COATED", "DIA": f"{fmt(d)} MM", "LENGTH": "L 305 MM"}
    for d in (1.6, 2.4, 3.2):
        for cls in ("EWTH-2 RED", "EWCE-2 GREY", "EWLA-15 GOLD"):
            yield {"TYPE": "TUNGSTEN", "CLASS": cls, "DIA": f"{fmt(d)} MM", "LENGTH": "L 175 MM", "PACK": "PACK OF 10"}


@WIRE.generator(group=G_WLD)
def filler_wires():
    for cls in GTAW:
        spec = "AWS A5.18" if cls.startswith("ER70") else "AWS A5.28" if cls.startswith(("ER80", "ER90")) else \
            "AWS A5.9" if cls.startswith(("ER3", "ER2")) else "AWS A5.14" if cls.startswith("ERNI") else \
            "AWS A5.10" if cls.startswith(("ER4", "ER5")) else "AWS A5.7" if cls.startswith("ERCU") else "AWS A5.16"
        for d in (1.6, 2.0, 2.4, 3.2):
            for make in WELDING_MAKES:
                yield {"TYPE": "TIG FILLER ROD", "SPEC": f"{spec} {cls}", "DIA": f"{fmt(d)} MM", "PACK": "5 KG PACK",
                       "MAKE": make}
        if cls in ("ER70S-6", "ER308L", "ER309L", "ER316L", "ER4043", "ER5356", "ER80S-B2"):
            for d in (0.8, 1.0, 1.2, 1.6):
                for make in WELDING_MAKES:
                    yield {"TYPE": "MIG SOLID WIRE", "SPEC": f"{spec} {cls}", "DIA": f"{fmt(d)} MM", "PACK": "15 KG SPOOL",
                           "MAKE": make}
    for cls, spec in (("E71T-1C", "AWS A5.20"), ("E81T1-NI1C", "AWS A5.29"), ("E308LT1-1", "AWS A5.22"),
                      ("E316LT1-1", "AWS A5.22")):
        for d in (1.2, 1.6):
            for make in WELDING_MAKES:
                yield {"TYPE": "FLUX CORED WIRE", "SPEC": f"{spec} {cls}", "DIA": f"{fmt(d)} MM", "PACK": "15 KG SPOOL",
                       "MAKE": make}
    for cls in ("EM12K", "EH14", "EA2", "EB2", "EB3"):
        for d in (2.4, 3.2, 4.0, 5.0):
            for make in WELDING_MAKES:
                yield {"TYPE": "SAW WIRE", "SPEC": f"AWS A5.17 {cls}" if cls[1] != "B" and cls != "EA2" else f"AWS A5.23 {cls}",
                       "DIA": f"{fmt(d)} MM", "PACK": "25 KG COIL", "MAKE": make}


@FLUX.generator
def fluxes():
    for cls in ("F7A2-EM12K AGGLOMERATED", "F7A4-EH14 AGGLOMERATED", "FUSED NEUTRAL", "BASIC AGGLOMERATED"):
        for make in WELDING_MAKES:
            yield {"TYPE": "SAW", "CLASS": cls, "PACK": "25 KG BAG", "MAKE": make}
    for typ in ("BRAZING BORAX", "SOLDERING PASTE", "TIG BACK PURGING SS"):
        yield {"TYPE": typ, "PACK": "500 G"}


@GAS.generator
def gases():
    for typ, purity, caps in (("OXYGEN INDUSTRIAL", "99.5 PCT", ("7 M3", "10 M3")), ("OXYGEN MEDICAL", "99.5 PCT", ("7 M3",)),
                              ("DISSOLVED ACETYLENE", "98 PCT", ("6 KG", "9 KG")), ("ARGON", "99.999 PCT", ("7 M3", "10 M3")),
                              ("CARBON DIOXIDE", "99.9 PCT", ("30 KG", "45 KG")), ("NITROGEN", "99.999 PCT", ("7 M3", "10 M3")),
                              ("NITROGEN", "99.9 PCT", ("7 M3",)), ("HELIUM", "99.999 PCT", ("7 M3",)),
                              ("HYDROGEN", "99.99 PCT", ("7 M3",)), ("ARGON CO2 MIXTURE 80/20", "", ("10 M3",)),
                              ("ARGON CO2 MIXTURE 92/8", "", ("10 M3",)), ("LPG INDUSTRIAL", "", ("19 KG", "47.5 KG")),
                              ("AMMONIA", "99.5 PCT", ("50 KG",)), ("CHLORINE", "99.5 PCT", ("100 KG", "900 KG"))):
        for cap in caps:
            yield {"TYPE": typ, "PURITY": purity, "CAPACITY": cap, "PACK": "CYLINDER REFILL"}


VG = {"HYDRAULIC AW": (22, 32, 46, 68, 100), "HYDRAULIC HVLP": (32, 46, 68), "GEAR EP": (68, 100, 150, 220, 320, 460, 680),
      "TURBINE": (32, 46, 68), "COMPRESSOR SCREW": (32, 46, 68), "COMPRESSOR RECIPROCATING": (68, 100, 150),
      "SPINDLE": (5, 10, 22), "CIRCULATING": (100, 150, 220, 320), "SLIDEWAY": (68, 220), "WORM GEAR SYNTHETIC PAG": (220, 320, 460),
      "VACUUM PUMP": (68, 100), "REFRIGERATION": (32, 68), "HEAT TRANSFER THERMIC FLUID": (32,)}
OIL_PACKS = ("1 LTR", "5 LTR", "20 LTR", "50 LTR", "210 LTR BARREL")


@OIL.generator
def oils():
    for typ, grades in VG.items():
        for g in grades:
            for pack in OIL_PACKS:
                for make in LUBE_MAKES:
                    yield {"TYPE": typ, "GRADE": f"ISO VG {g}", "PACK": pack, "MAKE": make}
    for g, spec in (("SAE 15W40", "API CI-4"), ("SAE 20W50", "API CF-4"), ("SAE 10W30", "API SN"), ("SAE 5W30", "API SP"),
                    ("SAE 40", "API CF"), ("SAE 90", "API GL-4"), ("SAE 80W90", "API GL-5"), ("SAE 85W140", "API GL-5")):
        for pack in OIL_PACKS:
            for make in LUBE_MAKES:
                yield {"TYPE": "ENGINE" if "W" in g and "90" not in g and "140" not in g else "GEAR AUTOMOTIVE",
                       "GRADE": g, "SPEC": spec, "PACK": pack, "MAKE": make}
    for pack in ("20 LTR", "210 LTR BARREL"):
        yield {"TYPE": "TRANSFORMER INSULATING", "SPEC": "IS 335", "PACK": pack, "MAKE": "SAVITA"}
        for make in LUBE_MAKES:
            yield {"TYPE": "CUTTING NEAT", "PACK": pack, "MAKE": make}
            yield {"TYPE": "QUENCHING", "PACK": pack, "MAKE": make}
            yield {"TYPE": "RUST PREVENTIVE", "PACK": pack, "MAKE": make}


@GREASE.generator
def greases():
    for typ, grades in (("LITHIUM EP", (0, 1, 2, 3)), ("LITHIUM COMPLEX EP", (1, 2, 3)), ("CALCIUM", (2, 3)),
                        ("MOLYBDENUM DISULPHIDE", (2,)), ("HIGH TEMPERATURE BENTONITE", (2,)), ("FOOD GRADE H1", (1, 2)),
                        ("POLYUREA", (2, 3)), ("SYNTHETIC", (1, 2)), ("SILICONE VALVE", (3,)), ("OPEN GEAR", (0,))):
        for g in grades:
            for pack in ("400 G CARTRIDGE", "1 KG", "18 KG", "180 KG"):
                for make in LUBE_MAKES:
                    yield {"TYPE": typ, "GRADE": f"NLGI {g}", "PACK": pack, "MAKE": make}
    for typ in ("ANTI SEIZE COPPER", "ANTI SEIZE NICKEL", "ANTI SEIZE MOLY"):
        for pack in ("250 G", "500 G", "1 KG"):
            for make in ("MOLYKOTE", "LOCTITE", "CRC"):
                yield {"TYPE": typ, "PACK": pack, "MAKE": make}


@COOLANT.generator
def coolants():
    for typ, grade in (("SOLUBLE CUTTING OIL", "MINERAL"), ("SEMI SYNTHETIC CUTTING FLUID", ""), ("SYNTHETIC GRINDING FLUID", ""),
                       ("ENGINE RADIATOR", "ETHYLENE GLYCOL 50 PCT"), ("ENGINE RADIATOR", "CONCENTRATE")):
        for pack in ("5 LTR", "20 LTR", "50 LTR", "210 LTR BARREL"):
            for make in LUBE_MAKES:
                yield {"TYPE": typ, "GRADE": grade, "PACK": pack, "MAKE": make}


PAINT_TYPES = [
    ("PRIMER RED OXIDE ZINC PHOSPHATE", "ALKYD", "MATT"), ("PRIMER ZINC CHROMATE", "ALKYD", "MATT"),
    ("PRIMER EPOXY ZINC PHOSPHATE", "EPOXY 2 PACK", "MATT"), ("PRIMER INORGANIC ZINC SILICATE", "ETHYL SILICATE 2 PACK", "MATT"),
    ("PRIMER EPOXY ZINC RICH", "EPOXY 2 PACK", "MATT"), ("INTERMEDIATE EPOXY MIO", "EPOXY 2 PACK", "MATT"),
    ("FINISH POLYURETHANE", "ALIPHATIC PU 2 PACK", "GLOSS"), ("FINISH EPOXY", "EPOXY 2 PACK", "GLOSS"),
    ("FINISH SYNTHETIC ENAMEL", "ALKYD", "GLOSS"), ("FINISH CHLORINATED RUBBER", "CR", "SEMI GLOSS"),
    ("HEAT RESISTANT SILICONE 600 DEG C", "SILICONE", "MATT"), ("HEAT RESISTANT ALUMINIUM 250 DEG C", "ALKYD", "SEMI GLOSS"),
    ("COAL TAR EPOXY", "EPOXY 2 PACK", "SEMI GLOSS"), ("ROAD MARKING", "THERMOPLASTIC", "MATT"),
    ("FLOOR COATING", "EPOXY SELF LEVELLING", "GLOSS"),
]
SHADES = ["RAL 1003 SIGNAL YELLOW", "RAL 1015 LIGHT IVORY", "RAL 2004 PURE ORANGE", "RAL 3000 FLAME RED",
          "RAL 5012 LIGHT BLUE", "RAL 6002 LEAF GREEN", "RAL 7032 PEBBLE GREY", "RAL 7035 LIGHT GREY",
          "RAL 9005 JET BLACK", "RAL 9010 PURE WHITE", "IS 631 LIGHT GREY", "IS 632 DARK ADMIRALTY GREY",
          "IS 356 GOLDEN YELLOW", "IS 538 SIGNAL RED", "IS 221 FRENCH BLUE", "IS 410 LIGHT BROWN", "ALUMINIUM"]


@PAINT.generator
def paints():
    for typ, system, finish in PAINT_TYPES:
        shades = (["RED OXIDE"] if "RED OXIDE" in typ else ["YELLOW"] if "CHROMATE" in typ else ["GREY"]) \
            if typ.startswith(("PRIMER", "INTERMEDIATE")) else ["ALUMINIUM", "BLACK"] if typ.startswith("HEAT RESISTANT SILICONE") \
            else ["ALUMINIUM"] if "ALUMINIUM" in typ else ["BLACK"] if "COAL TAR" in typ else \
            ["WHITE", "YELLOW"] if "ROAD" in typ else SHADES
        for shade in shades:
            for pack in ("1 LTR", "4 LTR", "20 LTR"):
                for make in PAINT_MAKES:
                    yield {"TYPE": typ, "SYSTEM": system, "SHADE": shade, "FINISH": finish, "PACK": pack, "MAKE": make}
    for shade in SHADES:
        for make in ("ASIAN PAINTS", "AKZO NOBEL", "JOTUN"):
            yield {"TYPE": "POWDER COATING", "SYSTEM": "POLYESTER", "SHADE": shade, "PACK": "20 KG BOX", "MAKE": make}
            yield {"TYPE": "AEROSOL SPRAY", "SYSTEM": "ACRYLIC", "SHADE": shade, "PACK": "400 ML", "MAKE": make}


@THINNER.generator
def thinners():
    for typ in ("SYNTHETIC GENERAL PURPOSE", "EPOXY", "POLYURETHANE", "ZINC SILICATE", "NC LACQUER", "CHLORINATED RUBBER"):
        for pack in ("1 LTR", "5 LTR", "20 LTR"):
            for make in PAINT_MAKES[:4]:
                yield {"TYPE": typ, "PACK": pack, "MAKE": make}


LOCTITE = {"222": ("THREADLOCKER", "LOW"), "243": ("THREADLOCKER", "MEDIUM"), "262": ("THREADLOCKER", "HIGH"),
           "270": ("THREADLOCKER", "HIGH"), "277": ("THREADLOCKER", "HIGH"), "290": ("THREADLOCKER WICKING", "MEDIUM"),
           "401": ("INSTANT CYANOACRYLATE", ""), "406": ("INSTANT CYANOACRYLATE", ""), "480": ("INSTANT TOUGHENED", ""),
           "603": ("RETAINING COMPOUND", "HIGH"), "609": ("RETAINING COMPOUND", "MEDIUM"), "620": ("RETAINING COMPOUND HIGH TEMP", "HIGH"),
           "638": ("RETAINING COMPOUND", "HIGH"), "648": ("RETAINING COMPOUND", "HIGH"), "660": ("RETAINING QUICK METAL", "HIGH"),
           "3090": ("INSTANT GAP FILLING", ""), "EA 3421": ("EPOXY 2 PART", ""), "EA 9466": ("EPOXY 2 PART", "")}


@ADHESIVE.generator
def adhesives():
    for grade, (typ, strength) in LOCTITE.items():
        for pack in ("10 ML", "50 ML", "250 ML"):
            yield {"TYPE": typ, "GRADE": f"LOCTITE {grade}", "STRENGTH": f"{strength} STRENGTH" if strength else "",
                   "PACK": pack, "MAKE": "HENKEL"}
    for typ, make in (("SYNTHETIC RUBBER CONTACT", "FEVICOL SR"), ("PVA WOOD", "FEVICOL SH"), ("EPOXY 2 PART STEEL", "ARALDITE"),
                      ("EPOXY 2 PART STANDARD", "ARALDITE"), ("PVC SOLVENT CEMENT", "ASTRAL"), ("CPVC SOLVENT CEMENT", "ASTRAL"),
                      ("METAL REPAIR PUTTY", "DEVCON"), ("CERAMIC WEAR COMPOUND", "BELZONA")):
        for pack in ("100 G", "500 G", "1 KG"):
            yield {"TYPE": typ, "PACK": pack, "MAKE": make}


@SEALANT.generator
def sealants():
    for grade, typ in (("LOCTITE 510", "GASKET ELIMINATOR"), ("LOCTITE 518", "GASKET ELIMINATOR"), ("LOCTITE 542", "THREAD SEALANT HYDRAULIC"),
                       ("LOCTITE 545", "THREAD SEALANT PNEUMATIC"), ("LOCTITE 567", "THREAD SEALANT PTFE"),
                       ("LOCTITE 577", "THREAD SEALANT"), ("LOCTITE 5699", "SILICONE GASKET"), ("LOCTITE 5910", "SILICONE GASKET")):
        for pack in ("50 ML", "250 ML"):
            yield {"TYPE": typ, "GRADE": grade, "PACK": pack, "MAKE": "HENKEL"}
    for typ in ("SILICONE NEUTRAL CURE", "SILICONE ACETIC", "SILICONE HIGH TEMPERATURE RTV", "POLYURETHANE", "ACRYLIC",
                "FIRE RATED INTUMESCENT"):
        colors = ("RED",) if "HIGH TEMPERATURE" in typ else ("CLEAR", "WHITE", "BLACK", "GREY")
        for color in colors:
            for make in ("DOW CORNING", "WACKER", "PIDILITE", "SIKA"):
                yield {"TYPE": typ, "COLOR": color, "PACK": "300 ML CARTRIDGE", "MAKE": make}
    for typ in ("JOINTING COMPOUND HYLOMAR", "PIPE THREAD COMPOUND", "BOILER MANHOLE COMPOUND"):
        yield {"TYPE": typ, "PACK": "250 G"}


@CHEMICAL.generator
def chemicals():
    for name, concs in (("HYDROCHLORIC ACID", ("33 PCT",)), ("SULPHURIC ACID", ("98 PCT",)), ("NITRIC ACID", ("68 PCT",)),
                        ("CAUSTIC SODA FLAKES", ("98 PCT",)), ("CAUSTIC SODA LYE", ("48 PCT",)),
                        ("SODIUM HYPOCHLORITE", ("10 PCT", "12 PCT")), ("HYDROGEN PEROXIDE", ("50 PCT",)),
                        ("PHOSPHORIC ACID", ("85 PCT",)), ("ACETONE", ("99.5 PCT",)), ("ISOPROPYL ALCOHOL", ("99.9 PCT",)),
                        ("METHANOL", ("99.85 PCT",)), ("TRISODIUM PHOSPHATE", ("",)), ("HYDRAZINE HYDRATE", ("40 PCT",)),
                        ("ALUM", ("",)), ("POLY ALUMINIUM CHLORIDE", ("",)), ("ANTISCALANT RO", ("",)),
                        ("CORROSION INHIBITOR COOLING TOWER", ("",)), ("BIOCIDE NON OXIDISING", ("",)),
                        ("DEGREASER SOLVENT", ("",)), ("PICKLING PASTE SS", ("",)), ("PASSIVATION GEL SS", ("",)),
                        ("DYE PENETRANT TEST KIT", ("",)), ("MAGNETIC PARTICLE INK", ("",)), ("ION EXCHANGE RESIN CATION", ("",)),
                        ("ION EXCHANGE RESIN ANION", ("",)), ("ACTIVATED CARBON", ("",)), ("SILICA GEL BLUE", ("",))):
        for conc in concs:
            for grade in ("TECHNICAL GRADE", "LR GRADE", "AR GRADE") if "PCT" in conc else ("INDUSTRIAL",):
                for pack in ("1 KG", "25 KG", "50 KG") if "PCT" not in conc or "FLAKES" in name else ("2.5 LTR", "35 LTR", "200 LTR"):
                    yield {"NAME": name, "CONCENTRATION": conc, "GRADE": grade, "PACK": pack}


@TAPE.generator
def tapes():
    for w in (12, 19, 25):
        for color in ("WHITE",):
            for typ in ("PTFE THREAD SEAL",):
                for L in ("10 M", "12 M"):
                    yield {"TYPE": typ, "MOC": "PTFE", "SIZE": f"{w} MM X {L}", "COLOR": color, "MAKE": "UNIK"}
    for color in ("RED", "YELLOW", "BLUE", "GREEN", "BLACK", "WHITE", "GREEN YELLOW"):
        for make in ("ANCHOR", "3M", "STEELGRIP"):
            yield {"TYPE": "INSULATION ELECTRICAL", "MOC": "PVC", "SIZE": "19 MM X 8 M", "COLOR": color, "MAKE": make}
    for typ, moc, sizes, colors in (("MASKING", "CREPE PAPER", ("24 MM X 20 M", "48 MM X 20 M"), ("BEIGE",)),
                                    ("DUCT", "CLOTH", ("48 MM X 25 M",), ("SILVER", "BLACK")),
                                    ("PACKING", "BOPP", ("48 MM X 65 M", "72 MM X 65 M"), ("CLEAR", "BROWN")),
                                    ("DOUBLE SIDED FOAM", "PE FOAM", ("12 MM X 5 M", "24 MM X 5 M"), ("WHITE",)),
                                    ("FLOOR MARKING", "PVC", ("50 MM X 33 M", "75 MM X 33 M"), ("YELLOW", "YELLOW BLACK", "RED WHITE", "GREEN")),
                                    ("ANTI CORROSION PETROLATUM", "PETROLATUM", ("50 MM X 10 M", "100 MM X 10 M"), ("BROWN",)),
                                    ("ALUMINIUM FOIL", "AL", ("48 MM X 50 M",), ("SILVER",)),
                                    ("GLASS FIBRE", "GLASS FIBRE", ("25 MM X 30 M", "50 MM X 30 M"), ("WHITE",)),
                                    ("SELF AMALGAMATING", "EPR", ("19 MM X 10 M",), ("BLACK",)),
                                    ("WARNING CAUTION", "PE", ("75 MM X 300 M",), ("YELLOW BLACK", "RED WHITE"))):
        for size in sizes:
            for color in colors:
                yield {"TYPE": typ, "MOC": moc, "SIZE": size, "COLOR": color, "MAKE": "3M"}


PPE_MAKES = ("KARAM", "3M", "UDYOGI", "HONEYWELL")


@SHOE.generator
def safety_shoes():
    for typ in ("LOW ANKLE", "HIGH ANKLE", "GUMBOOT"):
        for toe in ("STEEL TOE", "COMPOSITE TOE"):
            for sole in ("PU SOLE", "DUAL DENSITY PU SOLE", "NITRILE RUBBER HEAT RESISTANT SOLE") if typ != "GUMBOOT" else ("PVC",):
                for size in range(5, 13):
                    for make in ("BATA", "KARAM", "ALLEN COOPER", "LIBERTY WARRIOR"):
                        yield {"TYPE": typ, "TOE": toe, "SOLE": sole, "SIZE": f"UK {size}",
                               "STANDARD": "IS 15298 S1P" if typ != "GUMBOOT" else "IS 15298 S5", "MAKE": make}


@HELMET.generator
def helmets():
    for color in ("WHITE", "YELLOW", "BLUE", "RED", "GREEN", "ORANGE"):
        for susp in ("NAPE STRAP", "RATCHET"):
            for make in PPE_MAKES:
                yield {"TYPE": "HDPE", "COLOR": color, "SUSPENSION": f"{susp} SUSPENSION", "STANDARD": "IS 2925", "MAKE": make}


@GLOVES.generator
def gloves():
    for typ, moc, std in (("CUT RESISTANT LEVEL 5", "HPPE NITRILE COATED", "EN 388"), ("GENERAL PURPOSE", "COTTON KNITTED", ""),
                          ("WELDING GAUNTLET", "LEATHER", "EN 12477"), ("CHEMICAL RESISTANT", "NITRILE", "EN 374"),
                          ("CHEMICAL RESISTANT", "NEOPRENE", "EN 374"), ("CHEMICAL RESISTANT", "PVC", "EN 374"),
                          ("HEAT RESISTANT", "KEVLAR", "EN 407"), ("DISPOSABLE", "NITRILE", "EN 455"),
                          ("ELECTRICAL INSULATING CLASS 0 1KV", "RUBBER", "IEC 60903"),
                          ("ELECTRICAL INSULATING CLASS 2 17KV", "RUBBER", "IEC 60903"), ("ANTI VIBRATION", "LEATHER", "EN ISO 10819"),
                          ("CANVAS", "COTTON CANVAS", "")):
        for size in ("S", "M", "L", "XL", "XXL") if typ != "WELDING GAUNTLET" else ("FREE SIZE",):
            for make in PPE_MAKES:
                yield {"TYPE": typ, "MOC": moc, "SIZE": size, "STANDARD": std, "MAKE": make}


@GOGGLES.generator
def goggles():
    for typ, lenses in (("SAFETY SPECTACLES", ("CLEAR", "SMOKE", "YELLOW")), ("CHEMICAL SPLASH GOGGLES", ("CLEAR",)),
                        ("WELDING GOGGLES", ("SHADE 5",)), ("WELDING HELMET AUTO DARKENING", ("SHADE 9-13",)),
                        ("WELDING HAND SCREEN", ("SHADE 10", "SHADE 11", "SHADE 12")), ("FACE SHIELD", ("CLEAR",))):
        for lens in lenses:
            for make in PPE_MAKES:
                yield {"TYPE": typ, "LENS": f"{lens} LENS", "STANDARD": "EN 166" if "WELD" not in typ else "EN 175", "MAKE": make}


@MASK.generator
def masks():
    for typ, flt in (("DISPOSABLE RESPIRATOR", "FFP1"), ("DISPOSABLE RESPIRATOR", "FFP2"), ("DISPOSABLE RESPIRATOR", "FFP3"),
                     ("DISPOSABLE RESPIRATOR", "N95"), ("HALF FACE RESPIRATOR", "ORGANIC VAPOUR CARTRIDGE"),
                     ("HALF FACE RESPIRATOR", "ACID GAS CARTRIDGE"), ("HALF FACE RESPIRATOR", "P100 PARTICULATE"),
                     ("FULL FACE RESPIRATOR", "ABEK1 CARTRIDGE"), ("SCBA 30 MIN", "6.8 LTR CYLINDER"),
                     ("RESPIRATOR CARTRIDGE", "ORGANIC VAPOUR"), ("RESPIRATOR CARTRIDGE", "MULTI GAS")):
        for make in ("3M", "HONEYWELL", "DRAEGER", "KARAM"):
            yield {"TYPE": typ, "FILTER": flt, "STANDARD": "EN 149" if "DISPOSABLE" in typ else "EN 140", "MAKE": make}


@PPE.generator
def other_ppe():
    for typ in ("EAR PLUG DISPOSABLE FOAM", "EAR PLUG REUSABLE CORDED", "EAR MUFF HELMET MOUNTED", "EAR MUFF HEADBAND"):
        for make in PPE_MAKES:
            yield {"TYPE": typ, "STANDARD": "EN 352", "MAKE": make}
    for size in ("M", "L", "XL", "XXL"):
        for color in ("FLUORESCENT ORANGE", "FLUORESCENT YELLOW"):
            yield {"TYPE": "REFLECTIVE SAFETY VEST", "SIZE": size, "COLOR": color, "STANDARD": "EN ISO 20471"}
        for typ in ("RAINCOAT PVC", "WELDING APRON LEATHER", "WELDING JACKET LEATHER", "CHEMICAL APRON PVC"):
            yield {"TYPE": typ, "SIZE": size}
    for typ in ("FIRST AID KIT 25 PERSON", "EYE WASH STATION PORTABLE", "SAFETY CONE 750 MM", "BARRICADE TAPE ROLL",
                "LOCKOUT PADLOCK", "LOCKOUT HASP", "LOCKOUT TAG", "LOCKOUT MCB DEVICE", "LOCKOUT VALVE BALL"):
        yield {"TYPE": typ, "COLOR": "RED" if "LOCKOUT" in typ else ""}


@HARNESS.generator
def harnesses():
    for typ in ("FULL BODY 1 POINT", "FULL BODY 3 POINT", "FULL BODY 5 POINT"):
        for lanyard in ("WITHOUT LANYARD", "DOUBLE LANYARD WITH SCAFFOLD HOOK", "DOUBLE LANYARD WITH ENERGY ABSORBER"):
            for make in PPE_MAKES:
                yield {"TYPE": typ, "LANYARD": lanyard, "STANDARD": "IS 3521", "MAKE": make}
    for typ in ("FALL ARRESTER RETRACTABLE 6 M", "FALL ARRESTER RETRACTABLE 10 M", "LIFELINE ROPE 10 M"):
        yield {"TYPE": typ, "STANDARD": "EN 360", "MAKE": "KARAM"}


@COVERALL.generator
def coveralls():
    for typ, moc, std in (("BOILER SUIT", "COTTON", ""), ("FR COVERALL", "FR COTTON", "NFPA 2112"),
                          ("DISPOSABLE COVERALL TYPE 5/6", "SMS NONWOVEN", "EN 13982"), ("ARC FLASH SUIT 40 CAL", "ARAMID", "NFPA 70E")):
        for color in ("NAVY BLUE", "ORANGE", "GREY") if "DISPOSABLE" not in typ else ("WHITE",):
            for size in ("S", "M", "L", "XL", "XXL", "XXXL"):
                yield {"TYPE": typ, "MOC": moc, "COLOR": color, "SIZE": size, "STANDARD": std}


NPS_INS = ["1/2", "3/4", "1", "1-1/2", "2", "3", "4", "6", "8", "10", "12", "14", "16", "18", "20", "24"]


@INSULATION.generator
def insulation():
    for moc, densities, std in (("ROCK WOOL", (48, 64, 100, 120, 150), "IS 8183"), ("GLASS WOOL", (24, 32, 48), "IS 8183"),
                                ("CERAMIC FIBRE BLANKET", (64, 96, 128), "ASTM C892")):
        for d in densities:
            for t in (25, 38, 50, 75, 100):
                for facing in ("", "ALUMINIUM FOIL FACED", "WIRE MESH ONE SIDE"):
                    if moc.startswith("CERAMIC") and facing:
                        continue
                    yield {"TYPE": "SLAB" if not moc.startswith("CERAMIC") else "BLANKET", "MOC": moc,
                           "DENSITY": f"{d} KG/M3", "SIZE": "1200 X 600 MM" if not moc.startswith("CERAMIC") else "7320 X 610 MM",
                           "THICKNESS": f"{t} MM THK", "FACING": facing, "STANDARD": std}
    for nps in NPS_INS:
        for t in (25, 40, 50, 65, 75, 100):
            for moc, d in (("ROCK WOOL", 120), ("CALCIUM SILICATE", 240), ("PUF", 40), ("NITRILE RUBBER", 0)):
                if moc == "NITRILE RUBBER" and t > 40:
                    continue
                yield {"TYPE": "PIPE SECTION", "MOC": moc, "DENSITY": f"{d} KG/M3" if d else "",
                       "SIZE": f'FOR {nps}" NPS PIPE', "THICKNESS": f"{t} MM THK"}
    for t in (0.5, 0.6, 0.8, 1.0):
        yield {"TYPE": "CLADDING SHEET", "MOC": "ALUMINIUM", "SIZE": "1000 MM WIDE COIL", "THICKNESS": f"{fmt(t)} MM THK"}
        yield {"TYPE": "CLADDING SHEET", "MOC": "SS304", "SIZE": "1000 MM WIDE COIL", "THICKNESS": f"{fmt(t)} MM THK"}


@BRICK.generator
def bricks():
    shapes = (("STRAIGHT", "230 X 114 X 75 MM"), ("STRAIGHT", "230 X 114 X 65 MM"), ("END ARCH", "230 X 114 X 75/65 MM"),
              ("SIDE ARCH", "230 X 114 X 75/65 MM"), ("KEY WEDGE", "230 X 114 X 75/55 MM"))
    for typ, moc, grades, std in (("FIRE CLAY", "ALUMINA 30-40 PCT", ("IS 8 GRADE 1", "IS 8 GRADE 2"), "IS 6"),
                                  ("HIGH ALUMINA", "ALUMINA", ("45 PCT", "50 PCT", "60 PCT", "70 PCT", "80 PCT"), "IS 8"),
                                  ("INSULATION", "HOT FACE", ("IS 2042 GRADE 1", "IS 2042 GRADE 2"), "IS 2042"),
                                  ("ACID RESISTANT", "", ("TYPE I", "TYPE II"), "IS 4860"),
                                  ("SILICA", "", ("93 PCT SIO2",), "IS 2050"), ("MAGNESITE", "", ("85 PCT MGO", "90 PCT MGO"), "")):
        for g in grades:
            for shape, size in shapes:
                yield {"TYPE": typ, "MOC": moc, "GRADE": g, "SHAPE": shape, "SIZE": size, "STANDARD": std}


@CASTABLE.generator
def castables():
    for typ, temps in (("DENSE", (1300, 1400, 1500, 1600, 1700)), ("LOW CEMENT", (1500, 1600, 1700)),
                       ("INSULATING", (1000, 1100, 1200, 1300)), ("ACID RESISTANT", (1000,))):
        for t in temps:
            for d in ((2.0, 2.2, 2.4, 2.6) if typ != "INSULATING" else (0.8, 1.0, 1.2, 1.4)):
                yield {"TYPE": typ, "TEMPERATURE": f"{t} DEG C", "DENSITY": f"{fmt(d)} G/CC", "PACK": "50 KG BAG"}
    for typ in ("FIRE CLAY MORTAR", "HIGH ALUMINA MORTAR", "RAMMING MASS", "GUNNING MASS", "CERAMIC FIBRE MODULE"):
        yield {"TYPE": typ, "PACK": "50 KG BAG" if "MODULE" not in typ else "300 X 300 X 250 MM"}


@FILTER.generator(group="FILTERS")
def filters():
    for typ, sizes in (("AIR PANEL PRE FILTER G4", ("595 X 595 X 48 MM", "595 X 295 X 48 MM", "610 X 610 X 50 MM")),
                       ("AIR BAG FILTER F7", ("592 X 592 X 600 MM", "592 X 287 X 600 MM")),
                       ("AIR HEPA H13", ("610 X 610 X 150 MM", "610 X 610 X 292 MM", "305 X 610 X 150 MM"))):
        for size in sizes:
            for make in ("CAMFIL", "SPECTRUM", "DONALDSON"):
                yield {"TYPE": typ, "SIZE": size, "MAKE": make}
    for typ, microns in (("WATER CARTRIDGE PP SPUN", (1, 5, 10, 20, 50)), ("WATER CARTRIDGE PLEATED", (0.2, 1, 5)),
                         ("WATER CARTRIDGE ACTIVATED CARBON", (10,))):
        for m in microns:
            for L in ("10 IN", "20 IN", "30 IN", "40 IN"):
                yield {"TYPE": typ, "MICRON": f"{fmt(m)} MICRON", "SIZE": f"{L} LONG"}
    for typ in ("DUST COLLECTOR BAG POLYESTER", "DUST COLLECTOR BAG PTFE MEMBRANE", "DUST COLLECTOR CARTRIDGE"):
        for size in ("DIA 130 X 2000 MM", "DIA 150 X 2500 MM", "DIA 160 X 3000 MM", "DIA 325 X 660 MM"):
            if ("CARTRIDGE" in typ) != size.startswith("DIA 325"):
                continue
            yield {"TYPE": typ, "SIZE": size, "MAKE": "DONALDSON"}
    for typ in ("ENGINE OIL", "ENGINE FUEL PRIMARY", "ENGINE FUEL SECONDARY", "ENGINE AIR PRIMARY", "ENGINE AIR SAFETY",
                "COMPRESSOR AIR INTAKE", "COMPRESSOR OIL", "COMPRESSOR SEPARATOR"):
        for make in ("DONALDSON", "FLEETGUARD", "BALDWIN", "MANN"):
            yield {"TYPE": f"{typ} ELEMENT", "MAKE": make}


@ANODE.generator
def anodes():
    for moc, std in (("ZINC", "MIL-DTL-18001"), ("ALUMINIUM INDIUM", "DNV RP B401"), ("MAGNESIUM", "ASTM B843")):
        for w in (1, 2, 3, 5, 7.5, 10, 15, 20, 25, 50):
            for typ in ("SACRIFICIAL BRACELET", "SACRIFICIAL STAND OFF", "SACRIFICIAL FLUSH MOUNT") if moc != "MAGNESIUM" else \
                    ("SACRIFICIAL PREPACKAGED",):
                yield {"TYPE": typ, "MOC": moc, "WEIGHT": f"{fmt(w)} KG", "STANDARD": std}
    for typ in ("IMPRESSED CURRENT MMO TUBULAR", "IMPRESSED CURRENT HSCI"):
        for size in ("25 X 1000 MM", "50 X 1500 MM"):
            yield {"TYPE": typ, "SIZE": size}


@SHIM.generator
def shims():
    for t in (0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 2.5, 3):
        for moc in ("SS304", "BRASS", "CS"):
            for size in ("50 X 50 MM", "75 X 75 MM", "100 X 100 MM", "125 X 125 MM", "150 X 150 MM", "200 X 200 MM"):
                yield {"TYPE": "PRECUT SLOTTED", "MOC": moc, "SIZE": size, "THICKNESS": f"{fmt(t)} MM THK"}
        for moc in ("SS304", "BRASS"):
            yield {"TYPE": "SHIM STOCK ROLL", "MOC": moc, "SIZE": "150 MM X 2.5 M", "THICKNESS": f"{fmt(t)} MM THK"}


@CLOTH.generator
def cloths():
    for typ, moc in (("COTTON WASTE", "WHITE"), ("COTTON WASTE", "COLOURED"), ("HOSIERY RAGS", "COTTON"),
                     ("LINT FREE WIPES", "NONWOVEN"), ("OIL ABSORBENT PADS", "POLYPROPYLENE"),
                     ("EMERY CLOTH", "ALUMINIUM OXIDE"), ("ASBESTOS FREE FIRE BLANKET", "GLASS FIBRE"),
                     ("WELDING BLANKET", "SILICA"), ("HESSIAN", "JUTE"), ("TARPAULIN", "HDPE")):
        yield {"TYPE": typ, "MOC": moc}


@LABEL.generator
def labels():
    for typ, sizes in (("CABLE TAG", ("30 X 10 MM", "50 X 15 MM")), ("VALVE TAG", ("DIA 50 MM", "75 X 25 MM")),
                       ("EQUIPMENT NAMEPLATE", ("100 X 50 MM", "150 X 75 MM")), ("PIPE MARKER", ("STD",)),
                       ("SAFETY SIGN", ("300 X 200 MM", "450 X 300 MM"))):
        for size in sizes:
            for moc in ("SS316", "AL ANODISED", "PVC", "ACRYLIC") if "SIGN" not in typ else ("PHOTOLUMINESCENT", "ACP"):
                yield {"TYPE": typ, "MOC": moc, "SIZE": size}
    for typ in ("CABLE FERRULE PVC 0-9", "CABLE FERRULE PVC A-Z"):
        for size in ("1.5 SQ MM", "2.5 SQ MM", "4 SQ MM", "6 SQ MM"):
            yield {"TYPE": typ, "MOC": "PVC", "SIZE": size, "COLOR": "YELLOW"}


@MARKER.generator
def markers():
    for typ, tips in (("PERMANENT", ("BULLET", "CHISEL")), ("PAINT MARKER", ("BULLET",)), ("METAL MARKING CRAYON", ("STICK",)),
                      ("SOAPSTONE FLAT", ("STICK",)), ("TEMPERATURE INDICATING STICK", ("STICK",))):
        for tip in tips:
            for color in ("BLACK", "RED", "BLUE", "WHITE", "YELLOW", "SILVER"):
                if typ.startswith(("SOAPSTONE", "TEMPERATURE")) and color != "WHITE":
                    continue
                yield {"TYPE": typ, "TIP": f"{tip} TIP", "COLOR": color, "MAKE": "MARKAL" if "MARK" in typ or "STONE" in typ else "CAMLIN"}


@CONTAINER.generator
def containers():
    for typ, moc, caps in (("DRUM OPEN TOP", "HDPE", (50, 100, 200)), ("DRUM CLOSED TOP", "MS", (200, 210)),
                           ("PAIL WITH LID", "HDPE", (5, 10, 20)), ("JERRY CAN", "HDPE", (5, 20, 35)),
                           ("DUSTBIN WITH LID", "HDPE", (60, 120, 240)), ("STORAGE TANK", "HDPE", (500, 1000, 2000, 5000)),
                           ("OIL CAN WITH SPOUT", "MS", (1, 2, 5)), ("SAFETY CAN", "MS", (5, 10)),
                           ("BIN STACKABLE", "PP", (5, 10, 20, 40))):
        for cap in caps:
            for color in ("BLUE", "GREEN", "RED", "YELLOW") if typ.startswith(("DUSTBIN", "BIN")) else ("",):
                yield {"TYPE": typ, "MOC": moc, "CAPACITY": f"{cap} LTR", "COLOR": color}
