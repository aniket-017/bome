"""Field instruments, instrument valves, tube fittings, actuators."""
from app.catalog import noun
from app.catalog.data import GAUGE_MAKES, INSTRUMENT_MAKES, TUBE_FITTING_MAKES, dn
from app.catalog.electrical import METER
from app.catalog.piping import TUBE
from app.catalog.rotating import FITTING
from app.catalog.valves import VALVE

G = "INSTRUMENTATION"
GAUGE = noun("GAUGE", G, "NOS", ("TYPE", "DIAL", "RANGE", "MOC", "CONNECTION", "FILL", "ACCURACY", "STANDARD",
                                 "FEATURE", "MAKE"))
THERMOWELL = noun("THERMOWELL", G, "NOS", ("TYPE", "MOC", "CONNECTION", "LENGTH", "BORE", "STANDARD"))
THERMOCOUPLE = noun("THERMOCOUPLE", G, "NOS", ("TYPE", "CONSTRUCTION", "SHEATH", "DIA", "LENGTH", "HEAD", "STANDARD"))
RTD = noun("RTD", G, "NOS", ("TYPE", "CONSTRUCTION", "WIRES", "CLASS", "SHEATH", "DIA", "LENGTH", "HEAD", "STANDARD"))
TRANSMITTER = noun("TRANSMITTER", G, "NOS", ("TYPE", "RANGE", "MOC", "CONNECTION", "OUTPUT", "PROTECTION", "FEATURE",
                                             "MAKE"))
SENSOR = noun("SENSOR", G, "NOS", ("TYPE", "SIZE", "RANGE", "OUTPUT", "CONNECTION", "MAKE"))
ACTUATOR = noun("ACTUATOR", G, "NOS", ("TYPE", "SIZE", "TORQUE", "ACTION", "VOLTAGE", "PROTECTION", "MAKE"))
POSITIONER = noun("POSITIONER", G, "NOS", ("TYPE", "ACTION", "SIGNAL", "PROTECTION", "MAKE"))
DETECTOR = noun("DETECTOR", G, "NOS", ("TYPE", "GAS", "RANGE", "PRINCIPLE", "OUTPUT", "PROTECTION", "MAKE"))
ORIFICE = noun("ORIFICE PLATE", G, "NOS", ("TYPE", "MOC", "SIZE", "RATING", "THICKNESS", "STANDARD"))

P_RANGES = ["-1-0", "-1-1.5", "-1-3", "0-1", "0-1.6", "0-2.5", "0-4", "0-6", "0-10", "0-16", "0-25", "0-40", "0-60",
            "0-100", "0-160", "0-250", "0-400", "0-600", "0-1000"]


