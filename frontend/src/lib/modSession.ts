import type { LoginResponse } from "@/lib/api";

// JWT is stored in localStorage (readable by XSS, but the backend only exposes
// an OAuth2 password flow that returns the token in the response body, so this
// is the pragmatic choice for this stack). Revoke via logout / token expiry.
const STORAGE_KEY = "tn_mod_token";

let listeners: Array<() => void> = [];
let cached: LoginResponse | null = null;

try {
  if (typeof window !== "undefined") {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) cached = JSON.parse(raw);
  }
} catch {
  /* ignore */
}

function emit() {
  for (const l of listeners) l();
}

export function subscribeSession(cb: () => void) {
  listeners.push(cb);
  // Keep other tabs in sync (same pattern as ThemeToggle).
  window.addEventListener("storage", onStorage);
  return () => {
    listeners = listeners.filter((l) => l !== cb);
    window.removeEventListener("storage", onStorage);
  };
}

function onStorage(e: StorageEvent) {
  if (e.key !== null && e.key !== STORAGE_KEY) return;
  try {
    cached = e.newValue ? JSON.parse(e.newValue) : null;
  } catch {
    cached = null;
  }
  emit();
}

export function getSessionSnapshot(): LoginResponse | null {
  return cached;
}

// During SSR/hydration we always render the logged-out state; the client
// snapshot is applied right after mount (hydration-safe, no mismatch).
export function getServerSessionSnapshot(): LoginResponse | null {
  return null;
}

export function storeSession(s: LoginResponse | null) {
  cached = s;
  try {
    if (s) localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
  emit();
}
