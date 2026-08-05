"use client";

import { useEffect, useState } from "react";
import { getIncidents, Incident } from "@/lib/api";
import StatusBadge, { severityColor } from "@/components/StatusBadge";

const STATUSES = ["", "open", "investigating", "resolved", "dismissed"];

export default function IncidentsPage() {
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    getIncidents(status || undefined, 10, offset)
      .then((page) => {
        setItems(page.items);
        setTotal(page.total);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load incidents"));
  }, [status, offset]);

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Incident Database</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            Attacks, scams, phishing campaigns, and Soroban contract vulnerabilities with timelines and mitigations.
          </p>
        </div>
        <div className="flex gap-2">
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => {
                setStatus(s);
                setOffset(0);
              }}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold capitalize transition ${
                status === s
                  ? "bg-threat-accent/15 text-threat-accent ring-1 ring-threat-accent/40"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              {s === "" ? "All" : s}
            </button>
          ))}
        </div>
      </section>

      {error ? <div className="panel border-rose-500/40 p-4 text-sm text-rose-400">{error}</div> : null}
      {!error && total === 0 && !items.length ? (
        <div className="panel p-10 text-center text-sm text-slate-500">
          No incidents yet — analysts can publish the first one via <span className="mono">POST /api/v1/incidents</span>.
        </div>
      ) : null}

      <section className="space-y-4">
        {items.map((inc) => (
          <article key={inc.id} className="panel panel-hover p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-3">
                <span className="mono text-xs text-slate-500">{inc.id}</span>
                <StatusBadge status={inc.status} />
              </div>
              <span className={`text-xs font-bold uppercase ${severityColor(inc.severity)}`}>{inc.severity}</span>
            </div>
            <h2 className="mt-2 text-base font-semibold text-white">{inc.title}</h2>
            <p className="mt-1 text-sm leading-relaxed text-slate-400">{inc.description}</p>
            <div className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
              <div>
                <p className="label mb-1">Affected services</p>
                <p className="text-slate-300">{inc.affected_services}</p>
              </div>
              <div>
                <p className="label mb-1">Mitigations</p>
                <p className="text-slate-300">{inc.mitigations}</p>
              </div>
            </div>
            {inc.references ? (
              <p className="mt-3 text-xs text-slate-500">
                References: <span className="mono text-threat-accent">{inc.references}</span>
              </p>
            ) : null}
          </article>
        ))}
      </section>

      {total > 10 ? (
        <div className="flex items-center justify-between">
          <button className="btn-ghost" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 10))}>
            ← Previous
          </button>
          <span className="text-xs text-slate-500">
            {offset + 1}–{Math.min(offset + 10, total)} of {total}
          </span>
          <button className="btn-ghost" disabled={offset + 10 >= total} onClick={() => setOffset(offset + 10)}>
            Next →
          </button>
        </div>
      ) : null}
    </div>
  );
}
