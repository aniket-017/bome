import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { Highlight } from "../components/Highlight";
import { errorText, money, qty } from "../format";
import { MIN_QUERY_LENGTH, usePartSearch } from "../hooks/usePartSearch";
import type { Part, PartDetail, PartInput } from "../types";

interface FormState {
  item_no: string;
  description: string;
  item_group: string;
  uom_group: string;
  standard_cost: string;
  opening_stock: string;
}

const EMPTY: FormState = { item_no: "", description: "", item_group: "", uom_group: "", standard_cost: "", opening_stock: "" };

const toForm = (p: PartDetail): FormState => ({
  item_no: p.item_no,
  description: p.description,
  item_group: p.item_group ?? "",
  uom_group: p.uom_group ?? "",
  standard_cost: p.standard_cost == null ? "" : String(p.standard_cost),
  opening_stock: "",
});

const numOrNull = (s: string) => (s.trim() === "" ? null : Number(s));

export function ItemMasterPage() {
  const qc = useQueryClient();
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [edited, setEdited] = useState<Record<number, Part>>({});
  const [removed, setRemoved] = useState<Set<number>>(new Set());

  const groups = useQuery({ queryKey: ["groups"], queryFn: api.partGroups });
  const groupNames = (groups.data ?? []).map((g) => g.item_group).filter((g): g is string => !!g);
  const search = usePartSearch(query, { group, limit: 50 });
  const detail = useQuery({
    queryKey: ["part", selectedId],
    queryFn: () => api.getPart(selectedId!),
    enabled: selectedId !== null,
  });

  useEffect(() => {
    if (detail.data && !adding) setForm(toForm(detail.data));
  }, [detail.data, adding]);

  const rows = (search.data?.items ?? []).filter((p) => !removed.has(p.id)).map((p) => edited[p.id] ?? p);
  const part = adding ? null : detail.data ?? null;

  const startAdd = () => {
    setAdding(true);
    setSelectedId(null);
    setForm(EMPTY);
    setError(null);
    setNotice(null);
  };

  const select = (id: number) => {
    setAdding(false);
    setSelectedId(id);
    setError(null);
    setNotice(null);
  };

  const run = async (fn: () => Promise<void>) => {
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      await fn();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setSaving(false);
    }
  };

  const save = () =>
    run(async () => {
      const body: PartInput = {
        description: form.description.trim(),
        item_group: form.item_group.trim() || null,
        uom_group: form.uom_group.trim() || null,
        standard_cost: numOrNull(form.standard_cost),
      };
      let saved: PartDetail;
      if (adding) {
        saved = await api.createPart({ ...body, item_no: form.item_no.trim(), opening_stock: numOrNull(form.opening_stock) });
        setNotice(`Item ${saved.item_no} added.`);
        setAdding(false);
      } else {
        saved = await api.updatePart(selectedId!, body);
        setNotice(`Item ${saved.item_no} saved.`);
      }
      qc.setQueryData(["part", saved.id], saved);
      setEdited((m) => ({ ...m, [saved.id]: saved }));
      setSelectedId(saved.id);
      void qc.invalidateQueries({ queryKey: ["groups"] });
    });

  const remove = () => {
    if (!part || !confirm(`Delete item ${part.item_no}? It will be marked inactive and hidden from search.`)) return;
    void run(async () => {
      await api.deletePart(part.id);
      setRemoved((s) => new Set(s).add(part.id));
      setNotice(`Item ${part.item_no} deleted (inactive).`);
      setSelectedId(null);
      setForm(EMPTY);
      void qc.invalidateQueries({ queryKey: ["part", part.id] });
    });
  };

  const reactivate = () =>
    part &&
    run(async () => {
      const saved = await api.updatePart(part.id, { is_active: true });
      qc.setQueryData(["part", saved.id], saved);
      setNotice(`Item ${saved.item_no} reactivated.`);
    });

  const set = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const canSave = form.description.trim() && (!adding || form.item_no.trim()) && (adding || part);

  return (
    <div className="page wide">
      <header className="page-header">
        <div>
          <h1>Item Master</h1>
          <div className="muted">Materials, components and finished products with their unit, group and cost.</div>
        </div>
        <div className="actions">
          <button className="primary" onClick={startAdd}>
            + Add item
          </button>
        </div>
      </header>

      <div className="master-detail">
        <section className="card">
          <div className="toolbar">
            <div className="grow">
              <label>Search</label>
              <input
                type="search"
                value={query}
                placeholder="Description or item number"
                onChange={(e) => setQuery(e.target.value)}
                autoFocus
              />
            </div>
            <div>
              <label>Group</label>
              <select value={group ?? ""} onChange={(e) => setGroup(e.target.value || null)}>
                <option value="">All groups</option>
                {groupNames.map((g) => (
                  <option key={g}>{g}</option>
                ))}
              </select>
            </div>
            {search.loading && <span className="spinner" />}
          </div>
          {search.error && <div className="error">{search.error}</div>}
          {query.trim().length < MIN_QUERY_LENGTH ? (
            <p className="muted">Type at least {MIN_QUERY_LENGTH} characters to find an item, or add a new one.</p>
          ) : (
            search.data && (
              <table className="grid">
                <thead>
                  <tr>
                    <th>Item No.</th>
                    <th>Description</th>
                    <th>Group</th>
                    <th>UoM</th>
                    <th className="num">Stock</th>
                    <th className="num">Std cost</th>
                    <th className="num">Avg cost</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((p) => (
                    <tr
                      key={p.id}
                      className={`selectable ${p.id === selectedId ? "selected" : ""}`}
                      onClick={() => select(p.id)}
                    >
                      <td className="mono">{p.item_no}</td>
                      <td>
                        <Highlight text={p.description} query={query} />
                      </td>
                      <td>{p.item_group}</td>
                      <td>{p.uom_group}</td>
                      <td className="num">{qty(p.in_stock)}</td>
                      <td className="num">{money(p.standard_cost)}</td>
                      <td className="num">{money(p.avg_cost)}</td>
                    </tr>
                  ))}
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={7} className="muted">
                        No items found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            )
          )}
        </section>

        <aside className="card detail">
          {!adding && selectedId === null ? (
            <p className="muted">Select an item to modify it, or click "Add item".</p>
          ) : !adding && detail.isLoading ? (
            <span className="spinner" />
          ) : (
            <>
              <h2>{adding ? "Add item" : `Modify ${part?.item_no ?? ""}`}</h2>
              {part && !part.is_active && (
                <div className="notice">
                  This item is inactive.{" "}
                  <button className="link" onClick={reactivate} disabled={saving}>
                    Reactivate
                  </button>
                </div>
              )}
              <label>Item number</label>
              <input type="text" value={form.item_no} onChange={set("item_no")} disabled={!adding} maxLength={50} />
              <label style={{ marginTop: 10 }}>Description</label>
              <textarea rows={3} value={form.description} onChange={set("description")} />
              <div className="form-row" style={{ marginTop: 10 }}>
                <div>
                  <label>Item group</label>
                  <input type="text" list="item-groups" value={form.item_group} onChange={set("item_group")} />
                  <datalist id="item-groups">
                    {groupNames.map((g) => (
                      <option key={g} value={g} />
                    ))}
                  </datalist>
                </div>
                <div>
                  <label>UoM</label>
                  <input type="text" value={form.uom_group} onChange={set("uom_group")} placeholder="NOS, KG, MTR" />
                </div>
              </div>
              <div className="form-row">
                <div>
                  <label>Standard cost (INR)</label>
                  <input type="number" min={0} step="0.01" value={form.standard_cost} onChange={set("standard_cost")} />
                </div>
                {adding && (
                  <div>
                    <label>Opening stock</label>
                    <input type="number" min={0} value={form.opening_stock} onChange={set("opening_stock")} />
                  </div>
                )}
              </div>
              {part && (
                <div className="readonly-fields">
                  <div>
                    <span>In stock</span> {qty(part.in_stock) || "0"} {part.uom_group}
                  </div>
                  <div>
                    <span>Weighted avg cost</span> {money(part.avg_cost) || "-"}
                  </div>
                  <div>
                    <span>Noun</span> {part.noun ?? "-"}
                  </div>
                  <div>
                    <Link to={`/inventory/stock?part=${part.id}`}>Stock ledger</Link>
                  </div>
                </div>
              )}
              <p className="muted small">
                Stock and average cost change only through GRN entry and material issue.
              </p>
              {error && <div className="error">{error}</div>}
              {notice && <div className="picked">{notice}</div>}
              <div className="actions-row">
                <button className="primary" disabled={!canSave || saving} onClick={() => void save()}>
                  {saving ? "Saving..." : "Save"}
                </button>
                {part && part.is_active && (
                  <button className="danger" disabled={saving} onClick={remove}>
                    Delete
                  </button>
                )}
                {adding && <button onClick={() => setAdding(false)}>Cancel</button>}
              </div>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
