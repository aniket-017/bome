"""Motors, pumps, compressors, fans, springs, pneumatics and hydraulics."""
from app.catalog import noun
from app.catalog.data import MOTOR_MAKES, PNEUMATIC_MAKES, fmt
from app.catalog.piping import TUBE
from app.catalog.valves import VALVE

G_ROT = "ROTATING EQUIPMENT"
G_FP = "PNEUMATICS AND HYDRAULICS"
MOTOR = noun("MOTOR", "MOTORS", "NOS", ("TYPE", "POWER", "POLES", "FRAME", "MOUNTING", "VOLTAGE", "EFFICIENCY",
                                        "ENCLOSURE", "FEATURE", "MAKE"))
PUMP = noun("PUMP", G_ROT, "NOS", ("TYPE", "SIZE", "CAPACITY", "HEAD", "MOC", "SEAL", "DRIVE", "STANDARD", "MAKE"))
COMPRESSOR = noun("COMPRESSOR", G_ROT, "NOS", ("TYPE", "POWER", "CAPACITY", "PRESSURE", "COOLING", "FEATURE", "MAKE"))
FAN = noun("FAN", G_ROT, "NOS", ("TYPE", "SIZE", "POWER", "SPEED", "VOLTAGE", "MOC", "MAKE"))
BLOWER = noun("BLOWER", G_ROT, "NOS", ("TYPE", "SIZE", "CAPACITY", "PRESSURE", "POWER", "MAKE"))
SPRING = noun("SPRING", "SPRINGS", "NOS", ("TYPE", "MOC", "WIRE DIA", "SIZE", "LENGTH", "FINISH", "STANDARD"))
CYLINDER = noun("CYLINDER", G_FP, "NOS", ("TYPE", "BORE", "ROD", "STROKE", "MOUNTING", "PRESSURE", "FEATURE",
                                          "STANDARD", "MAKE"))
FITTING = noun("FITTING", G_FP, "NOS", ("TYPE", "MOC", "SIZE", "END", "RATING", "STANDARD", "MAKE"))
FILTER = noun("FILTER", "FILTERS", "NOS", ("TYPE", "MEDIA", "MICRON", "SIZE", "PORT", "RATING", "FEATURE", "MAKE"))

KW = [0.18, 0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.7, 5.5, 7.5, 9.3, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110,
      132, 160, 200, 250, 315, 355]
# IEC frame size per kW for 2/4/6/8 pole TEFC motors (IS 12615)
FRAMES = {
    2: ["63", "63", "71", "71", "80", "80", "90S", "90L", "100L", "132S", "132S", "160M", "160M", "160M", "160L", "180M",
        "200L", "200L", "225M", "250M", "280S", "280M", "315S", "315M", "315L", "315L", "355", "355", "355"],
    4: ["63", "71", "71", "80", "80", "90S", "90L", "100L", "112M", "132S", "132M", "160M", "160M", "160L", "180M",
        "180L", "200L", "225S", "225M", "250M", "280S", "280M", "315S", "315M", "315L", "315L", "355", "355", "355"],
    6: ["71", "71", "80", "80", "90S", "90L", "100L", "112M", "132M", "132M", "160M", "160L", "160L", "180L", "200L",
        "200L", "225M", "250M", "280S", "280M", "315S", "315M", "315L", "315L", "355", "355", "355", None, None],
    8: ["80", "80", "90S", "90L", "100L", "100L", "112M", "132S", "132M", "160M", "160L", "160L", "180L", "200L", "225S",
        "225M", "250M", "280S", "280M", "315S", "315M", "315L", "315L", "355", "355", "355", None, None, None],
}


def _frame_no(frame: str) -> int:
    return int(frame.rstrip("SML"))


