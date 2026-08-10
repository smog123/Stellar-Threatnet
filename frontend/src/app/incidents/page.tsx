"use client";

import { useEffect, useState } from "react";
import { getIncidents, Incident } from "@/lib/api";
import IncidentCard from "@/components/IncidentCard";
import StatusFilter from "@/components/StatusFilter";

const STATUSES = ["", "open", "investigating", "resolved", "dismissed"];

export default function IncidentsPage() {
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getIncidents(status || undefined, 10, offset)
      .then((page) => {
        setError(null);
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
        <StatusFilter options={STATUSES} value={status} onChange={(s) => { setStatus(s); setOffset(0); }} />
      </section>

      {error ? <div className="panel border-rose-500/40 p-4 text-sm text-rose-400">{error}</div> : null}
      {!error && total === 0 && !items.length ? (
        <div className="panel p-10 text-center text-sm text-slate-500">
          No incidents yet — analysts can publish the first one via <span className="mono">POST /api/v1/incidents</span>.
        </div>
      ) : null}

      <section className="space-y-4">
        {items.map((inc) => (
          <IncidentCard key={inc.id} incident={inc} />
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
