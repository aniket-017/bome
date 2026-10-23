import { Link } from "react-router-dom";
import type { ErpModule, ModuleItem } from "../modules";

export function ComingSoonPage({ module, item }: { module: ErpModule; item: ModuleItem }) {
  const live = module.items.filter((i) => i.enabled);
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="muted">{module.label}</div>
          <h1>{item.label}</h1>
        </div>
      </header>
      <section className="card">
        <span className="soon-tag">Coming soon</span>
        <p>{item.description ?? module.description}</p>
        <p className="muted">Example: {module.example}</p>
        <p className="muted">This module is planned for a later phase.</p>
        {live.length > 0 && (
          <p>
            Available now in {module.label}:{" "}
            {live.map((i, n) => (
              <span key={i.label}>
                {n > 0 && ", "}
                <Link to={i.to}>{i.label}</Link>
              </span>
            ))}
          </p>
        )}
        <Link to="/">Back to home</Link>
      </section>
    </div>
  );
}
