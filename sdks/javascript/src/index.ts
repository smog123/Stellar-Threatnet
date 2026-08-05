export interface WalletReputation {
  address: string;
  reputation_score: number;
  status: string;
  category: string | null;
  reason: string;
  report_count: number;
  last_updated: string;
}

export interface DomainReputation {
  domain_name: string;
  confidence_score: number;
  status: string;
  category: string;
  reason: string;
  ip_address: string | null;
  first_detected: string;
}

export interface TokenReputation {
  asset_identifier: string;
  asset_code: string;
  issuer_address: string;
  status: string;
  category: string;
  reason: string;
  confidence_score: number;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  affected_services: string;
  mitigations: string;
  references: string | null;
  severity: string;
  status: string;
  created_at: string;
  updated_at: string;
}

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
  entity_type: string;
  identifier: string;
  status: string;
  score: number;
  category: string | null;
  reason: string;
  updated_at: string;
}

export interface SearchResults {
  query: string;
  total: number;
  results: Array<Record<string, unknown>>;
}

export interface AIResponse {
  query: string;
  analysis: string;
  confidence_disclaimer: string;
  sources_referenced: string[];
}

export interface ThreatNetClientOptions {
  baseUrl?: string;
  apiKey?: string;
  token?: string;
  fetch?: typeof fetch;
}

export class ThreatNetClient {
  private readonly baseUrl: string;
  private readonly headers: Record<string, string>;
  private readonly fetchFn: typeof fetch;

  constructor(options: ThreatNetClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? "https://api.stellar-threatnet.org/api/v1").replace(/\/$/, "");
    this.headers = {};
    if (options.apiKey) this.headers["X-API-Key"] = options.apiKey;
    else if (options.token) this.headers["Authorization"] = `Bearer ${options.token}`;
    this.fetchFn = options.fetch ?? fetch;
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await this.fetchFn(`${this.baseUrl}${path}`, {
      ...init,
      headers: { ...this.headers, ...(init?.headers ?? {}) },
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = (await res.json()) as { detail?: string };
        if (body.detail) detail = body.detail;
      } catch {
        /* non-JSON error body */
      }
      throw new Error(`ThreatNet API ${res.status}: ${detail}`);
    }
    return (await res.json()) as T;
  }

  lookupWallet(address: string): Promise<WalletReputation> {
    return this.request(`/lookup/wallet/${encodeURIComponent(address)}`);
  }

  lookupDomain(domain: string): Promise<DomainReputation> {
    return this.request(`/lookup/domain/${encodeURIComponent(domain)}`);
  }

  lookupToken(assetCode: string, issuer: string): Promise<TokenReputation> {
    return this.request(`/lookup/token/${encodeURIComponent(assetCode)}/${encodeURIComponent(issuer)}`);
  }

  incidents(status?: string, limit = 20, offset = 0): Promise<{ total: number; items: Incident[] }> {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (status) params.set("status", status);
    return this.request(`/incidents?${params.toString()}`);
  }

  incident(id: string): Promise<Incident> {
    return this.request(`/incidents/${encodeURIComponent(id)}`);
  }

  latestThreats(limit = 10): Promise<LatestThreat[]> {
    return this.request(`/threats/latest?limit=${limit}`);
  }

  stats(): Promise<GlobalStats> {
    return this.request("/stats");
  }

  search(query: string, entityType?: string, limit = 20): Promise<SearchResults> {
    const params = new URLSearchParams({ q: query, limit: String(limit) });
    if (entityType) params.set("type", entityType);
    return this.request(`/search?${params.toString()}`);
  }

  async downloadFeed(): Promise<string> {
    const res = await this.fetchFn(`${this.baseUrl}/feed`);
    if (!res.ok) throw new Error(`ThreatNet API ${res.status}: feed download failed`);
    return res.text();
  }

  submitReport(input: {
    targetType: "wallet" | "domain" | "token";
    targetValue: string;
    description: string;
    category?: string;
    evidenceUrl?: string;
  }): Promise<{ id: string; status: string }> {
    return this.request("/reports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_type: input.targetType,
        target_value: input.targetValue,
        description: input.description,
        category: input.category,
        evidence_url: input.evidenceUrl,
      }),
    });
  }

  aiQuery(query: string, contextType = "general"): Promise<AIResponse> {
    return this.request("/ai/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, context_type: contextType }),
    });
  }
}

export default ThreatNetClient;
