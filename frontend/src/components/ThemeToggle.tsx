"use client";

import { useEffect, useRef, useSyncExternalStore } from "react";

const STORAGE_KEY = "tn-theme";

function subscribe(cb: () => void) {
  window.addEventListener("storage", cb);
  return () => window.removeEventListener("storage", cb);
}

function getSnapshot(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) !== "dark";
  } catch {
    return true;
  }
}

// Server snapshot — during hydration React re-checks the client snapshot and
// re-renders if it differs, without emitting a hydration mismatch warning.
function getServerSnapshot(): boolean {
  return true;
}

export default function ThemeToggle() {
  const light = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  const firstApply = useRef(true);

  // Keep the external DOM class in sync with the store value. The first run is
  // skipped: the layout's pre-paint script already applied the correct theme,
  // and applying the server-snapshot value first would flash the wrong theme
  // (e.g. flipping a dark-mode user to light for one frame after hydration).
  useEffect(() => {
    if (firstApply.current) {
      firstApply.current = false;
      return;
    }
    document.documentElement.classList.toggle("light", light);
  }, [light]);

  function toggle() {
    const next = !light;
    try {
      localStorage.setItem(STORAGE_KEY, next ? "light" : "dark");
    } catch {
      /* storage unavailable (private mode, etc.) — theme still applies for this session */
    }
    // Notify the store synchronously so the UI flips immediately.
    window.dispatchEvent(new StorageEvent("storage", { key: STORAGE_KEY }));
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={light ? "Switch to dark mode" : "Switch to light mode"}
      aria-pressed={light}
      title={light ? "Switch to dark mode" : "Switch to light mode"}
      className="ml-2 grid h-9 w-9 place-items-center rounded-lg border border-threat-border text-slate-400 transition hover:border-threat-accent/50 hover:text-threat-accent"
    >
      {light ? (
        /* Moon — currently in light mode, click to go dark */
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-[18px] w-[18px]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      ) : (
        /* Sun — currently in dark mode, click to go light */
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-[18px] w-[18px]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
        </svg>
      )}
    </button>
  );
}
