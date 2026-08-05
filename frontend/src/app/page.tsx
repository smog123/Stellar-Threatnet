"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getIncidents, getLatestThreats, getStats, GlobalStats, Incident, LatestThreat } from "@/lib/api";
import StatCard from "@/components/StatCard";
import StatusBadge, { severityColor } from "@/components/StatusBadge";

export default function Dashboard() {
  const [stats, setStats] = useState<GlobalStats | null>(null);
  const [threats, setThreats] = useState<LatestThreat[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.allSettled([getStats(), getLatestThreats(8), getIncidents(undefined, 5)])
      .then(([s, t, i]) => {
        if (s.status === "fulfilled") setStats(s.value);
        if (t.status === "fulfilled") setThreats(t.value);
        if (i.status === "fulfilled") setIncidents(i.value.items);
        if (s.status === "rejected") setError("API unreachable — start the backend on :8000");
      });
  }, []);

  const entityIcon = (type: string) => (type === "wallet" ? "👛" : type === "domain" ? "🌐" : "🪙");

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
          Ecosystem Threat Intelligence
        </h1>
        <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
          Real-time reputation for Stellar wallets, domains, and tokens — the shared security layer
          for wallets, exchanges, dApps, and researchers.
        </p>
      </section>

      {error ? (
        <div className="panel border-rose-500/40 p-4 text-sm text-rose-400">{error}</div>
      ) : null}

      {stats ? (
        <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <StatCard label="Malicious wallets" value={stats.total_malicious_wallets} accent="rose" />
          <StatCard label="Phishing domains" value={stats.total_phishing_domains} accent="rose" />
          <StatCard label="Scam tokens" value={stats.total_scam_tokens} accent="rose" />
          <StatCard label="Incidents" value={stats.total_incidents_recorded} accent="sky" />
          <StatCard label="Active campaigns" value={stats.active_campaigns_count} accent="amber" />
          <StatCard label="Pending reports" value={stats.pending_reports} accent="cyan" />
        </section>
      ) : (
        <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="panel h-24 animate-pulse" />
          ))}
        </section>
      )}

      <section className="grid gap-6 lg:grid-cols-5">
        <div className="panel p-5 lg:col-span-3">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Latest Threats</h2>
            <Link href="/lookup" className="text-xs text-threat-accent hover:underline">
              Lookup an entity →
            </Link>
          </div>
          {threats.length === 0 ? (
            <p className="text-sm text-slate-500">
              No flagged entities yet — seed data via approved community reports or the CSV feed.
            </p>
          ) : (
            <ul className="divide-y divide-threat-border/60">
              {threats.map((t) => (
                <li key={`${t.entity_type}-${t.identifier}`} className="flex items-center gap-3 py-3">
                  <span className="text-lg">{entityIcon(t.entity_type)}</span>
                  <div className="min-w-0 flex-1">
                    <p className="mono truncate text-slate-200">{t.identifier}</p>
                    <p className="truncate text-xs text-slate-500">{t.reason}</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <span className="mono text-sm text-slate-300">{Math.round(t.score)}</span>
                    <StatusBadge status={t.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Recent Incidents</h2>
            <Link href="/incidents" className="text-xs text-threat-accent hover:underline">
              View all →
            </Link>
          </div>
          {incidents.length === 0 ? (
            <p className="text-sm text-slate-500">No incidents published yet.</p>
          ) : (
            <ul className="space-y-3">
              {incidents.map((inc) => (
                <li key={inc.id} className="rounded-lg border border-threat-border/60 p-3 transition hover:border-threat-accent/40">
                  <div className="flex items-center justify-between gap-2">
                    <span className="mono text-[11px] text-slate-500">{inc.id}</span>
                    <span className={`text-[11px] font-bold uppercase ${severityColor(inc.severity)}`}>
                      {inc.severity}
                    </span>
                  </div>
                  <p className="mt-1 text-sm font-medium text-slate-200">{inc.title}</p>
                  <div className="mt-2">
                    <StatusBadge status={inc.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
