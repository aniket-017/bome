import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { PartAutocomplete } from "../components/PartAutocomplete";
import { errorText, money, qty, unitCost } from "../format";
import type { Part } from "../types";

interface Row {
  key: number;
  part: Part | null;
  qty: string;
  unitCost: string;
}

let nextKey = 1;
const blankRow = (): Row => ({ key: nextKey++, part: null, qty: "", unitCost: "" });

export function GrnFormPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [supplier, setSupplier] = useState("");
  const [receivedOn, setReceivedOn] = useState(new Date().toISOString().slice(0, 10));
  const [remarks, setRemarks] = useState("");
  const [rows, setRows] = useState<Row[]>([blankRow()]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = (key: number, patch: Partial<Row>) => setRows((rs) => rs.map((r) => (r.key === key ? { ...r, ...patch } : r)));
  const pick = (key: number, part: Part) => {
    const cost = unitCost(part);
    update(key, { part, unitCost: cost == null ? "" : String(cost) });
  };

  const valid = rows.filter((r) => r.part && Number(r.qty) > 0 && r.unitCost !== "" && Number(r.unitCost) >= 0);
  const total = valid.reduce((s, r) => s + Number(r.qty) * Number(r.unitCost), 0);

  const submit = async () => {
    setSaving(true);
    setError(null);
    try {
      const grn = await api.createGrn({
        supplier: supplier.trim() || null,
        received_on: receivedOn || null,
        remarks: remarks.trim() || null,
        lines: valid.map((r) => ({ part_id: r.part!.id, qty: Number(r.qty), unit_cost: Number(r.unitCost) })),
      });
      await qc.invalidateQueries({ queryKey: ["grns"] });
      void qc.invalidateQueries({ queryKey: ["stock"] });
      navigate(`/inventory/grn/${grn.id}`);
    } catch (e) {
      setError(errorText(e));
      setSaving(false);
    }
  };

  return (
    <div className="page wide">
      <header className="page-header">
        <div>
          <div className="muted">Inventory</div>
          <h1>New GRN</h1>
          <div className="muted">Record materials received from a supplier.</div>
        </div>
      </header>

      <section className="card">
        <div className="form-row">
          <div>
            <label>Supplier</label>
            <input type="text" value={supplier} onChange={(e) => setSupplier(e.target.value)} maxLength={200} />
          </div>
          <div>
            <label>Received on</label>
            <input type="date" value={receivedOn} onChange={(e) => setReceivedOn(e.target.value)} />
          </div>
          <div>
            <label>Remarks</label>
            <input type="text" value={remarks} onChange={(e) => setRemarks(e.target.value)} placeholder="PO / challan number" />
          </div>
        </div>
      </section>

      <section className="card">
        <h2>Items received</h2>
        <table className="grid line-grid">
          <thead>
            <tr>
              <th className="num">#</th>
              <th>Item</th>
              <th className="num">In stock</th>
              <th className="num">Qty received</th>
              <th>UoM</th>
              <th className="num">Unit cost (INR)</th>
              <th className="num">Value</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={r.key}>
                <td className="num">{i + 1}</td>
                <td>
                  <PartAutocomplete compact onSelect={(p) => pick(r.key, p)} placeholder="Search item..." />
                  {r.part && <div className="muted small mono">{r.part.item_no}</div>}
                </td>
                <td className="num">{r.part ? qty(r.part.in_stock ?? 0) : ""}</td>
                <td className="num">
                  <input type="number" min={0} className="qty-input" value={r.qty} onChange={(e) => update(r.key, { qty: e.target.value })} />
                </td>
                <td>{r.part?.uom_group}</td>
                <td className="num">
                  <input type="number" min={0} step="0.01" style={{ width: 110 }} value={r.unitCost}
                         onChange={(e) => update(r.key, { unitCost: e.target.value })} />
                </td>
                <td className="num">{r.qty && r.unitCost ? money(Number(r.qty) * Number(r.unitCost)) : ""}</td>
                <td>
                  {rows.length > 1 && (
                    <button className="link danger" onClick={() => setRows((rs) => rs.filter((x) => x.key !== r.key))}>
                      Remove
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={6} className="num">
                Total
              </td>
              <td className="num">{money(total)}</td>
              <td />
            </tr>
          </tfoot>
        </table>
        <div className="actions-row">
          <button onClick={() => setRows((rs) => [...rs, blankRow()])}>+ Add line</button>
        </div>
      </section>

      {error && <div className="error">{error}</div>}
      <div className="actions-row">
        <button className="primary" disabled={saving || valid.length === 0} onClick={() => void submit()}>
          {saving ? "Posting..." : `Post GRN (${valid.length} line${valid.length === 1 ? "" : "s"})`}
        </button>
        <button onClick={() => navigate("/inventory/grn")}>Cancel</button>
      </div>
    </div>
  );
}
