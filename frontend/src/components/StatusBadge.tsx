const STATUS_STYLES: Record<string, string> = {
  confirmed_malicious: "bg-rose-500/15 text-rose-400 border-rose-500/30",
  suspicious: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  under_investigation: "bg-sky-500/15 text-sky-400 border-sky-500/30",
  trusted: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  open: "bg-rose-500/15 text-rose-400 border-rose-500/30",
  investigating: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  resolved: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  dismissed: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  pending: "bg-sky-500/15 text-sky-400 border-sky-500/30",
  approved: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  rejected: "bg-slate-500/15 text-slate-400 border-slate-500/30",
};

export default function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${style}`}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}

export function severityColor(severity: string): string {
  switch (severity) {
    case "critical":
      return "text-rose-400";
    case "high":
      return "text-orange-400";
    case "medium":
      return "text-amber-400";
    default:
      return "text-sky-400";
  }
}
