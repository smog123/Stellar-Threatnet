# feat(frontend): copy-to-clipboard on lookup results

## Summary

Add a copy button to the lookup result cards (wallet, domain, token) on the
dashboard so users can copy the result summary or JSON to the clipboard, with
visible feedback.

## Why it matters

Security researchers and support staff copy lookup results into reports and
tickets constantly. A one-click copy with feedback is a small interaction that
saves real time.

## Acceptance Criteria

- [ ] Each lookup result card has a copy button
- [ ] Clicking copies the result (JSON or formatted summary) to the clipboard
- [ ] A brief "copied" confirmation is shown on success, and an error state on failure
- [ ] Button is keyboard accessible and has an `aria-label`
- [ ] Works in both light and dark modes

## Tech Stack

Next.js 14 · TypeScript · Tailwind CSS · `navigator.clipboard`
