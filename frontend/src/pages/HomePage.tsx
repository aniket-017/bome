import { Link } from "react-router-dom";
import { MODULES, WORKFLOW } from "../modules";

export function HomePage() {
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Manufacturing ERP</h1>
          <div className="muted">Materials, BOMs, costing and inventory in one place.</div>
        </div>
      </header>

      <section className="card">
        <h2>How the modules work together</h2>
        <ol className="workflow">
          {WORKFLOW.map((step, i) => {
            const body = (
              <>
                <span className="step-no">{i + 1}</span>
                <strong>{step.title}</strong>
                <span className="muted small">{step.detail}</span>
                {!step.enabled && <span className="soon-tag">Coming soon</span>}
              </>
            );
            return (
              <li key={step.title} className={step.enabled ? "" : "soon"}>
                {step.enabled ? <Link to={step.to}>{body}</Link> : <div>{body}</div>}
              </li>
            );
          })}
        </ol>
      </section>

      <div className="module-tiles">
        {MODULES.map((m) => {
          const live = m.items.filter((i) => i.enabled);
          return (
            <section key={m.key} className={`card module-tile ${live.length ? "" : "soon"}`}>
              <h2>
                {m.label}
                {!live.length && <span className="soon-tag">Coming soon</span>}
              </h2>
              <p>{m.description}</p>
              <p className="muted small">Example: {m.example}</p>
              <div className="tile-links">
                {m.items.map((i) => (
                  <Link key={i.label} to={i.to} className={i.enabled ? "" : "muted"}>
                    {i.label}
                  </Link>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
