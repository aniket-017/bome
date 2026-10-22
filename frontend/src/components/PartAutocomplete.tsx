import { useEffect, useId, useRef, useState } from "react";
import { MIN_QUERY_LENGTH, usePartSearch } from "../hooks/usePartSearch";
import type { Part } from "../types";
import { Highlight } from "./Highlight";

interface Props {
  onSelect: (part: Part) => void;
  onQueryChange?: (query: string) => void;
  initialQuery?: string;
  placeholder?: string;
  group?: string | null;
  groups?: string[];
  autoFocus?: boolean;
  compact?: boolean;
  clearOnSelect?: boolean;
  limit?: number;
}

export function PartAutocomplete({
  onSelect,
  onQueryChange,
  initialQuery = "",
  placeholder = "Type part description or item number...",
  group: fixedGroup = null,
  groups,
  autoFocus,
  compact,
  clearOnSelect = false,
  limit = 20,
}: Props) {
  const [query, setQuery] = useState(initialQuery);
  const [group, setGroup] = useState<string | null>(fixedGroup);
  const [open, setOpen] = useState(!!autoFocus);
  const [active, setActive] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const listId = useId();
  const { data, loading, error } = usePartSearch(query, { group, limit, enabled: open });
  const items = data?.items ?? [];

  useEffect(() => setActive(0), [data]);

  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  useEffect(() => {
    listRef.current?.querySelector<HTMLElement>(`[data-index="${active}"]`)?.scrollIntoView({ block: "nearest" });
  }, [active]);

  const choose = (part: Part) => {
    onSelect(part);
    setOpen(false);
    setQuery(clearOnSelect ? "" : part.description);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!showDropdown) {
        setOpen(true);
        return;
      }
      setActive((a) => Math.min(a + 1, Math.max(items.length - 1, 0)));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((a) => Math.max(a - 1, 0));
    } else if (e.key === "Enter") {
      if (open && items[active]) {
        e.preventDefault();
        choose(items[active]);
      }
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  const showDropdown = open && query.trim().length >= MIN_QUERY_LENGTH;

  return (
    <div className={`autocomplete ${compact ? "compact" : ""}`} ref={rootRef}>
      <div className="autocomplete-inputs">
        {groups && (
          <select
            className="group-select"
            value={group ?? ""}
            onChange={(e) => setGroup(e.target.value || null)}
            title="Filter by item group"
          >
            <option value="">All groups</option>
            {groups.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        )}
        <input
          type="text"
          role="combobox"
          aria-expanded={showDropdown}
          aria-controls={listId}
          aria-autocomplete="list"
          value={query}
          placeholder={placeholder}
          autoFocus={autoFocus}
          onChange={(e) => {
            setQuery(e.target.value);
            onQueryChange?.(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={onKeyDown}
        />
        {loading && <span className="spinner" aria-label="searching" />}
      </div>

      {showDropdown && (
        <div className="autocomplete-dropdown">
          {data?.corrected_query && <div className="dropdown-note">Showing results for "{data.corrected_query}"</div>}
          {data?.fuzzy && items.length > 0 && <div className="dropdown-note">No exact match, showing similar parts</div>}
          {error && <div className="dropdown-note error">{error}</div>}
          {!loading && data && items.length === 0 && <div className="dropdown-note">No parts found</div>}
          <ul id={listId} role="listbox" ref={listRef}>
            {items.map((p, i) => (
              <li
                key={p.id}
                role="option"
                aria-selected={i === active}
                data-index={i}
                className={i === active ? "active" : ""}
                onMouseEnter={() => setActive(i)}
                onMouseDown={(e) => {
                  e.preventDefault();
                  choose(p);
                }}
              >
                <span className="item-no">{p.item_no}</span>
                <span className="desc">
                  <Highlight text={p.description} query={query} />
                </span>
                {p.item_group && <span className="group-tag">{p.item_group}</span>}
              </li>
            ))}
          </ul>
          {data && <div className="dropdown-footer">{items.length} shown · {data.took_ms} ms</div>}
        </div>
      )}
    </div>
  );
}