@GAUGE.generator
def gauges():
    for dial, conn in (("63 MM", "1/4 NPT(M)"), ("100 MM", "1/2 NPT(M)"), ("150 MM", "1/2 NPT(M)")):
        for r in P_RANGES:
            for mount in ("BOTTOM", "BACK"):
                for moc in ("SS304 CASE SS316 WETTED", "SS304 CASE BRASS WETTED"):
                    if moc.endswith("BRASS WETTED") and float(r.split("-")[-1]) > 60:
                        continue
                    for fill in ("DRY", "GLYCERINE FILLED"):
                        for make in GAUGE_MAKES:
                            yield {"TYPE": "PRESSURE BOURDON", "DIAL": f"{dial} DIAL", "RANGE": f"{r} BAR", "MOC": moc,
                                   "CONNECTION": f"{conn} {mount}", "FILL": fill,
                                   "ACCURACY": "CLASS 1.0" if dial != "63 MM" else "CLASS 1.6", "STANDARD": "EN 837-1",
                                   "MAKE": make}
        for r in P_RANGES[3:]:
            for seal in ("DIAPHRAGM SEAL FLANGED 1 IN CL150", "DIAPHRAGM SEAL FLANGED 2 IN CL300",
                         "DIAPHRAGM SEAL THREADED 1/2 NPT"):
                if dial == "63 MM":
                    continue
                for make in GAUGE_MAKES:
                    yield {"TYPE": "PRESSURE WITH DIAPHRAGM SEAL", "DIAL": f"{dial} DIAL", "RANGE": f"{r} BAR",
                           "MOC": "SS316 WETTED", "CONNECTION": seal, "FILL": "GLYCERINE FILLED",
                           "ACCURACY": "CLASS 1.6", "STANDARD": "EN 837-1", "MAKE": make}
    for r in ("0-25 MMWC", "0-50 MMWC", "0-100 MMWC", "0-250 MMWC", "0-500 MMWC", "0-1000 MMWC", "0-0.6 BAR", "0-1 BAR",
              "0-2.5 BAR", "0-6 BAR", "0-10 BAR"):
        for dial in ("100 MM", "150 MM"):
            for make in GAUGE_MAKES:
                yield {"TYPE": "DIFFERENTIAL PRESSURE", "DIAL": f"{dial} DIAL", "RANGE": r, "MOC": "SS316 WETTED",
                       "CONNECTION": "1/4 NPT(F) BOTTOM", "ACCURACY": "CLASS 1.6", "MAKE": make}
    for dial in ("100 MM", "150 MM"):
        for r in ("-50-50", "0-60", "0-100", "0-120", "0-150", "0-200", "0-250", "0-300", "0-400", "0-500"):
            for stem in (100, 150, 200, 250, 300):
                for conn in ("1/2 NPT(M) EVERY ANGLE", "1/2 NPT(M) BOTTOM"):
                    for make in GAUGE_MAKES:
                        yield {"TYPE": "TEMPERATURE BIMETALLIC", "DIAL": f"{dial} DIAL", "RANGE": f"{r} DEG C",
                               "MOC": f"SS304 CASE SS316 STEM {stem} MM", "CONNECTION": conn,
                               "ACCURACY": "CLASS 1.0", "STANDARD": "EN 13190", "MAKE": make}
    for typ in ("LEVEL REFLEX", "LEVEL TRANSPARENT", "LEVEL MAGNETIC"):
        for cc in (300, 500, 750, 1000, 1250, 1500, 2000, 2500, 3000):
            for rating in ("CL150", "CL300", "CL600"):
                for moc in ("CS", "SS316"):
                    for make in ("LEVCON", "CHEMTROLS", "KROHNE"):
                        yield {"TYPE": typ, "RANGE": f"CC {cc} MM", "MOC": moc,
                               "CONNECTION": f"FLANGED 3/4 IN {rating} RF SIDE SIDE", "MAKE": make}


TW_CONNS = ["1/2 NPT", "3/4 NPT", "1 NPT", "FLANGED 1 IN CL150 RF", "FLANGED 1-1/2 IN CL150 RF", "FLANGED 1-1/2 IN CL300 RF",
            "FLANGED 1-1/2 IN CL600 RF", "FLANGED 1-1/2 IN CL600 RTJ"]
TW_MOC = ["SS304", "SS316", "SS316L", "SS321", "ASTM A105", "ASTM A182 F11", "ASTM A182 F22", "HASTELLOY C276",
          "INCONEL 600", "MONEL 400"]


@THERMOWELL.generator
def thermowells():
    for conn in TW_CONNS:
        for typ in ("BAR STOCK TAPERED", "BAR STOCK STRAIGHT", "BAR STOCK STEPPED"):
            for moc in TW_MOC:
                for L in (100, 150, 200, 250, 300, 350, 400, 450, 500):
                    yield {"TYPE": typ, "MOC": moc, "CONNECTION": conn, "LENGTH": f"U {L} MM", "BORE": "BORE 6.6 MM",
                           "STANDARD": "ASME PTC 19.3 TW"}


LENGTHS = (150, 200, 250, 300, 400, 500, 600, 750, 1000)
HEADS = ("WEATHERPROOF HEAD IP66", "EX D HEAD IIC T6", "WITH HEAD MOUNTED TRANSMITTER 4-20 MA HART")


