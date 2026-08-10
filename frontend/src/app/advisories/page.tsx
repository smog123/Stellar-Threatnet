"use client";

import { useEffect, useState } from "react";
import { getIncidents, Incident } from "@/lib/api";
import IncidentCard from "@/components/IncidentCard";
import StatusFilter from "@/components/StatusFilter";

const STATUSES = ["", "open", "investigating", "resolved", "dismissed"];

export default function AdvisoriesPage() {
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getIncidents(status || undefined, 25, 0)
      .then((page) => {
        setError(null);
        setItems(page.items);
        setTotal(page.total);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load advisories"));
  }, [status]);

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <section className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Security Advisories</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            Public advisory center: attacks, scams, phishing campaigns, and Soroban contract
            vulnerabilities with status, mitigations, and references.
          </p>
        </div>
        <StatusFilter options={STATUSES} value={status} onChange={setStatus} />
      </section>

      {error ? <div className="panel border-rose-500/40 p-4 text-sm text-rose-400">{error}</div> : null}
      {!error && total === 0 ? (
        <div className="panel p-10 text-center text-sm text-slate-500">
          No advisories published yet — analysts can publish the first one via <span className="mono">POST /api/v1/incidents</span>.
        </div>
      ) : null}

      <section className="space-y-4">
        {items.map((inc) => (
          <IncidentCard key={inc.id} incident={inc} />
        ))}
      </section>
    </div>
  );
}
