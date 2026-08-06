export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export interface GlobalStats {
  total_malicious_wallets: number;
  total_phishing_domains: number;
  total_scam_tokens: number;
  total_incidents_recorded: number;
  active_campaigns_count: number;
  pending_reports: number;
  total_indicators: number;
}

export interface LatestThreat {
  entity_type: "wallet" | "domain" | "token";
  identifier: string;
  status: string;
  score: number;
  category: string | null;
  reason: string;
  updated_at: string;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  affected_services: string;
  mitigations: string;
  references: string | null;
  severity: "critical" | "high" | "medium" | "low";
  status: string;
  created_at: string;
  updated_at: string;
}

export interface IncidentsPage {
  total: number;
  offset: number;
  limit: number;
  items: Incident[];
}

export interface WalletLookup {
  address: string;
  reputation_score: number;
  status: string;
  category: string | null;
  reason: string;
  report_count: number;
  last_updated: string;
}

export interface DomainLookup {
  domain_name: string;
  confidence_score: number;
  status: string;
  category: string;
  reason: string;
  ip_address: string | null;
  first_detected: string;
}

export interface TokenLookup {
  asset_identifier: string;
  asset_code: string;
  issuer_address: string;
  status: string;
  category: string;
  reason: string;
  confidence_score: number;
}

// ---- Security Operations Center (SOC) overview ---- //
export interface StatusCounts {
  confirmed_malicious: number;
  suspicious: number;
  under_investigation: number;
  trusted: number;
}

export interface ThreatLandscape {
  wallets: StatusCounts;
  domains: StatusCounts;
  tokens: StatusCounts;
}

export interface ModuleStats {
  anchors: number;
  soroban_scans: number;
  sep_validations: number;
}

export interface NetworkStatus {
  level: "normal" | "elevated" | "high";
  label: string;
  summary: string;
}

export interface ReportItem {
  id: string;
  target_type: string;
  target_value: string;
  category: string | null;
  description: string;
  evidence_url: string | null;
  upvotes: number;
  downvotes: number;
  status: string;
  created_at: string;
}

export interface SocOverview {
  generated_at: string;
  network_status: NetworkStatus;
  landscape: ThreatLandscape;
  counts: GlobalStats;
  modules: ModuleStats;
  active_campaigns: Incident[];
  latest_threats: LatestThreat[];
  recent_reports: ReportItem[];
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const headers: Record<string, string> = { ...(init?.headers as Record<string, string>) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${path}`, { ...init, headers, cache: "no-store" });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export function getStats(): Promise<GlobalStats> {
  return request("/stats");
}

export function getSocOverview(): Promise<SocOverview> {
  return request("/stats/overview");
}

export function getLatestThreats(limit = 8): Promise<LatestThreat[]> {
  return request(`/threats/latest?limit=${limit}`);
}

export function getIncidents(status?: string, limit = 10, offset = 0): Promise<IncidentsPage> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (status) params.set("status", status);
  return request(`/incidents?${params.toString()}`);
}

export function lookupWallet(address: string): Promise<WalletLookup> {
  return request(`/lookup/wallet/${encodeURIComponent(address)}`);
}

export function lookupDomain(domain: string): Promise<DomainLookup> {
  return request(`/lookup/domain/${encodeURIComponent(domain)}`);
}

export function lookupToken(assetCode: string, issuer: string): Promise<TokenLookup> {
  return request(`/lookup/token/${encodeURIComponent(assetCode)}/${encodeURIComponent(issuer)}`);
}

export interface SearchResultItem {
  entity_type: string;
  identifier: string;
  status: string | null;
  score: number | null;
  category: string | null;
  reason: string | null;
  updated_at: string | null;
}

export interface SearchResults {
  query: string;
  total: number;
  results: SearchResultItem[];
}

export interface ReportPayload {
  target_type: string;
  target_value: string;
  category?: string;
  description: string;
  evidence_url?: string;
}

export function search(query: string, entityType?: string, limit = 20): Promise<SearchResults> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  if (entityType) params.set("type", entityType);
  return request(`/search?${params.toString()}`);
}

export function submitReport(payload: ReportPayload, token?: string): Promise<{ id: string; status: string }> {
  return request(
    "/reports",
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) },
    token,
  );
}
