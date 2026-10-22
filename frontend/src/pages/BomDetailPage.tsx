import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { BomReviewGrid, type LineActions } from "../components/BomReviewGrid";
import { PartAutocomplete } from "../components/PartAutocomplete";
import type { Bom, BomLine, BomLineInput } from "../types";

export function BomDetailPage() {
  const id = Number(useParams().id);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const bomQuery = useQuery({ queryKey: ["bom", id], queryFn: () => api.getBom(id) });
  const [busyLines, setBusyLines] = useState<Set<number>>(new Set());
  const [pageBusy, setPageBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showImage, setShowImage] = useState(true);

  const replaceLine = (line: BomLine) =>
    qc.setQueryData<Bom>(["bom", id], (b) => (b ? { ...b, lines: b.lines.map((l) => (l.id === line.id ? line : l)) } : b));

  const lineMutation = useMutation({
    mutationFn: ({ line, body }: { line: BomLine; body: BomLineInput & { clear_match?: boolean } }) =>
      api.updateLine(id, line.id, body),
    onMutate: ({ line }) => setBusyLines((s) => new Set(s).add(line.id)),
    onSuccess: (updated) => {
      replaceLine(updated);
      void qc.invalidateQueries({ queryKey: ["bom", id] });
    },
    onError: (e) => setError(e instanceof Error ? e.message : String(e)),
    onSettled: (_d, _e, { line }) =>
      setBusyLines((s) => {
        const n = new Set(s);
        n.delete(line.id);
        return n;
      }),
  });

  const runPageAction = async (label: string, fn: () => Promise<unknown>) => {
    setPageBusy(label);
    setError(null);
    try {
      await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setPageBusy(null);
    }
  };

  const actions: LineActions = {
    setPart: (line, partId) => lineMutation.mutate({ line, body: { matched_part_id: partId } }),
    clear: (line) => lineMutation.mutate({ line, body: { clear_match: true } }),
    editText: (line, description) => lineMutation.mutate({ line, body: { raw_description: description } }),
    editQty: (line, qty) => lineMutation.mutate({ line, body: { qty } }),
    remove: (line) =>
      runPageAction("Deleting line...", async () => {
        await api.deleteLine(id, line.id);
        await qc.invalidateQueries({ queryKey: ["bom", id] });
      }),
  };

  if (bomQuery.isLoading) return <div className="page"><span className="spinner" /> Loading BOM...</div>;
  if (bomQuery.error || !bomQuery.data)
    return <div className="page error">Could not load BOM: {String(bomQuery.error)}</div>;
  const bom = bomQuery.data;
  const reviewCount = bom.lines.filter((l) => l.match_status === "review" && l.candidates.length).length;
  const matched = bom.lines.filter((l) => l.matched_part).length;
  const hasImage = bom.source_type === "image" && !!bom.image_path;

  return (
    <div className="page wide">
      <header className="page-header">
        <div>
          <h1>{bom.name}</h1>
          <div className="muted">
            {bom.project && <>{bom.project} · </>}
            {bom.source_type === "excel" ? `Excel: ${bom.source_file}` : bom.source_type === "image" ? "From image" : "Manual entry"}
            {" · "}
            {matched} of {bom.lines.length} lines linked to master parts
          </div>
        </div>
        <div className="actions">
          {hasImage && <button onClick={() => setShowImage((v) => !v)}>{showImage ? "Hide" : "Show"} image</button>}
          <button
            disabled={!!pageBusy}
            onClick={() =>
              runPageAction("Re-matching...", async () => {
                qc.setQueryData(["bom", id], await api.matchBom(id));
              })
            }
            title="Re-run matching for all lines that were not set manually"
          >
            Re-match
          </button>
          <button
            disabled={!!pageBusy || reviewCount === 0}
            onClick={() =>
              runPageAction("Accepting suggestions...", async () => {
                qc.setQueryData(["bom", id], await api.acceptBom(id, {}));
              })
            }
            title="Link every 'Review' line to its top suggestion"
          >
            Accept all suggestions ({reviewCount})
          </button>
          <a className="btn primary" href={api.exportUrl(id)}>
            Export Excel
          </a>
          <button
            className="danger"
            disabled={!!pageBusy}
            onClick={() => {
              if (confirm(`Delete BOM "${bom.name}"?`))
                void runPageAction("Deleting...", async () => {
                  await api.deleteBom(id);
                  await qc.invalidateQueries({ queryKey: ["boms"] });
                  navigate("/boms");
                });
            }}
          >
            Delete
          </button>
        </div>
      </header>

      {pageBusy && (
        <p className="busy">
          <span className="spinner" /> {pageBusy}
        </p>
      )}
      {error && <div className="error">{error}</div>}

      <div className={hasImage && showImage ? "split" : ""}>
        {hasImage && showImage && (
          <aside className="card image-pane">
            {bom.image_path?.toLowerCase().endsWith(".pdf") ? (
              <iframe className="pdf-preview" src={api.imageUrl(id)} title="Source drawing" />
            ) : (
              <img src={api.imageUrl(id)} alt="Source BOM" />
            )}
          </aside>
        )}
        <section className="card">
          <BomReviewGrid lines={bom.lines} actions={actions} busyLineIds={busyLines} />
          <AddLine bomId={id} />
        </section>
      </div>
    </div>
  );
}

function AddLine({ bomId }: { bomId: number }) {
  const qc = useQueryClient();
  const [desc, setDesc] = useState("");
  const [qty, setQty] = useState("");
  const [key, setKey] = useState(0);
  const add = useMutation({
    mutationFn: (body: BomLineInput) => api.addLine(bomId, body),
    onSuccess: () => {
      setDesc("");
      setQty("");
      setKey((k) => k + 1);
      void qc.invalidateQueries({ queryKey: ["bom", bomId] });
    },
  });
  return (
    <div className="add-line">
      <h3>Add line</h3>
      <div className="add-line-row">
        <PartAutocomplete
          key={key}
          compact
          placeholder="Type a description (pick from the list to link directly)"
          onQueryChange={setDesc}
          onSelect={(p) => add.mutate({ raw_description: p.description, matched_part_id: p.id, qty: qty ? Number(qty) : null })}
        />
        <input type="number" placeholder="Qty" value={qty} onChange={(e) => setQty(e.target.value)} />
        <button
          disabled={!desc.trim() || add.isPending}
          onClick={() => add.mutate({ raw_description: desc.trim(), qty: qty ? Number(qty) : null })}
        >
          {add.isPending ? "Adding..." : "Add & match"}
        </button>
      </div>
    </div>
  );
}
