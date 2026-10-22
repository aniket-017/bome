import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Part } from "../types";
import { PartAutocomplete } from "./PartAutocomplete";

interface Row {
  key: number;
  description: string;
  part: Part | null;
  qty: string;
  uom: string;
}

let nextKey = 1;
const emptyRow = (): Row => ({ key: nextKey++, description: "", part: null, qty: "", uom: "NOS" });

/** Parses rows pasted from Excel: "description [TAB qty [TAB uom]]" per line. */
function parsePasted(text: string): Row[] {
  return text
    .split(/\r?\n/)
    .map((l) => l.split("\t").map((c) => c.trim()))
    .filter((cells) => cells[0])
    .map((cells) => ({ ...emptyRow(), description: cells[0], qty: cells[1] ?? "", uom: cells[2] || "NOS" }));
}

export function ManualBomGrid() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [project, setProject] = useState("");
  const [rows, setRows] = useState<Row[]>([emptyRow(), emptyRow(), emptyRow()]);
  const [paste, setPaste] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = (key: number, patch: Partial<Row>) =>
    setRows((rs) => rs.map((r) => (r.key === key ? { ...r, ...patch } : r)));

  const filled = rows.filter((r) => r.description.trim() || r.part);

  const save = async () => {
    if (!name.trim()) {
      setError("Give the BOM a name");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const bom = await api.createBom({
        name: name.trim(),
        project: project.trim() || null,
        lines: filled.map((r, i) => ({
          line_no: i + 1,
          raw_description: r.part ? r.part.description : r.description.trim(),
          raw_item_no: r.part ? r.part.item_no : null,
          matched_part_id: r.part?.id ?? null,
          qty: r.qty === "" ? null : Number(r.qty),
          uom: r.uom || null,
        })),
      });
      navigate(`/boms/${bom.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="form-row">
        <div>
          <label>BOM name</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label>Project (optional)</label>
          <input type="text" value={project} onChange={(e) => setProject(e.target.value)} />
        </div>
      </div>

      <p className="muted">
        Type in the description box: pick a part from the dropdown to link it directly, or leave your own text and it
        will be matched automatically when you save.
      </p>
      <table className="grid manual-grid">
        <thead>
          <tr>
            <th style={{ width: 40 }}>#</th>
            <th>Description</th>
            <th style={{ width: 110 }}>Linked part</th>
            <th style={{ width: 90 }}>Qty</th>
            <th style={{ width: 90 }}>Unit</th>
            <th style={{ width: 40 }} />
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.key}>
              <td className="muted">{i + 1}</td>
              <td>
                <PartAutocomplete
                  compact
                  initialQuery={r.description}
                  placeholder="Type description..."
                  onQueryChange={(q) => update(r.key, { description: q, part: null })}
                  onSelect={(p) => update(r.key, { description: p.description, part: p })}
                />
              </td>
              <td className="mono">{r.part ? r.part.item_no : <span className="muted">auto</span>}</td>
              <td>
                <input type="number" value={r.qty} onChange={(e) => update(r.key, { qty: e.target.value })} />
              </td>
              <td>
                <input type="text" value={r.uom} onChange={(e) => update(r.key, { uom: e.target.value })} />
              </td>
              <td>
                <button
                  className="link danger"
                  title="Remove line"
                  onClick={() => setRows((rs) => (rs.length > 1 ? rs.filter((x) => x.key !== r.key) : rs))}
                >
                  x
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="actions-row">
        <button onClick={() => setRows((rs) => [...rs, emptyRow()])}>+ Add line</button>
      </div>

      <details className="paste-box">
        <summary>Paste lines from Excel</summary>
        <p className="muted">Copy columns Description, Qty, Unit from Excel and paste below.</p>
        <textarea rows={5} value={paste} onChange={(e) => setPaste(e.target.value)} />
        <button
          disabled={!paste.trim()}
          onClick={() => {
            const parsed = parsePasted(paste);
            setRows((rs) => [...rs.filter((r) => r.description.trim() || r.part), ...parsed]);
            setPaste("");
          }}
        >
          Add pasted lines
        </button>
      </details>

      {error && <div className="error">{error}</div>}
      <div className="actions-row">
        <button className="primary" disabled={busy || filled.length === 0} onClick={save}>
          {busy ? "Saving and matching..." : `Save BOM (${filled.length} lines)`}
        </button>
      </div>
    </div>
  );
}
