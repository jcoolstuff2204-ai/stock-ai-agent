import type { StockSignal } from "../types";
import { score } from "../utils/format";

export function ScoreBreakdown({ signal }: { signal: StockSignal }) {
  const rows = [
    ["Promising score", signal.promising_score],
    ["Confidence", signal.confidence_score],
  ];

  return (
    <div className="space-y-3">
      {rows.map(([label, value]) => (
        <div key={label}>
          <div className="mb-1 flex items-center justify-between text-xs text-soft">
            <span>{label}</span>
            <span className="tabular font-mono">{score(Number(value))}/100</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-midnight">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan to-purpleAi"
              style={{ width: `${Math.min(100, Number(value))}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
