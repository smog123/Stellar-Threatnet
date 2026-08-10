import { API_URL } from "@/lib/api";
import { GITBOOK_URL } from "@/lib/site";

const ENDPOINTS = [
  { method: "GET", path: "/lookup/wallet/{address}", auth: "public", desc: "Wallet reputation score and category" },
  { method: "GET", path: "/lookup/domain/{domain}", auth: "public", desc: "Phishing/impersonation domain score" },
  { method: "GET", path: "/lookup/token/{code}/{issuer}", auth: "public", desc: "Token reputation by CODE:ISSUER" },
  { method: "GET", path: "/incidents", auth: "public", desc: "Paginated incident timeline" },
  { method: "POST", path: "/incidents", auth: "analyst+", desc: "Publish a security incident" },
  { method: "GET", path: "/threats/latest", auth: "public", desc: "Most recently updated threats" },
  { method: "GET", path: "/feed", auth: "public", desc: "Full threat feed as CSV" },
  { method: "GET", path: "/stats", auth: "public", desc: "Global dashboard statistics" },
  { method: "GET", path: "/search?q=", auth: "public", desc: "Search wallets, domains, tokens, incidents" },
  { method: "POST", path: "/reports", auth: "auth", desc: "Submit a community threat report" },
  { method: "POST", path: "/reports/{id}/vote", auth: "auth", desc: "Up/down-vote a pending report" },
  { method: "POST", path: "/reports/{id}/moderate", auth: "moderator+", desc: "Approve/reject and attach evidence" },
  { method: "POST", path: "/ai/query", auth: "public", desc: "Ask the AI threat assistant" },
  { method: "POST", path: "/auth/register", auth: "public", desc: "Create an account" },
  { method: "POST", path: "/auth/token", auth: "public", desc: "Login → JWT" },
];

export default function DocsPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">API Documentation</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Base URL: <span className="mono text-threat-accent">{API_URL}</span> · Interactive docs at{" "}
          <span className="mono text-threat-accent">/docs</span> (Swagger UI) · Full guides on{" "}
          <a
            href={GITBOOK_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-threat-accent underline-offset-2 transition hover:underline"
          >
            GitBook ↗
          </a>
        </p>
      </section>

      <section className="panel overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-threat-border text-xs uppercase tracking-widest text-slate-500">
              <th className="px-4 py-3">Method</th>
              <th className="px-4 py-3">Endpoint</th>
              <th className="px-4 py-3">Auth</th>
              <th className="px-4 py-3">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-threat-border/60">
            {ENDPOINTS.map((ep) => (
              <tr key={ep.method + ep.path} className="transition hover:bg-white/[0.02]">
                <td className="px-4 py-3">
                  <span
                    className={`rounded px-1.5 py-0.5 font-mono text-[11px] font-bold ${
                      ep.method === "GET" ? "bg-emerald-500/15 text-emerald-400" : "bg-amber-500/15 text-amber-400"
                    }`}
                  >
                    {ep.method}
                  </span>
                </td>
                <td className="mono px-4 py-3 text-slate-300">{ep.path}</td>
                <td className="px-4 py-3 text-xs text-slate-500">{ep.auth}</td>
                <td className="px-4 py-3 text-slate-400">{ep.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel space-y-3 p-6">
        <h2 className="text-sm font-semibold text-white">Authentication</h2>
        <pre className="overflow-x-auto rounded-lg bg-threat-bg p-4 font-mono text-xs leading-relaxed text-slate-300">{`# JWT (interactive clients)
Authorization: Bearer <jwt>

# API key (programmatic clients / SDKs)
X-API-Key: tn_...`}</pre>
      </section>

      <section className="panel space-y-3 p-6">
        <h2 className="text-sm font-semibold text-white">Scoring model</h2>
        <p className="text-sm leading-relaxed text-slate-400">
          Reputation scores run <span className="mono text-slate-300">0–100</span>:
          <span className="mono text-rose-400"> 0–20 confirmed malicious</span> (block),
          <span className="mono text-amber-400"> 21–50 suspicious</span> (warn),
          <span className="mono text-sky-400"> 51–79 under investigation</span> (info),
          <span className="mono text-emerald-400"> 80–100 trusted</span> (allow).
          A <span className="mono">404</span> on lookup means <em>no data</em> — never treat it as trusted.
          Full formula: <span className="mono text-slate-300">S(E) = 80 − Σ(Wᵢ × Cᵢ) + 20(verified)</span>.
        </p>
      </section>

      <section className="panel space-y-3 p-6">
        <h2 className="text-sm font-semibold text-white">SDKs & CLI</h2>
        <ul className="list-inside list-disc space-y-1.5 text-sm text-slate-400">
          <li>
            Python SDK — <span className="mono text-slate-300">pip install -e ./sdks/python</span>
          </li>
          <li>
            TypeScript SDK — <span className="mono text-slate-300">./sdks/javascript</span>
          </li>
          <li>
            CLI — <span className="mono text-slate-300">threatnet lookup wallet G…</span>
          </li>
        </ul>
      </section>
    </div>
  );
}
