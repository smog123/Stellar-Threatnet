import Link from "next/link";
import ReportForm from "@/components/ReportForm";

const PROCESS = [
  { step: "1", title: "Submit", desc: "Verified users report wallets, domains, and assets with evidence URLs." },
  { step: "2", title: "Vote", desc: "Community members up/down-vote pending reports — one vote per user." },
  { step: "3", title: "Moderate", desc: "Moderators approve or reject; approvals attach evidence and recompute scores." },
  { step: "4", title: "Distribute", desc: "Approved indicators flow into lookups, the feed, and the intelligence database." },
];

export default function CommunityPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Community</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          The community is the sensor network: verified users submit threat reports, vote for
          consensus, and every approved report improves ecosystem reputation data.
        </p>
      </section>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {PROCESS.map((p) => (
          <div key={p.step} className="panel p-4">
            <span className="mono grid h-7 w-7 place-items-center rounded-lg bg-threat-accent/15 text-xs font-bold text-threat-accent">
              {p.step}
            </span>
            <h3 className="mt-2 text-sm font-semibold text-white">{p.title}</h3>
            <p className="mt-1 text-xs leading-relaxed text-slate-400">{p.desc}</p>
          </div>
        ))}
      </section>

      <div className="grid gap-8 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <h2 className="mb-3 text-sm font-semibold text-white">Submit a threat report</h2>
          <ReportForm />
        </div>
        <aside className="space-y-4 lg:col-span-2">
          <div className="panel p-5">
            <h3 className="text-sm font-semibold text-white">Moderation status</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-400">
              <li className="flex items-center justify-between">
                <span>Pending review</span>
                <StatusPill className="bg-sky-500/15 text-sky-400 border-sky-500/30">pending</StatusPill>
              </li>
              <li className="flex items-center justify-between">
                <span>Approved</span>
                <StatusPill className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30">approved</StatusPill>
              </li>
              <li className="flex items-center justify-between">
                <span>Rejected</span>
                <StatusPill className="bg-slate-500/15 text-slate-400 border-slate-500/30">rejected</StatusPill>
              </li>
            </ul>
            <p className="mt-4 text-xs leading-relaxed text-slate-500">
              Track your report by its ID in the API (<span className="mono">GET /reports/queue</span> for
              moderators) or watch the activity feed on the dashboard.
            </p>
          </div>
          <div className="panel p-5">
            <h3 className="text-sm font-semibold text-white">Authenticate</h3>
            <p className="mt-2 text-xs leading-relaxed text-slate-500">
              Reporting requires an account. Create one with{" "}
              <span className="mono">POST /api/v1/auth/register</span>, then use the returned token (or an{" "}
              <span className="mono">tn_...</span> API key) in the form.
            </p>
            <Link href="/docs" className="mt-3 inline-block text-xs text-threat-accent hover:underline">
              API documentation →
            </Link>
          </div>
        </aside>
      </div>
    </div>
  );
}

function StatusPill({ className, children }: { className: string; children: React.ReactNode }) {
  return (
    <span className={`rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${className}`}>
      {children}
    </span>
  );
}
