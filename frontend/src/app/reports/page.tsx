import ReportForm from "@/components/ReportForm";

export default function ReportsPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <section>
        <h1 className="text-2xl font-bold tracking-tight text-white">Community Reporting</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Report a malicious wallet, phishing site, or fake token. Every report is reviewed by a
          moderator before it affects reputation scores.
        </p>
      </section>

      <ReportForm />
    </div>
  );
}
