"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type LookupType = "wallet" | "domain" | "token";

const PLACEHOLDERS: Record<LookupType, string> = {
  wallet: "G… (Stellar public key, 56 chars)",
  domain: "example-phishing-site.com",
  token: "USDC",
};

export default function LookupPage() {
  const router = useRouter();
  const [type, setType] = useState<LookupType>("wallet");
  const [primary, setPrimary] = useState("");
  const [issuer, setIssuer] = useState("");
  const [error, setError] = useState<string | null>(null);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (type === "token") {
      if (!primary.trim() || !issuer.trim()) {
        setError("Asset code and issuer are required for token lookups.");
        return;
      }
      router.push(`/lookup/token/${encodeURIComponent(primary.trim())}/${encodeURIComponent(issuer.trim())}`);
    } else if (!primary.trim()) {
      setError("Please enter a value to look up.");
      return;
    } else {
      router.push(`/lookup/${type}/${encodeURIComponent(primary.trim())}`);
    }
  }

  const tabs: LookupType[] = ["wallet", "domain", "token"];

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Reputation Lookup</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Check any Stellar wallet, phishing domain, or token against the ThreatNet database.
          Unknown entities return <span className="mono text-slate-300">404 — no data</span> (neutral, never trusted).
        </p>
      </section>

      <form onSubmit={submit} className="panel p-6">
        <div className="mb-5 flex gap-2">
          {tabs.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setType(t)}
              className={`flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition ${
                type === t
                  ? "bg-threat-accent/15 text-threat-accent ring-1 ring-threat-accent/40"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              {t === "wallet" ? "👛 Wallet" : t === "domain" ? "🌐 Domain" : "🪙 Token"}
            </button>
          ))}
        </div>

        <div className="space-y-4">
          <div>
            <label className="label mb-1.5 block">
              {type === "wallet" ? "Wallet address" : type === "domain" ? "Domain" : "Asset code"}
            </label>
            <input
              className="input mono"
              value={primary}
              onChange={(e) => setPrimary(e.target.value)}
              placeholder={PLACEHOLDERS[type]}
              spellCheck={false}
            />
          </div>

          {type === "token" ? (
            <div>
              <label className="label mb-1.5 block">Issuer address</label>
              <input
                className="input mono"
                value={issuer}
                onChange={(e) => setIssuer(e.target.value)}
                placeholder="G… (issuer public key)"
                spellCheck={false}
              />
            </div>
          ) : null}

          {error ? <p className="text-sm text-rose-400">{error}</p> : null}

          <button type="submit" className="btn-primary w-full">
            Run lookup
          </button>
        </div>
      </form>
    </div>
  );
}
