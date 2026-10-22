export interface Part {
  id: number;
  item_no: string;
  description: string;
  item_group: string | null;
  uom_group: string | null;
  in_stock: number | null;
  noun?: string | null;
}

export interface PartSearchItem extends Part {
  score: number;
}

export interface PartSearchResponse {
  items: PartSearchItem[];
  fuzzy: boolean;
  corrected_query: string | null;
  took_ms: number;
}

export interface GroupCount {
  item_group: string | null;
  count: number;
}

export type MatchStatus = "exact_item_no" | "exact_desc" | "auto" | "review" | "unmatched" | "manual";

export interface Candidate {
  part_id: number;
  item_no: string;
  description: string;
  item_group: string | null;
  score: number;
}

export interface BomLine {
  id: number;
  line_no: number;
  raw_item_no: string | null;
  raw_description: string | null;
  qty: number | null;
  uom: string | null;
  matched_part_id: number | null;
  match_score: number | null;
  match_status: MatchStatus;
  candidates: Candidate[];
  extra: Record<string, unknown>;
  matched_part: Part | null;
}

export interface BomSummary {
  id: number;
  name: string;
  project: string | null;
  source_type: "excel" | "manual" | "image";
  source_file: string | null;
  status: string;
  created_at: string;
  line_count: number;
  status_counts: Partial<Record<MatchStatus, number>>;
}

export interface Bom extends BomSummary {
  image_path: string | null;
  lines: BomLine[];
}

export interface BomLineInput {
  line_no?: number;
  raw_item_no?: string | null;
  raw_description?: string | null;
  qty?: number | null;
  uom?: string | null;
  matched_part_id?: number | null;
}

export type ColumnField = "line_no" | "item_no" | "description" | "qty" | "uom";

export interface UploadPreview {
  sheets: string[];
  sheet: string;
  header_row: number;
  headers: string[];
  rows: (string | number | null)[][];
  total_rows: number;
  suggested_mapping: Partial<Record<ColumnField, number>>;
}

export interface ImportJob {
  id: string;
  status: "running" | "done" | "error";
  stage: string;
  info: Record<string, unknown>;
  stats: Record<string, unknown> | null;
  error: string | null;
}
