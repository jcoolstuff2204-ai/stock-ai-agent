function actionClass(label: string): string {
  if (label.includes("Strong") || label.includes("Buy")) return "border-profit/40 bg-profit/10 text-profit";
  if (label.includes("Avoid") || label.includes("Sell")) return "border-risk/40 bg-risk/10 text-risk";
  if (label.includes("Watch")) return "border-cyan/40 bg-cyan/10 text-cyan";
  return "border-borderDeep bg-panel text-soft";
}

export function ActionBadge({ label }: { label: string }) {
  return <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-bold ${actionClass(label)}`}>{label}</span>;
}
