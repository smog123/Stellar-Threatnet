/**
 * Stellar ThreatNet — background service worker.
 *
 * Checks page hostnames against the ThreatNet API and caches results for
 * CACHE_TTL_MS so we don't hammer the API on every navigation.
 */
const API_BASE = "https://api.stellar-threatnet.org/api/v1";
const CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes

async function lookupDomain(hostname) {
  const cacheKey = `tn:${hostname}`;
  const cached = await chrome.storage.local.get(cacheKey);
  if (cached[cacheKey] && Date.now() - cached[cacheKey].fetchedAt < CACHE_TTL_MS) {
    return cached[cacheKey].data;
  }

  try {
    const res = await fetch(`${API_BASE}/lookup/domain/${encodeURIComponent(hostname)}`);
    if (res.status === 404) {
      // Not tracked: cache a neutral result briefly.
      const neutral = { status: "untracked", confidence_score: 0, category: null, reason: "Not in ThreatNet database" };
      await chrome.storage.local.set({ [cacheKey]: { fetchedAt: Date.now(), data: neutral } });
      return neutral;
    }
    if (!res.ok) return { status: "unknown", confidence_score: 0, category: null, reason: `API error ${res.status}` };
    const data = await res.json();
    await chrome.storage.local.set({ [cacheKey]: { fetchedAt: Date.now(), data } });
    return data;
  } catch (err) {
    return { status: "unknown", confidence_score: 0, category: null, reason: "API unreachable" };
  }
}

function classify(record) {
  if (!record || record.status === "untracked" || record.status === "unknown") {
    return { level: "none", reason: record?.reason || "No threat data" };
  }
  if (record.status === "confirmed_malicious") return { level: "block", reason: record.reason };
  if (record.status === "suspicious") return { level: "warn", reason: record.reason };
  return { level: "info", reason: record.reason };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "TN_CHECK_DOMAIN") {
    lookupDomain(message.hostname)
      .then((record) => sendResponse({ hostname: message.hostname, record, classification: classify(record) }))
      .catch(() => sendResponse({ hostname: message.hostname, record: null, classification: { level: "none", reason: "Lookup failed" } }));
    return true; // async response
  }
});
