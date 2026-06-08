import type { UserSettings } from "../types";
import { compactNumber } from "../utils/format";

type Props = {
  settings: UserSettings;
  onChange: (settings: UserSettings) => void;
  onSave: () => void;
};

export function PortfolioSettings({ settings, onChange, onSave }: Props) {
  const update = (key: keyof UserSettings, value: number | boolean | string[]) => onChange({ ...settings, [key]: value });

  return (
    <section className="rounded-3xl border border-borderDeep bg-panel p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-black">Low-capital risk rules</h2>
          <p className="text-sm text-soft">The scanner sizes ideas around your account before showing them as tradable.</p>
        </div>
        <button className="rounded-2xl bg-cyan px-4 py-3 font-black text-midnight" onClick={onSave}>Save</button>
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <NumberField label="Account size" value={settings.account_size} onChange={(v) => update("account_size", v)} prefix="$" />
        <NumberField label="Risk per trade" value={settings.risk_per_trade_percent} onChange={(v) => update("risk_per_trade_percent", v)} suffix="%" />
        <NumberField label="Max position" value={settings.max_position_percent} onChange={(v) => update("max_position_percent", v)} suffix="%" />
        <NumberField label="Max active positions" value={settings.max_positions} onChange={(v) => update("max_positions", v)} />
        <NumberField label="Minimum stock price" value={settings.min_price} onChange={(v) => update("min_price", v)} prefix="$" />
        <NumberField label="Minimum average volume" value={settings.min_avg_volume} onChange={(v) => update("min_avg_volume", v)} helper={compactNumber(settings.min_avg_volume)} />
      </div>
      <div className="mt-5 flex flex-wrap gap-3">
        <Toggle label="Avoid stocks under minimum price" checked={settings.avoid_penny_stocks} onChange={(v) => update("avoid_penny_stocks", v)} />
        <Toggle label="Paper trading only" checked={settings.paper_mode_enabled} onChange={(v) => update("paper_mode_enabled", v)} />
      </div>
    </section>
  );
}

function NumberField({
  label,
  value,
  onChange,
  prefix,
  suffix,
  helper,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  prefix?: string;
  suffix?: string;
  helper?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-bold text-soft">{label}</span>
      <div className="mt-2 flex items-center rounded-2xl border border-borderDeep bg-midnight px-4 py-3 focus-within:border-cyan">
        {prefix ? <span className="text-soft">{prefix}</span> : null}
        <input className="tabular w-full bg-transparent px-2 font-mono font-bold outline-none" type="number" value={value} onChange={(event) => onChange(Number(event.target.value))} />
        {suffix ? <span className="text-soft">{suffix}</span> : null}
      </div>
      {helper ? <span className="mt-1 block text-xs text-soft">{helper}</span> : null}
    </label>
  );
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (checked: boolean) => void }) {
  return (
    <button
      className={`rounded-2xl border px-4 py-3 text-sm font-bold ${checked ? "border-cyan bg-cyan/10 text-cyan" : "border-borderDeep text-soft"}`}
      onClick={() => onChange(!checked)}
    >
      {checked ? "On" : "Off"} · {label}
    </button>
  );
}
