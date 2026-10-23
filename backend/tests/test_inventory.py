import uuid
from decimal import Decimal

import pytest

from app.inventory_service import weighted_avg
from tests.conftest import requires_erp_db


def test_weighted_average_cost():
    assert weighted_avg(Decimal(0), None, Decimal(10), Decimal(100)) == Decimal(100)
    assert weighted_avg(Decimal(10), Decimal(100), Decimal(10), Decimal(120)) == Decimal(110)
    assert weighted_avg(Decimal(30), Decimal(10), Decimal(10), Decimal(30)) == Decimal(15)
    # an empty (or oversold) stock carries no value forward: the receipt sets the cost
    assert weighted_avg(Decimal(-2), Decimal(50), Decimal(5), Decimal(80)) == Decimal(80)


def _new_part(client, description: str, **extra) -> dict:
    r = client.post("/api/parts", json={"item_no": f"PYT-{uuid.uuid4().hex[:10]}", "description": description, **extra})
    assert r.status_code == 201, r.text
    return r.json()


@requires_erp_db
def test_grn_issue_and_ledger(tx_client):
    part = _new_part(tx_client, "Ball bearing 6205 2RS pytest", standard_cost=90)
    pid = part["id"]

    r = tx_client.post("/api/inventory/grns", json={"supplier": "ACME", "lines": [{"part_id": pid, "qty": 10, "unit_cost": 100}]})
    assert r.status_code == 201, r.text
    grn = r.json()
    assert grn["grn_no"].startswith("GRN-") and grn["total_value"] == 1000
    tx_client.post("/api/inventory/grns", json={"lines": [{"part_id": pid, "qty": 10, "unit_cost": 120}]})
    p = tx_client.get(f"/api/parts/{pid}").json()
    assert (p["in_stock"], p["avg_cost"]) == (20, 110)

    mr = tx_client.post("/api/inventory/mrs", json={"department": "Fabrication",
                                                     "lines": [{"part_id": pid, "qty_requested": 15}]}).json()
    assert mr["status"] == "open" and mr["mr_no"].startswith("MR-")
    line_id = mr["lines"][0]["id"]
    r = tx_client.post(f"/api/inventory/mrs/{mr['id']}/issue", json={"lines": [{"line_id": line_id, "qty": 5}]})
    assert r.status_code == 200 and r.json()["status"] == "partial"
    r = tx_client.post(f"/api/inventory/mrs/{mr['id']}/issue", json={})
    assert r.json()["status"] == "issued" and r.json()["lines"][0]["qty_issued"] == 15
    assert tx_client.get(f"/api/parts/{pid}").json()["in_stock"] == 5
    assert tx_client.post(f"/api/inventory/mrs/{mr['id']}/issue", json={}).status_code == 422

    ledger = tx_client.get(f"/api/inventory/ledger/{pid}").json()
    assert [e["txn_type"] for e in ledger] == ["ISSUE", "ISSUE", "GRN", "GRN"]
    assert ledger[0]["balance"] == 5 and ledger[0]["ref_no"] == mr["mr_no"]
    assert ledger[-1]["ref_no"] == grn["grn_no"]


@requires_erp_db
def test_over_issue_is_rejected(tx_client):
    pid = _new_part(tx_client, "Gate valve CL150 DN 100 pytest", opening_stock=3, standard_cost=500)["id"]
    mr = tx_client.post("/api/inventory/mrs", json={"lines": [{"part_id": pid, "qty_requested": 4}]}).json()
    r = tx_client.post(f"/api/inventory/mrs/{mr['id']}/issue", json={})
    assert r.status_code == 409 and "Insufficient stock" in r.json()["detail"]
    assert tx_client.get(f"/api/parts/{pid}").json()["in_stock"] == 3
    r = tx_client.post(f"/api/inventory/mrs/{mr['id']}/issue",
                       json={"lines": [{"line_id": mr["lines"][0]["id"], "qty": 5}]})
    assert r.status_code == 422
    assert [e["txn_type"] for e in tx_client.get(f"/api/inventory/ledger/{pid}").json()] == ["OPENING"]


@requires_erp_db
def test_mr_from_bom_copies_matched_lines_and_costing(tx_client):
    part = _new_part(tx_client, "Hex bolt IS 1367 Gr 8.8 M24 x 100 HDG pytest", standard_cost=25)
    bom = tx_client.post("/api/boms", json={"name": "pytest frame", "auto_match": False, "lines": [
        {"raw_description": "bolt", "qty": 4, "matched_part_id": part["id"]},
        {"raw_description": "Lifting lug as per drawing", "qty": 2},
    ]}).json()

    r = tx_client.post(f"/api/inventory/mrs/from-bom/{bom['id']}", json={"batch_qty": 20})
    assert r.status_code == 201, r.text
    mr = r.json()
    assert mr["bom_id"] == bom["id"]
    assert [(l["part_id"], l["qty_requested"]) for l in mr["lines"]] == [(part["id"], 80)]

    costing = tx_client.get(f"/api/boms/{bom['id']}/costing", params={"batch_qty": 20}).json()
    assert costing["material_cost"] == pytest.approx(2000)
    assert costing["unmatched_count"] == 1 and costing["costed_count"] == 1
    export = tx_client.get(f"/api/boms/{bom['id']}/costing/export", params={"batch_qty": 20})
    assert export.status_code == 200 and "costing" in export.headers["content-disposition"]
