"use client";

import { useEffect, use, useState } from "react";
import Link from "next/link";
import { ApiError, lookupWallet, lookupWalletOnChain, WalletLookup, WalletOnChain } from "@/lib/api";
import ScoreGauge from "@/components/ScoreGauge";
import StatusBadge from "@/components/StatusBadge";

const RISK_STYLES: Record<string, string> = {
  caution: "border-amber-500/40",
  info: "border-emerald-500/30",
  neutral: "border-slate-500/30",
};

const RISK_ICON: Record<string, string> = {
  caution: "⚠️",
  info: "🔗",
  neutral: "🔍",
};

function OnChainCard({ data }: { data: WalletOnChain }) {
  const p = data.profile;
  return (
    <div className={`panel p-8 ${RISK_STYLES[data.risk_level] ?? RISK_STYLES.neutral}`}>
      <div className="text-center">
        <p className="text-3xl">{RISK_ICON[data.risk_level] ?? "🔍"}</p>
        <h1 className="mt-3 text-lg font-semibold text-white">No threat reports — live on-chain profile</h1>
        <p className="mt-1.5 mono mx-auto max-w-md break-all text-sm text-slate-400">{data.address}</p>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-slate-300">{data.summary}</p>

      {data.signals.length > 0 && (
        <ul className="mt-4 space-y-1.5">
          {data.signals.map((s, i) => (
            <li key={i} className="flex gap-2 text-sm text-slate-300">
              <span className="text-threat-accent">›</span>
              <span>{s}</span>
            </li>
          ))}
        </ul>
      )}

      {p && p.funded && (
        <dl className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3">
          <Fact label="XLM balance" value={p.native_balance ?? "—"} />
          <Fact label="Age (days)" value={p.account_age_days != null ? String(p.account_age_days) : "unknown"} />
          <Fact label="Trustlines" value={String(p.trustline_count ?? 0)} />
          <Fact label="Signers" value={String(p.signer_count ?? 1)} />
          <Fact label="Sub-entries" value={String(p.num_subentries ?? 0)} />
          <Fact label="home_domain" value={p.home_domain ?? "none"} />
        </dl>
      )}

      <p className="mt-6 border-t border-threat-border pt-4 text-xs text-slate-500">
        On-chain maturity is context, not a safety guarantee. An aged account can still be
        malicious and a new one can be legitimate. Always verify the counterparty independently.
      </p>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="label">{label}</dt>
      <dd className="mono mt-1 break-all text-sm text-slate-200">{value}</dd>
    </div>
  );
}

export default function WalletLookupPage({ params }: { params: Promise<{ address: string }> }) {
  // Next 15+ passes `params` as a Promise — unwrap it with React's `use()`.
  const { address: rawAddress } = use(params);
  const address = decodeURIComponent(rawAddress);
  const [data, setData] = useState<WalletLookup | null>(null);
  const [onchain, setOnchain] = useState<WalletOnChain | null>(null);
  const [status, setStatus] = useState<"loading" | "onchain" | "error" | "ok">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    lookupWallet(address)
      .then((d) => {
        setData(d);
        setStatus("ok");
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          lookupWalletOnChain(address)
            .then((o) => {
              setOnchain(o);
              setStatus("onchain");
            })
            .catch((e) => {
              setStatus("error");
              setMessage(e instanceof Error ? e.message : "On-chain lookup failed");
            });
        } else {
          setStatus("error");
          setMessage(err instanceof Error ? err.message : "Lookup failed");
        }
      });
  }, [address]);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link href="/lookup" className="text-xs text-threat-accent hover:underline">← New lookup</Link>

      {status === "loading" ? (
        <div className="panel h-48 animate-pulse" />
      ) : status === "onchain" && onchain ? (
        <OnChainCard data={onchain} />
      ) : status === "error" ? (
        <div className="panel border-rose-500/40 p-8 text-center">
          <p className="text-3xl">⚠️</p>
          <h1 className="mt-3 text-lg font-semibold text-white">Lookup failed</h1>
          <p className="mt-1.5 mono mx-auto max-w-md break-all text-sm text-amber-300">{address}</p>
          <p className="mt-3 text-sm text-slate-400">{message}</p>
        </div>
      ) : data ? (
        <>
          <section className="panel p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="label">Wallet address</p>
                <p className="mono mt-1 break-all text-slate-200">{data.address}</p>
                <div className="mt-3">
                  <StatusBadge status={data.status} />
                </div>
              </div>
            </div>
            <div className="mt-6">
              <ScoreGauge score={data.reputation_score} />
            </div>
          </section>

          <section className="grid gap-4 sm:grid-cols-2">
            <div className="panel p-5">
              <p className="label">Category</p>
              <p className="mt-1.5 text-sm text-slate-200">{data.category ?? "Unspecified"}</p>
            </div>
            <div className="panel p-5">
              <p className="label">Community reports</p>
              <p className="mt-1.5 font-mono text-sm text-slate-200">{data.report_count}</p>
            </div>
          </section>

          <section className="panel p-5">
            <p className="label">Assessment</p>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">{data.reason}</p>
          </section>
        </>
      ) : null}
    </div>
  );
}
