import ModuleShell from "@/components/ModuleShell";

export default function ScannerPage() {
  return (
    <ModuleShell
      title="Soroban Contract Scanner"
      subtitle="Static security analysis for Soroban smart contracts — upload Rust source, paste code, or connect a GitHub repository for a rule-based audit with severity-ranked findings."
      phase="Phase 3"
      stats={[
        { label: "Scans run", value: 0 },
        { label: "Rules", value: "25+" },
        { label: "Avg risk score", value: "—" },
        { label: "Critical findings", value: "—" },
      ]}
      capabilities={[
        { icon: "🔑", title: "Authorization issues", desc: "require_auth misuse, missing authentication, admin-only functions callable by anyone." },
        { icon: "🕸️", title: "Permission graph", desc: "Visualize which addresses can invoke which contract functions." },
        { icon: "🗄️", title: "Storage analysis", desc: "Unbounded storage growth, missing ttl bumps, persistent vs instance misuse." },
        { icon: "⬆️", title: "Upgrade safety", desc: "Admin upgrade functions without timelock or contract version pinning." },
        { icon: "🪙", title: "Token logic", desc: "Clawback/freeze abuse, unwrapped token handling, balance rounding issues." },
        { icon: "🧰", title: "Fix recommendations", desc: "Every finding includes severity, confidence, explanation, and remediation." },
      ]}
      note="The rule engine is being built as a modular, extensible detector framework (register new rules without touching core code). Input methods (upload / paste / GitHub) and the analysis API land with it — then this page becomes interactive."
    />
  );
}
