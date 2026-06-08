import { PortfolioSettings } from "../components/PortfolioSettings";
import { WatchlistPanel } from "../components/WatchlistPanel";
import type { UserSettings } from "../types";

export function SettingsPage({ settings, onChange, onSave }: { settings: UserSettings; onChange: (settings: UserSettings) => void; onSave: () => void }) {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-black">Settings</h1>
        <p className="mt-1 text-soft">Tune the scanner for your account size and opportunity universe.</p>
      </div>
      <PortfolioSettings settings={settings} onChange={onChange} onSave={onSave} />
      <WatchlistPanel settings={settings} onChange={onChange} />
    </div>
  );
}
