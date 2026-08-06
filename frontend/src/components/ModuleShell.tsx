export interface ModuleStat {
  label: string;
  value: number | string;
}

export interface ModuleCapability {
  icon: string;
  title: string;
  desc: string;
}

export default function ModuleShell({
  title,
  subtitle,
  phase,
  stats,
  capabilities,
  note,
}: {
  title: string;
  subtitle: string;
  phase: string;
  stats: ModuleStat[];
  capabilities: ModuleCapability[];
  note: string;
}) {
  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <section className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">{title}</h1>
          <p className="mt-1.5 max-w-2xl text-sm text-slate-400">{subtitle}</p>
        </div>
        <span className="rounded-lg border border-threat-accent/40 bg-threat-accent/10 px-3 py-1.5 text-xs font-bold uppercase tracking-widest text-threat-accent">
          {phase}
        </span>
      </section>

      <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label} className="panel p-4">
            <p className="mono text-2xl font-bold text-white">{s.value}</p>
            <p className="label mt-1">{s.label}</p>
          </div>
        ))}
      </section>

      <section>
        <h2 className="mb-4 text-sm font-semibold text-white">Planned capabilities</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((c) => (
            <div key={c.title} className="panel panel-hover p-4">
              <span className="text-xl">{c.icon}</span>
              <h3 className="mt-2 text-sm font-semibold text-white">{c.title}</h3>
              <p className="mt-1 text-xs leading-relaxed text-slate-400">{c.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="panel border-threat-accent/20 bg-threat-accent/5 p-5">
        <p className="text-sm leading-relaxed text-slate-300">
          <span className="font-semibold text-threat-accent">Status:</span> {note}
        </p>
      </section>
    </div>
  );
}
