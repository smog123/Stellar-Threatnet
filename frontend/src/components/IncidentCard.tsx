import { Incident } from "@/lib/api";
import StatusBadge, { severityColor } from "@/components/StatusBadge";
import { timeAgo } from "@/lib/time";

export default function IncidentCard({ incident }: { incident: Incident }) {
  const inc = incident;
  return (
    <article className="panel panel-hover p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span className="mono text-xs text-slate-500">{inc.id}</span>
          <StatusBadge status={inc.status} />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px] text-slate-500">updated {timeAgo(inc.updated_at)}</span>
          <span className={`text-xs font-bold uppercase ${severityColor(inc.severity)}`}>{inc.severity}</span>
        </div>
      </div>
      <h2 className="mt-2 text-base font-semibold text-white">{inc.title}</h2>
      <p className="mt-1 text-sm leading-relaxed text-slate-400">{inc.description}</p>
      <div className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
        <div>
          <p className="label mb-1">Affected components</p>
          <p className="text-slate-300">{inc.affected_services}</p>
        </div>
        <div>
          <p className="label mb-1">Mitigation</p>
          <p className="text-slate-300">{inc.mitigations}</p>
        </div>
      </div>
      {inc.references ? (
        <p className="mt-3 text-xs text-slate-500">
          References: <span className="mono text-threat-accent">{inc.references}</span>
        </p>
      ) : null}
    </article>
  );
}
