import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api";
import { STATUS_LABELS, STATUS_ORDER } from "../components/StatusBadge";

const BOM_STATUS: Record<string, string> = { draft: "Draft", matched: "Matched", needs_review: "Needs review" };

export function BomListPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["boms"], queryFn: api.listBoms });

  return (
    <div className="page">
      <header className="page-header">
        <h1>BOMs</h1>
        <div className="actions">
          <Link className="btn primary" to="/boms/new">
            + New BOM
          </Link>
        </div>
      </header>
      {isLoading && <span className="spinner" />}
      {error && <div className="error">{String(error)}</div>}
      {data && data.length === 0 && (
        <div className="card">
          No BOMs yet. <Link to="/boms/new">Upload an Excel BOM or enter one manually.</Link>
        </div>
      )}
      {data && data.length > 0 && (
        <div className="card">
          <table className="grid">
            <thead>
              <tr>
                <th>Name</th>
                <th>Project</th>
                <th>Source</th>
                <th className="num">Lines</th>
                <th>Match summary</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {data.map((b) => (
                <tr key={b.id}>
                  <td>
                    <Link to={`/boms/${b.id}`}>{b.name}</Link>
                  </td>
                  <td>{b.project}</td>
                  <td>{b.source_type}</td>
                  <td className="num">{b.line_count}</td>
                  <td>
                    <div className="mini-badges">
                      {STATUS_ORDER.filter((s) => b.status_counts[s]).map((s) => (
                        <span key={s} className={`badge st-${s}`}>
                          {STATUS_LABELS[s]} {b.status_counts[s]}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>{BOM_STATUS[b.status] ?? b.status}</td>
                  <td className="muted">{new Date(b.created_at).toLocaleString("en-IN")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