@THERMOCOUPLE.generator
def thermocouples():
    for t in ("K", "J", "T", "N"):
        for cons in ("SIMPLEX MI", "DUPLEX MI"):
            for sheath in ("SS316", "INCONEL 600"):
                for dia in (3, 4.5, 6, 8):
                    for L in LENGTHS:
                        for head in HEADS:
                            yield {"TYPE": f"TYPE {t}", "CONSTRUCTION": cons, "SHEATH": f"{sheath} SHEATH",
                                   "DIA": f"{dia} MM DIA", "LENGTH": f"L {L} MM", "HEAD": head,
                                   "STANDARD": "IEC 60584"}
    for t in ("R", "S", "B"):
        for cons in ("SIMPLEX", "DUPLEX"):
            for L in (300, 500, 750, 1000, 1250, 1500):
                yield {"TYPE": f"TYPE {t}", "CONSTRUCTION": cons, "SHEATH": "RECRYSTALLISED ALUMINA SHEATH",
                       "DIA": "10 MM DIA", "LENGTH": f"L {L} MM", "HEAD": HEADS[0], "STANDARD": "IEC 60584"}


@RTD.generator
def rtds():
    for cons in ("SIMPLEX", "DUPLEX"):
        for wires in ("3 WIRE", "4 WIRE"):
            for cls in ("CLASS A", "CLASS B"):
                for dia in (3, 6, 8):
                    for L in LENGTHS:
                        for head in HEADS:
                            yield {"TYPE": "PT100", "CONSTRUCTION": cons, "WIRES": wires, "CLASS": cls,
                                   "SHEATH": "SS316 SHEATH", "DIA": f"{dia} MM DIA", "LENGTH": f"L {L} MM",
                                   "HEAD": head, "STANDARD": "IEC 60751"}


OUTPUTS = ("4-20 MA HART", "FOUNDATION FIELDBUS", "PROFIBUS PA")
PROTECTIONS = ("EX D IIC T6", "EX IA IIC T4")


@TRANSMITTER.generator
def transmitters():
    for typ, ranges in (("PRESSURE GAUGE", ["0-1 BAR", "0-2.5 BAR", "0-6 BAR", "0-10 BAR", "0-16 BAR", "0-40 BAR",
                                            "0-100 BAR", "0-250 BAR", "0-400 BAR", "0-700 BAR"]),
                        ("PRESSURE ABSOLUTE", ["0-1 BAR A", "0-2.5 BAR A", "0-6 BAR A", "0-16 BAR A"]),
                        ("DIFFERENTIAL PRESSURE", ["0-25 MBAR", "0-62 MBAR", "0-250 MBAR", "0-1 BAR", "0-2.5 BAR",
                                                   "0-7 BAR", "0-20 BAR"])):
        for r in ranges:
            for moc in ("SS316L DIAPHRAGM", "HASTELLOY C276 DIAPHRAGM"):
                for out in OUTPUTS:
                    for prot in PROTECTIONS:
                        for make in INSTRUMENT_MAKES:
                            yield {"TYPE": typ, "RANGE": r, "MOC": moc,
                                   "CONNECTION": "1/2 NPT(F)" if typ != "DIFFERENTIAL PRESSURE" else "1/4 NPT(F) FLANGE ADAPTER",
                                   "OUTPUT": out, "PROTECTION": prot, "MAKE": make}
    for seal in ("FLANGED 2 IN CL150 DIAPHRAGM SEAL", "FLANGED 3 IN CL150 EXTENDED DIAPHRAGM SEAL",
                 "FLANGED 3 IN CL300 DIAPHRAGM SEAL"):
        for r in ("0-250 MBAR", "0-1 BAR", "0-2.5 BAR"):
            for out in OUTPUTS[:2]:
                for make in INSTRUMENT_MAKES:
                    yield {"TYPE": "DP LEVEL WITH REMOTE SEALS", "RANGE": r, "MOC": "SS316L DIAPHRAGM", "CONNECTION": seal,
                           "OUTPUT": out, "PROTECTION": PROTECTIONS[0], "MAKE": make}
    for typ, ranges in (("LEVEL RADAR 80 GHZ", ("0-10 M", "0-20 M", "0-30 M", "0-70 M")),
                        ("LEVEL RADAR 26 GHZ", ("0-10 M", "0-20 M", "0-35 M")),
                        ("LEVEL GUIDED WAVE RADAR ROD", ("0-2 M", "0-4 M", "0-6 M")),
                        ("LEVEL GUIDED WAVE RADAR CABLE", ("0-10 M", "0-20 M", "0-30 M")),
                        ("LEVEL ULTRASONIC", ("0-5 M", "0-8 M", "0-15 M"))):
        for r in ranges:
            for conn in ("FLANGED 2 IN CL150", "FLANGED 3 IN CL150", "FLANGED 4 IN CL150"):
                for out in OUTPUTS[:2]:
                    for make in INSTRUMENT_MAKES:
                        yield {"TYPE": typ, "RANGE": r, "MOC": "SS316L WETTED", "CONNECTION": conn, "OUTPUT": out,
                               "PROTECTION": PROTECTIONS[0], "MAKE": make}
    for inp in ("RTD PT100", "THERMOCOUPLE", "UNIVERSAL"):
        for mount in ("HEAD MOUNTED", "FIELD MOUNTED DUAL COMPARTMENT", "DIN RAIL"):
            for out in OUTPUTS:
                if mount == "DIN RAIL" and out != "4-20 MA HART":
                    continue
                for make in INSTRUMENT_MAKES:
                    yield {"TYPE": f"TEMPERATURE {mount}", "RANGE": f"INPUT {inp}", "OUTPUT": out,
                           "PROTECTION": PROTECTIONS[0] if mount.startswith("FIELD") else "", "MAKE": make}


