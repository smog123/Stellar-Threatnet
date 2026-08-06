"use client";

import { useState } from "react";
import SearchBox from "@/components/SearchBox";

type LookupType = "wallet" | "domain" | "token";

const TABS: { value: LookupType; icon: string; label: string; mode: "wallet" | "domain" | "asset" }[] = [
  { value: "wallet", icon: "👛", label: "Wallet", mode: "wallet" },
  { value: "domain", icon: "🌐", label: "Domain", mode: "domain" },
  { value: "token", icon: "🪙", label: "Token", mode: "asset" },
];

export default function LookupPage() {
  const [type, setType] = useState<LookupType>("wallet");
  const active = TABS.find((t) => t.value === type)!;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Reputation Lookup</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Check any Stellar wallet, phishing domain, or token against the ThreatNet database.
          Unknown entities return <span className="mono text-slate-300">404 — no data</span> (neutral, never trusted).
        </p>
      </section>

      <div className="panel p-6">
        <div className="mb-5 flex gap-2">
          {TABS.map((t) => (
            <button
              key={t.value}
              type="button"
              onClick={() => setType(t.value)}
              className={`flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition ${
                type === t.value
                  ? "bg-threat-accent/15 text-threat-accent ring-1 ring-threat-accent/40"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>
        <SearchBox key={active.value} mode={active.mode} />
      </div>
    </div>
  );
}
