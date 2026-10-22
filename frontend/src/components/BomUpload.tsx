import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { ColumnField, UploadPreview } from "../types";

const FIELD_LABELS: Record<ColumnField, string> = {
  line_no: "Line / Sr. No.",
  item_no: "Item number",
  description: "Description",
  qty: "Quantity",
  uom: "Unit",
};
const FIELDS = Object.keys(FIELD_LABELS) as ColumnField[];

export function BomUpload() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<UploadPreview | null>(null);
  const [mapping, setMapping] = useState<Partial<Record<ColumnField, number>>>({});
  const [name, setName] = useState("");
  const [project, setProject] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const loadPreview = async (f: File, sheet?: string, headerRow?: number) => {
    setBusy("Reading file...");
    setError(null);
    try {
      const p = await api.previewUpload(f, sheet, headerRow);
      setPreview(p);
      setMapping(p.suggested_mapping);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };

  const pickFile = (f: File | undefined) => {
    if (!f) return;
    setFile(f);
    setName(f.name.replace(/\.[^.]+$/, ""));
    void loadPreview(f);
  };

  const submit = async () => {
    if (!file || !preview) return;
    setBusy(`Matching ${preview.total_rows} lines against the parts master...`);
    setError(null);
    try {
      const bom = await api.uploadBom(file, {
        name: name.trim() || file.name,
        project: project.trim() || undefined,
        sheet: preview.sheet,
        header_row: preview.header_row,
        mapping,
      });
      navigate(`/boms/${bom.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setBusy(null);
    }
  };

  const mappedCols = new Map(Object.entries(mapping).map(([f, i]) => [i, f as ColumnField]));
  const canSubmit = !!preview && (mapping.description !== undefined || mapping.item_no !== undefined) && !busy;

  return (
    <div>
      <label
        className={`dropzone ${dragOver ? "over" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          pickFile(e.dataTransfer.files[0]);
        }}
      >
        <input
          type="file"
          accept=".xlsx,.xlsm,.xls,.xlsb,.ods,.csv"
          onChange={(e) => pickFile(e.target.files?.[0])}
          hidden
        />
        {file ? (
          <span>
            <strong>{file.name}</strong> <span className="muted">(click to choose another file)</span>
          </span>
        ) : (
          <span>Drop a BOM Excel / CSV file here, or click to choose</span>
        )}
      </label>

      {busy && (
        <p className="busy">
          <span className="spinner" /> {busy}
        </p>
      )}
      {error && <div className="error">{error}</div>}

      {preview && file && (
        <>
          <div className="form-row">
            <div>
              <label>BOM name</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
              <label>Project (optional)</label>
              <input type="text" value={project} onChange={(e) => setProject(e.target.value)} />
            </div>
            {preview.sheets.length > 1 && (
              <div>
                <label>Sheet</label>
                <select value={preview.sheet} onChange={(e) => loadPreview(file, e.target.value)}>
                  {preview.sheets.map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label>Header row (1 = first row)</label>
              <input
                type="number"
                min={1}
                value={preview.header_row + 1}
                onChange={(e) => {
                  const n = Number(e.target.value);
                  if (n >= 1) void loadPreview(file, preview.sheet, n - 1);
                }}
              />
            </div>
          </div>

          <h3>Column mapping</h3>
          <div className="form-row mapping">
            {FIELDS.map((field) => (
              <div key={field}>
                <label>
                  {FIELD_LABELS[field]}
                  {field === "description" && <span className="muted"> (recommended)</span>}
                </label>
                <select
                  value={mapping[field] ?? ""}
                  onChange={(e) =>
                    setMapping((m) => {
                      const next = { ...m };
                      if (e.target.value === "") delete next[field];
                      else next[field] = Number(e.target.value);
                      return next;
                    })
                  }
                >
                  <option value="">(not in file)</option>
                  {preview.headers.map((h, i) => (
                    <option key={i} value={i}>
                      {h}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          <p className="muted">
            {preview.total_rows} data rows found. Preview of the first {preview.rows.length}:
          </p>
          <div className="table-wrap preview-table">
            <table className="grid">
              <thead>
                <tr>
                  {preview.headers.map((h, i) => (
                    <th key={i} className={mappedCols.has(i) ? "mapped" : ""}>
                      {h}
                      {mappedCols.has(i) && <div className="mapped-as">{FIELD_LABELS[mappedCols.get(i)!]}</div>}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((r, ri) => (
                  <tr key={ri}>
                    {preview.headers.map((_, ci) => (
                      <td key={ci} className={mappedCols.has(ci) ? "mapped" : ""}>
                        {r[ci] ?? ""}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="actions-row">
            <button className="primary" disabled={!canSubmit} onClick={submit}>
              Upload and match {preview.total_rows} lines
            </button>
          </div>
        </>
      )}
    </div>
  );
}
