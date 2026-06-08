import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Bot, ClipboardList, Gauge, LineChart, Settings, ShieldCheck } from "lucide-react";
import { api } from "./api/client";
import { ExplanationPanel } from "./components/ExplanationPanel";
import { HomePage } from "./pages/HomePage";
import { PaperTradingPage } from "./pages/PaperTradingPage";
import { SettingsPage } from "./pages/SettingsPage";
import { SignalsPage } from "./pages/SignalsPage";
import type { PageKey, PaperTrade, ScanResponse, StockSignal, UserSettings } from "./types";

const defaultSettings: UserSettings = {
  account_size: 1000,
  risk_per_trade_percent: 1,
  max_position_percent: 15,
  max_positions: 5,
  min_price: 5,
  min_avg_volume: 500000,
  avoid_penny_stocks: true,
  paper_mode_enabled: true,
  universe: [],
};

export default function App() {
  const [page, setPage] = useState<PageKey>("dashboard");
  const [settings, setSettings] = useState<UserSettings>(defaultSettings);
  const [signals, setSignals] = useState<StockSignal[]>([]);
  const [selectedSignal, setSelectedSignal] = useState<StockSignal | null>(null);
  const [scanMeta, setScanMeta] = useState<ScanResponse | null>(null);
  const [trades, setTrades] = useState<PaperTrade[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [status, setStatus] = useState("Ready to scan");

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    try {
      const [savedSettings, latestSignals, paperTrades] = await Promise.all([
        api.getSettings(),
        api.latestSignals().catch(() => []),
        api.listPaperTrades().catch(() => []),
      ]);
      setSettings(savedSettings);
      setSignals(latestSignals);
      setTrades(paperTrades);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Backend is not reachable yet.");
    }
  }

  async function runScan() {
    setIsScanning(true);
    setStatus("Scanning market...");
    try {
      const response = await api.runScan(settings);
      setScanMeta(response);
      setSignals(response.results);
      setStatus(`Scan complete: ${response.results.length} symbols ranked`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Scan failed.");
    } finally {
      setIsScanning(false);
    }
  }

  async function saveSettings() {
    try {
      const saved = await api.saveSettings(settings);
      setSettings(saved);
      setStatus("Settings saved");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not save settings.");
    }
  }

  async function addPaperTrade(signal: StockSignal) {
    try {
      await api.addPaperTrade(signal);
      setTrades(await api.listPaperTrades());
      setStatus(`${signal.ticker} added to paper trades`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not add paper trade.");
    }
  }

  async function closePaperTrade(trade: PaperTrade) {
    const closePrice = window.prompt(`Close ${trade.ticker} at what price?`, trade.target_price.toString());
    if (!closePrice) return;
    try {
      await api.closePaperTrade(trade.id, Number(closePrice));
      setTrades(await api.listPaperTrades());
      setStatus(`${trade.ticker} paper trade closed`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not close paper trade.");
    }
  }

  const currentPage = useMemo(() => {
    if (page === "signals") return <SignalsPage signals={signals} onSelect={setSelectedSignal} onPaperTrade={addPaperTrade} />;
    if (page === "paper") return <PaperTradingPage trades={trades} onCloseTrade={closePaperTrade} />;
    if (page === "settings") return <SettingsPage settings={settings} onChange={setSettings} onSave={saveSettings} />;
    return (
      <HomePage
        signals={signals}
        settings={settings}
        isScanning={isScanning}
        demoMode={Boolean(scanMeta?.demo_data_mode || signals.some((signal) => signal.demo_data))}
        onRunScan={runScan}
        onSelect={setSelectedSignal}
        onPaperTrade={addPaperTrade}
      />
    );
  }, [page, signals, settings, isScanning, scanMeta, trades]);

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-borderDeep bg-midnight/95 p-5 lg:block">
        <Brand />
        <nav className="mt-10 space-y-2">
          <NavButton icon={<Gauge size={18} />} label="Dashboard" active={page === "dashboard"} onClick={() => setPage("dashboard")} />
          <NavButton icon={<LineChart size={18} />} label="Signals" active={page === "signals"} onClick={() => setPage("signals")} />
          <NavButton icon={<ClipboardList size={18} />} label="Paper Trading" active={page === "paper"} onClick={() => setPage("paper")} />
          <NavButton icon={<Settings size={18} />} label="Settings" active={page === "settings"} onClick={() => setPage("settings")} />
        </nav>
        <div className="absolute bottom-5 left-5 right-5 rounded-3xl border border-borderDeep bg-panel p-4 text-sm leading-6 text-soft">
          <ShieldCheck className="mb-3 text-cyan" size={22} />
          Educational research only. Signals are not financial advice. No result is guaranteed.
        </div>
      </aside>

      <main className="lg:pl-72">
        <header className="sticky top-0 z-30 border-b border-borderDeep bg-midnight/80 px-4 py-4 backdrop-blur md:px-8">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
            <div className="lg:hidden"><Brand compact /></div>
            <div className="hidden text-sm text-soft lg:block">{status}</div>
            <div className="flex flex-wrap gap-2 lg:hidden">
              <MobileTab label="Home" active={page === "dashboard"} onClick={() => setPage("dashboard")} />
              <MobileTab label="Signals" active={page === "signals"} onClick={() => setPage("signals")} />
              <MobileTab label="Paper" active={page === "paper"} onClick={() => setPage("paper")} />
              <MobileTab label="Settings" active={page === "settings"} onClick={() => setPage("settings")} />
            </div>
            <button className="rounded-2xl bg-cyan px-4 py-3 text-sm font-black text-midnight" onClick={runScan} disabled={isScanning}>
              {isScanning ? "Scanning..." : "Run Scan"}
            </button>
          </div>
        </header>
        <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">{currentPage}</div>
      </main>
      <ExplanationPanel signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}

function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan/30 bg-panel shadow-glow">
        <Bot className="text-cyan" size={24} />
      </div>
      <div>
        <div className="text-lg font-black">QuanTrade AI Agent</div>
        {!compact ? <div className="text-sm text-soft">AI-powered stock scanner</div> : null}
      </div>
    </div>
  );
}

function NavButton({ icon, label, active, onClick }: { icon: ReactNode; label: string; active: boolean; onClick: () => void }) {
  return (
    <button className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left font-bold ${active ? "bg-cyan text-midnight" : "text-soft hover:bg-panel hover:text-white"}`} onClick={onClick}>
      {icon}
      {label}
    </button>
  );
}

function MobileTab({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return <button className={`rounded-xl px-3 py-2 text-xs font-bold ${active ? "bg-cyan text-midnight" : "border border-borderDeep text-soft"}`} onClick={onClick}>{label}</button>;
}
