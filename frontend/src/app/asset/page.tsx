"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getLatestThreats, LatestThreat } from "@/lib/api";
import SearchBox from "@/components/SearchBox";
import StatusBadge from "@/components/StatusBadge";
import SectionHeader from "@/components/SectionHeader";

export default function AssetReputationPage() {
  const [tokens, setTokens] = useState<LatestThreat[]>([]);

  useEffect(() => {
    getLatestThreats(12)
      .then((items) => setTokens(items.filter((t) => t.entity_type === "token")))
      .catch(() => setTokens([]));
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Asset Reputation</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Trust scores for Stellar assets (<span className="mono">CODE:ISSUER</span>): verified issuers,
          impersonation tokens, rugpulls, and abandoned assets.
        </p>
      </section>

      <section className="panel p-6">
        <SectionHeader title="Search an asset" subtitle="Enter the asset code and issuer address" />
        <SearchBox mode="asset" />
      </section>

      <section className="panel p-5">
        <SectionHeader
          title="Recently flagged assets"
          subtitle="Most recently updated non-trusted tokens"
          action={
            <Link href="/threat-intel" className="text-xs text-threat-accent hover:underline">
              Threat intelligence →
            </Link>
          }
        />
        {tokens.length === 0 ? (
          <p className="py-6 text-center text-sm text-slate-500">
            No flagged assets yet — new reports appear here after moderation.
          </p>
        ) : (
          <ul className="divide-y divide-threat-border/60">
            {tokens.map((t) => (
              <li key={t.identifier} className="flex items-center gap-3 py-3">
                <span className="text-lg">🪙</span>
                <div className="min-w-0 flex-1">
                  <p className="mono truncate text-slate-200">{t.identifier}</p>
                  <p className="truncate text-xs text-slate-500">{t.reason}</p>
                </div>
                <span className="mono shrink-0 text-sm text-slate-300">{Math.round(t.score)}</span>
                <StatusBadge status={t.status} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
