import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api";
import { date, errorText, money } from "../format";

export function GrnListPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["grns"], queryFn: api.listGrns });

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="muted">Inventory</div>
          <h1>Goods Receipt Notes</h1>
          <div className="muted">Materials received from suppliers. Posting a GRN adds to stock and updates the average cost.</div>
        </div>
        <div className="actions">
          <Link className="btn primary" to="/inventory/grn/new">
            + New GRN
          </Link>
        </div>
      </header>
      {isLoading && <span className="spinner" />}
      {error && <div className="error">{errorText(error)}</div>}
      {data && data.length === 0 && (
        <div className="card">
          No GRNs yet. <Link to="/inventory/grn/new">Record the first receipt.</Link>
        </div>
      )}
      {data && data.length > 0 && (
        <div className="card">
          <table className="grid">
            <thead>
              <tr>
                <th>GRN No.</th>
                <th>Received on</th>
                <th>Supplier</th>
                <th className="num">Lines</th>
                <th className="num">Value</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {data.map((g) => (
                <tr key={g.id}>
                  <td className="mono">
                    <Link to={`/inventory/grn/${g.id}`}>{g.grn_no}</Link>
                  </td>
                  <td>{date(g.received_on)}</td>
                  <td>{g.supplier}</td>
                  <td className="num">{g.line_count}</td>
                  <td className="num">{money(g.total_value)}</td>
                  <td className="muted">{g.remarks}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
