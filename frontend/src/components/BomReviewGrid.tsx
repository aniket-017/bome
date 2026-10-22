import { useMemo, useState } from "react";
import type { BomLine, MatchStatus } from "../types";
import { PartAutocomplete } from "./PartAutocomplete";
import { STATUS_LABELS, STATUS_ORDER, StatusBadge } from "./StatusBadge";

export interface LineActions {
  setPart: (line: BomLine, partId: number) => void;
  clear: (line: BomLine) => void;
  editText: (line: BomLine, description: string) => void;
  editQty: (line: BomLine, qty: number | null) => void;
  remove: (line: BomLine) => void;
}

interface Props {
  lines: BomLine[];
  actions: LineActions;
  busyLineIds: Set<number>;
  onSelectLine?: (line: BomLine) => void;
}

export function BomReviewGrid({ lines, actions, busyLineIds, onSelectLine }: Props) {
  const [filter, setFilter] = useState<MatchStatus | "all" | "todo">("all");
  const [text, setText] = useState("");

  const counts = useMemo(() => {
    const c: Partial<Record<MatchStatus, number>> = {};
    lines.forEach((l) => (c[l.match_status] = (c[l.match_status] ?? 0) + 1));
    return c;
  }, [lines]);

  const visible = lines.filter((l) => {
    if (filter === "todo" && !(l.match_status === "review" || l.match_status === "unmatched")) return false;
    if (filter !== "all" && filter !== "todo" && l.match_status !== filter) return false;
    if (text) {
      const hay = `${l.raw_description ?? ""} ${l.raw_item_no ?? ""} ${l.matched_part?.description ?? ""} ${
        l.matched_part?.item_no ?? ""
      }`.toLowerCase();
      if (!hay.includes(text.toLowerCase())) return false;
    }
    return true;
  });
  const todo = (counts.review ?? 0) + (counts.unmatched ?? 0);

  return (
    <div>
      <div className="grid-toolbar">
        <div className="chips">
          <button className={`chip ${filter === "all" ? "active" : ""}`} onClick={() => setFilter("all")}>
            All <span className="muted">{lines.length}</span>
          </button>
          <button className={`chip ${filter === "todo" ? "active" : ""}`} onClick={() => setFilter("todo")}>
            Needs attention <span className="muted">{todo}</span>
          </button>
          {STATUS_ORDER.filter((s) => counts[s]).map((s) => (
            <button key={s} className={`chip st-chip-${s} ${filter === s ? "active" : ""}`} onClick={() => setFilter(s)}>
              {STATUS_LABELS[s]} <span className="muted">{counts[s]}</span>
            </button>
          ))}
        </div>
        <input
          type="search"
          className="grid-filter"
          placeholder="Filter lines..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </div>

      <div>
        <table className="grid review-grid">
          <thead>
            <tr>
              <th style={{ width: 50 }}>Line</th>
              <th>BOM line</th>
              <th style={{ width: 80 }} className="num">
                Qty
              </th>
              <th style={{ width: 110 }}>Status</th>
              <th>Matched part from master</th>
              <th style={{ width: 70 }} />
            </tr>
          </thead>
          <tbody>
            {visible.map((l) => (
              <ReviewRow
                key={l.id}
                line={l}
                actions={actions}
                busy={busyLineIds.has(l.id)}
                onFocus={() => onSelectLine?.(l)}
              />
            ))}
          </tbody>
        </table>
        {visible.length === 0 && <p className="muted center">No lines in this view.</p>}
      </div>
    </div>
  );
}

function ReviewRow({
  line,
  actions,
  busy,
  onFocus,
}: {
  line: BomLine;
  actions: LineActions;
  busy: boolean;
  onFocus: () => void;
}) {
  const [searching, setSearching] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(line.raw_description ?? "");
  const [picked, setChoice] = useState<number | null>(null);
  const choice = line.candidates.some((c) => c.part_id === picked) ? picked : line.candidates[0]?.part_id ?? null;
  const part = line.matched_part;

  return (
    <tr className={`row-${line.match_status} ${busy ? "row-busy" : ""}`} onClick={onFocus}>
      <td className="muted">{line.line_no}</td>
      <td>
        {editing ? (
          <div className="inline-edit">
            <input
              type="text"
              value={draft}
              autoFocus
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  actions.editText(line, draft);
                  setEditing(false);
                } else if (e.key === "Escape") setEditing(false);
              }}
            />
            <button
              className="primary"
              onClick={() => {
                actions.editText(line, draft);
                setEditing(false);
              }}
            >
              Save
            </button>
            <button onClick={() => setEditing(false)}>Cancel</button>
          </div>
        ) : (
          <div className="bom-text">
            {line.raw_item_no && <span className="mono muted">{line.raw_item_no} · </span>}
            {line.raw_description || <span className="muted">(no description)</span>}
            <button
              className="link edit-btn"
              title="Edit description (re-matches the line)"
              onClick={() => {
                setDraft(line.raw_description ?? "");
                setEditing(true);
              }}
            >
              edit
            </button>
          </div>
        )}
      </td>
      <td className="num">
        <input
          type="number"
          className="qty-input"
          defaultValue={line.qty ?? ""}
          onBlur={(e) => {
            const v = e.target.value === "" ? null : Number(e.target.value);
            if (v !== line.qty) actions.editQty(line, v);
          }}
        />
        <div className="muted small">{line.uom}</div>
      </td>
      <td>
        <StatusBadge status={line.match_status} score={line.match_score} />
      </td>
      <td>
        {busy ? (
          <span className="spinner" />
        ) : searching ? (
          <div className="inline-search">
            <PartAutocomplete
              compact
              autoFocus
              initialQuery={line.raw_description ?? ""}
              onSelect={(p) => {
                actions.setPart(line, p.id);
                setSearching(false);
              }}
            />
            <button className="link" onClick={() => setSearching(false)}>
              cancel
            </button>
          </div>
        ) : part ? (
          <div className="matched">
            <span className="mono item">{part.item_no}</span> {part.description}
            {part.item_group && <span className="group-tag">{part.item_group}</span>}
            <div className="row-links">
              <button className="link" onClick={() => setSearching(true)}>
                change
              </button>
              <button className="link" onClick={() => actions.clear(line)}>
                clear
              </button>
            </div>
          </div>
        ) : (
          <div className="suggest">
            {line.candidates.length > 0 ? (
              <div className="suggest-pick">
                <select value={choice ?? ""} onChange={(e) => setChoice(Number(e.target.value))}>
                  {line.candidates.map((c) => (
                    <option key={c.part_id} value={c.part_id}>
                      {Math.round(c.score)} · {c.item_no} · {c.description}
                    </option>
                  ))}
                </select>
                <button className="primary" disabled={choice == null} onClick={() => choice && actions.setPart(line, choice)}>
                  Accept
                </button>
              </div>
            ) : (
              <span className="muted">No similar part in master. </span>
            )}
            <button className="link" onClick={() => setSearching(true)}>
              search master...
            </button>
          </div>
        )}
      </td>
      <td>
        <button className="link danger" title="Delete line" onClick={() => actions.remove(line)}>
          delete
        </button>
      </td>
    </tr>
  );
}
