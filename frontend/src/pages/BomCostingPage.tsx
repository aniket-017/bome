import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { errorText, money, qty } from "../format";
import type { CostIssue, CostingLine } from "../types";

const ISSUE_LABELS: Record<CostIssue, string> = {
  unmatched: "Not linked to an item",
  no_qty: "No quantity",
  no_cost: "Item has no cost",
};

/** BOM Costing (mode "cost") and Quantity Estimation (mode "quantity") over the same BOM x batch calculation. */
export function BomCostingPage({ mode }: { mode: "cost" | "quantity" }) {
  const routeId = useParams().id;
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const bomId = Number(routeId ?? params.get("bom")) || null;
  const [batchInput, setBatchInput] = useState(params.get("batch") ?? "1");
  const batchQty = Number(batchInput) > 0 ? Number(batchInput) : 1;
  const [mrBusy, setMrBusy] = useState(false);
  const [mrError, setMrError] = useState<string | null>(null);

  const boms = useQuery({ queryKey: ["boms"], queryFn: api.listBoms, enabled: !routeId });
  const costing = useQuery({
    queryKey: ["costing", bomId, batchQty],
    queryFn: () => api.bomCosting(bomId!, batchQty),
    enabled: bomId !== null,
  });

  const pickBom = (id: string) => {
    const next = new URLSearchParams(params);
    if (id) next.set("bom", id);
    else next.delete("bom");
    setParams(next, { replace: true });
  };

  const createMr = async () => {
    if (!bomId) return;
    setMrBusy(true);
    setMrError(null);
    try {
      const mr = await api.mrFromBom(bomId, { batch_qty: batchQty });
      navigate(`/inventory/mr/${mr.id}`);
    } catch (e) {
      setMrError(errorText(e));
      setMrBusy(false);
    }
  };

  const c = costing.data;
  const title = mode === "cost" ? "BOM Costing" : "Quantity Estimation";
  const shortOf = (l: CostingLine) =>
    l.part && l.total_qty != null ? Math.max(l.total_qty - (l.part.in_stock ?? 0), 0) : null;
  const shortLines = c ? c.lines.filter((l) => (shortOf(l) ?? 0) > 0).length : 0;

  return (
    <div className="page wide">
      <header className="page-header">
        <div>
          <div className="muted">Estimation</div>
          <h1>
            {title}
            {c && routeId && <> · {c.bom_name}</>}
          </h1>
          <div className="muted">
            {mode === "cost"
              ? "Material cost of a BOM at weighted-average cost (standard cost where nothing has been received yet)."
              : "Quantities needed for a batch, compared with stock on hand."}
          </div>
        </div>
        <div className="actions">
          {bomId && (
            <Link className="btn" to={mode === "cost" ? `/estimation/quantity?bom=${bomId}&batch=${batchQty}` : `/estimation/bom-costing?bom=${bomId}&batch=${batchQty}`}>
              {mode === "cost" ? "Quantities & shortages" : "Costing"}
            </Link>
          )}
          {bomId && (
            <a className="btn" href={api.costingExportUrl(bomId, batchQty)}>
              Export Excel
            </a>
          )}
          {bomId && (
            <button className="primary" disabled={mrBusy} onClick={() => void createMr()}>
              {mrBusy ? "Creating MR..." : "Create MR for this batch"}
            </button>
          )}
        </div>
      </header>

      <section className="card toolbar">
        {!routeId && (
          <div className="grow">
            <label>BOM</label>
            <select value={bomId ?? ""} onChange={(e) => pickBom(e.target.value)}>
              <option value="">Select a BOM...</option>
              {(boms.data ?? []).map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                  {b.project ? ` (${b.project})` : ""} · {b.line_count} lines
                </option>
              ))}
            </select>
          </div>
        )}
        <div>
          <label>Batch quantity (assemblies)</label>
          <input type="number" min={1} value={batchInput} onChange={(e) => setBatchInput(e.target.value)} />
        </div>
        {routeId && (
          <Link to={`/boms/${routeId}`} className="btn">
            Back to BOM
          </Link>
        )}
        {costing.isFetching && <span className="spinner" />}
      </section>

      {mrError && <div className="error">{mrError}</div>}
      {costing.error && <div className="error">{errorText(costing.error)}</div>}
      {!bomId && <p className="muted">Select a BOM to estimate.</p>}

      {c && (
        <>
          <div className="stats">
            {mode === "cost" ? (
              <>
                <div className="stat">
                  <div className="muted small">Material cost ({qty(c.batch_qty)} units)</div>
                  <div className="value">{money(c.material_cost)}</div>
                </div>
                <div className="stat">
                  <div className="muted small">Per unit</div>
                  <div className="value">{money(c.unit_material_cost)}</div>
                </div>
              </>
            ) : (
              <div className={`stat ${shortLines ? "bad" : ""}`}>
                <div className="muted small">Lines short of stock</div>
                <div className="value">{shortLines}</div>
              </div>
            )}
            <div className="stat">
              <div className="muted small">Costed lines</div>
              <div className="value">
                {c.costed_count} / {c.line_count}
              </div>
            </div>
            <div className={`stat ${c.unmatched_count ? "bad" : ""}`}>
              <div className="muted small">Not linked to an item</div>
              <div className="value">{c.unmatched_count}</div>
            </div>
            <div className={`stat ${c.uncosted_count ? "warn" : ""}`}>
              <div className="muted small">Missing cost or quantity</div>
              <div className="value">{c.uncosted_count}</div>
            </div>
          </div>
          {(c.unmatched_count > 0 || c.uncosted_count > 0) && (
            <div className="notice">
              Some lines are not included in the total. Link them on the <Link to={`/boms/${c.bom_id}`}>BOM</Link> or set a
              standard cost in the <Link to="/items">Item Master</Link>.
            </div>
          )}

          <section className="card table-wrap">
            <table className="grid">
              <thead>
                <tr>
                  <th className="num">#</th>
                  <th>Item No.</th>
                  <th>Description</th>
                  <th className="num">Qty / unit</th>
                  <th className="num">Total qty</th>
                  <th>UoM</th>
                  {mode === "cost" ? (
                    <>
                      <th className="num">Unit cost</th>
                      <th>Basis</th>
                      <th className="num">Line cost</th>
                    </>
                  ) : (
                    <>
                      <th className="num">In stock</th>
                      <th className="num">Shortage</th>
                    </>
                  )}
                  <th>Issue</th>
                </tr>
              </thead>
              <tbody>
                {c.lines.map((l) => {
                  const short = shortOf(l);
                  return (
                    <tr key={l.line_id} className={l.issue || (mode === "quantity" && short) ? "row-warn" : ""}>
                      <td className="num">{l.line_no}</td>
                      <td className="mono">{l.part?.item_no ?? l.raw_item_no}</td>
                      <td>{l.part?.description ?? l.raw_description}</td>
                      <td className="num">{qty(l.qty)}</td>
                      <td className="num">{qty(l.total_qty)}</td>
                      <td>{l.uom}</td>
                      {mode === "cost" ? (
                        <>
                          <td className="num">{money(l.unit_cost)}</td>
                          <td className="muted small">
                            {l.cost_source === "avg_cost" ? "Weighted avg" : l.cost_source === "standard_cost" ? "Standard" : ""}
                          </td>
                          <td className="num">{money(l.line_cost)}</td>
                        </>
                      ) : (
                        <>
                          <td className="num">{l.part ? qty(l.part.in_stock ?? 0) : ""}</td>
                          <td className="num">{short ? <strong className="txn-out">{qty(short)}</strong> : ""}</td>
                        </>
                      )}
                      <td className="small">{l.issue ? ISSUE_LABELS[l.issue] : ""}</td>
                    </tr>
                  );
                })}
              </tbody>
              {mode === "cost" && (
                <tfoot>
                  <tr>
                    <td colSpan={8} className="num">
                      Total material cost
                    </td>
                    <td className="num">{money(c.material_cost)}</td>
                    <td />
                  </tr>
                </tfoot>
              )}
            </table>
          </section>
        </>
      )}
    </div>
  );
}
