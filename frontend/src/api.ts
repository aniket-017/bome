import type {
  Bom,
  BomLine,
  BomLineInput,
  BomSummary,
  ColumnField,
  GroupCount,
  ImportJob,
  PartSearchResponse,
  UploadPreview,
} from "./types";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const res = await fetch(path, { ...init, headers });
  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = await res.json();
      message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? body);
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, message);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

const json = (body: unknown) => JSON.stringify(body);

export const api = {
  searchParts(q: string, opts: { group?: string | null; limit?: number; offset?: number; signal?: AbortSignal } = {}) {
    const params = new URLSearchParams({ q, limit: String(opts.limit ?? 20), offset: String(opts.offset ?? 0) });
    if (opts.group) params.set("group", opts.group);
    return request<PartSearchResponse>(`/api/parts/search?${params}`, { signal: opts.signal });
  },
  partGroups: () => request<GroupCount[]>("/api/parts/groups"),
  partStats: () => request<{ total: number; active: number }>("/api/parts/stats"),

  listBoms: () => request<BomSummary[]>("/api/boms"),
  getBom: (id: number) => request<Bom>(`/api/boms/${id}`),
  deleteBom: (id: number) => request<void>(`/api/boms/${id}`, { method: "DELETE" }),
  createBom: (body: { name: string; project?: string | null; lines: BomLineInput[]; auto_match?: boolean }) =>
    request<Bom>("/api/boms", { method: "POST", body: json(body) }),
  matchBom: (id: number, force = false) =>
    request<Bom>(`/api/boms/${id}/match`, { method: "POST", body: json({ force }) }),
  acceptBom: (id: number, body: { line_ids?: number[]; min_score?: number }) =>
    request<Bom>(`/api/boms/${id}/accept`, { method: "POST", body: json(body) }),
  addLine: (bomId: number, line: BomLineInput) =>
    request<BomLine>(`/api/boms/${bomId}/lines`, { method: "POST", body: json(line) }),
  updateLine: (
    bomId: number,
    lineId: number,
    body: BomLineInput & { clear_match?: boolean; rematch?: boolean },
  ) => request<BomLine>(`/api/boms/${bomId}/lines/${lineId}`, { method: "PATCH", body: json(body) }),
  deleteLine: (bomId: number, lineId: number) =>
    request<void>(`/api/boms/${bomId}/lines/${lineId}`, { method: "DELETE" }),
  exportUrl: (id: number) => `/api/boms/${id}/export`,
  imageUrl: (id: number) => `/api/boms/${id}/image`,

  previewUpload(file: File, sheet?: string, headerRow?: number) {
    const fd = new FormData();
    fd.append("file", file);
    if (sheet) fd.append("sheet", sheet);
    if (headerRow !== undefined) fd.append("header_row", String(headerRow));
    return request<UploadPreview>("/api/boms/upload/preview", { method: "POST", body: fd });
  },
  uploadBom(
    file: File,
    meta: { name: string; project?: string; sheet?: string; header_row: number; mapping: Partial<Record<ColumnField, number>> },
  ) {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("name", meta.name);
    if (meta.project) fd.append("project", meta.project);
    if (meta.sheet) fd.append("sheet", meta.sheet);
    fd.append("header_row", String(meta.header_row));
    fd.append("mapping", JSON.stringify(meta.mapping));
    return request<Bom>("/api/boms/upload", { method: "POST", body: fd });
  },
  uploadBomImage(file: File, meta: { name: string; project?: string }) {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("name", meta.name);
    if (meta.project) fd.append("project", meta.project);
    return request<Bom>("/api/boms/upload-image", { method: "POST", body: fd });
  },

  startPartsImport(file: File, sheet?: string) {
    const fd = new FormData();
    fd.append("file", file);
    if (sheet) fd.append("sheet", sheet);
    return request<ImportJob>("/api/admin/import-parts", { method: "POST", body: fd });
  },
  importJob: (id: string) => request<ImportJob>(`/api/admin/import-jobs/${id}`),
  adminConfig: () => request<{ vision_provider: string; vision_configured: boolean }>("/api/admin/config"),
};
