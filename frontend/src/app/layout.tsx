import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Stellar ThreatNet — Open Threat Intelligence for Stellar",
  description:
    "The open threat intelligence platform for the Stellar ecosystem: wallet, domain and token reputation, incidents, and community reports.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
        <footer className="border-t border-threat-border/60 py-6 text-center text-xs text-slate-500">
          Stellar ThreatNet — open-source security infrastructure for the Stellar ecosystem. Not a wallet, not an antivirus.
        </footer>
      </body>
    </html>
  );
}
