import { X } from "lucide-react";
import type { StockSignal } from "../types";
import { money } from "../utils/format";
import { ActionBadge } from "./ActionBadge";
import { RiskBadge } from "./RiskBadge";

export function ExplanationPanel({ signal, onClose }: { signal: StockSignal | null; onClose: () => void }) {
  if (!signal) return null;
  const explanation = signal.explanation || {};
  const bullish = explanation.bullish_factors || [];
  const risks = [
    ...(explanation.bearish_or_risk_factors || explanation.bearish_risk_factors || []),
    ...(explanation.warnings || []),
  ];

  return (
    <aside className="fixed inset-y-0 right-0 z-40 w-full max-w-xl overflow-y-auto border-l border-borderDeep bg-panel p-6 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.16em] text-cyan">Signal explanation</p>
          <h2 className="mt-2 text-3xl font-black">{signal.ticker}</h2>
          <p className="text-soft">{signal.company_name}</p>
        </div>
        <button className="rounded-xl border border-borderDeep p-2 text-soft hover:text-white" onClick={onClose}>
          <X size={20} />
        </button>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <ActionBadge label={signal.action_label} />
        <RiskBadge risk={signal.risk_level} />
      </div>

      <div className="mt-6 rounded-3xl border border-borderDeep bg-midnight p-5">
        <p className="text-lg leading-7">{explanation.summary || signal.main_reason}</p>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-3">
        <Metric label="Entry zone" value={`${money(signal.entry_low)} - ${money(signal.entry_high)}`} />
        <Metric label="Stop loss" value={money(signal.stop_loss)} tone="risk" />
        <Metric label="Target" value={money(signal.target_price)} tone="profit" />
        <Metric label="Paper size" value={`${signal.suggested_shares} shares`} />
      </div>

      <Section title="Bullish factors" items={bullish} empty="No strong bullish factors detected yet." />
      <Section title="Risk factors" items={risks} empty="No major risk warnings from the current rules." risk />

      <div className="mt-6 rounded-3xl border border-cyan/30 bg-cyan/10 p-5 text-sm leading-6 text-soft">
        <strong className="text-white">Risk note: </strong>
        {explanation.risk_management_note || "Use position sizing, review the setup, and paper trade before risking real money."}
      </div>
      <p className="mt-4 text-xs leading-5 text-soft">
        This is a research signal. No outcome is guaranteed. Signals are informational, not financial advice.
      </p>
    </aside>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: "risk" | "profit" }) {
  const color = tone === "risk" ? "text-risk" : tone === "profit" ? "text-profit" : "text-white";
  return (
    <div className="rounded-2xl bg-midnight p-4">
      <div className="text-xs uppercase tracking-[0.14em] text-soft">{label}</div>
      <div className={`tabular mt-2 font-mono text-lg font-black ${color}`}>{value}</div>
    </div>
  );
}

function Section({ title, items, empty, risk = false }: { title: string; items: string[]; empty: string; risk?: boolean }) {
  return (
    <section className="mt-6">
      <h3 className="text-sm font-black uppercase tracking-[0.16em] text-soft">{title}</h3>
      <div className="mt-3 space-y-3">
        {(items.length ? items : [empty]).map((item) => (
          <div key={item} className={`rounded-2xl border p-4 text-sm leading-6 ${risk ? "border-risk/30 bg-risk/10" : "border-profit/30 bg-profit/10"}`}>
            {item}
          </div>
        ))}
      </div>
    </section>
  );
}
