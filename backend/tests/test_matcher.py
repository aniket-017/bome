import pytest

from app.matcher import AUTO_THRESHOLD, score_candidate
from app.normalize import extract_attrs, normalize


def _score(line: str, cand: str) -> float:
    ln, cn = normalize(line), normalize(cand)
    return score_candidate(ln, extract_attrs(ln), cn, extract_attrs(cn))


def test_same_part_written_differently_scores_auto():
    assert _score(
        "Conc Red. A403 WP304 6\" x 4\" BW Sch 40",
        "Reducer Concentric SA-403 WP304 DN150 x DN100 BW B16.9 SCH 40",
    ) >= AUTO_THRESHOLD


@pytest.mark.parametrize(
    "wrong",
    [
        "Reducer Concentric SA-403 WP304 DN150 x DN80 BW B16.9 SCH 40",  # size
        "Reducer Concentric SA-403 WP304L DN150 x DN100 BW B16.9 SCH 40",  # grade
        "Reducer Concentric SA-403 WP304 DN150 x DN100 BW B16.9 SCH 80",  # schedule
        "Reducer Eccentric SA - 403 WP304 DN150 x DN100 BW B16.9 SCH 40",  # subtype
        "IBR Reducer Concentric SA-403 WP304 DN150 x DN100 BW B16.9 SCH 40",  # flag
    ],
)
def test_wrong_attribute_is_never_auto(wrong):
    line = "Conc Red. A403 WP304 6\" x 4\" BW Sch 40"
    right = "Reducer Concentric SA-403 WP304 DN150 x DN100 BW B16.9 SCH 40"
    assert _score(line, wrong) < AUTO_THRESHOLD
    assert _score(line, wrong) < _score(line, right)


def test_bolt_length_mismatch_is_penalized():
    line = "Hex bolt IS 1367 Gr 8.8 M24 x 230 HDG full thread"
    assert _score(line, "HEX BOLT FULL THRD IS 1367 GR 8.8 M24 x 230 mm HDG") >= AUTO_THRESHOLD
    assert _score(line, "HEX BOLT FULL THRD IS 1367 GR 8.8 M24 x 120 mm HDG") < 80


def test_matching_accuracy_on_messy_testset():
    pytest.importorskip("psycopg")
    try:
        from scripts.eval_matching import evaluate

        summary = evaluate()
    except Exception as exc:  # database not reachable in this environment
        pytest.skip(f"database unavailable: {exc}")
    assert summary["auto_precision"] >= 0.9
    assert summary["top5_recall"] >= 0.9