FLOW_SIZES = [15, 25, 40, 50, 80, 100, 150, 200, 250, 300, 400, 500, 600]


@METER.generator(group=G)
def flow_meters():
    for d in FLOW_SIZES:
        for liner, electrodes in (("PTFE", ("SS316L", "HASTELLOY C", "TANTALUM")), ("PFA", ("SS316L", "HASTELLOY C")),
                                  ("HARD RUBBER", ("SS316L",)), ("POLYURETHANE", ("SS316L",))):
            if liner == "PFA" and d > 200:
                continue
            for el in electrodes:
                for end in ("FLANGED CL150 RF", "FLANGED PN16"):
                    for make in ("ENDRESS HAUSER", "YOKOGAWA", "KROHNE", "ABB", "SIEMENS", "EMERSON"):
                        yield {"TYPE": "FLOW", "PRINCIPLE": "ELECTROMAGNETIC", "SIZE": dn(d), "LINER": f"{liner} LINER",
                               "MOC": f"{el} ELECTRODES", "END": end, "ACCURACY": "0.5 PCT", "OUTPUT": "4-20 MA HART",
                               "MAKE": make}
    for d in FLOW_SIZES[:10]:
        for rating in ("CL150", "CL300", "CL600"):
            for make in ("YOKOGAWA", "ENDRESS HAUSER", "EMERSON", "KROHNE"):
                yield {"TYPE": "FLOW", "PRINCIPLE": "VORTEX", "SIZE": dn(d), "MOC": "SS316", "RATING": rating,
                       "END": "FLANGED RF", "ACCURACY": "0.75 PCT", "OUTPUT": "4-20 MA HART", "MAKE": make}
    for d in (8, 15, 25, 40, 50, 80, 100, 150):
        for rating in ("CL150", "CL300", "CL600"):
            for make in ("EMERSON", "ENDRESS HAUSER", "YOKOGAWA", "KROHNE"):
                yield {"TYPE": "FLOW", "PRINCIPLE": "CORIOLIS MASS", "SIZE": dn(d), "MOC": "SS316L", "RATING": rating,
                       "END": "FLANGED RF", "ACCURACY": "0.1 PCT", "OUTPUT": "4-20 MA HART", "MAKE": make}
    for d in (15, 25, 40, 50, 80):
        for rng in ("0-100 LPH", "0-500 LPH", "0-1000 LPH", "0-2500 LPH", "0-5000 LPH", "0-10 M3/HR", "0-25 M3/HR"):
            for typ in ("GLASS TUBE", "METAL TUBE"):
                yield {"TYPE": "FLOW", "PRINCIPLE": f"ROTAMETER {typ}", "SIZE": dn(d), "RANGE": rng, "MOC": "SS316",
                       "END": "FLANGED CL150 RF", "ACCURACY": "2 PCT", "MAKE": "EUREKA"}
    for d in FLOW_SIZES:
        yield {"TYPE": "FLOW", "PRINCIPLE": "ULTRASONIC CLAMP ON", "SIZE": dn(d), "ACCURACY": "1 PCT",
               "OUTPUT": "4-20 MA", "MAKE": "SIEMENS"}
        for rating in ("CL150", "CL300"):
            yield {"TYPE": "FLOW", "PRINCIPLE": "TURBINE", "SIZE": dn(d), "MOC": "SS316", "RATING": rating,
                   "END": "FLANGED RF", "ACCURACY": "0.5 PCT", "OUTPUT": "PULSE", "MAKE": "EMERSON"}