@MOTOR.generator
def ac_motors():
    for poles, frames in FRAMES.items():
        for kw, frame in zip(KW, frames):
            if frame is None:
                continue
            f = _frame_no(frame)
            mountings = ["FOOT B3", "FOOT CUM FLANGE B35"]
            if f <= 225:
                mountings.append("FLANGE B5")
            if f <= 132:
                mountings.append("FACE B14")
            for mounting in mountings:
                for eff in ("IE2", "IE3", "IE4"):
                    if eff == "IE4" and kw < 0.75:
                        continue
                    for make in MOTOR_MAKES:
                        yield {"TYPE": "INDUCTION SQUIRREL CAGE", "POWER": f"{fmt(kw)} KW", "POLES": f"{poles} POLE",
                               "FRAME": f"FRAME {frame}", "MOUNTING": mounting, "VOLTAGE": "415V 3PH 50HZ",
                               "EFFICIENCY": eff, "ENCLOSURE": "TEFC IP55", "MAKE": make}
                if f >= 80:
                    for zone in ("EX D IIB T4", "EX D IIC T4", "EX E II T3"):
                        for make in MOTOR_MAKES[:4]:
                            yield {"TYPE": "INDUCTION FLAMEPROOF", "POWER": f"{fmt(kw)} KW", "POLES": f"{poles} POLE",
                                   "FRAME": f"FRAME {frame}", "MOUNTING": mounting, "VOLTAGE": "415V 3PH 50HZ",
                                   "EFFICIENCY": "IE2", "ENCLOSURE": "TEFC IP55", "FEATURE": zone, "MAKE": make}
            if kw in (5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315) and poles in (2, 4):
                for make in MOTOR_MAKES:
                    yield {"TYPE": "INDUCTION SQUIRREL CAGE", "POWER": f"{fmt(kw)} KW", "POLES": f"{poles} POLE",
                           "FRAME": f"FRAME {frame}", "MOUNTING": "FOOT B3", "VOLTAGE": "415V 3PH 50HZ",
                           "EFFICIENCY": "IE3", "ENCLOSURE": "TEFC IP55", "FEATURE": "INVERTER DUTY WITH PTC THERMISTOR",
                           "MAKE": make}
    for kw in (0.18, 0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2):
        for poles in (2, 4):
            for typ in ("SINGLE PHASE CAPACITOR START", "SINGLE PHASE CAPACITOR START RUN"):
                for mounting in ("FOOT B3", "FLANGE B5"):
                    for make in MOTOR_MAKES[:5]:
                        yield {"TYPE": typ, "POWER": f"{fmt(kw)} KW", "POLES": f"{poles} POLE", "MOUNTING": mounting,
                               "VOLTAGE": "230V 1PH 50HZ", "ENCLOSURE": "TEFC IP55", "MAKE": make}
    for kv, kws in (("3.3KV", (160, 200, 250, 315, 400, 500, 630, 800, 1000)),
                    ("6.6KV", (250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500))):
        for kw in kws:
            for poles in (2, 4, 6):
                for make in ("ABB", "SIEMENS", "CROMPTON GREAVES", "BHEL", "WEG"):
                    yield {"TYPE": "HT INDUCTION SQUIRREL CAGE", "POWER": f"{kw} KW", "POLES": f"{poles} POLE",
                           "MOUNTING": "FOOT B3", "VOLTAGE": f"{kv} 3PH 50HZ", "ENCLOSURE": "CACA IP55", "MAKE": make}


ISO2858 = ["50-32-125", "50-32-160", "50-32-200", "50-32-250", "65-50-125", "65-50-160", "65-50-200", "65-50-250",
           "65-40-315", "80-65-125", "80-65-160", "80-65-200", "80-65-250", "80-50-315", "100-80-160", "100-80-200",
           "100-80-250", "100-65-315", "125-100-200", "125-100-250", "125-80-315", "125-100-400", "150-125-250",
           "150-125-315", "150-125-400", "200-150-250", "200-150-315", "200-150-400"]
PUMP_MAKES = ["KSB", "KIRLOSKAR", "GRUNDFOS", "FLOWSERVE", "SULZER", "XYLEM"]


