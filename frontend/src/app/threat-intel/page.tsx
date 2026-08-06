"use client";

import { useEffect, useState } from "react";
import { ApiError, search, SearchResultItem } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";
import SectionHeader from "@/components/SectionHeader";

type EntityFilter = "wallet" | "domain" | "token" | "incident";

const FILTERS: { value: EntityFilter; label: string; icon: string }[] = [
  { value: "wallet", label: "Wallets", icon: "👛" },
  { value: "domain", label: "Domains", icon: "🌐" },
  { value: "token", label: "Tokens", icon: "🪙" },
  { value: "incident", label: "Incidents", icon: "🚨" },
];

export default function ThreatIntelPage() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<Set<EntityFilter>>(new Set());
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  function toggleFilter(f: EntityFilter) {
    setFilters((prev) => {
      const next = new Set(prev);
      if (next.has(f)) next.delete(f);
      else next.add(f);
      return next;
    });
  }

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setTotal(0);
      return;
    }
    const type = filters.size ? Array.from(filters).join(",") : undefined;
    const timer = setTimeout(() => {
      search(query.trim(), type, 50)
        .then((r) => {
          setResults(r.results);
          setTotal(r.total);
          setSearched(true);
          setError(null);
        })
        .catch((err) => setError(err instanceof ApiError ? err.message : "Search failed"));
    }, 350);
    return () => clearTimeout(timer);
  }, [query, filters]);

  const entityIcon = (t: string) => (t === "wallet" ? "👛" : t === "domain" ? "🌐" : t === "token" ? "🪙" : "🚨");

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Threat Intelligence</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Search the shared database of malicious wallets, phishing domains, scam assets, and attack
          campaigns — everything ThreatNet tracks in one place.
        </p>
      </section>

      <section className="panel p-6">
        <SectionHeader title="Search the intelligence database" subtitle="Matches wallets, domains, tokens, and incidents" />
        <div className="relative">
          <input
            className="input mono"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. stellar airdrop, G…, getxlm.org, USDC…"
            spellCheck={false}
            autoFocus
          />
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => toggleFilter(f.value)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                filters.has(f.value)
                  ? "bg-threat-accent/15 text-threat-accent ring-1 ring-threat-accent/40"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              {f.icon} {f.label}
            </button>
          ))}
          {filters.size > 0 ? (
            <button onClick={() => setFilters(new Set())} className="text-xs text-slate-500 hover:text-white">
              clear
            </button>
          ) : null}
        </div>
      </section>

      {error ? <div className="panel border-rose-500/40 p-4 text-sm text-rose-400">{error}</div> : null}

      <section className="panel p-5">
        {!searched && results.length === 0 ? (
          <p className="py-8 text-center text-sm text-slate-500">
            Type a query above to search wallets, domains, tokens, and incidents.
          </p>
        ) : (
          <>
            <p className="mb-3 text-xs text-slate-500">{total} result{total === 1 ? "" : "s"}</p>
            {results.length === 0 ? (
              <p className="py-8 text-center text-sm text-slate-500">No matches — the entity may be untracked (neutral, not trusted).</p>
            ) : (
              <ul className="divide-y divide-threat-border/60">
                {results.map((r, i) => (
                  <li key={`${r.entity_type}-${r.identifier}-${i}`} className="flex items-center gap-3 py-3">
                    <span className="text-lg">{entityIcon(r.entity_type)}</span>
                    <div className="min-w-0 flex-1">
                      <p className="mono truncate text-slate-200">{r.identifier}</p>
                      <p className="truncate text-xs text-slate-500">
                        {r.category ?? r.entity_type} — {r.reason ?? ""}
                      </p>
                    </div>
                    {r.score !== null && r.score !== undefined ? (
                      <span className="mono shrink-0 text-sm text-slate-300">{Math.round(r.score)}</span>
                    ) : null}
                    {r.status ? <StatusBadge status={r.status} /> : null}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>
    </div>
  );
}
