import { ActionBadge } from "./ActionBadge";
import { RiskBadge } from "./RiskBadge";
import type { StockSignal } from "../types";
import { money, score } from "../utils/format";

type Props = {
  signals: StockSignal[];
  onSelect: (signal: StockSignal) => void;
  onPaperTrade: (signal: StockSignal) => void;
};

export function SignalTable({ signals, onSelect, onPaperTrade }: Props) {
  return (
    <div className="overflow-hidden rounded-3xl border border-borderDeep bg-panel">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[980px] text-left text-sm">
          <thead className="bg-midnight text-xs uppercase tracking-[0.16em] text-soft">
            <tr>
              <th className="px-5 py-4">Rank</th>
              <th className="px-5 py-4">Ticker</th>
              <th className="px-5 py-4">Action</th>
              <th className="px-5 py-4">Score</th>
              <th className="px-5 py-4">Risk</th>
              <th className="px-5 py-4">Entry</th>
              <th className="px-5 py-4">Stop</th>
              <th className="px-5 py-4">Size</th>
              <th className="px-5 py-4">Reason</th>
              <th className="px-5 py-4">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-borderDeep">
            {signals.map((signal, index) => (
              <tr key={signal.ticker} className="align-top hover:bg-white/[0.03]">
                <td className="px-5 py-4 font-bold text-cyan">#{index + 1}</td>
                <td className="px-5 py-4">
                  <div className="text-lg font-black">{signal.ticker}</div>
                  <div className="max-w-44 truncate text-xs text-soft">{signal.company_name}</div>
                </td>
                <td className="px-5 py-4"><ActionBadge label={signal.action_label} /></td>
                <td className="px-5 py-4 tabular font-mono text-lg font-bold">{score(signal.promising_score)}</td>
                <td className="px-5 py-4"><RiskBadge risk={signal.risk_level} /></td>
                <td className="px-5 py-4 tabular font-mono">{money(signal.entry_low)} - {money(signal.entry_high)}</td>
                <td className="px-5 py-4 tabular font-mono text-risk">{money(signal.stop_loss)}</td>
                <td className="px-5 py-4 tabular font-mono">{signal.suggested_shares} sh</td>
                <td className="px-5 py-4 max-w-72 text-soft">{signal.main_reason}</td>
                <td className="px-5 py-4">
                  <div className="flex gap-2">
                    <button className="rounded-xl border border-borderDeep px-3 py-2 font-bold text-soft hover:text-white" onClick={() => onSelect(signal)}>
                      Why?
                    </button>
                    <button
                      className="rounded-xl bg-cyan px-3 py-2 font-black text-midnight disabled:opacity-50"
                      onClick={() => onPaperTrade(signal)}
                      disabled={signal.do_not_trade || signal.suggested_shares <= 0}
                    >
                      Paper
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