@PUMP.generator
def pumps():
    for size in ISO2858:
        for moc in ("CI", "CI WITH SS316 IMPELLER", "SS316", "CF8M"):
            for seal in ("GLAND PACKING", "MECHANICAL SEAL"):
                for drive in ("BARE SHAFT", "WITH MOTOR AND BASEPLATE"):
                    for make in PUMP_MAKES:
                        yield {"TYPE": "CENTRIFUGAL END SUCTION", "SIZE": size, "MOC": moc, "SEAL": seal,
                               "DRIVE": drive, "STANDARD": "ISO 2858", "MAKE": make}
    for size in ISO2858[4:]:
        for moc in ("CS", "SS316", "DUPLEX"):
            for typ in ("CENTRIFUGAL OH2", "CENTRIFUGAL BB2"):
                yield {"TYPE": typ, "SIZE": size, "MOC": moc, "SEAL": "CARTRIDGE MECHANICAL SEAL API 682",
                       "DRIVE": "BARE SHAFT", "STANDARD": "API 610", "MAKE": "FLOWSERVE"}
    for model in (1, 3, 5, 10, 15, 20, 32, 45, 64, 90, 120, 150):
        for stages in range(2, 17, 2):
            for moc in ("CI", "SS304", "SS316"):
                yield {"TYPE": "VERTICAL MULTISTAGE", "SIZE": f"CR {model}-{stages}", "MOC": moc,
                       "SEAL": "CARTRIDGE MECHANICAL SEAL", "DRIVE": "WITH MOTOR", "MAKE": "GRUNDFOS"}
    for kw in (0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.7, 5.5, 7.5, 9.3, 11, 15):
        for head in (10, 15, 20, 25, 30, 40, 50, 60):
            for typ in ("MONOBLOCK CENTRIFUGAL", "OPENWELL SUBMERSIBLE", "DEWATERING SUBMERSIBLE"):
                for make in PUMP_MAKES[:3] + ["CROMPTON GREAVES", "CRI"]:
                    yield {"TYPE": typ, "HEAD": f"HEAD {head} M", "MOC": "CI", "DRIVE": f"{fmt(kw)} KW MOTOR",
                           "MAKE": make}
    for cc in (1, 2, 4, 6, 8, 10, 12, 16, 20, 25, 32, 40, 50, 63, 80, 100):
        for make in ("BOSCH REXROTH", "PARKER", "EATON", "DYNAMATIC", "MARZOCCHI"):
            yield {"TYPE": "HYDRAULIC GEAR", "CAPACITY": f"{cc} CC/REV", "MOC": "AL", "DRIVE": "BARE SHAFT", "MAKE": make}
    for size in ("1/2 IN", "1 IN", "1-1/2 IN", "2 IN", "3 IN"):
        for moc in ("AL", "SS316", "PP", "PVDF"):
            for dia in ("PTFE", "SANTOPRENE", "NBR", "EPDM"):
                for make in ("GRACO", "WILDEN", "ARO", "YAMADA"):
                    yield {"TYPE": "AIR OPERATED DOUBLE DIAPHRAGM", "SIZE": size, "MOC": moc,
                           "SEAL": f"{dia} DIAPHRAGM", "MAKE": make}
    for lph in (2, 6, 10, 20, 30, 50, 100, 200, 300, 500, 1000):
        for bar in (5, 10, 20, 40):
            for moc in ("PP", "SS316", "PVDF"):
                for make in ("MILTON ROY", "PROMINENT", "GRUNDFOS"):
                    yield {"TYPE": "DOSING DIAPHRAGM", "CAPACITY": f"{lph} LPH", "HEAD": f"{bar} BAR", "MOC": moc,
                           "MAKE": make}
    for m3h in (1, 2, 5, 10, 20, 30, 50, 75, 100, 150):
        for typ in ("SCREW TWIN", "PROGRESSIVE CAVITY", "INTERNAL GEAR"):
            for moc in ("CI", "CS", "SS316"):
                for make in ("ROTO PUMPS", "NETZSCH", "TUSHACO", "VIKING"):
                    yield {"TYPE": typ, "CAPACITY": f"{m3h} M3/HR", "MOC": moc, "SEAL": "MECHANICAL SEAL", "MAKE": make}


