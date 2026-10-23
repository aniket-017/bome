import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { dateTime, errorText, qty } from "../format";
import type { Mr, MrLine } from "../types";
import { MR_STATUS_LABELS } from "./MrListPage";

const outstanding = (l: MrLine) => Math.max(l.qty_requested - l.qty_issued, 0);

/** Issue quantity defaulted to what is outstanding and in stock. */
const defaultIssue = (l: MrLine) => {
  const n = Math.min(outstanding(l), Math.max(l.part.in_stock ?? 0, 0));
  return n > 0 ? String(n) : "";
};

export function MrDetailPage() {
  const id = Number(useParams().id);
  const qc = useQueryClient();
  const { data: mr, isLoading, error } = useQuery({ queryKey: ["mr", id], queryFn: () => api.getMr(id) });
  const [issueQty, setIssueQty] = useState<Record<number, string>>({});
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (mr) setIssueQty(Object.fromEntries(mr.lines.map((l) => [l.id, defaultIssue(l)])));
  }, [mr]);

  if (isLoading) return <div className="page"><span className="spinner" /> Loading requisition...</div>;
  if (error || !mr) return <div className="page error">Could not load requisition: {errorText(error)}</div>;

  const open = mr.lines.filter((l) => outstanding(l) > 0);
  const toIssue = open
    .map((l) => ({ line_id: l.id, qty: Number(issueQty[l.id] || 0) }))
    .filter((l) => l.qty > 0);

  const issue = async (lines?: { line_id: number; qty: number }[]) => {
    setBusy(true);
    setActionError(null);
    setNotice(null);
    try {
      const updated: Mr = await api.issueMr(id, lines);
      qc.setQueryData(["mr", id], updated);
      void qc.invalidateQueries({ queryKey: ["mrs"] });
      void qc.invalidateQueries({ queryKey: ["stock"] });
      setNotice(updated.status === "issued" ? "All lines issued." : "Issue recorded.");
    } catch (e) {
      setActionError(errorText(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page wide">
      <header className="page-header">
        <div>
          <div className="muted">Material Requisition</div>
          <h1>
            {mr.mr_no} <span className={`status status-${mr.status}`}>{MR_STATUS_LABELS[mr.status]}</span>
          </h1>
        </div>
        <div className="actions">
          <Link className="btn" to="/inventory/mr">
            All MRs
          </Link>
          <button onClick={() => window.print()}>Print</button>
          {open.length > 0 && (
            <>
              <button disabled={busy || toIssue.length === 0} onClick={() => void issue(toIssue)}>
                Issue entered quantities
              </button>
              <button className="primary" disabled={busy} onClick={() => void issue()}>
                Issue all outstanding
              </button>
            </>
          )}
        </div>
      </header>

      {actionError && <div className="error">{actionError}</div>}
      {notice && <div className="picked no-print">{notice}</div>}

      <section className="card">
        <h2 className="print-only">MATERIAL REQUISITION & ISSUE SLIP</h2>
        <div className="doc-head">
          <div>
            <span>MR No.</span>
            <strong>{mr.mr_no}</strong>
          </div>
          <div>
            <span>Department</span>
            {mr.department ?? "-"}
          </div>
          <div>
            <span>Job / reference</span>
            {mr.job_ref ?? "-"}
            {mr.bom_id && (
              <>
                {" "}
                <Link className="no-print" to={`/boms/${mr.bom_id}`}>
                  (BOM)
                </Link>
              </>
            )}
          </div>
          <div>
            <span>Created</span>
            {dateTime(mr.created_at)}
          </div>
          {mr.remarks && (
            <div>
              <span>Remarks</span>
              {mr.remarks}
            </div>
          )}
        </div>
        <table className="grid line-grid">
          <thead>
            <tr>
              <th className="num">#</th>
              <th>Item No.</th>
              <th>Description</th>
              <th>UoM</th>
              <th className="num">Requested</th>
              <th className="num">Issued</th>
              <th className="num">Outstanding</th>
              <th className="num no-print">In stock</th>
              <th className="num no-print">Issue now</th>
            </tr>
          </thead>
          <tbody>
            {mr.lines.map((l) => {
              const out = outstanding(l);
              const stock = l.part.in_stock ?? 0;
              return (
                <tr key={l.id} className={out > 0 && stock < out ? "row-warn" : ""}>
                  <td className="num">{l.line_no}</td>
                  <td className="mono">{l.part.item_no}</td>
                  <td>{l.part.description}</td>
                  <td>{l.part.uom_group}</td>
                  <td className="num">{qty(l.qty_requested)}</td>
                  <td className="num">{qty(l.qty_issued)}</td>
                  <td className="num">{out > 0 ? qty(out) : ""}</td>
                  <td className={`num no-print ${stock < out ? "txn-out" : ""}`}>{qty(stock)}</td>
                  <td className="num no-print">
                    {out > 0 && (
                      <input
                        type="number"
                        min={0}
                        max={out}
                        className="qty-input"
                        value={issueQty[l.id] ?? ""}
                        onChange={(e) => setIssueQty((m) => ({ ...m, [l.id]: e.target.value }))}
                      />
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className="signatures print-only">
          <div>Requested by</div>
          <div>Approved by</div>
          <div>Issued by (Stores)</div>
        </div>
      </section>
    </div>
  );
}
