import { GlobalStats, NetworkStatus } from "@/lib/api";

const LEVEL_STYLES: Record<NetworkStatus["level"], { border: string; bg: string; text: string; dot: string; glow: string }> = {
  high: {
    border: "border-rose-500/40",
    bg: "bg-rose-500/10",
    text: "text-rose-400",
    dot: "bg-rose-500",
    glow: "shadow-[0_0_28px_rgba(244,63,94,0.12)]",
  },
  elevated: {
    border: "border-amber-500/40",
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    dot: "bg-amber-500",
    glow: "shadow-[0_0_28px_rgba(245,158,11,0.12)]",
  },
  normal: {
    border: "border-emerald-500/40",
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    dot: "bg-emerald-500",
    glow: "shadow-[0_0_28px_rgba(16,185,129,0.12)]",
  },
};

export default function NetworkStatusBanner({ status, counts }: { status: NetworkStatus; counts: GlobalStats }) {
  const style = LEVEL_STYLES[status.level] ?? LEVEL_STYLES.normal;
  return (
    <section className={`panel relative overflow-hidden border ${style.border} ${style.bg} ${style.glow} p-5 sm:p-6`}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <span className="relative mt-1 flex h-3 w-3 shrink-0">
            <span className={`absolute inline-flex h-full w-full animate-pulse rounded-full ${style.dot} opacity-60`} />
            <span className={`relative inline-flex h-3 w-3 rounded-full ${style.dot}`} />
          </span>
          <div className="min-w-0">
            <p className={`text-xs font-bold uppercase tracking-[0.18em] ${style.text}`}>Network Security Status</p>
            <h2 className="mt-1 text-lg font-bold tracking-tight text-white sm:text-xl">{status.label}</h2>
            <p className="mt-1 max-w-2xl text-sm leading-relaxed text-slate-400">{status.summary}</p>
          </div>
        </div>
        <div className="flex shrink-0 gap-6 text-right">
          <div>
            <p className="mono text-2xl font-bold text-white">{counts.active_campaigns_count}</p>
            <p className="label">Active campaigns</p>
          </div>
          <div>
            <p className="mono text-2xl font-bold text-rose-400">{counts.total_indicators}</p>
            <p className="label">Confirmed indicators</p>
          </div>
          <div>
            <p className="mono text-2xl font-bold text-amber-400">{counts.pending_reports}</p>
            <p className="label">Pending reports</p>
          </div>
        </div>
      </div>
    </section>
  );
}