@COMPRESSOR.generator
def compressors():
    for kw in (5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250):
        for bar in (7.5, 8.5, 10, 13):
            for typ, cooling in (("SCREW OIL INJECTED", "AIR COOLED"), ("SCREW OIL INJECTED", "WATER COOLED"),
                                 ("SCREW OIL FREE", "AIR COOLED"), ("SCREW OIL FREE", "WATER COOLED")):
                if cooling == "WATER COOLED" and kw < 37:
                    continue
                for vsd in ("", "VFD"):
                    for make in ("ATLAS COPCO", "INGERSOLL RAND", "ELGI", "KAESER", "CHICAGO PNEUMATIC"):
                        yield {"TYPE": typ, "POWER": f"{fmt(kw)} KW", "PRESSURE": f"{fmt(bar)} BAR",
                               "COOLING": cooling, "FEATURE": vsd, "MAKE": make}
    for hp in (1, 2, 3, 5, 7.5, 10, 15, 20, 25, 30, 40, 50):
        for stage, bar in (("SINGLE STAGE", 8), ("TWO STAGE", 12)):
            for make in ("ELGI", "INGERSOLL RAND", "KIRLOSKAR", "ATLAS COPCO"):
                yield {"TYPE": f"RECIPROCATING {stage}", "POWER": f"{fmt(hp)} HP", "PRESSURE": f"{bar} BAR",
                       "COOLING": "AIR COOLED", "FEATURE": "WITH AIR RECEIVER", "MAKE": make}


@FAN.generator
def fans():
    for sweep in (225, 300, 375, 450, 600, 750, 900):
        for speed in ("900 RPM", "1400 RPM"):
            for typ in ("EXHAUST WALL MOUNTED", "AXIAL FLOW", "PEDESTAL", "MAN COOLER"):
                for moc in ("MS", "AL"):
                    for make in ("CROMPTON GREAVES", "ALMONARD", "HAVELLS", "USHA"):
                        yield {"TYPE": typ, "SIZE": f"{sweep} MM SWEEP", "SPEED": speed, "VOLTAGE": "230V 1PH",
                               "MOC": moc, "MAKE": make}
    for sweep in (900, 1200, 1400):
        for make in ("CROMPTON GREAVES", "HAVELLS", "USHA", "ORIENT"):
            yield {"TYPE": "CEILING", "SIZE": f"{sweep} MM SWEEP", "VOLTAGE": "230V 1PH", "MAKE": make}
    for kw in (0.37, 0.75, 1.5, 2.2, 3.7, 5.5, 7.5, 11, 15, 22, 30, 37, 55, 75):
        for typ in ("CENTRIFUGAL INDUCED DRAFT", "CENTRIFUGAL FORCED DRAFT", "CENTRIFUGAL BACKWARD CURVED"):
            for moc in ("MS", "SS304", "FRP"):
                yield {"TYPE": typ, "POWER": f"{fmt(kw)} KW", "SPEED": "1440 RPM", "VOLTAGE": "415V 3PH", "MOC": moc}


@BLOWER.generator
def blowers():
    for size in ("1 IN", "1-1/2 IN", "2 IN", "2-1/2 IN", "3 IN", "4 IN", "5 IN", "6 IN", "8 IN", "10 IN"):
        for mbar in (300, 500, 700, 1000):
            for make in ("KAY", "EVEREST", "SWAM", "AERZEN"):
                yield {"TYPE": "TWIN LOBE ROOTS", "SIZE": size, "PRESSURE": f"{mbar} MBAR", "MAKE": make}
    for kw in (0.37, 0.75, 1.1, 2.2, 3, 4, 5.5, 7.5):
        for make in ("SIEMENS", "BUSCH", "EVEREST"):
            yield {"TYPE": "RING SIDE CHANNEL", "POWER": f"{fmt(kw)} KW", "MAKE": make}


DISC_SPRINGS_A = [(8, 4.2, 0.4), (10, 5.2, 0.5), (12.5, 6.2, 0.7), (14, 7.2, 0.8), (16, 8.2, 0.9), (18, 9.2, 1),
                  (20, 10.2, 1.1), (22.5, 11.2, 1.25), (25, 12.2, 1.5), (28, 14.2, 1.5), (31.5, 16.3, 1.75),
                  (35.5, 18.3, 2), (40, 20.4, 2.25), (45, 22.4, 2.5), (50, 25.4, 3), (56, 28.5, 3), (63, 31, 3.5),
                  (71, 36, 4), (80, 41, 5), (90, 46, 5), (100, 51, 6), (112, 57, 6), (125, 64, 8), (140, 72, 8),
                  (160, 82, 10), (180, 92, 10), (200, 102, 12), (225, 112, 12), (250, 127, 14)]


