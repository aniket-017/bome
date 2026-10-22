import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api";
import { Highlight } from "../components/Highlight";
import { PartAutocomplete } from "../components/PartAutocomplete";
import { MIN_QUERY_LENGTH, usePartSearch } from "../hooks/usePartSearch";
import type { Part } from "../types";

export function PartsSearchPage() {
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState<string | null>(null);
  const [picked, setPicked] = useState<Part | null>(null);
  const groups = useQuery({ queryKey: ["groups"], queryFn: api.partGroups });
  const stats = useQuery({ queryKey: ["stats"], queryFn: api.partStats });
  const { data, loading, error } = usePartSearch(query, { group, limit: 100 });
  const groupNames = (groups.data ?? []).map((g) => g.item_group).filter((g): g is string => !!g);

  return (
    <div className="page">
      <header className="page-header">
        <h1>Parts master</h1>
        {stats.data && <span className="muted">{stats.data.active.toLocaleString("en-IN")} active parts</span>}
      </header>

      <section className="card">
        <h2>Quick pick (type-ahead)</h2>
        <p className="muted">
          The same dropdown is used on BOM lines. Try <code>elbow 316l dn 100 lr</code>, <code>stud m20 x 310</code>,{" "}
          <code>4" elbow sch 40</code> or an item number.
        </p>
        <PartAutocomplete onSelect={setPicked} groups={groupNames} />
        {picked && (
          <div className="picked">
            Selected: <strong>{picked.item_no}</strong> - {picked.description}
          </div>
        )}
      </section>

      <section className="card">
        <h2>Browse results</h2>
        <div className="search-bar">
          <input
            type="search"
            value={query}
            placeholder="Search description or item number"
            onChange={(e) => setQuery(e.target.value)}
          />
          {loading && <span className="spinner" />}
        </div>
        <div className="chips">
          <button className={`chip ${group === null ? "active" : ""}`} onClick={() => setGroup(null)}>
            All
          </button>
          {(groups.data ?? []).map((g) => (
            <button
              key={g.item_group ?? "none"}
              className={`chip ${group === g.item_group ? "active" : ""}`}
              onClick={() => setGroup(g.item_group)}
            >
              {g.item_group ?? "(none)"} <span className="muted">{g.count.toLocaleString("en-IN")}</span>
            </button>
          ))}
        </div>

        {error && <div className="error">{error}</div>}
        {query.trim().length < MIN_QUERY_LENGTH ? (
          <p className="muted">Type at least {MIN_QUERY_LENGTH} characters.</p>
        ) : (
          data && (
            <>
              <p className="muted">
                {data.items.length} results in {data.took_ms} ms
                {data.corrected_query && <> · showing results for "{data.corrected_query}"</>}
                {data.fuzzy && <> · similar matches</>}
              </p>
              <table className="grid">
                <thead>
                  <tr>
                    <th>Item No.</th>
                    <th>Description</th>
                    <th>Group</th>
                    <th>UoM</th>
                    <th className="num">In stock</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((p) => (
                    <tr key={p.id}>
                      <td className="mono">{p.item_no}</td>
                      <td>
                        <Highlight text={p.description} query={query} />
                      </td>
                      <td>{p.item_group}</td>
                      <td>{p.uom_group}</td>
                      <td className="num">{p.in_stock ?? ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )
        )}
      </section>
    </div>
  );
}
