import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { PartAutocomplete } from "../components/PartAutocomplete";
import { errorText, qty } from "../format";
import type { Mr, Part } from "../types";

interface Row {
  key: number;
  part: Part | null;
  qty: string;
}

let nextKey = 1;
const blankRow = (): Row => ({ key: nextKey++, part: null, qty: "" });

export function MrFormPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [params] = useSearchParams();
  const presetBom = params.get("bom") ?? "";
  const [source, setSource] = useState<"bom" | "manual">(presetBom ? "bom" : "manual");
  const [department, setDepartment] = useState("");
  const [jobRef, setJobRef] = useState("");
  const [remarks, setRemarks] = useState("");
  const [bomId, setBomId] = useState(presetBom);
  const [batchQty, setBatchQty] = useState("1");
  const [rows, setRows] = useState<Row[]>([blankRow()]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const boms = useQuery({ queryKey: ["boms"], queryFn: api.listBoms, enabled: source === "bom" });

  const update = (key: number, patch: Partial<Row>) => setRows((rs) => rs.map((r) => (r.key === key ? { ...r, ...patch } : r)));
  const valid = rows.filter((r) => r.part && Number(r.qty) > 0);
  const canSubmit = source === "bom" ? !!bomId && Number(batchQty) > 0 : valid.length > 0;

  const submit = async () => {
    setSaving(true);
    setError(null);
    try {
      let mr: Mr;
      if (source === "bom") {
        mr = await api.mrFromBom(Number(bomId), {
          batch_qty: Number(batchQty),
          department: department.trim() || null,
          job_ref: jobRef.trim() || null,
        });
      } else {
        mr = await api.createMr({
          department: department.trim() || null,
          job_ref: jobRef.trim() || null,
          remarks: remarks.trim() || null,
          lines: valid.map((r) => ({ part_id: r.part!.id, qty_requested: Number(r.qty) })),
        });
      }
      await qc.invalidateQueries({ queryKey: ["mrs"] });
      navigate(`/inventory/mr/${mr.id}`);
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
          <h1>New Material Requisition</h1>
          <div className="muted">Request materials for a job or department; issue them from the requisition afterwards.</div>
        </div>
      </header>

      <section className="card">
        <div className="form-row">
          <div>
            <label>Department</label>
            <input type="text" value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="Fabrication, Assembly..." />
          </div>
          <div>
            <label>Job / reference</label>
            <input type="text" value={jobRef} onChange={(e) => setJobRef(e.target.value)}
                   placeholder={source === "bom" ? "Defaults to the BOM project" : "Job number"} />
          </div>
          {source === "manual" && (
            <div>
              <label>Remarks</label>
              <input type="text" value={remarks} onChange={(e) => setRemarks(e.target.value)} />
            </div>
          )}
        </div>
      </section>

      <div className="tabs">
        <button className={`tab ${source === "bom" ? "active" : ""}`} onClick={() => setSource("bom")}>
          From a BOM
        </button>
        <button className={`tab ${source === "manual" ? "active" : ""}`} onClick={() => setSource("manual")}>
          Enter items
        </button>
      </div>
      <section className="card">
        {source === "bom" ? (
          <div className="form-row">
            <div>
              <label>BOM</label>
              <select value={bomId} onChange={(e) => setBomId(e.target.value)}>
                <option value="">Select a BOM...</option>
                {(boms.data ?? []).map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                    {b.project ? ` (${b.project})` : ""} · {b.line_count} lines
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label>Batch quantity (assemblies)</label>
              <input type="number" min={1} value={batchQty} onChange={(e) => setBatchQty(e.target.value)} />
            </div>
            <p className="muted small" style={{ gridColumn: "1 / -1", margin: 0 }}>
              One requisition line per BOM line that is linked to an item, with quantity x batch. Unlinked lines are skipped.
            </p>
          </div>
        ) : (
          <>
            <table className="grid line-grid">
              <thead>
                <tr>
                  <th className="num">#</th>
                  <th>Item</th>
                  <th className="num">In stock</th>
                  <th className="num">Qty required</th>
                  <th>UoM</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={r.key}>
                    <td className="num">{i + 1}</td>
                    <td>
                      <PartAutocomplete compact onSelect={(p) => update(r.key, { part: p })} placeholder="Search item..." />
                      {r.part && <div className="muted small mono">{r.part.item_no}</div>}
                    </td>
                    <td className="num">{r.part ? qty(r.part.in_stock ?? 0) : ""}</td>
                    <td className="num">
                      <input type="number" min={0} className="qty-input" value={r.qty} onChange={(e) => update(r.key, { qty: e.target.value })} />
                    </td>
                    <td>{r.part?.uom_group}</td>
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
            </table>
            <div className="actions-row">
              <button onClick={() => setRows((rs) => [...rs, blankRow()])}>+ Add line</button>
            </div>
          </>
        )}
      </section>

      {error && <div className="error">{error}</div>}
      <div className="actions-row">
        <button className="primary" disabled={saving || !canSubmit} onClick={() => void submit()}>
          {saving ? "Creating..." : "Create MR"}
        </button>
        <button onClick={() => navigate("/inventory/mr")}>Cancel</button>
      </div>
    </div>
  );
}
