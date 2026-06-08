import type { RiskLevel } from "../types";

const riskStyle: Record<RiskLevel, string> = {
  Low: "border-profit/40 bg-profit/10 text-profit",
  Medium: "border-cyan/40 bg-cyan/10 text-cyan",
  High: "border-risk/40 bg-risk/10 text-risk",
};

export function RiskBadge({ risk }: { risk: RiskLevel }) {
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-bold uppercase tracking-wide ${riskStyle[risk]}`}>
      {risk} risk
    </span>
  );
}
