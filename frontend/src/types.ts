export interface Part {
  id: number;
  item_no: string;
  description: string;
  item_group: string | null;
  uom_group: string | null;
  in_stock: number | null;
  standard_cost?: number | null;
  avg_cost?: number | null;
  noun?: string | null;
}

export interface PartDetail extends Part {
  description_norm: string;
  attrs: Record<string, unknown>;
  modifiers: Record<string, string>;
  wtax_liable: boolean | null;
  is_active: boolean;
}

export interface PartInput {
  item_no?: string;
  description?: string;
  item_group?: string | null;
  uom_group?: string | null;
  standard_cost?: number | null;
  opening_stock?: number | null;
  is_active?: boolean;
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

export type CostIssue = "unmatched" | "no_qty" | "no_cost";

export interface CostingLine {
  line_id: number;
  line_no: number;
  raw_item_no: string | null;
  raw_description: string | null;
  part: Part | null;
  qty: number | null;
  total_qty: number | null;
  uom: string | null;
  unit_cost: number | null;
  cost_source: "avg_cost" | "standard_cost" | null;
  line_cost: number | null;
  issue: CostIssue | null;
}

export interface BomCosting {
  bom_id: number;
  bom_name: string;
  project: string | null;
  batch_qty: number;
  lines: CostingLine[];
  material_cost: number;
  unit_material_cost: number;
  line_count: number;
  costed_count: number;
  unmatched_count: number;
  uncosted_count: number;
}

export interface GrnLineInput {
  part_id: number;
  qty: number;
  unit_cost: number;
}

export interface GrnInput {
  supplier?: string | null;
  received_on?: string | null;
  remarks?: string | null;
  lines: GrnLineInput[];
}

export interface GrnSummary {
  id: number;
  grn_no: string;
  supplier: string | null;
  received_on: string;
  remarks: string | null;
  created_at: string;
  line_count: number;
  total_value: number;
}

export interface Grn extends GrnSummary {
  lines: { id: number; line_no: number; part_id: number; qty: number; unit_cost: number; part: Part }[];
}

export type MrStatus = "open" | "partial" | "issued";

export interface MrInput {
  department?: string | null;
  job_ref?: string | null;
  bom_id?: number | null;
  remarks?: string | null;
  lines: { part_id: number; qty_requested: number }[];
}

export interface MrSummary {
  id: number;
  mr_no: string;
  department: string | null;
  job_ref: string | null;
  bom_id: number | null;
  status: MrStatus;
  remarks: string | null;
  created_at: string;
  line_count: number;
}

export interface MrLine {
  id: number;
  line_no: number;
  part_id: number;
  qty_requested: number;
  qty_issued: number;
  part: Part;
}

export interface Mr extends MrSummary {
  lines: MrLine[];
}

export type StockAvailability = "all" | "in_stock" | "out_of_stock";

export interface StockItem extends Part {
  stock_value: number | null;
}

export interface StockResponse {
  items: StockItem[];
  total: number;
  total_value: number;
}

export interface LedgerEntry {
  id: number;
  txn_type: "OPENING" | "GRN" | "ISSUE";
  qty: number;
  unit_cost: number | null;
  ref_type: string | null;
  ref_id: number | null;
  ref_no: string | null;
  balance: number | null;
  created_at: string;
}

export interface ImportJob {
  id: string;
  status: "running" | "done" | "error";
  stage: string;
  info: Record<string, unknown>;
  stats: Record<string, unknown> | null;
  error: string | null;
}
