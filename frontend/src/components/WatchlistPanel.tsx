import type { UserSettings } from "../types";

export function WatchlistPanel({ settings, onChange }: { settings: UserSettings; onChange: (settings: UserSettings) => void }) {
  const text = settings.universe.join(", ");
  return (
    <section className="rounded-3xl border border-borderDeep bg-panel p-5">
      <h2 className="text-xl font-black">Scan universe</h2>
      <p className="mt-1 text-sm leading-6 text-soft">
        This is the market basket the agent scans. It includes mega-cap leaders plus cheaper, high-turnover candidates.
      </p>
      <textarea
        className="mt-4 h-40 w-full rounded-2xl border border-borderDeep bg-midnight p-4 font-mono text-sm outline-none focus:border-cyan"
        value={text}
        onChange={(event) =>
          onChange({
            ...settings,
            universe: event.target.value.split(/[,\s]+/).map((item) => item.trim().toUpperCase()).filter(Boolean),
          })
        }
      />
    </section>
  );
}