@SPRING.generator
def springs():
    wires = [0.5, 0.6, 0.8, 1, 1.2, 1.5, 1.6, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
    mocs = [("SPRING STEEL", "IS 4454 GR 2", "BLACK OXIDE"), ("SS302", "", ""), ("MUSIC WIRE", "ASTM A228", "ZINC PLATED")]
    for d in wires:
        for index in (6, 8, 10, 12):
            od = d * index
            for typ, mult in (("COMPRESSION", (1, 1.5, 2, 3, 4)), ("EXTENSION", (2, 3, 5)), ("TORSION 90 DEG", (1,))):
                if typ.startswith("TORSION") and d > 5:
                    continue
                for m in mult:
                    for moc, spec, finish in mocs:
                        yield {"TYPE": typ, "MOC": f"{moc} {spec}".strip(), "WIRE DIA": f"WIRE {fmt(d)} MM",
                               "SIZE": f"OD {fmt(od)} MM", "LENGTH": f"FREE LENGTH {fmt(round(od * m))} MM",
                               "FINISH": finish}
    for od, i, t in DISC_SPRINGS_A:
        for moc in ("50CRV4", "SS301", "INCONEL X750"):
            yield {"TYPE": "DISC BELLEVILLE", "MOC": moc, "SIZE": f"{fmt(od)} X {fmt(i)} X {fmt(t)} MM",
                   "STANDARD": "DIN 2093 GROUP A"}


PISTON_RODS = {32: 12, 40: 16, 50: 20, 63: 20, 80: 25, 100: 25, 125: 32, 160: 40, 200: 40}
HYD_RODS = {25: (12, 18), 32: (14, 22), 40: (18, 28), 50: (22, 36), 63: (28, 45), 80: (36, 56), 100: (45, 70),
            125: (56, 90), 160: (70, 110), 200: (90, 140)}


@CYLINDER.generator
def cylinders():
    strokes = (25, 50, 75, 100, 125, 150, 160, 200, 250, 300, 320, 400, 500, 600, 800, 1000)
    for bore, rod in PISTON_RODS.items():
        for stroke in strokes:
            for feature in ("DOUBLE ACTING MAGNETIC PISTON", "DOUBLE ACTING MAGNETIC PISTON THROUGH ROD"):
                for make in PNEUMATIC_MAKES:
                    yield {"TYPE": "PNEUMATIC PROFILE", "BORE": f"BORE {bore} MM", "ROD": f"ROD {rod} MM",
                           "STROKE": f"STROKE {stroke} MM", "PRESSURE": "10 BAR", "FEATURE": feature,
                           "STANDARD": "ISO 15552", "MAKE": make}
    for bore in (12, 16, 20, 25, 32, 40, 50, 63, 80, 100):
        for stroke in (5, 10, 15, 20, 25, 30, 40, 50, 80, 100):
            for make in PNEUMATIC_MAKES:
                yield {"TYPE": "PNEUMATIC COMPACT", "BORE": f"BORE {bore} MM", "STROKE": f"STROKE {stroke} MM",
                       "PRESSURE": "10 BAR", "FEATURE": "DOUBLE ACTING MAGNETIC PISTON", "STANDARD": "ISO 21287",
                       "MAKE": make}
    for bore in (8, 10, 12, 16, 20, 25):
        for stroke in (10, 25, 50, 75, 100, 125, 150, 200):
            for make in PNEUMATIC_MAKES:
                yield {"TYPE": "PNEUMATIC MINI ROUND", "BORE": f"BORE {bore} MM", "STROKE": f"STROKE {stroke} MM",
                       "PRESSURE": "10 BAR", "FEATURE": "DOUBLE ACTING", "STANDARD": "ISO 6432", "MAKE": make}
    for bore, rods in HYD_RODS.items():
        for rod in rods:
            for stroke in (50, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000):
                for mounting in ("FRONT FLANGE ME5", "REAR CLEVIS MP1", "FOOT MS2", "TRUNNION MT4"):
                    yield {"TYPE": "HYDRAULIC TIE ROD", "BORE": f"BORE {bore} MM", "ROD": f"ROD {rod} MM",
                           "STROKE": f"STROKE {stroke} MM", "MOUNTING": mounting, "PRESSURE": "160 BAR",
                           "STANDARD": "ISO 6020-2"}


@VALVE.generator(group=G_FP)
def fluid_power_valves():
    for typ in ("PNEUMATIC 3/2 SOLENOID", "PNEUMATIC 5/2 SOLENOID", "PNEUMATIC 5/3 SOLENOID CLOSED CENTRE",
                "PNEUMATIC 5/2 DOUBLE SOLENOID", "PNEUMATIC 5/2 PILOT OPERATED", "PNEUMATIC 5/2 HAND LEVER"):
        for size in ("1/8 IN", "1/4 IN", "3/8 IN", "1/2 IN", "3/4 IN", "1 IN"):
            coils = ("",) if "PILOT" in typ or "LEVER" in typ else ("24 VDC COIL", "230 VAC COIL", "110 VAC COIL")
            for coil in coils:
                yield {"TYPE": typ, "BODY": "AL BODY", "SIZE": size, "END": "BSP", "OPERATION": coil,
                       "STANDARD": "NAMUR" if size == "1/4 IN" else ""}
    for ng, cetop in (("NG6", "CETOP 3"), ("NG10", "CETOP 5"), ("NG16", "CETOP 7"), ("NG25", "CETOP 8")):
        for spool in ("4/3 CLOSED CENTRE", "4/3 OPEN CENTRE", "4/3 TANDEM CENTRE", "4/3 FLOAT CENTRE", "4/2 SPRING OFFSET"):
            for coil in ("24 VDC COIL", "230 VAC COIL"):
                yield {"TYPE": f"HYDRAULIC DIRECTIONAL CONTROL {spool}", "SIZE": ng, "RATING": "315 BAR",
                       "END": f"SUBPLATE {cetop}", "OPERATION": coil}
        for typ in ("HYDRAULIC PRESSURE RELIEF", "HYDRAULIC PRESSURE REDUCING", "HYDRAULIC FLOW CONTROL",
                    "HYDRAULIC PILOT OPERATED CHECK"):
            yield {"TYPE": typ, "SIZE": ng, "RATING": "315 BAR", "END": f"SUBPLATE {cetop}"}


PUSH_IN = [(4, "M5"), (4, "1/8"), (6, "1/8"), (6, "1/4"), (8, "1/8"), (8, "1/4"), (8, "3/8"), (10, "1/4"),
           (10, "3/8"), (10, "1/2"), (12, "1/4"), (12, "3/8"), (12, "1/2"), (16, "3/8"), (16, "1/2")]


@FITTING.generator
def fluid_power_fittings():
    for od, thread in PUSH_IN:
        for typ in ("PUSH IN MALE STRAIGHT", "PUSH IN MALE ELBOW", "PUSH IN MALE BRANCH TEE", "PUSH IN MALE RUN TEE"):
            for make in PNEUMATIC_MAKES[:4]:
                yield {"TYPE": typ, "MOC": "NICKEL PLATED BRASS", "SIZE": f"TUBE OD {od} MM X {thread} BSPT"
                       if thread != "M5" else f"TUBE OD {od} MM X M5", "MAKE": make}
    for od in (4, 6, 8, 10, 12, 14, 16):
        for typ in ("PUSH IN UNION STRAIGHT", "PUSH IN UNION ELBOW", "PUSH IN UNION TEE", "PUSH IN UNION Y",
                    "PUSH IN BULKHEAD UNION"):
            for make in PNEUMATIC_MAKES[:4]:
                yield {"TYPE": typ, "MOC": "POLYMER", "SIZE": f"TUBE OD {od} MM", "MAKE": make}
    bsp = ["1/4", "3/8", "1/2", "3/4", "1", "1-1/4"]
    jic = {"1/4": "7/16-20 JIC", "3/8": "9/16-18 JIC", "1/2": "3/4-16 JIC", "3/4": "1-1/16-12 JIC",
           "1": "1-5/16-12 JIC", "1-1/4": "1-5/8-12 JIC"}
    for i, a in enumerate(bsp):
        for b in bsp[max(0, i - 1): i + 2]:
            for typ in ("HYDRAULIC ADAPTER MALE STRAIGHT", "HYDRAULIC ADAPTER MALE 90 DEG ELBOW",
                        "HYDRAULIC ADAPTER MALE 45 DEG ELBOW", "HYDRAULIC ADAPTER MALE BRANCH TEE"):
                yield {"TYPE": typ, "MOC": "ZINC PLATED CS", "SIZE": f"{a} BSP X {jic[b]}", "RATING": "350 BAR",
                       "STANDARD": "ISO 8434-2"}
                yield {"TYPE": typ, "MOC": "SS316", "SIZE": f"{a} BSP X {jic[b]}", "RATING": "350 BAR",
                       "STANDARD": "ISO 8434-2"}
    for size in ("DN 6", "DN 8", "DN 10", "DN 12", "DN 16", "DN 19", "DN 25", "DN 31", "DN 38", "DN 51"):
        for end in ("BSP FEMALE SWIVEL", "JIC FEMALE SWIVEL", "ORFS FEMALE SWIVEL", "BSP MALE", "NPT MALE",
                    "SAE CODE 61 FLANGE", "SAE CODE 62 FLANGE"):
            for angle in ("STRAIGHT", "90 DEG"):
                yield {"TYPE": f"HYDRAULIC HOSE {angle}", "MOC": "ZINC PLATED CS", "SIZE": size, "END": end,
                       "STANDARD": "ISO 12151"}
    for size in ("1/4 IN", "3/8 IN", "1/2 IN", "3/4 IN", "1 IN"):
        for typ in ("QUICK RELEASE COUPLING PLUG", "QUICK RELEASE COUPLING SOCKET"):
            for moc in ("BRASS", "ZINC PLATED CS", "SS316"):
                yield {"TYPE": typ, "MOC": moc, "SIZE": size, "END": "BSP FEMALE", "STANDARD": "ISO 7241-A"}


@TUBE.generator(group=G_FP)
def pneumatic_tubes():
    for od, i in ((4, 2.5), (6, 4), (8, 5), (10, 6.5), (12, 8), (14, 10), (16, 12)):
        for moc in ("PU", "NYLON PA12", "PE"):
            for color in ("BLUE", "BLACK", "NATURAL", "RED"):
                for make in PNEUMATIC_MAKES[:4]:
                    yield {"TYPE": "PNEUMATIC", "MOC": moc, "OD": f"OD {od} MM", "ID": f"ID {fmt(i)} MM",
                           "COLOR": color, "MAKE": make}


@FILTER.generator
def fluid_power_filters():
    for port in ("1/8 IN", "1/4 IN", "3/8 IN", "1/2 IN", "3/4 IN", "1 IN"):
        for typ in ("AIR FILTER REGULATOR LUBRICATOR FRL", "AIR FILTER REGULATOR", "AIR FILTER", "AIR LUBRICATOR"):
            for micron in ("5 MICRON", "40 MICRON"):
                if typ == "AIR LUBRICATOR" and micron == "5 MICRON":
                    continue
                for make in PNEUMATIC_MAKES:
                    yield {"TYPE": typ, "MICRON": micron if typ != "AIR LUBRICATOR" else "", "PORT": f"{port} BSP",
                           "FEATURE": "WITH GAUGE AND AUTO DRAIN" if "REGULATOR" in typ else "", "MAKE": make}
    for typ, ports in (("HYDRAULIC SUCTION STRAINER", ("1/2 IN", "3/4 IN", "1 IN", "1-1/4 IN", "1-1/2 IN", "2 IN")),
                       ("HYDRAULIC RETURN LINE", ("1/2 IN", "3/4 IN", "1 IN", "1-1/4 IN", "1-1/2 IN", "2 IN")),
                       ("HYDRAULIC PRESSURE LINE", ("1/2 IN", "3/4 IN", "1 IN", "1-1/4 IN"))):
        strainer = "STRAINER" in typ
        media = "SS WIRE MESH" if strainer else "GLASS FIBRE"
        microns = ("74 MICRON", "149 MICRON") if strainer else ("3 MICRON", "10 MICRON", "25 MICRON")
        for port in ports:
            for micron in microns:
                for make in ("HYDAC", "PARKER", "DONALDSON", "PALL"):
                    yield {"TYPE": typ, "MEDIA": media, "MICRON": micron, "PORT": f"{port} BSP",
                           "RATING": "420 BAR" if "PRESSURE" in typ else "", "MAKE": make}
                    if not strainer:
                        yield {"TYPE": f"{typ} ELEMENT", "MEDIA": media, "MICRON": micron, "SIZE": f"FOR {port} HOUSING",
                               "MAKE": make}
