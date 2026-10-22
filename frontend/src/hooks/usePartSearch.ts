import { useEffect, useState } from "react";
import { api } from "../api";
import type { PartSearchResponse } from "../types";

export const MIN_QUERY_LENGTH = 2;
const DEBOUNCE_MS = 200;

interface State {
  data: PartSearchResponse | null;
  loading: boolean;
  error: string | null;
}

/** Debounced part search; outdated requests are aborted so results never arrive out of order. */
export function usePartSearch(query: string, opts: { group?: string | null; limit?: number; enabled?: boolean } = {}) {
  const { group = null, limit = 20, enabled = true } = opts;
  const [state, setState] = useState<State>({ data: null, loading: false, error: null });

  useEffect(() => {
    const q = query.trim();
    if (!enabled || q.length < MIN_QUERY_LENGTH) {
      setState({ data: null, loading: false, error: null });
      return;
    }
    const controller = new AbortController();
    setState((s) => ({ ...s, loading: true, error: null }));
    const timer = window.setTimeout(() => {
      api
        .searchParts(q, { group, limit, signal: controller.signal })
        .then((data) => setState({ data, loading: false, error: null }))
        .catch((err: unknown) => {
          if (controller.signal.aborted) return;
          setState({ data: null, loading: false, error: err instanceof Error ? err.message : String(err) });
        });
    }, DEBOUNCE_MS);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [query, group, limit, enabled]);

  return state;
}
