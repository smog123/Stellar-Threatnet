"use client";

import { useEffect, useSyncExternalStore, useState } from "react";
import {
  login,
  getModerationQueue,
  moderateReport,
  PROOF_TYPES,
  ApiError,
  ReportItem,
} from "@/lib/api";
import {
  subscribeSession,
  getSessionSnapshot,
  getServerSessionSnapshot,
  storeSession,
} from "@/lib/modSession";
import StatusBadge from "@/components/StatusBadge";
import SectionHeader from "@/components/SectionHeader";
import { timeAgo } from "@/lib/time";

const entityIcon = (type: string) => (type === "wallet" ? "👛" : type === "domain" ? "🌐" : "🪙");

export default function ModerationPage() {
  const session = useSyncExternalStore(subscribeSession, getSessionSnapshot, getServerSessionSnapshot);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [queue, setQueue] = useState<ReportItem[] | null>(null);
  const [queueError, setQueueError] = useState<string | null>(null);

  // Expanded per-report moderation drawer state: reportId -> {proof, confidence, note}
  const [open, setOpen] = useState<string | null>(null);
  const [proof, setProof] = useState("tx_hash");
  const [confidence, setConfidence] = useState(0.9);
  const [note, setNote] = useState("");
  const [acting, setActing] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  // Load queue + self-refresh when a session is active.
  useEffect(() => {
    if (!session) return;
    let cancelled = false;
    const load = () =>
      getModerationQueue(session.access_token)
        .then((q) => {
          if (cancelled) return;
          setQueue(q);
          setQueueError(null); // clear stale errors once the queue loads
        })
        .catch((err) =>
          !cancelled &&
            setQueueError(err instanceof ApiError ? err.message : "Failed to load the moderation queue"),
        );
    load();
    const id = setInterval(load, 30_000); // self-refreshing queue
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [session]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setLoginError(null);
    try {
      const res = await login(email.trim(), password);
      storeSession(res);
      setEmail("");
      setPassword("");
    } catch (err) {
      setLoginError(err instanceof ApiError ? err.message : "Login failed — check your credentials");
    } finally {
      setBusy(false);
    }
  }

  function handleLogout() {
    storeSession(null);
    setQueue(null);
    setOpen(null);
  }

  async function handleAction(reportId: string, action: "approve" | "reject") {
    if (!session) return;
    if (action === "reject" && !note.trim()) {
      setActionError("A moderation note is required on rejection (governance rule).");
      return;
    }
    setActing(reportId);
    setActionError(null);
    try {
      await moderateReport(
        reportId,
        action,
        session.access_token,
        action === "approve"
          ? { proof_type: proof, confidence, moderation_note: note.trim() || undefined }
          : { moderation_note: note.trim() },
      );
      setQueue((q) => (q ? q.filter((r) => r.id !== reportId) : q));
      setOpen(null);
      setNote("");
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : "Moderation failed — try again");
    } finally {
      setActing(null);
    }
  }

  // ---- Login screen ---- //
  if (!session) {
    return (
      <div className="mx-auto max-w-md space-y-6">
        <section className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-white">Moderation Queue</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            Review community threat reports. Approvals attach evidence and recompute reputation;
            every decision is audit-logged.
          </p>
        </section>

        <form onSubmit={handleLogin} className="panel space-y-4 p-6">
          <div>
            <label htmlFor="mod-email" className="mb-1 block text-xs font-medium text-slate-400">
              Moderator email
            </label>
            <input
              id="mod-email"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-threat-border bg-slate-950/60 px-3 py-2 text-sm text-white outline-none transition focus:border-threat-accent/60"
              placeholder="moderator@stellar-threatnet.org"
            />
          </div>
          <div>
            <label htmlFor="mod-pass" className="mb-1 block text-xs font-medium text-slate-400">
              Password
            </label>
            <input
              id="mod-pass"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-threat-border bg-slate-950/60 px-3 py-2 text-sm text-white outline-none transition focus:border-threat-accent/60"
              placeholder="••••••••"
            />
          </div>
          {loginError && <p className="text-xs text-rose-400">{loginError}</p>}
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-lg bg-threat-accent px-4 py-2 text-sm font-semibold text-slate-950 transition hover:opacity-90 disabled:opacity-50"
          >
            {busy ? "Signing in…" : "Sign in"}
          </button>
          <p className="text-center text-[11px] text-slate-500">
            Requires a moderator or admin account. Demo: <span className="mono">moderator@stellar-threatnet.org</span> /{" "}
            <span className="mono">threatnet-demo</span>
          </p>
        </form>
      </div>
    );
  }

  // ---- Queue screen ---- //
  const pending = queue ?? [];
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <section className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Moderation Queue</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            Signed in as <span className="mono text-slate-200">{session.user.email}</span>{" "}
            <span className="rounded border border-threat-border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-threat-accent">
              {session.user.role}
            </span>
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="rounded-lg border border-threat-border px-3 py-1.5 text-xs text-slate-400 transition hover:border-rose-500/40 hover:text-rose-400"
        >
          Sign out
        </button>
      </section>

      <div className="panel p-4">
        <SectionHeader
          title="Awaiting review"
          subtitle="Auto-refreshes every 30s — approvals recompute scores immediately"
          action={<span className="mono text-xs text-slate-400">{pending.length} pending</span>}
        />
        {queueError && <p className="mt-2 text-xs text-rose-400">{queueError}</p>}
        {actionError && <p className="mt-2 text-xs text-rose-400">{actionError}</p>}

        {queue === null ? (
          <div className="h-24 animate-pulse rounded-lg bg-white/5" />
        ) : pending.length === 0 ? (
          <p className="py-8 text-center text-sm text-slate-500">
            Queue is clear — no reports awaiting moderation. New reports appear here automatically.
          </p>
        ) : (
          <ul className="mt-4 space-y-3">
            {pending.map((r) => (
              <li key={r.id} className="rounded-lg border border-threat-border/60 p-4 transition hover:border-threat-accent/30">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{entityIcon(r.target_type)}</span>
                      <span className="mono truncate text-sm text-slate-200">{r.target_value}</span>
                    </div>
                    <p className="mt-1.5 text-xs leading-relaxed text-slate-400">{r.description}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-slate-500">
                      <span className="mono">{r.id}</span>
                      <span>{r.category || "uncategorized"}</span>
                      <span>submitted {timeAgo(r.created_at)}</span>
                      <span>▲{r.upvotes} ▼{r.downvotes}</span>
                      {r.evidence_url && (
                        <a
                          href={r.evidence_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-threat-accent hover:underline"
                        >
                          evidence ↗
                        </a>
                      )}
                    </div>
                  </div>
                  <StatusBadge status="pending" />
                </div>

                <div className="mt-3 flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      setOpen(open === r.id ? null : r.id);
                      setProof("tx_hash");
                      setConfidence(0.9);
                      setNote("");
                      setActionError(null);
                    }}
                    className="rounded-lg border border-threat-border px-3 py-1.5 text-xs text-slate-300 transition hover:border-threat-accent/50 hover:text-white"
                  >
                    {open === r.id ? "Close" : "Review"}
                  </button>
                </div>

                {open === r.id && (
                  <div className="mt-4 rounded-lg border border-threat-border/60 bg-slate-950/40 p-4">
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <label className="mb-1 block text-[11px] font-medium text-slate-400">Proof type (approve)</label>
                        <select
                          value={proof}
                          onChange={(e) => setProof(e.target.value)}
                          className="w-full rounded-lg border border-threat-border bg-slate-950/60 px-2 py-1.5 text-xs text-white outline-none focus:border-threat-accent/60"
                        >
                          {PROOF_TYPES.map((p) => (
                            <option key={p.value} value={p.value}>
                              {p.value} (weight {p.weight}) — {p.hint}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="mb-1 block text-[11px] font-medium text-slate-400">
                          Confidence: {confidence.toFixed(2)}
                        </label>
                        <input
                          type="range"
                          min={0.1}
                          max={1}
                          step={0.05}
                          value={confidence}
                          onChange={(e) => setConfidence(Number(e.target.value))}
                          className="w-full accent-threat-accent"
                        />
                      </div>
                    </div>
                    <div className="mt-3">
                      <label className="mb-1 block text-[11px] font-medium text-slate-400">Moderation note</label>
                      <textarea
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        rows={2}
                        placeholder="Required on reject — e.g. duplicate, lacks evidence, wrong target"
                        className="w-full rounded-lg border border-threat-border bg-slate-950/60 px-2 py-1.5 text-xs text-white outline-none focus:border-threat-accent/60"
                      />
                    </div>
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={() => handleAction(r.id, "approve")}
                        disabled={acting !== null}
                        className="rounded-lg bg-emerald-500/90 px-4 py-1.5 text-xs font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:opacity-50"
                      >
                        {acting === r.id ? "Working…" : "✓ Approve"}
                      </button>
                      <button
                        onClick={() => handleAction(r.id, "reject")}
                        disabled={acting !== null}
                        className="rounded-lg bg-rose-500/90 px-4 py-1.5 text-xs font-semibold text-slate-950 transition hover:bg-rose-400 disabled:opacity-50"
                      >
                        {acting === r.id ? "Working…" : "✕ Reject"}
                      </button>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
