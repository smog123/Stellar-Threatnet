interface StatCardProps {
  label: string;
  value: number | string;
  accent?: "rose" | "amber" | "sky" | "emerald" | "cyan";
  hint?: string;
}

const ACCENTS = {
  rose: "text-rose-400",
  amber: "text-amber-400",
  sky: "text-sky-400",
  emerald: "text-emerald-400",
  cyan: "text-threat-accent",
};

export default function StatCard({ label, value, accent = "cyan", hint }: StatCardProps) {
  return (
    <div className="panel panel-hover p-5">
      <p className="label">{label}</p>
      <p className={`mt-2 font-mono text-3xl font-bold ${ACCENTS[accent]}`}>{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-500">{hint}</p> : null}
    </div>
  );
}
