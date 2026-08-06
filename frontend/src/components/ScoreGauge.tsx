export default function ScoreGauge({ score }: { score: number }) {
  const color = score <= 20 ? "text-rose-400" : score <= 50 ? "text-amber-400" : score <= 79 ? "text-sky-400" : "text-emerald-400";
  const barColor = score <= 20 ? "bg-rose-500" : score <= 50 ? "bg-amber-500" : score <= 79 ? "bg-sky-500" : "bg-emerald-500";

  return (
    <div className="flex items-center gap-4">
      <div className="relative h-24 w-24 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="10" className="text-threat-border" />
          <circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 263.9} 263.9`}
            className={color}
          />
        </svg>
        <span className={`absolute inset-0 grid place-items-center font-mono text-xl font-bold ${color}`}>
          {Math.round(score)}
        </span>
      </div>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-threat-border">
        <div className={`h-full rounded-full ${barColor} transition-all duration-700`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}
