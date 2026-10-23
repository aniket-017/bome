import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { dateTime, errorText, money, qty } from "../format";
import type { StockAvailability } from "../types";

const PAGE_SIZE = 50;
const REF_LINKS: Record<string, string> = { GRN: "/inventory/grn", MR: "/inventory/mr" };

export function StockPage() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [group, setGroup] = useState<string | null>(null);
  const [availability, setAvailability] = useState<StockAvailability>("in_stock");
  const [offset, setOffset] = useState(0);
  const ledgerPart = Number(params.get("part")) || null;

  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(query.trim()), 250);
    return () => window.clearTimeout(t);
  }, [query]);
  useEffect(() => setOffset(0), [debounced, group, availability]);

  const groups = useQuery({ queryKey: ["groups"], queryFn: api.partGroups });
  const stock = useQuery({
    queryKey: ["stock", debounced, group, availability, offset],
    queryFn: () => api.stock({ q: debounced, group, availability, limit: PAGE_SIZE, offset }),
    placeholderData: keepPreviousData,
  });
  const data = stock.data;

  const openLedger = (id: number | null) => {
    const next = new URLSearchParams(params);
    if (id) next.set("part", String(id));
    else next.delete("part");
    setParams(next, { replace: true });
  };

  return (
    <div className="page wide">
      <header className="page-header">
        <div>
          <div className="muted">Inventory</div>
          <h1>Stock</h1>
          <div className="muted">Quantity on hand valued at weighted-average cost (standard cost if nothing was received).</div>
        </div>
        <div className="actions">
          <Link className="btn" to="/inventory/grn/new">
            + GRN
          </Link>
          <Link className="btn" to="/inventory/mr/new">
            + MR
          </Link>
        </div>
      </header>

      <section className="card toolbar">
        <div className="grow">
          <label>Search</label>
          <input type="search" value={query} placeholder="Description or item number" onChange={(e) => setQuery(e.target.value)} />
        </div>
        <div>
          <label>Group</label>
          <select value={group ?? ""} onChange={(e) => setGroup(e.target.value || null)}>
            <option value="">All groups</option>
            {(groups.data ?? []).filter((g) => g.item_group).map((g) => (
              <option key={g.item_group}>{g.item_group}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Show</label>
          <select value={availability} onChange={(e) => setAvailability(e.target.value as StockAvailability)}>
            <option value="in_stock">In stock</option>
            <option value="out_of_stock">Out of stock</option>
            <option value="all">All items</option>
          </select>
        </div>
        {stock.isFetching && <span className="spinner" />}
      </section>

      {stock.error && <div className="error">{errorText(stock.error)}</div>}
      {data && (
        <>
          <div className="stats">
            <div className="stat">
              <div className="muted small">{debounced ? "Items in results" : "Items"}</div>
              <div className="value">{data.total.toLocaleString("en-IN")}</div>
            </div>
            <div className="stat">
              <div className="muted small">Stock value</div>
              <div className="value">{money(data.total_value)}</div>
            </div>
          </div>
          <section className="card">
            <table className="grid">
              <thead>
                <tr>
                  <th>Item No.</th>
                  <th>Description</th>
                  <th>Group</th>
                  <th>UoM</th>
                  <th className="num">In stock</th>
                  <th className="num">Avg cost</th>
                  <th className="num">Std cost</th>
                  <th className="num">Value</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((p) => (
                  <tr key={p.id} className={`selectable ${p.id === ledgerPart ? "selected" : ""}`} onClick={() => openLedger(p.id)}>
                    <td className="mono">{p.item_no}</td>
                    <td>{p.description}</td>
                    <td>{p.item_group}</td>
                    <td>{p.uom_group}</td>
                    <td className={`num ${(p.in_stock ?? 0) <= 0 ? "txn-out" : ""}`}>{qty(p.in_stock ?? 0)}</td>
                    <td className="num">{money(p.avg_cost)}</td>
                    <td className="num">{money(p.standard_cost)}</td>
                    <td className="num">{money(p.stock_value)}</td>
                  </tr>
                ))}
                {data.items.length === 0 && (
                  <tr>
                    <td colSpan={8} className="muted">
                      Nothing to show.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            {!debounced && data.total > PAGE_SIZE && (
              <div className="actions-row">
                <button disabled={offset === 0} onClick={() => setOffset((o) => Math.max(o - PAGE_SIZE, 0))}>
                  Previous
                </button>
                <span className="muted">
                  {offset + 1}-{Math.min(offset + PAGE_SIZE, data.total)} of {data.total.toLocaleString("en-IN")}
                </span>
                <button disabled={offset + PAGE_SIZE >= data.total} onClick={() => setOffset((o) => o + PAGE_SIZE)}>
                  Next
                </button>
              </div>
            )}
          </section>
        </>
      )}

      {ledgerPart && <LedgerDrawer partId={ledgerPart} onClose={() => openLedger(null)} />}
    </div>
  );
}

function LedgerDrawer({ partId, onClose }: { partId: number; onClose: () => void }) {
  const part = useQuery({ queryKey: ["part", partId], queryFn: () => api.getPart(partId) });
  const ledger = useQuery({ queryKey: ["ledger", partId], queryFn: () => api.ledger(partId) });

  return (
    <aside className="drawer">
      <div className="drawer-header">
        <div>
          <div className="muted small">Stock ledger</div>
          <h2>{part.data ? `${part.data.item_no}` : "..."}</h2>
          {part.data && <div className="small">{part.data.description}</div>}
        </div>
        <button onClick={onClose}>Close</button>
      </div>
      {part.data && (
        <div className="readonly-fields">
          <div>
            <span>In stock</span> {qty(part.data.in_stock ?? 0)} {part.data.uom_group}
          </div>
          <div>
            <span>Avg cost</span> {money(part.data.avg_cost) || "-"}
          </div>
        </div>
      )}
      {ledger.isLoading && <span className="spinner" />}
      {ledger.error && <div className="error">{errorText(ledger.error)}</div>}
      {ledger.data && ledger.data.length === 0 && <p className="muted">No stock movements yet.</p>}
      {ledger.data && ledger.data.length > 0 && (
        <table className="grid">
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Reference</th>
              <th className="num">Qty</th>
              <th className="num">Rate</th>
              <th className="num">Balance</th>
            </tr>
          </thead>
          <tbody>
            {ledger.data.map((t) => (
              <tr key={t.id}>
                <td className="small">{dateTime(t.created_at)}</td>
                <td>{t.txn_type}</td>
                <td className="mono small">
                  {t.ref_no && t.ref_type && REF_LINKS[t.ref_type] ? (
                    <Link to={`${REF_LINKS[t.ref_type]}/${t.ref_id}`}>{t.ref_no}</Link>
                  ) : (
                    t.ref_type ?? ""
                  )}
                </td>
                <td className={`num ${t.qty >= 0 ? "txn-in" : "txn-out"}`}>
                  {t.qty > 0 ? "+" : ""}
                  {qty(t.qty)}
                </td>
                <td className="num">{money(t.unit_cost)}</td>
                <td className="num">{qty(t.balance)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </aside>
  );
}
