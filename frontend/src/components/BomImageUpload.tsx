import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const ACCEPT = ".png,.jpg,.jpeg,.webp,.pdf";
const ALLOWED_TYPES: Record<string, string> = {
  "image/png": "png",
  "image/jpeg": "jpg",
  "image/webp": "webp",
  "application/pdf": "pdf",
};

export function BomImageUpload() {
  const navigate = useNavigate();
  const config = useQuery({ queryKey: ["admin-config"], queryFn: api.adminConfig });
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [project, setProject] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const pickFile = (f: File | undefined | null) => {
    if (!f) return;
    if (!ALLOWED_TYPES[f.type]) {
      setError("Use a PNG, JPG, WEBP image or a PDF drawing");
      return;
    }
    // pasted screenshots arrive as "image.png"; give them a unique name
    const named = f.name && f.name !== "image.png" ? f : new File([f], `pasted-${Date.now()}.${ALLOWED_TYPES[f.type]}`, { type: f.type });
    setError(null);
    setFile(named);
    setName((n) => n || named.name.replace(/\.[^.]+$/, ""));
  };

  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  useEffect(() => {
    const onPaste = (e: ClipboardEvent) => {
      const item = Array.from(e.clipboardData?.items ?? []).find((i) => i.type.startsWith("image/"));
      if (item) pickFile(item.getAsFile());
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, []);

  const submit = async () => {
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      const bom = await api.uploadBomImage(file, { name: name.trim() || file.name, project: project.trim() || undefined });
      navigate(`/boms/${bom.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setBusy(false);
    }
  };

  const configured = config.data?.vision_configured;
  const isPdf = file?.type === "application/pdf";
  const pdfUnsupported = isPdf && config.data && config.data.vision_provider !== "gemini";

  return (
    <div>
      {config.data && !configured && (
        <div className="notice">
          Image reading is not set up yet. Add an API key for <strong>{config.data.vision_provider}</strong> in{" "}
          <code>backend/.env</code> (<code>OPENAI_API_KEY</code> or <code>GEMINI_API_KEY</code> with{" "}
          <code>VISION_PROVIDER</code>) and restart the backend.
        </div>
      )}
      <p className="muted">
        Upload a drawing with a bill of material (PDF or image), or a photo, scan or screenshot of a BOM table. The
        BOM lines are read by {config.data ? config.data.vision_provider : "the vision AI"}, then matched against the
        parts master like an Excel upload. You can also paste a screenshot with Ctrl+V.
      </p>

      <label
        className={`dropzone ${dragOver ? "over" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          pickFile(e.dataTransfer.files[0]);
        }}
      >
        <input type="file" accept={ACCEPT} onChange={(e) => pickFile(e.target.files?.[0])} hidden />
        {file ? (
          <span>
            <strong>{file.name}</strong> <span className="muted">(click to choose another image)</span>
          </span>
        ) : (
          <span>Drop a drawing (PDF / image) here, click to choose, or paste a screenshot</span>
        )}
      </label>

      {error && <div className="error">{error}</div>}

      {file && previewUrl && (
        <>
          <div className="form-row">
            <div>
              <label>BOM name</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
              <label>Project (optional)</label>
              <input type="text" value={project} onChange={(e) => setProject(e.target.value)} />
            </div>
          </div>
          <div className="image-preview">
            {isPdf ? (
              <iframe className="pdf-preview" src={previewUrl} title="Drawing to read" />
            ) : (
              <img src={previewUrl} alt="BOM to read" />
            )}
          </div>
          {pdfUnsupported && (
            <div className="error">
              PDF drawings need <code>VISION_PROVIDER=gemini</code> in <code>backend/.env</code>. Upload a PNG/JPG
              of the drawing instead, or switch the provider.
            </div>
          )}
          {busy && (
            <p className="busy">
              <span className="spinner" /> Reading the image and matching lines against the parts master... this can
              take up to a minute.
            </p>
          )}
          <div className="actions-row">
            <button className="primary" disabled={busy || !configured || !!pdfUnsupported} onClick={submit}>
              Read BOM and match
            </button>
          </div>
        </>
      )}
    </div>
  );
}