@SENSOR.generator
def sensors():
    for size, dists in (("M8", (1.5, 2)), ("M12", (2, 4)), ("M18", (5, 8)), ("M30", (10, 15))):
        for d in dists:
            for out in ("PNP NO", "PNP NC", "NPN NO", "NPN NC"):
                for conn in ("2M CABLE", "M12 CONNECTOR"):
                    for make in ("PEPPERL FUCHS", "SICK", "IFM", "OMRON", "BALLUFF"):
                        yield {"TYPE": "INDUCTIVE PROXIMITY", "SIZE": size, "RANGE": f"{d} MM SENSING",
                               "OUTPUT": f"{out} 10-30 VDC", "CONNECTION": conn, "MAKE": make}
    for typ, ranges in (("PHOTOELECTRIC DIFFUSE", ("100 MM", "300 MM", "1 M")), ("PHOTOELECTRIC RETROREFLECTIVE", ("3 M", "8 M")),
                        ("PHOTOELECTRIC THROUGH BEAM", ("10 M", "20 M")), ("CAPACITIVE", ("8 MM", "15 MM")),
                        ("ULTRASONIC", ("400 MM", "1000 MM", "3000 MM"))):
        for r in ranges:
            for out in ("PNP", "NPN"):
                for make in ("SICK", "OMRON", "PEPPERL FUCHS", "IFM"):
                    yield {"TYPE": typ, "RANGE": r, "OUTPUT": f"{out} 10-30 VDC", "CONNECTION": "M12 CONNECTOR",
                           "MAKE": make}
    for ppr in (100, 200, 360, 500, 600, 1000, 1024, 2000, 2500, 5000):
        for shaft in ("6 MM SOLID SHAFT", "10 MM SOLID SHAFT", "12 MM HOLLOW SHAFT"):
            for make in ("AUTONICS", "KUBLER", "SICK", "OMRON"):
                yield {"TYPE": "ROTARY ENCODER INCREMENTAL", "SIZE": shaft, "RANGE": f"{ppr} PPR",
                       "OUTPUT": "PUSH PULL 10-30 VDC", "MAKE": make}


