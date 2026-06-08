import { useMemo, useState } from "react";
import { SignalTable } from "../components/SignalTable";
import type { StockSignal } from "../types";

export function SignalsPage({ signals, onSelect, onPaperTrade }: { signals: StockSignal[]; onSelect: (signal: StockSignal) => void; onPaperTrade: (signal: StockSignal) => void }) {
  const [query, setQuery] = useState("");
  const [action, setAction] = useState("All");
  const [risk, setRisk] = useState("All");
  const [minScore, setMinScore] = useState(0);

  const filtered = useMemo(() => {
    return signals.filter((signal) => {
      const matchQuery = `${signal.ticker} ${signal.company_name}`.toLowerCase().includes(query.toLowerCase());
      const matchAction = action === "All" || signal.action_label.includes(action);
      const matchRisk = risk === "All" || signal.risk_level === risk;
      return matchQuery && matchAction && matchRisk && signal.promising_score >= minScore;
    });
  }, [signals, query, action, risk, minScore]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-black">Full signal scanner</h1>
        <p className="mt-1 text-soft">Filter the market scan without entering tickers one by one.</p>
      </div>
      <div className="grid gap-3 rounded-3xl border border-borderDeep bg-panel p-4 lg:grid-cols-[1fr_auto_auto_auto]">
        <input className="rounded-2xl border border-borderDeep bg-midnight px-4 py-3 outline-none focus:border-cyan" placeholder="Search ticker or company" value={query} onChange={(event) => setQuery(event.target.value)} />
        <select className="rounded-2xl border border-borderDeep bg-midnight px-4 py-3 outline-none" value={action} onChange={(event) => setAction(event.target.value)}>
          {["All", "Buy", "Watch", "Hold", "Avoid"].map((item) => <option key={item}>{item}</option>)}
        </select>
        <select className="rounded-2xl border border-borderDeep bg-midnight px-4 py-3 outline-none" value={risk} onChange={(event) => setRisk(event.target.value)}>
          {["All", "Low", "Medium", "High"].map((item) => <option key={item}>{item}</option>)}
        </select>
        <label className="flex items-center gap-3 rounded-2xl border border-borderDeep bg-midnight px-4 py-3 text-sm text-soft">
          Min score
          <input className="w-24 bg-transparent font-mono text-white outline-none" type="number" value={minScore} onChange={(event) => setMinScore(Number(event.target.value))} />
        </label>
      </div>
      <SignalTable signals={filtered} onSelect={onSelect} onPaperTrade={onPaperTrade} />
    </div>
  );
}
