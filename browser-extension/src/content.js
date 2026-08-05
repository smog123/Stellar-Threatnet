/**
 * Stellar ThreatNet — content script.
 *
 * On every page, asks the background worker to check the current hostname.
 * If the domain is confirmed malicious or suspicious, an interstitial-style
 * warning banner is injected at the top of the page.
 */
(() => {
  "use strict";

  const hostname = window.location.hostname;
  const EXCLUDE = ["localhost", "127.0.0.1"];

  function injectWarning(level, record) {
    const banner = document.createElement("div");
    banner.id = "tn-warning-banner";
    banner.dataset.level = level;

    const icon = level === "block" ? "🚫" : level === "warn" ? "⚠️" : "ℹ️";
    const title =
      level === "block"
        ? "Blocked by Stellar ThreatNet — confirmed phishing site"
        : level === "warn"
          ? "Warning: flagged as suspicious by Stellar ThreatNet"
          : "Stellar ThreatNet notice";

    banner.innerHTML = `
      <div class="tn-banner-inner">
        <span class="tn-icon">${icon}</span>
        <div class="tn-body">
          <div class="tn-title">${title}</div>
          <div class="tn-detail">${hostname} — ${record?.category || "flagged entity"}.</div>
          <div class="tn-reason">${record?.reason || "No details available."}</div>
          <div class="tn-actions">
            <button class="tn-btn tn-btn-danger" id="tn-leave">Leave this site</button>
            <button class="tn-btn tn-btn-ghost" id="tn-continue">I understand the risk, continue</button>
          </div>
        </div>
      </div>`;

    document.documentElement.prepend(banner);

    document.getElementById("tn-leave")?.addEventListener("click", () => {
      window.location.href = "about:blank";
    });
    document.getElementById("tn-continue")?.addEventListener("click", () => {
      banner.remove();
      window.__tn_dismissed = true;
    });
  }

  if (EXCLUDE.includes(hostname)) return;
  if (window.__tn_checked) return;
  window.__tn_checked = true;

  chrome.runtime.sendMessage({ type: "TN_CHECK_DOMAIN", hostname }, (response) => {
    if (!response || !response.classification) return;
    const { level, reason } = response.classification;
    if (level === "block" || level === "warn") {
      injectWarning(level, response.record);
    }
  });
})();