@VALVE.generator(group=G)
def instrument_valves():
    sizes = ("1/4 IN", "3/8 IN", "1/2 IN", "3/4 IN")
    for moc in ("SS316", "CS ASTM A105", "MONEL 400", "DUPLEX F51"):
        for size in sizes:
            for end in ("NPT(M) X NPT(F)", "NPT(F) X NPT(F)", "NPT(M) X NPT(M)"):
                for rating in ("6000 PSI", "10000 PSI"):
                    yield {"TYPE": "NEEDLE", "DESIGN": "T PATTERN", "MOC": moc, "SIZE": size, "RATING": rating,
                           "END": end, "FEATURE": "PTFE PACKING"}
            for typ in ("GAUGE ROOT", "MULTIPORT GAUGE"):
                yield {"TYPE": typ, "MOC": moc, "SIZE": size, "RATING": "6000 PSI", "END": "NPT(M) X NPT(F)"}
        for typ in ("2 VALVE MANIFOLD", "3 VALVE MANIFOLD", "5 VALVE MANIFOLD"):
            for design in ("DIRECT MOUNT FLANGE X FLANGE", "REMOTE MOUNT NPT(F) X NPT(F)", "DIRECT MOUNT NPT(F) X FLANGE"):
                if typ.startswith("2") and design.endswith("FLANGE X FLANGE"):
                    continue
                yield {"TYPE": typ, "DESIGN": design, "MOC": moc, "SIZE": "1/2 IN", "RATING": "6000 PSI"}
        for size in ("1/2 IN", "3/4 IN", "1 IN", "1-1/2 IN", "2 IN"):
            for rating in ("CL150", "CL300", "CL600", "CL900", "CL1500"):
                yield {"TYPE": "DOUBLE BLOCK AND BLEED MONOFLANGE", "MOC": moc, "SIZE": size, "RATING": rating,
                       "END": "FLANGED RF X 1/2 NPT(F)"}
    for od in ("1/4 IN", "3/8 IN", "1/2 IN", "6 MM", "10 MM", "12 MM"):
        for typ in ("BALL INSTRUMENT 2 WAY", "BALL INSTRUMENT 3 WAY", "CHECK INSTRUMENT POPPET"):
            yield {"TYPE": typ, "MOC": "SS316", "SIZE": f"TUBE OD {od}", "RATING": "3000 PSI",
                   "END": "DOUBLE FERRULE COMPRESSION"}


TUBE_OD = ["1/8 IN", "1/4 IN", "3/8 IN", "1/2 IN", "3/4 IN", "1 IN", "6 MM", "8 MM", "10 MM", "12 MM", "16 MM",
           "20 MM", "25 MM"]
NPT = ["1/8", "1/4", "3/8", "1/2", "3/4", "1"]
OD_NPT = {"1/8 IN": NPT[0:2], "1/4 IN": NPT[0:4], "3/8 IN": NPT[1:4], "1/2 IN": NPT[2:5], "3/4 IN": NPT[3:6],
          "1 IN": NPT[4:6], "6 MM": NPT[0:3], "8 MM": NPT[1:3], "10 MM": NPT[1:4], "12 MM": NPT[2:5],
          "16 MM": NPT[3:5], "20 MM": NPT[3:6], "25 MM": NPT[4:6]}


@FITTING.generator(group=G)
def tube_fittings():
    mocs = ("SS316", "BRASS", "MONEL 400")
    for od in TUBE_OD:
        for typ in ("UNION", "UNION ELBOW", "UNION TEE", "UNION CROSS", "BULKHEAD UNION", "PLUG", "CAP",
                    "FERRULE SET", "NUT", "PORT CONNECTOR"):
            for moc in mocs:
                for make in TUBE_FITTING_MAKES:
                    yield {"TYPE": f"COMPRESSION DOUBLE FERRULE {typ}", "MOC": moc, "SIZE": f"TUBE OD {od}",
                           "RATING": "6000 PSI", "MAKE": make}
        for npt in OD_NPT[od]:
            for typ in ("MALE CONNECTOR", "FEMALE CONNECTOR", "MALE ELBOW", "FEMALE ELBOW", "MALE BRANCH TEE",
                        "MALE RUN TEE", "BULKHEAD MALE CONNECTOR"):
                for moc in mocs:
                    for make in TUBE_FITTING_MAKES:
                        yield {"TYPE": f"COMPRESSION DOUBLE FERRULE {typ}", "MOC": moc,
                               "SIZE": f"TUBE OD {od} X {npt} NPT", "RATING": "6000 PSI", "MAKE": make}
    for i, a in enumerate(TUBE_OD):
        for b in TUBE_OD[i + 1:]:
            if a.endswith("IN") != b.endswith("IN"):
                continue
            for moc in mocs[:2]:
                for make in TUBE_FITTING_MAKES:
                    yield {"TYPE": "COMPRESSION DOUBLE FERRULE REDUCING UNION", "MOC": moc,
                           "SIZE": f"TUBE OD {b} X {a}", "RATING": "6000 PSI", "MAKE": make}


