"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ApiError, lookupToken, TokenLookup } from "@/lib/api";
import ScoreGauge from "@/components/ScoreGauge";
import StatusBadge from "@/components/StatusBadge";

export default function TokenLookupPage({ params }: { params: { code: string; issuer: string } }) {
  const code = decodeURIComponent(params.code);
  const issuer = decodeURIComponent(params.issuer);
  const [data, setData] = useState<TokenLookup | null>(null);
  const [status, setStatus] = useState<"loading" | "notfound" | "error" | "ok">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    lookupToken(code, issuer)
      .then((d) => {
        setData(d);
        setStatus("ok");
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setStatus("notfound");
          setMessage("No threat data found for this asset.");
        } else {
          setStatus("error");
          setMessage(err instanceof Error ? err.message : "Lookup failed");
        }
      });
  }, [code, issuer]);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link href="/lookup" className="text-xs text-threat-accent hover:underline">← New lookup</Link>

      {status === "loading" ? (
        <div className="panel h-48 animate-pulse" />
      ) : status === "notfound" || status === "error" ? (
        <div className="panel border-amber-500/40 p-8 text-center">
          <p className="text-3xl">🪙</p>
          <h1 className="mt-3 text-lg font-semibold text-white">No reputation data</h1>
          <p className="mt-1.5 mono break-all text-sm text-amber-300">
            {code}:{issuer}
          </p>
          <p className="mt-3 text-sm text-slate-400">{message}</p>
        </div>
      ) : data ? (
        <>
          <section className="panel p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="label">Asset</p>
                <p className="mono mt-1 break-all text-slate-200">{data.asset_identifier}</p>
                <div className="mt-3">
                  <StatusBadge status={data.status} />
                </div>
              </div>
            </div>
            <div className="mt-6">
              <ScoreGauge score={Math.round(data.confidence_score * 100)} />
            </div>
          </section>

          <section className="grid gap-4 sm:grid-cols-2">
            <div className="panel p-5">
              <p className="label">Category</p>
              <p className="mt-1.5 text-sm text-slate-200">{data.category}</p>
            </div>
            <div className="panel p-5">
              <p className="label">Issuer</p>
              <p className="mono mt-1.5 break-all text-xs text-slate-200">{data.issuer_address}</p>
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
