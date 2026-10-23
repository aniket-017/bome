const moneyFmt = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 });
const qtyFmt = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 4 });

export const money = (n: number | null | undefined) => (n === null || n === undefined ? "" : moneyFmt.format(n));
export const qty = (n: number | null | undefined) => (n === null || n === undefined ? "" : qtyFmt.format(n));
export const dateTime = (iso: string) => new Date(iso).toLocaleString("en-IN");
export const date = (iso: string) => new Date(iso).toLocaleDateString("en-IN");
export const errorText = (e: unknown) => (e instanceof Error ? e.message : String(e));

/** Unit cost used for costing and stock valuation: weighted average, else standard cost. */
export const unitCost = (p: { avg_cost?: number | null; standard_cost?: number | null }) =>
  p.avg_cost ?? p.standard_cost ?? null;