INSTR_TUBE = {"1/8 IN": ("0.028 IN", "0.035 IN"), "1/4 IN": ("0.035 IN", "0.049 IN", "0.065 IN"),
              "3/8 IN": ("0.035 IN", "0.049 IN", "0.065 IN"), "1/2 IN": ("0.049 IN", "0.065 IN", "0.083 IN"),
              "3/4 IN": ("0.065 IN", "0.083 IN", "0.095 IN"), "1 IN": ("0.083 IN", "0.109 IN"),
              "6 MM": ("1 MM", "1.5 MM"), "8 MM": ("1 MM", "1.5 MM"), "10 MM": ("1 MM", "1.5 MM"),
              "12 MM": ("1 MM", "1.5 MM", "2 MM"), "16 MM": ("1.5 MM", "2 MM"), "20 MM": ("2 MM", "2.5 MM"),
              "25 MM": ("2 MM", "2.5 MM", "3 MM")}


@TUBE.generator(group=G)
def instrument_tubes():
    for od, walls in INSTR_TUBE.items():
        for wall in walls:
            for moc, spec in (("SS316/316L", "ASTM A269"), ("SS304", "ASTM A269"), ("MONEL 400", "ASTM B165"),
                              ("ALLOY 825", "ASTM B163"), ("DUPLEX 2205", "ASTM A789")):
                yield {"TYPE": "INSTRUMENT SMLS", "MOC": moc, "SPEC": spec, "OD": f"OD {od}", "THICKNESS": f"{wall} WALL",
                       "FINISH": "BRIGHT ANNEALED", "FEATURE": "HARDNESS 80 HRB MAX" if moc.startswith("SS") else ""}
            yield {"TYPE": "INSTRUMENT SMLS PVC COATED", "MOC": "SS316/316L", "SPEC": "ASTM A269", "OD": f"OD {od}",
                   "THICKNESS": f"{wall} WALL", "COLOR": "BLACK"}


RP_SIZES = [(52, 10), (63, 20), (75, 40), (83, 60), (92, 90), (105, 130), (125, 230), (140, 350), (160, 550),
            (190, 900), (210, 1300), (240, 2000), (270, 2900)]


@ACTUATOR.generator
def actuators():
    for size, nm in RP_SIZES:
        for action in ("DOUBLE ACTING", "SPRING RETURN"):
            for make in ("ROTORK", "EMERSON", "AIR TORQUE", "SCHISCHEK", "ROTEX"):
                yield {"TYPE": "PNEUMATIC RACK AND PINION", "SIZE": f"SIZE {size}",
                       "TORQUE": f"{nm if action == 'DOUBLE ACTING' else round(nm * 0.5)} NM AT 6 BAR",
                       "ACTION": action, "PROTECTION": "ISO 5211 NAMUR", "MAKE": make}
    for nm in (50, 100, 150, 250, 500, 1000, 1500, 2000, 3000, 4000):
        for volt in ("24 VDC", "230 VAC 1PH", "415 VAC 3PH"):
            for typ in ("ELECTRIC QUARTER TURN ON OFF", "ELECTRIC QUARTER TURN MODULATING"):
                for prot in ("IP67", "EX D IIC T4"):
                    for make in ("ROTORK", "AUMA", "LIMITORQUE", "BERNARD"):
                        yield {"TYPE": typ, "TORQUE": f"{nm} NM", "VOLTAGE": volt, "PROTECTION": prot, "MAKE": make}
    for nm in (30, 60, 120, 250, 500, 1000, 2000):
        for prot in ("IP68", "EX D IIC T4"):
            for make in ("ROTORK", "AUMA", "LIMITORQUE"):
                yield {"TYPE": "ELECTRIC MULTI TURN", "TORQUE": f"{nm} NM", "VOLTAGE": "415 VAC 3PH", "PROTECTION": prot,
                       "MAKE": make}


