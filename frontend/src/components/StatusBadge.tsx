import type { MatchStatus } from "../types";

export const STATUS_LABELS: Record<MatchStatus, string> = {
  exact_item_no: "Item no.",
  exact_desc: "Exact",
  auto: "Auto",
  review: "Review",
  unmatched: "Unmatched",
  manual: "Manual",
};

export const STATUS_ORDER: MatchStatus[] = ["review", "unmatched", "auto", "exact_desc", "exact_item_no", "manual"];

export function StatusBadge({ status, score }: { status: MatchStatus; score?: number | null }) {
  return (
    <span className={`badge st-${status}`}>
      {STATUS_LABELS[status]}
      {score != null && status !== "exact_item_no" && status !== "exact_desc" && (
        <span className="badge-score">{Math.round(score)}</span>
      )}
    </span>
  );
}
