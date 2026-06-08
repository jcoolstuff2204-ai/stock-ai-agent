import type { PaperTrade, ScanResponse, StockSignal, UserSettings } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  getSettings: () => request<UserSettings>("/api/settings"),
  saveSettings: (settings: UserSettings) =>
    request<UserSettings>("/api/settings", { method: "POST", body: JSON.stringify(settings) }),
  runScan: (settings: UserSettings) =>
    request<ScanResponse>("/api/scan", { method: "POST", body: JSON.stringify({ settings }) }),
  latestSignals: () => request<StockSignal[]>("/api/signals/latest"),
  listPaperTrades: () => request<PaperTrade[]>("/api/paper-trades"),
  addPaperTrade: (signal: StockSignal) =>
    request<PaperTrade>("/api/paper-trades", {
      method: "POST",
      body: JSON.stringify({
        ticker: signal.ticker,
        action: "BUY",
        entry_price: signal.price,
        stop_loss: signal.stop_loss,
        target_price: signal.target_price,
        shares: Math.max(1, signal.suggested_shares),
      }),
    }),
  closePaperTrade: (tradeId: number, closePrice: number) =>
    request<PaperTrade>(`/api/paper-trades/${tradeId}/close`, {
      method: "PATCH",
      body: JSON.stringify({ close_price: closePrice }),
    }),
};
