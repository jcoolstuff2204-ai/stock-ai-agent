import { CircleAlert, Plus, ShieldCheck } from "lucide-react";
import { ActionBadge } from "./ActionBadge";
import { RiskBadge } from "./RiskBadge";
import { ScoreBreakdown } from "./ScoreBreakdown";
import type { StockSignal } from "../types";
import { money } from "../utils/format";

type Props = {
  signal: StockSignal;
  rank?: number;
  onSelect: (signal: StockSignal) => void;
  onPaperTrade: (signal: StockSignal) => void;
};

export function StockSignalCard({ signal, rank, onSelect, onPaperTrade }: Props) {
  return (
    <article className="rounded-3xl border border-borderDeep bg-panel p-5 shadow-glow">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            {rank ? <span className="text-sm font-bold text-cyan">#{rank}</span> : null}
            <h3 className="text-2xl font-black tracking-normal">{signal.ticker}</h3>
          </div>
          <p className="mt-1 line-clamp-1 text-sm text-soft">{signal.company_name}</p>
        </div>
        <div className="text-right">
          <div className="tabular font-mono text-lg font-bold">{money(signal.price)}</div>
          <div className="text-xs text-soft">last price</div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <ActionBadge label={signal.action_label} />
        <RiskBadge risk={signal.risk_level} />
        {signal.do_not_trade ? (
          <span className="inline-flex items-center gap-1 rounded-full border border-risk/40 bg-risk/10 px-3 py-1 text-xs font-bold text-risk">
            <CircleAlert size={14} /> Do not trade
          </span>
        ) : null}
      </div>

      <p className="mt-4 min-h-12 text-sm leading-6 text-soft">{signal.main_reason}</p>
      <div className="mt-5">
        <ScoreBreakdown signal={signal} />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-2xl bg-midnight p-3">
          <div className="text-soft">Entry zone</div>
          <div className="tabular font-mono font-bold">{money(signal.entry_low)} - {money(signal.entry_high)}</div>
        </div>
        <div className="rounded-2xl bg-midnight p-3">
          <div className="text-soft">Suggested size</div>
          <div className="tabular font-mono font-bold">{signal.suggested_shares} sh / {money(signal.suggested_position_value)}</div>
        </div>
      </div>

      <div className="mt-5 flex gap-3">
        <button
          className="rounded-2xl border border-borderDeep px-4 py-3 text-sm font-bold text-soft transition hover:border-cyan hover:text-white"
          onClick={() => onSelect(signal)}
        >
          Why?
        </button>
        <button
          className="inline-flex flex-1 items-center justify-center gap-2 rounded-2xl bg-cyan px-4 py-3 text-sm font-black text-midnight transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={() => onPaperTrade(signal)}
          disabled={signal.do_not_trade || signal.suggested_shares <= 0}
        >
          {signal.do_not_trade ? <ShieldCheck size={16} /> : <Plus size={16} />}
          Add paper trade
        </button>
      </div>
    </article>
  );
}
