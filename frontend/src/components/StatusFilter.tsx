export default function StatusFilter({
  options,
  value,
  onChange,
}: {
  options: string[];
  value: string;
  onChange: (next: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button
          key={o}
          onClick={() => onChange(o)}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold capitalize transition ${
            value === o
              ? "bg-threat-accent/15 text-threat-accent ring-1 ring-threat-accent/40"
              : "text-slate-400 hover:bg-white/5 hover:text-white"
          }`}
        >
          {o === "" ? "All" : o}
        </button>
      ))}
    </div>
  );
}
