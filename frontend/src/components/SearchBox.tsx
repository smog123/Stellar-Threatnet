"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Mode = "wallet" | "domain" | "asset";

const MODE_META: Record<Mode, { label: string; placeholder: string; button: string }> = {
  wallet: { label: "Wallet address", placeholder: "G… (56 chars)", button: "Check wallet reputation" },
  domain: { label: "Domain", placeholder: "example-phishing-site.com", button: "Check domain reputation" },
  asset: { label: "Asset code", placeholder: "USDC", button: "Check asset reputation" },
};

export default function SearchBox({ mode }: { mode: Mode }) {
  const router = useRouter();
  const [primary, setPrimary] = useState("");
  const [issuer, setIssuer] = useState("");
  const [error, setError] = useState<string | null>(null);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const value = primary.trim();
    if (mode === "wallet") {
      if (!value) return setError("Enter a Stellar wallet address (G…).");
      router.push(`/lookup/wallet/${encodeURIComponent(value)}`);
    } else if (mode === "domain") {
      if (!value) return setError("Enter a domain name.");
      router.push(`/lookup/domain/${encodeURIComponent(value)}`);
    } else {
      if (!value || !issuer.trim()) return setError("Asset code and issuer are both required.");
      router.push(`/lookup/token/${encodeURIComponent(value)}/${encodeURIComponent(issuer.trim())}`);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div>
        <label className="label mb-1.5 block">{MODE_META[mode].label}</label>
        <input
          className="input mono"
          value={primary}
          onChange={(e) => setPrimary(e.target.value)}
          placeholder={MODE_META[mode].placeholder}
          spellCheck={false}
          autoFocus
        />
      </div>
      {mode === "asset" ? (
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
        {MODE_META[mode].button}
      </button>
    </form>
  );
}
