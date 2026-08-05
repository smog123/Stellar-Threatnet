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
          bg: "#070b14",
          panel: "#0d1424",
          border: "#1c2942",
          accent: "#22d3ee",
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
