# Automated Recent Activity Feed

This repository exposes one machine-updated surface for the recurring portfolio automation.

## Public surface

- Section anchor: `#activity`
- UI title: **Recent Activity**
- Position: after **Evidence**, before **Systems**
- Data source: `activity-data.js`
- Renderer: stable site JavaScript; automation should not modify `index.html`, `style.css`, `script.js`, or `activity.css` during a routine feed update.

## Update contract

The recurring automation should replace only the array assigned to:

```js
window.RECENT_ACTIVITY = [...]
```

Each item uses:

```js
{
  id: "stable-unique-id",
  date: "YYYY-MM-DD",
  category: "SHORT CATEGORY",
  title: "Concise completed outcome",
  summary: "One short factual description of the completed work and concrete output.",
  href: "https://public-link.example", // optional; public links only
  status: "COMPLETED"
}
```

Rules:

1. Publish only work that is already completed and supported by concrete evidence such as a Git commit, deployed page, generated PDF, experiment result, validated plot, competition result, or finished code artifact.
2. Never publish plans, intentions, speculative achievements, unverified claims, secrets, credentials, private local paths, personal contact details, or sensitive information.
3. Keep the newest 3–6 items when enough verified items exist.
4. Sort newest first.
5. Deduplicate by `id`. Reuse the same `id` when an existing activity is updated rather than creating a near-duplicate.
6. Keep titles concise and summaries readable on a portfolio card.
7. `href` is optional and must point only to a public, safe destination. Omit it when no suitable public evidence exists.
8. A routine **activity-feed-only** update should contain only `activity-data.js` unless a deliberate schema/UI migration is being performed.
9. The scheduled workflow also treats the paper library as a first-class update target. Paper-index updates are governed by `PAPER_LIBRARY_CONTRACT.md` and may additionally stage `papers-data.js`.
10. Before pushing, inspect the staged diff and verify no unrelated file, private note, absolute local path, or third-party PDF binary is included.
11. Push to `main`; GitHub Pages will publish the updated static site from the configured source branch.

## Current cadence

The scheduler currently runs the broader intelligence/update workflow every 12 hours, around **09:00 and 21:00 Asia/Shanghai**. Scheduling is owned by the automation system, not by this repository.

## Paper library priority

The same 09:00 / 21:00 workflow should scan the configured local research-paper source and rebuild the categorized metadata index when files change. See `PAPER_LIBRARY_CONTRACT.md` for the stable updater contract. A material library update may also produce one concise Recent Activity item linking to `papers.html`.

## Local intelligence archive

The separate intelligence brief remains in the user's local scheduled-report workspace. This public feed is only the sanitized, concise portfolio-facing projection of verified completed work.
