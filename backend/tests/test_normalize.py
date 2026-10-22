import pytest

from app.normalize import CATALOG_NOUNS, extract_attrs, infer_noun, normalize


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            "IBR Reducer Eccentric SA - 403 WP317 DN350 x DN300 BW B16.9 SCH 80S",
            "IBR REDUCER ECCENTRIC SA403 317 DN350 X DN300 BW B16.9 SCH80S",
        ),
        (
            "ELBOW SA-403-GR.316 LR 90 DEG BW B16.9 DN 650 SCH 20",
            "ELBOW SA403 316 LR 90DEG BW B16.9 DN650 SCH20",
        ),
        ("END CAP SA-403WP317 BW B16.9 DN 125 SCH 40", "END CAP SA403 317 BW B16.9 DN125 SCH40"),
        ("Reducer Eccentric SA--234 GR WPB DN450 x DN400 BW B16.9 SCH 20",
         "REDUCER ECCENTRIC SA234 WPB DN450 X DN400 BW B16.9 SCH20"),
        ("PLUG SA-182-F-316L", "PLUG SA182 316L"),
        ("IBR FLANGE WNRF SA-182 GR F304L SCH 80S CL 300 B16.5 DN 400",
         "IBR FLANGE WN RF SA182 304L SCH80S CL300 B16.5 DN400"),
        ("HEX BOLT FULL THRD IS 1367 GR 4.6 M39 x 220 mm", "HEX BOLT FULL THRD IS1367 4.6 M39 X 220MM"),
        ("N+B+W SA-193 GR B8/SA-194 Gr.8- 3/3\" UNC X 260 mm", "N+B+W SA193 B8 SA194 8 3/3\" UNC X 260MM"),
        ("S+B+W SA-193 GR B7/SA 194 GR 2H- 1+1/8\" UN8 X 330 MM HDG",
         "S+B+W SA193 B7 SA194 2H 1+1/8\" UN8 X 330MM HDG"),
        ("GASKET SPW WITH GRAPHYTE FILLER DN  750 CLASS 300 x 4.5 THK SS 316L IR/ CS OR",
         "GASKET SPW GRAPHITE FILLER DN750 CL300 X 4.5 THK SS 316L IR CS OR"),
        ("ANGLE SA- 240 TYPE 304 SIZE- 100x100x10 mm", "ANGLE SA240 304 SIZE 100 X 100 X 10MM"),
        ("PIPE SA-312 TP317L DN 90  SCH 40S", "PIPE SA312 317L DN90 SCH40S"),
        ("FULL Coupling SA-182-F-316L DN 6 SW B16.11  NPTCL 6000",
         "FULL COUPLING SA182 316L DN6 SW B16.11 NPT CL6000"),
        ("PLUG SA-182-F-316L DN 65 SW B16.11  BSPTCL 9000", "PLUG SA182 316L DN65 SW B16.11 BSPT CL9000"),
        ("ELBOW IS:1239 90 DEG DN 25", "ELBOW IS1239 90DEG DN25"),
        ("PLATE IS-2062 E250 BO THK- 80 mm", "PLATE IS2062 E250 BO THK 80MM"),
        ("A3 PAPER RIM 70 GSM METRIX BUILT BRAND", "A3 PAPER RIM 70 GSM METRIX BUILT BRAND"),
        ("GARBAGE BAG - BLACK-30X50", "GARBAGE BAG BLACK 30 X 50"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_real_samples(raw, expected):
    assert normalize(raw) == expected


@pytest.mark.parametrize(
    "variants",
    [
        ["SA-403 WP304", "SA - 403 WP304", "SA-403-GR.304", "SA-403-GR-304", "SA403 GR 304", "ASTM A403 WP304",
         "A 403 TP304"],
        ["SA-234 GR WPB", "SA--234 GR WPB", "SA-234 Gr. WPB", "A234 WPB"],
        ["DN 100", "DN100", "DN-100", "100 NB", "100NB", "NPS 4\"", "NPS 4"],
        ["SCH 40S", "SCH40S", "SCHEDULE 40S", "SCH-40S"],
        ["CL 150", "CLASS 150", "CL-150", "150#", "#150", "150 LB", "CLASS-150"],
        ["90 DEG", "90DEG", "90°", "90 DEGREE"],
        ["WNRF", "WN RF", "WN-RF", "WELD NECK RAISED FACE"],
        ["M20 x 310 mm", "M 20 X 310 MM", "M20X310MM", "M20*310 mm"],
        ["1+1/8\"", "1-1/8\"", "1 1/8\"", "1-1/8''", "1+1/8 INCH"],
        ["LONG RADIUS", "LR"],
        ["GRAPHYTE", "GRAPHITE"],
    ],
)
def test_variants_collapse(variants):
    normed = {normalize(v) for v in variants}
    assert len(normed) == 1, normed


def test_inch_sizes_on_piping_become_dn():
    assert normalize('4" ELBOW 90 DEG SCH 40') == "DN100 ELBOW 90DEG SCH40"
    assert normalize('REDUCER CONC 6" X 4"') == "REDUCER CONCENTRIC DN150 X DN100"
    assert normalize('CONC RED 6" X DN40') == "CONCENTRIC REDUCER DN150 X DN40"
    assert normalize('ECC RED DN200 x 4" SW') == "ECCENTRIC REDUCER DN200 X DN100 SW"
    assert normalize('BOLT SA-193 GR B7-1" UNC X 50 MM') == 'BOLT SA193 B7 1" UNC X 50MM'


def test_non_ascii_junk_is_dropped():
    assert normalize("ELBOW SA-105 \ufffd\xa045 DEG SW B16.11 DN 300CL 3000") == "ELBOW SA105 45DEG SW B16.11 DN300 CL3000"


def test_reducer_dn_shorthand():
    assert normalize("REDUCER CONC DN125 X 80 SCH 40") == "REDUCER CONCENTRIC DN125 X DN80 SCH40"


def test_word_prefixes_are_not_mangled():
    assert normalize("GRINDING WHEEL 7\"") == 'GRINDING WHEEL 7"'
    assert normalize("GRAPHITE") == "GRAPHITE"
    assert normalize("CLASS ROOM") == "CLASS ROOM"


def test_extract_attrs_fitting():
    attrs = extract_attrs(normalize("IBR ELBOW SA-403-GR-317L SR 90 DEG BW B16.9 DN 125 SCH 100"))
    assert attrs["ptype"] == "ELBOW"
    assert attrs["dn"] == ["125"]
    assert attrs["sch"] == ["100"]
    assert attrs["deg"] == ["90"]
    assert attrs["spec"] == ["SA403"]
    assert attrs["grade"] == ["317L"]
    assert attrs["flags"] == ["IBR"]
    assert "SR" in attrs["subtype"] and "BW" in attrs["subtype"]


def test_extract_attrs_fastener():
    attrs = extract_attrs(normalize("S+B+W SA-193 GR B7/SA 194 GR 2H-1\" UNC X 370 mm"))
    assert attrs["ptype"] == "S+B+W"
    assert attrs["grade"] == ["2H", "B7"]
    assert attrs["inch"] == ["1"]
    assert attrs["mm"] == ["370"]
    assert infer_noun(attrs) == "STUD"


def test_extract_attrs_metric_bolt_and_property_class():
    attrs = extract_attrs(normalize("HEX BOLT FULL THRD IS 1367 GR 8.8 M24 x 230 mm HDG"))
    assert attrs["m"] == ["24"]
    assert attrs["grade"] == ["8.8"]
    assert attrs["flags"] == ["HDG", "THRD"]


def test_bolt_length_without_mm_unit():
    assert extract_attrs(normalize("Hex bolt IS 1367 Gr 8.8 M24 x 230 HDG"))["mm"] == ["230"]
    assert extract_attrs(normalize('STUD A193 B7 1" X 370'))["mm"] == ["370"]
    assert extract_attrs(normalize("Plate Is-2062 E250 Br Thk- 75 Be"))["mm"] == ["75"]
    assert extract_attrs(normalize("PLATE IS-2062 E250 BR THK- 75 mm"))["mm"] == ["75"]
    assert extract_attrs(normalize("FLAT IS-2062 E250 BO THK- 32 x 8 mm"))["mm"] == ["8"]


def test_bare_lengths_get_mm_and_are_not_grades():
    assert normalize("Stud full thread A193 B7 M20 x 310") == "STUD FULL THRD SA193 B7 M20 X 310MM"
    assert normalize("Stud full thread A193 B7 M20 x 310") == normalize("STUD FULL THRD SA-193 GR B7- M20 x 310 mm")
    assert normalize("Plate Is-2062 E250 Br Thk- 75") == "PLATE IS2062 E250BR THK 75MM"
    assert normalize("FLAT IS-2062 E250 BO THK- 32 x 8 mm") == "FLAT IS2062 E250 BO THK 32 X 8MM"
    assert extract_attrs(normalize("Stud A193 B7 M20 x 310"))["grade"] == ["B7"]


def test_ft_means_full_thread_only_for_fasteners():
    assert normalize("STUD FT IS 1367 Gr 8.8 M42 x 500 HDG") == "STUD FULL THRD IS1367 8.8 M42 X 500MM HDG"
    assert normalize("HOSE 10 FT") == "HOSE 10 FT"


def test_spiral_wound_is_spw():
    assert normalize("Spiral wound gasket") == "SPW GASKET"


def test_extract_attrs_reducer_and_flange():
    attrs = extract_attrs(normalize("Reducer Concentric SA-403 WP316L DN125 x DN80 BW B16.9 SCH 80"))
    assert attrs["dn"] == ["125", "80"]
    assert attrs["subtype"] == ["BW", "CONCENTRIC"]
    f = extract_attrs(normalize("FLANGE SORF SA-182 GR F316 CL 300 B16.47 DN 850"))
    assert f["cl"] == ["300"]
    assert f["subtype"] == ["RF", "SO"]
    assert infer_noun(f) == "FLANGE"


def test_product_type_is_the_first_noun_including_multi_word_nouns():
    assert extract_attrs(normalize("OIL SEAL TC NBR 30 X 47 X 7 MM"))["ptype"] == "OIL SEAL"
    assert extract_attrs(normalize("BEARING BALL DEEP GROOVE 6205 ZZ SKF"))["ptype"] == "BEARING"
    assert extract_attrs(normalize("6205 ZZ BEARING SKF"))["ptype"] == "BEARING"
    assert infer_noun(extract_attrs(normalize("O-Ring NBR 70 ID 20 X CS 2"))) == "O-RING"
    assert infer_noun(extract_attrs(normalize("SPECTACLE BLIND CL 150 DN 100"))) == "SPECTACLE BLIND"


def test_product_type_of_english_compounds_is_the_head_noun():
    assert extract_attrs(normalize("SPRING WASHER M12"))["ptype"] == "WASHER"
    assert extract_attrs(normalize("GEAR PUMP 10 CC"))["ptype"] == "PUMP"
    assert extract_attrs(normalize('PLUG VALVE 2" CL150'))["ptype"] == "VALVE"
    assert extract_attrs(normalize("WORM GEAR BOX 20:1"))["ptype"] == "GEARBOX"
    assert extract_attrs(normalize("VALVE PLUG SS DN 50 CL 150"))["ptype"] == "VALVE"
    assert extract_attrs(normalize("ANGLE PLATE 75X75X6 THK. IS 2062"))["ptype"] == "ANGLE"


def test_product_type_aliases():
    assert extract_attrs(normalize('WELDOLET 6" X 2" SCH 40'))["ptype"] == "OLET"
    assert extract_attrs(normalize('SOCKET 1/2" SW 3000#'))["ptype"] == "COUPLING"
    assert extract_attrs(normalize("INDUSTRIAL SOCKET 16A 3P IP67"))["ptype"] == "SOCKET"
    assert extract_attrs(normalize("TEE UNEQUAL DN 100 X DN 50"))["subtype"] == ["REDUCING"]


def test_mixed_dn_and_inch_branch_sizes():
    assert extract_attrs(normalize('WELDOLET 5" X 1-1/2" SCH 80S'))["dn"] == ["125", "40"]
    assert extract_attrs(normalize('SWAGE DN40 X 1-1/4" SCH 80S TBE'))["dn"] == ["32", "40"]
    assert extract_attrs(normalize('SPECTACLE BLIND RTJ A105 24" 600 LB'))["dn"] == ["600"]


def test_units_and_steel_grades_are_written_one_way():
    assert normalize("MOTOR 7.5kW 4 POLE") == normalize("MOTOR 7.5 KW 4 POLE")
    assert normalize("CABLE 4C 16 sq.mm") == normalize("CABLE 4C 16 SQ MM")
    assert normalize("BEAM IS 2062 E250 A ISMB 200") == normalize("BEAM IS2062 E250A ISMB 200")


def test_inch_written_as_in():
    assert normalize("VALVE NEEDLE SS316 1/2 IN NPT") == normalize('NEEDLE VALVE SS316 1/2" NPT').replace(
        "NEEDLE VALVE", "VALVE NEEDLE")
    assert extract_attrs(normalize("VALVE BALL 1-1/2 IN"))["dn"] == ["40"]
