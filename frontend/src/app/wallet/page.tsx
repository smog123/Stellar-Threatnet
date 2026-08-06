"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getLatestThreats, LatestThreat } from "@/lib/api";
import SearchBox from "@/components/SearchBox";
import StatusBadge from "@/components/StatusBadge";
import SectionHeader from "@/components/SectionHeader";

export default function WalletReputationPage() {
  const [wallets, setWallets] = useState<LatestThreat[]>([]);

  useEffect(() => {
    getLatestThreats(12)
      .then((items) => setWallets(items.filter((t) => t.entity_type === "wallet")))
      .catch(() => setWallets([]));
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Wallet Reputation</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Risk scores, threat categories, and evidence for Stellar <span className="mono">G…</span> addresses.
          Unknown wallets return no data — treat them as neutral, never trusted.
        </p>
      </section>

      <section className="panel p-6">
        <SectionHeader title="Search a wallet" subtitle="Enter a Stellar public key to check its reputation" />
        <SearchBox mode="wallet" />
      </section>

      <section className="panel p-5">
        <SectionHeader
          title="Recently flagged wallets"
          subtitle="Most recently updated non-trusted addresses"
          action={
            <Link href="/threat-intel" className="text-xs text-threat-accent hover:underline">
              Threat intelligence →
            </Link>
          }
        />
        {wallets.length === 0 ? (
          <p className="py-6 text-center text-sm text-slate-500">
            No flagged wallets yet — new reports appear here after moderation.
          </p>
        ) : (
          <ul className="divide-y divide-threat-border/60">
            {wallets.map((w) => (
              <li key={w.identifier} className="flex items-center gap-3 py-3">
                <span className="text-lg">👛</span>
                <div className="min-w-0 flex-1">
                  <Link href={`/lookup/wallet/${encodeURIComponent(w.identifier)}`} className="mono block truncate text-slate-200 hover:text-threat-accent">
                    {w.identifier}
                  </Link>
                  <p className="truncate text-xs text-slate-500">{w.reason}</p>
                </div>
                <span className="mono shrink-0 text-sm text-slate-300">{Math.round(w.score)}</span>
                <StatusBadge status={w.status} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
