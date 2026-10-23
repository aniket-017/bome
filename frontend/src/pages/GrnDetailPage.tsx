import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { date, dateTime, errorText, money, qty } from "../format";

export function GrnDetailPage() {
  const id = Number(useParams().id);
  const { data: grn, isLoading, error } = useQuery({ queryKey: ["grn", id], queryFn: () => api.getGrn(id) });

  if (isLoading) return <div className="page"><span className="spinner" /> Loading GRN...</div>;
  if (error || !grn) return <div className="page error">Could not load GRN: {errorText(error)}</div>;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="muted">Goods Receipt Note</div>
          <h1>{grn.grn_no}</h1>
        </div>
        <div className="actions">
          <Link className="btn" to="/inventory/grn">
            All GRNs
          </Link>
          <button className="primary" onClick={() => window.print()}>
            Print
          </button>
        </div>
      </header>

      <section className="card">
        <h2 className="print-only">GOODS RECEIPT NOTE</h2>
        <div className="doc-head">
          <div>
            <span>GRN No.</span>
            <strong>{grn.grn_no}</strong>
          </div>
          <div>
            <span>Received on</span>
            {date(grn.received_on)}
          </div>
          <div>
            <span>Supplier</span>
            {grn.supplier ?? "-"}
          </div>
          <div>
            <span>Remarks</span>
            {grn.remarks ?? "-"}
          </div>
          <div>
            <span>Posted</span>
            {dateTime(grn.created_at)}
          </div>
        </div>
        <table className="grid">
          <thead>
            <tr>
              <th className="num">#</th>
              <th>Item No.</th>
              <th>Description</th>
              <th className="num">Qty</th>
              <th>UoM</th>
              <th className="num">Unit cost</th>
              <th className="num">Value</th>
            </tr>
          </thead>
          <tbody>
            {grn.lines.map((l) => (
              <tr key={l.id}>
                <td className="num">{l.line_no}</td>
                <td className="mono">{l.part.item_no}</td>
                <td>{l.part.description}</td>
                <td className="num">{qty(l.qty)}</td>
                <td>{l.part.uom_group}</td>
                <td className="num">{money(l.unit_cost)}</td>
                <td className="num">{money(l.qty * l.unit_cost)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={6} className="num">
                Total
              </td>
              <td className="num">{money(grn.total_value)}</td>
            </tr>
          </tfoot>
        </table>
        <div className="signatures print-only">
          <div>Received by</div>
          <div>Checked by (QC)</div>
          <div>Stores in-charge</div>
        </div>
      </section>
    </div>
  );
}
