import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api";
import { dateTime, errorText } from "../format";

export const MR_STATUS_LABELS = { open: "Open", partial: "Partly issued", issued: "Issued" } as const;

export function MrListPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["mrs"], queryFn: api.listMrs });

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="muted">Inventory</div>
          <h1>Material Requisitions</h1>
          <div className="muted">Requests for materials by a job or department, issued from stock.</div>
        </div>
        <div className="actions">
          <Link className="btn primary" to="/inventory/mr/new">
            + New MR
          </Link>
        </div>
      </header>
      {isLoading && <span className="spinner" />}
      {error && <div className="error">{errorText(error)}</div>}
      {data && data.length === 0 && (
        <div className="card">
          No requisitions yet. <Link to="/inventory/mr/new">Create one manually or from a BOM.</Link>
        </div>
      )}
      {data && data.length > 0 && (
        <div className="card">
          <table className="grid">
            <thead>
              <tr>
                <th>MR No.</th>
                <th>Department</th>
                <th>Job / reference</th>
                <th className="num">Lines</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {data.map((m) => (
                <tr key={m.id}>
                  <td className="mono">
                    <Link to={`/inventory/mr/${m.id}`}>{m.mr_no}</Link>
                  </td>
                  <td>{m.department}</td>
                  <td>
                    {m.job_ref}
                    {m.bom_id && (
                      <>
                        {" "}
                        <Link className="small" to={`/boms/${m.bom_id}`}>
                          (BOM)
                        </Link>
                      </>
                    )}
                  </td>
                  <td className="num">{m.line_count}</td>
                  <td>
                    <span className={`status status-${m.status}`}>{MR_STATUS_LABELS[m.status]}</span>
                  </td>
                  <td className="muted">{dateTime(m.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
