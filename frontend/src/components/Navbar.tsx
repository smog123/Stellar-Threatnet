"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import ThemeToggle from "@/components/ThemeToggle";
import { GITBOOK_URL } from "@/lib/site";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/wallet", label: "Wallet Reputation" },
  { href: "/asset", label: "Asset Reputation" },
  { href: "/anchor", label: "Anchor Reputation" },
  { href: "/scanner", label: "Soroban Scanner" },
  { href: "/sep-validator", label: "SEP Validator" },
  { href: "/threat-intel", label: "Threat Intelligence" },
  { href: "/advisories", label: "Security Advisories" },
  { href: "/community", label: "Community" },
  { href: "/moderation", label: "Moderation" },
  { href: "/docs", label: "API Docs" },
  { href: GITBOOK_URL, label: "GitBook Docs", external: true },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-threat-border/70 bg-threat-bg/80 backdrop-blur-md">
      <nav className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link href="/" className="group flex shrink-0 items-center gap-2.5">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-linear-to-br from-threat-accent to-cyan-600 font-mono text-sm font-bold text-slate-950 shadow-glow">
            TN
          </span>
          <span className="hidden flex-col leading-tight sm:flex">
            <span className="text-sm font-bold tracking-tight text-white">Stellar ThreatNet</span>
            <span className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
              Security Operations Center
            </span>
          </span>
        </Link>

        <ul className="flex items-center gap-1 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {links.map((link) => {
            const active =
              !link.external && (pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href)));
            const cls = `whitespace-nowrap rounded-lg px-2.5 py-2 text-[13px] font-medium transition ${
              active
                ? "bg-threat-accent/10 text-threat-accent"
                : "text-slate-400 hover:bg-white/5 hover:text-white"
            }`;
            return (
              <li key={link.href} className="shrink-0">
                {link.external ? (
                  <a href={link.href} target="_blank" rel="noopener noreferrer" className={cls}>
                    {link.label}
                    <span className="ml-1 text-[10px] opacity-70" aria-hidden="true">
                      ↗
                    </span>
                    <span className="sr-only">(opens in a new tab)</span>
                  </a>
                ) : (
                  <Link href={link.href} className={cls}>
                    {link.label}
                  </Link>
                )}
              </li>
            );
          })}
          <li className="shrink-0">
            <ThemeToggle />
          </li>
        </ul>
      </nav>
    </header>
  );
}
