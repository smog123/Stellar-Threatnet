"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getSocOverview, SocOverview } from "@/lib/api";
import StatCard from "@/components/StatCard";
import StatusBadge, { severityColor } from "@/components/StatusBadge";
import NetworkStatusBanner from "@/components/NetworkStatusBanner";
import LandscapeChart from "@/components/LandscapeChart";
import ActivityFeed, { ActivityItem } from "@/components/ActivityFeed";
import SectionHeader from "@/components/SectionHeader";
import { timeAgo } from "@/lib/time";

const entityIcon = (type: string) => (type === "wallet" ? "👛" : type === "domain" ? "🌐" : "🪙");

export default function Dashboard() {
  const [data, setData] = useState<SocOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSocOverview()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "API unreachable — start the backend on :8000"));
  }, []);

  if (error && !data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold tracking-tight text-white">Stellar Security Operations Center</h1>
        <div className="panel border-rose-500/40 p-4 text-sm text-rose-400">{error}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold tracking-tight text-white">Stellar Security Operations Center</h1>
        <div className="panel h-32 animate-pulse" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="panel h-24 animate-pulse" />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="panel h-72 animate-pulse" />
          <div className="panel h-72 animate-pulse" />
        </div>
      </div>
    );
  }

  const { network_status: net, counts, landscape, modules, active_campaigns: campaigns, latest_threats: threats, recent_reports: reports } = data;

  const activity: ActivityItem[] = [
    ...campaigns.map<ActivityItem>((c) => ({
      kind: "incident",
      id: c.id,
      title: c.title,
      detail: `${c.affected_services} · ${c.description.slice(0, 80)}`,
      badge: c.status,
      badgeClass: c.status === "open" ? "bg-rose-500/15 text-rose-400 border-rose-500/30" : "bg-amber-500/15 text-amber-400 border-amber-500/30",
      time: c.updated_at,
    })),
    ...reports.map<ActivityItem>((r) => ({
      kind: "report",
      id: r.id,
      title: `${r.target_type} report — ${r.target_value.slice(0, 24)}`,
      detail: r.description.slice(0, 80),
      badge: r.status,
      badgeClass:
        r.status === "pending"
          ? "bg-sky-500/15 text-sky-400 border-sky-500/30"
          : r.status === "approved"
            ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
            : "bg-slate-500/15 text-slate-400 border-slate-500/30",
      time: r.created_at,
    })),
  ].sort((a, b) => (a.time < b.time ? 1 : -1));

  return (
    <div className="space-y-8">
      <section className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">Security Operations Center</h1>
          <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
            Live posture and intelligence for the Stellar ecosystem — wallets, assets, anchors, contracts, and SEP compliance.
          </p>
        </div>
        <span className="flex items-center gap-2 rounded-lg border border-threat-border px-3 py-1.5 text-xs text-slate-400">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
          Live feed · updated {timeAgo(data.generated_at)}
        </span>
      </section>

      <NetworkStatusBanner status={net} counts={counts} />

      <section>
        <SectionHeader title="Ecosystem threat counters" subtitle="Tracked indicators across every monitored surface" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <StatCard label="Malicious wallets" value={counts.total_malicious_wallets} accent="rose" />
          <StatCard label="Phishing domains" value={counts.total_phishing_domains} accent="rose" />
          <StatCard label="Scam tokens" value={counts.total_scam_tokens} accent="rose" />
          <StatCard label="Security advisories" value={counts.total_incidents_recorded} accent="sky" />
          <StatCard label="Active campaigns" value={counts.active_campaigns_count} accent="amber" />
          <StatCard label="Pending reports" value={counts.pending_reports} accent="cyan" />
          <StatCard label="Total indicators" value={counts.total_indicators} accent="sky" />
          <StatCard label="Anchors profiled" value={modules.anchors} accent="emerald" />
          <StatCard label="Soroban scans" value={modules.soroban_scans} accent="emerald" />
          <StatCard label="SEP validations" value={modules.sep_validations} accent="emerald" />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-5">
        <div className="panel p-5 lg:col-span-2">
          <SectionHeader title="Threat landscape" subtitle="Tracked entities by verdict" />
          <LandscapeChart landscape={landscape} />
        </div>

        <div className="panel p-5 lg:col-span-3">
          <SectionHeader
            title="Latest threat intelligence"
            subtitle="Most recently updated non-trusted entities"
            action={
              <Link href="/threat-intel" className="text-xs text-threat-accent hover:underline">
                Search intelligence →
              </Link>
            }
          />
          {threats.length === 0 ? (
            <p className="py-6 text-center text-sm text-slate-500">
              No flagged entities yet — seed the database or wait for approved community reports.
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
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-5">
          <SectionHeader
            title="Active phishing campaigns"
            subtitle="Open and under-investigation advisories"
            action={
              <Link href="/advisories" className="text-xs text-threat-accent hover:underline">
                All advisories →
              </Link>
            }
          />
          {campaigns.length === 0 ? (
            <p className="py-6 text-center text-sm text-slate-500">No active campaigns.</p>
          ) : (
            <ul className="space-y-3">
              {campaigns.map((c) => (
                <li key={c.id} className="rounded-lg border border-threat-border/60 p-3 transition hover:border-threat-accent/40">
                  <div className="flex items-center justify-between gap-2">
                    <span className="mono text-[11px] text-slate-500">{c.id}</span>
                    <span className={`text-[11px] font-bold uppercase ${severityColor(c.severity)}`}>{c.severity}</span>
                  </div>
                  <p className="mt-1 text-sm font-medium text-slate-200">{c.title}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <StatusBadge status={c.status} />
                    <span className="text-[11px] text-slate-500">updated {timeAgo(c.updated_at)}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel p-5">
          <SectionHeader
            title="Recent community reports"
            subtitle="Latest submissions and votes"
            action={
              <Link href="/community" className="text-xs text-threat-accent hover:underline">
                Community →
              </Link>
            }
          />
          {reports.length === 0 ? (
            <p className="py-6 text-center text-sm text-slate-500">No community reports yet.</p>
          ) : (
            <ul className="divide-y divide-threat-border/60">
              {reports.map((r) => (
                <li key={r.id} className="flex items-center gap-3 py-3">
                  <span className="text-lg">{entityIcon(r.target_type)}</span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-slate-200">
                      {r.target_type}: <span className="mono">{r.target_value.slice(0, 28)}</span>
                    </p>
                    <p className="truncate text-xs text-slate-500">{r.description.slice(0, 72)}</p>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1">
                    <StatusBadge status={r.status} />
                    <span className="text-[11px] text-slate-500">
                      ▲{r.upvotes} ▼{r.downvotes}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="panel p-5">
        <SectionHeader title="Activity feed" subtitle="Recent incidents and community reports across the ecosystem" />
        <ActivityFeed items={activity.slice(0, 10)} />
      </section>
    </div>
  );
}
