import ModuleShell from "@/components/ModuleShell";

export default function AnchorReputationPage() {
  return (
    <ModuleShell
      title="Anchor Reputation"
      subtitle="Security profiles for Stellar anchors: SEP compliance, custody posture, past incidents, and community feedback — the trust layer for issuing and redeeming assets."
      phase="Phase 2"
      stats={[
        { label: "Anchors profiled", value: 0 },
        { label: "High risk", value: "—" },
        { label: "Verified", value: "—" },
        { label: "Pending review", value: "—" },
      ]}
      capabilities={[
        { icon: "🛡️", title: "Security score", desc: "Composite posture score from SEP compliance, custody, and incident history." },
        { icon: "📋", title: "Compliance status", desc: "SEP-1 info file validity, KYC/KYB posture, and regulatory disclosures." },
        { icon: "🚨", title: "Past incidents", desc: "Linked security events and how they were resolved." },
        { icon: "🐛", title: "Reported issues", desc: "Community-reported problems surfaced from the moderation queue." },
        { icon: "💬", title: "Community feedback", desc: "Reputation-weighted sentiment from verified reporters." },
        { icon: "🔗", title: "Issued assets", desc: "Cross-links to asset reputation for everything the anchor issues." },
      ]}
      note="Anchor security profiles are being built in the next phase: model + API (GET /anchors, POST /anchors/{id}/report) with tests, then this page goes live with real scores."
    />
  );
}
