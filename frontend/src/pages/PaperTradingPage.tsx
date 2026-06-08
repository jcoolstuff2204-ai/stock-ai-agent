import { PaperTradePanel } from "../components/PaperTradePanel";
import type { PaperTrade } from "../types";

export function PaperTradingPage({ trades, onCloseTrade }: { trades: PaperTrade[]; onCloseTrade: (trade: PaperTrade) => void }) {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-black">Paper trading journal</h1>
        <p className="mt-1 text-soft">Track ideas without live orders. No brokerage execution is enabled in v1.</p>
      </div>
      <PaperTradePanel trades={trades} onCloseTrade={onCloseTrade} />
    </div>
  );
}