@POSITIONER.generator
def positioners():
    for typ in ("SMART ELECTRO PNEUMATIC", "ELECTRO PNEUMATIC ANALOG", "PNEUMATIC"):
        for action in ("LINEAR SINGLE ACTING", "LINEAR DOUBLE ACTING", "ROTARY SINGLE ACTING", "ROTARY DOUBLE ACTING"):
            for prot in ("IP66", "EX D IIC T6", "EX IA IIC T4"):
                for make in ("FISHER", "SIEMENS", "ABB", "MASONEILAN", "SAMSON"):
                    yield {"TYPE": typ, "ACTION": action,
                           "SIGNAL": "3-15 PSI" if typ == "PNEUMATIC" else "4-20 MA HART" if typ.startswith("SMART") else "4-20 MA",
                           "PROTECTION": prot, "MAKE": make}
    for make in ("FISHER", "ABB", "SAMSON", "MASONEILAN"):
        yield {"TYPE": "I/P CONVERTER", "SIGNAL": "4-20 MA TO 3-15 PSI", "PROTECTION": "EX D IIC T6", "MAKE": make}
        yield {"TYPE": "AIR FILTER REGULATOR INSTRUMENT", "SIGNAL": "0-4 BAR WITH GAUGE", "MAKE": make}


@DETECTOR.generator
def detectors():
    for gas, rng, principle in (("H2S", "0-100 PPM", "ELECTROCHEMICAL"), ("CO", "0-500 PPM", "ELECTROCHEMICAL"),
                                ("METHANE CH4", "0-100 PCT LEL", "CATALYTIC BEAD"), ("HYDROCARBON", "0-100 PCT LEL", "INFRARED"),
                                ("O2", "0-25 PCT VOL", "ELECTROCHEMICAL"), ("NH3", "0-100 PPM", "ELECTROCHEMICAL"),
                                ("CL2", "0-10 PPM", "ELECTROCHEMICAL"), ("H2", "0-100 PCT LEL", "CATALYTIC BEAD"),
                                ("SO2", "0-20 PPM", "ELECTROCHEMICAL")):
        for typ in ("GAS FIXED", "GAS PORTABLE SINGLE"):
            for make in ("HONEYWELL", "DRAEGER", "MSA", "CROWCON"):
                yield {"TYPE": typ, "GAS": gas, "RANGE": rng, "PRINCIPLE": principle,
                       "OUTPUT": "4-20 MA" if typ == "GAS FIXED" else "",
                       "PROTECTION": "EX D IIC T4" if typ == "GAS FIXED" else "", "MAKE": make}
    for make in ("HONEYWELL", "DRAEGER", "MSA"):
        yield {"TYPE": "GAS PORTABLE MULTI", "GAS": "LEL O2 H2S CO", "PRINCIPLE": "4 GAS", "MAKE": make}
    for typ in ("SMOKE OPTICAL", "HEAT RATE OF RISE", "HEAT FIXED TEMPERATURE", "MULTI SENSOR", "FLAME UV IR"):
        for out in ("CONVENTIONAL", "ADDRESSABLE"):
            for make in ("HONEYWELL", "SYSTEM SENSOR", "APOLLO", "BOSCH"):
                yield {"TYPE": f"FIRE {typ}", "OUTPUT": out, "MAKE": make}


@ORIFICE.generator
def orifice_plates():
    for d in (25, 40, 50, 80, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600):
        for rating in ("CL150", "CL300", "CL600", "CL900"):
            for typ in ("SQUARE EDGED CONCENTRIC", "RESTRICTION MULTI HOLE"):
                for moc in ("SS316", "SS304", "MONEL 400"):
                    t = 3 if d <= 150 else 6 if d <= 400 else 10
                    yield {"TYPE": typ, "MOC": moc, "SIZE": dn(d), "RATING": rating, "THICKNESS": f"{t} MM THK",
                           "STANDARD": "ISO 5167" if typ.startswith("SQUARE") else ""}
