import { Activity, BadgeDollarSign, ShieldAlert, Target } from "lucide-react";
import type { ReactNode } from "react";
import { StockSignalCard } from "../components/StockSignalCard";
import type { StockSignal, UserSettings } from "../types";
import { money } from "../utils/format";

type Props = {
  signals: StockSignal[];
  settings: UserSettings;
  isScanning: boolean;
  demoMode: boolean;
  onRunScan: () => void;
  onSelect: (signal: StockSignal) => void;
  onPaperTrade: (signal: StockSignal) => void;
};

export function HomePage({ signals, settings, isScanning, demoMode, onRunScan, onSelect, onPaperTrade }: Props) {
  const buyCandidates = signals.filter((signal) => signal.action_label.includes("Buy") && !signal.do_not_trade).slice(0, 5);
  const avoidCandidates = signals.filter((signal) => signal.action_label.includes("Avoid") || signal.do_not_trade).slice(0, 5);
  const watchlist = signals.filter((signal) => signal.action_label.includes("Watch")).slice(0, 5);

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-cyan/30 bg-gradient-to-br from-panel via-midnight to-panel p-6 shadow-glow lg:p-8">
        <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div>
            <div className="inline-flex rounded-full border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm font-bold text-cyan">
              Paper Mode Active
            </div>
            <h1 className="mt-5 max-w-3xl text-4xl font-black tracking-normal text-white md:text-6xl">
              Find risk-aware stock ideas before you trade.
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-soft">
              QuanTrade scans a starter universe, ranks promising buy candidates, flags avoid setups, and sizes every idea for a low-capital account.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                className="rounded-2xl bg-cyan px-6 py-4 font-black text-midnight transition hover:brightness-110 disabled:opacity-60"
                onClick={onRunScan}
                disabled={isScanning}
              >
                {isScanning ? "Scanning market..." : "Run Daily Scan"}
              </button>
              <span className="rounded-2xl border border-borderDeep px-4 py-4 text-sm font-bold text-soft">
                {demoMode ? "Demo data mode" : "Live market data when available"}
              </span>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <HeroMetric icon={<Target />} label="Top candidates" value={buyCandidates.length.toString()} />
            <HeroMetric icon={<Activity />} label="Scanned names" value={signals.length.toString()} />
            <HeroMetric icon={<BadgeDollarSign />} label="Account" value={money(settings.account_size)} />
            <HeroMetric icon={<ShieldAlert />} label="Max per stock" value={`${settings.max_position_percent}%`} />
          </div>
        </div>
      </section>

      <section>
        <SectionHeader title="Top promising buy candidates" subtitle="Names with stronger score, liquidity, trend, and position size fit." />
        <div className="mt-4 grid gap-4 xl:grid-cols-3">
          {buyCandidates.length ? buyCandidates.map((signal, index) => (
            <StockSignalCard key={signal.ticker} signal={signal} rank={index + 1} onSelect={onSelect} onPaperTrade={onPaperTrade} />
          )) : <Empty text="Run a scan to find buy candidates." />}
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <section>
          <SectionHeader title="Watchlist" subtitle="Interesting, but not ready enough for a small account." />
          <Stack signals={watchlist} empty="No watchlist ideas yet." onSelect={onSelect} onPaperTrade={onPaperTrade} />
        </section>
        <section>
          <SectionHeader title="Avoid / sell candidates" subtitle="Weak, too volatile, too illiquid, or outside risk rules." />
          <Stack signals={avoidCandidates} empty="No avoid candidates yet." onSelect={onSelect} onPaperTrade={onPaperTrade} />
        </section>
      </div>
    </div>
  );
}

function HeroMetric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-3xl border border-borderDeep bg-panel/80 p-5">
      <div className="text-cyan">{icon}</div>
      <div className="tabular mt-4 font-mono text-3xl font-black">{value}</div>
      <div className="mt-1 text-sm text-soft">{label}</div>
    </div>
  );
}

function SectionHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div>
      <h2 className="text-2xl font-black">{title}</h2>
      <p className="mt-1 text-soft">{subtitle}</p>
    </div>
  );
}

function Stack({ signals, empty, onSelect, onPaperTrade }: { signals: StockSignal[]; empty: string; onSelect: (signal: StockSignal) => void; onPaperTrade: (signal: StockSignal) => void }) {
  return <div className="mt-4 grid gap-4">{signals.length ? signals.map((signal) => <StockSignalCard key={signal.ticker} signal={signal} onSelect={onSelect} onPaperTrade={onPaperTrade} />) : <Empty text={empty} />}</div>;
}

function Empty({ text }: { text: string }) {
  return <div className="rounded-3xl border border-dashed border-borderDeep bg-panel p-8 text-soft">{text}</div>;
}
