"use client";

import { useState } from "react";
import { ApiError, submitReport } from "@/lib/api";

type TargetType = "wallet" | "domain" | "token";

export default function ReportsPage() {
  const [targetType, setTargetType] = useState<TargetType>("wallet");
  const [targetValue, setTargetValue] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [token, setToken] = useState("");
  const [state, setState] = useState<"idle" | "submitting" | "done" | "error">("idle");
  const [message, setMessage] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setState("submitting");
    setMessage("");
    try {
      const result = await submitReport(
        {
          target_type: targetType,
          target_value: targetValue.trim(),
          category: category.trim() || undefined,
          description: description.trim(),
          evidence_url: evidenceUrl.trim() || undefined,
        },
        token.trim() || undefined,
      );
      setState("done");
      setMessage(`Report ${result.id} queued for moderation (status: ${result.status}).`);
      setTargetValue("");
      setDescription("");
      setEvidenceUrl("");
    } catch (err) {
      setState("error");
      if (err instanceof ApiError && err.status === 401) {
        setMessage("Authentication required — paste a token (see below) or register via the API.");
      } else {
        setMessage(err instanceof Error ? err.message : "Submission failed");
      }
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Community Reporting</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Report a malicious wallet, phishing site, or fake token. Every report is reviewed by a
          moderator before it affects reputation scores.
        </p>
      </section>

      <form onSubmit={submit} className="panel space-y-5 p-6">
        <div>
          <p className="label mb-2">Target type</p>
          <div className="flex gap-2">
            {(["wallet", "domain", "token"] as TargetType[]).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTargetType(t)}
                className={`flex-1 rounded-lg px-4 py-2 text-sm font-semibold capitalize transition ${
                  targetType === t
                    ? "bg-threat-accent/15 text-threat-accent ring-1 ring-threat-accent/40"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="label mb-1.5 block">
            Target value {targetType === "token" ? "(CODE:ISSUER)" : ""}
          </label>
          <input
            className="input mono"
            value={targetValue}
            onChange={(e) => setTargetValue(e.target.value)}
            placeholder={targetType === "token" ? "USDC:G…" : targetType === "domain" ? "phishing-site.com" : "G…"}
            required
            spellCheck={false}
          />
        </div>

        <div>
          <label className="label mb-1.5 block">Suggested category (optional)</label>
          <input
            className="input"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder={targetType === "domain" ? "Fake Airdrop" : targetType === "token" ? "Impersonation Token" : "Malicious Drainer"}
          />
        </div>

        <div>
          <label className="label mb-1.5 block">Description</label>
          <textarea
            className="input min-h-28 resize-y"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Why is this a threat? Include transaction hashes, URLs, or screenshots links."
            required
          />
        </div>

        <div>
          <label className="label mb-1.5 block">Evidence URL (optional)</label>
          <input
            className="input mono"
            value={evidenceUrl}
            onChange={(e) => setEvidenceUrl(e.target.value)}
            placeholder="https://stellar.expert/tx/…"
            spellCheck={false}
          />
        </div>

        <details className="rounded-lg border border-threat-border/60 p-3 text-xs text-slate-400">
          <summary className="cursor-pointer font-medium text-slate-300">Authenticated? Paste an API token (optional)</summary>
          <p className="mt-2">
            Reports require authentication. Paste a JWT or <span className="mono">tn_...</span> API key, or
            register via <span className="mono">POST /api/v1/auth/register</span>.
          </p>
          <input
            className="input mt-2"
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="tn_… or JWT"
          />
        </details>

        {state === "done" ? <p className="text-sm text-emerald-400">{message}</p> : null}
        {state === "error" ? <p className="text-sm text-rose-400">{message}</p> : null}

        <button type="submit" className="btn-primary w-full" disabled={state === "submitting"}>
          {state === "submitting" ? "Submitting…" : "Submit report"}
        </button>
      </form>
    </div>
  );
}
