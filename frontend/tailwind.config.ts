import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        threat: {
          malicious: "#f43f5e",
          suspicious: "#f59e0b",
          investigating: "#38bdf8",
          trusted: "#10b981",
          bg: "rgb(var(--threat-bg-rgb) / <alpha-value>)",
          panel: "rgb(var(--threat-panel-rgb) / <alpha-value>)",
          border: "rgb(var(--threat-border-rgb) / <alpha-value>)",
          accent: "rgb(var(--threat-accent-rgb) / <alpha-value>)",
        },
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        glow: "0 0 24px rgba(34, 211, 238, 0.15)",
      },
    },
  },
  plugins: [],
};

export default config;
