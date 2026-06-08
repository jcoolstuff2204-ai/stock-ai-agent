import type { PaperTrade } from "../types";
import { money } from "../utils/format";

type Props = {
  trades: PaperTrade[];
  onCloseTrade: (trade: PaperTrade) => void;
};

export function PaperTradePanel({ trades, onCloseTrade }: Props) {
  const openTrades = trades.filter((trade) => trade.status === "OPEN");
  const closedTrades = trades.filter((trade) => trade.status === "CLOSED");
  const pnl = trades.reduce((sum, trade) => sum + (trade.realized_pnl || 0), 0);

  return (
    <section className="rounded-3xl border border-borderDeep bg-panel p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-black">Paper trading</h2>
          <p className="text-sm text-soft">Practice the plan before risking cash.</p>
        </div>
        <div className={`tabular font-mono text-2xl font-black ${pnl >= 0 ? "text-profit" : "text-risk"}`}>{money(pnl)}</div>
      </div>

      <TradeList title="Open trades" trades={openTrades} onCloseTrade={onCloseTrade} />
      <TradeList title="Closed trades" trades={closedTrades} />
    </section>
  );
}

function TradeList({ title, trades, onCloseTrade }: { title: string; trades: PaperTrade[]; onCloseTrade?: (trade: PaperTrade) => void }) {
  return (
    <div className="mt-5">
      <h3 className="text-sm font-black uppercase tracking-[0.16em] text-soft">{title}</h3>
      <div className="mt-3 space-y-3">
        {trades.length === 0 ? <div className="rounded-2xl bg-midnight p-4 text-sm text-soft">No {title.toLowerCase()} yet.</div> : null}
        {trades.map((trade) => (
          <div key={trade.id} className="grid gap-3 rounded-2xl border border-borderDeep bg-midnight p-4 md:grid-cols-[1fr_auto]">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xl font-black">{trade.ticker}</span>
                <span className="rounded-full border border-borderDeep px-3 py-1 text-xs font-bold text-soft">{trade.status}</span>
              </div>
              <div className="mt-2 grid gap-2 text-sm text-soft sm:grid-cols-4">
                <span>Entry <b className="tabular font-mono text-white">{money(trade.entry_price)}</b></span>
                <span>Stop <b className="tabular font-mono text-risk">{money(trade.stop_loss)}</b></span>
                <span>Target <b className="tabular font-mono text-profit">{money(trade.target_price)}</b></span>
                <span>Shares <b className="tabular font-mono text-white">{trade.shares}</b></span>
              </div>
            </div>
            {onCloseTrade ? (
              <button className="rounded-2xl border border-borderDeep px-4 py-3 text-sm font-bold text-soft hover:text-white" onClick={() => onCloseTrade(trade)}>
                Close
              </button>
            ) : (
              <div className={`tabular font-mono font-bold ${Number(trade.realized_pnl || 0) >= 0 ? "text-profit" : "text-risk"}`}>{money(trade.realized_pnl || 0)}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
