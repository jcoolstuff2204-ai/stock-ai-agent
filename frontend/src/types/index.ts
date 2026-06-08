export type RiskLevel = "Low" | "Medium" | "High";

export type UserSettings = {
  account_size: number;
  risk_per_trade_percent: number;
  max_position_percent: number;
  max_positions: number;
  min_price: number;
  min_avg_volume: number;
  avoid_penny_stocks: boolean;
  paper_mode_enabled: boolean;
  universe: string[];
};

export type SignalExplanation = {
  summary?: string;
  bullish_factors?: string[];
  bearish_or_risk_factors?: string[];
  bearish_risk_factors?: string[];
  risk_management_note?: string;
  suggested_next_action?: string;
  warnings?: string[];
};

export type StockSignal = {
  ticker: string;
  company_name: string;
  price: number;
  action_label: string;
  confidence_score: number;
  promising_score: number;
  risk_level: RiskLevel;
  entry_low: number;
  entry_high: number;
  stop_loss: number;
  target_price: number;
  suggested_shares: number;
  suggested_position_value: number;
  main_reason: string;
  explanation: SignalExplanation;
  demo_data: boolean;
  do_not_trade: boolean;
};

export type ScanResponse = {
  scan_date: string;
  demo_data_mode: boolean;
  disclosure: string;
  results: StockSignal[];
};

export type PaperTrade = {
  id: number;
  ticker: string;
  action: string;
  entry_price: number;
  stop_loss: number;
  target_price: number;
  shares: number;
  opened_at: string;
  closed_at: string | null;
  close_price: number | null;
  status: "OPEN" | "CLOSED";
  realized_pnl: number | null;
};

export type PageKey = "dashboard" | "signals" | "paper" | "settings";
