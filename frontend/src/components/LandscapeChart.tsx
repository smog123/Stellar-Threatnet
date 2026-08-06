import { StatusCounts, ThreatLandscape } from "@/lib/api";

const STATUS_META = [
  { key: "confirmed_malicious" as const, label: "Malicious", color: "bg-rose-500", text: "text-rose-400" },
  { key: "suspicious" as const, label: "Suspicious", color: "bg-amber-500", text: "text-amber-400" },
  { key: "under_investigation" as const, label: "Investigating", color: "bg-sky-500", text: "text-sky-400" },
  { key: "trusted" as const, label: "Trusted", color: "bg-emerald-500", text: "text-emerald-400" },
];

function total(counts: StatusCounts): number {
  return Object.values(counts).reduce((a, b) => a + b, 0);
}

export default function LandscapeChart({ landscape }: { landscape: ThreatLandscape }) {
  const rows = [
    { label: "Wallets", icon: "👛", counts: landscape.wallets },
    { label: "Domains", icon: "🌐", counts: landscape.domains },
    { label: "Tokens", icon: "🪙", counts: landscape.tokens },
  ];
  const max = Math.max(1, ...rows.map((r) => total(r.counts)));
  const grand = rows.reduce((a, r) => a + total(r.counts), 0);

  return (
    <div>
      <div className="space-y-4">
        {rows.map((row) => {
          const rowTotal = total(row.counts);
          return (
            <div key={row.label} className="flex items-center gap-3">
              <div className="w-20 shrink-0">
                <p className="truncate text-xs font-medium text-slate-300">
                  {row.icon} {row.label}
                </p>
              </div>
              <div className="flex h-5 flex-1 overflow-hidden rounded-md border border-threat-border/60 bg-threat-bg">
                {STATUS_META.map((s) =>
                  row.counts[s.key] > 0 ? (
                    <div
                      key={s.key}
                      className={`${s.color} transition-all`}
                      style={{ width: `${(row.counts[s.key] / max) * 100}%` }}
                      title={`${s.label}: ${row.counts[s.key]}`}
                    />
                  ) : null,
                )}
              </div>
              <div className="w-14 shrink-0 text-right">
                <p className="mono text-xs text-slate-400">{rowTotal}</p>
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-threat-border/60 pt-4">
        {STATUS_META.map((s) => {
          const count = rows.reduce((a, r) => a + r.counts[s.key], 0);
          return (
            <div key={s.key} className="flex items-center gap-1.5 text-xs text-slate-400">
              <span className={`h-2.5 w-2.5 rounded-sm ${s.color}`} />
              {s.label}
              <span className={`mono ${s.text}`}>{count}</span>
            </div>
          );
        })}
        <span className="ml-auto text-xs text-slate-500">
          {grand} tracked entities
        </span>
      </div>
    </div>
  );
}
