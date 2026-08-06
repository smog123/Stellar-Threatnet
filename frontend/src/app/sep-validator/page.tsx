import ModuleShell from "@/components/ModuleShell";

const SEP_LIST = ["SEP-1", "SEP-6", "SEP-10", "SEP-12", "SEP-24", "SEP-31", "SEP-38"];

export default function SepValidatorPage() {
  return (
    <ModuleShell
      title="SEP Validator"
      subtitle="Validate Stellar Ecosystem Proposals (SEPs) against the actual specifications — compliance score, per-check pass/fail, warnings, and remediation for every failed rule."
      phase="Phase 3"
      stats={[
        { label: "Validations", value: 0 },
        { label: "SEPs covered", value: SEP_LIST.length },
        { label: "Avg compliance", value: "—" },
        { label: "Failed checks", value: "—" },
      ]}
      capabilities={[
        { icon: "📜", title: SEP_LIST.slice(0, 4).join(" · "), desc: "Info file, deposit/withdrawal, auth, and KYC flow validation." },
        { icon: "🔁", title: SEP_LIST.slice(4).join(" · "), desc: "Interactive custody flows, cross-border payments, and FX quotes." },
        { icon: "✅", title: "Per-check pass/fail", desc: "Every required field and behavior is validated, not keyword-matched." },
        { icon: "📊", title: "Compliance score", desc: "Aggregated score with failed checks listed and explained." },
        { icon: "🛠️", title: "Remediation", desc: "Actionable fixes for every failed rule." },
        { icon: "🧩", title: "Extensible", desc: "New SEP versions and checks slot in as data-driven rules — no core changes." },
      ]}
      note="The validator architecture is designed as a rule registry: each SEP check is a self-contained, versioned rule with a pass/fail evaluation, explanation, and remediation. New SEPs are added without touching the core engine."
    />
  );
}
