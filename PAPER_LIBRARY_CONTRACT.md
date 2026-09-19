# Paper Library Automation Contract

## Purpose

The public portfolio exposes a categorized research-paper index at `papers.html` and a local-first reading desk for notes.

The source collection is the user's local research workspace. The absolute source path must never be written into public site data.

## Public files

- `papers.html` — stable reading-desk UI
- `papers.css` — stable styling
- `papers.js` — stable filtering, local PDF reader and browser-local notes
- `paper-folder.js` — optional browser-local research-folder connector; never uploads file contents
- `papers-data.js` — machine-generated paper metadata; this is the routine automation update target
- `paper-summary.js` — small machine-generated homepage summary (total and category counts)
- `tools/build_paper_index.py` — deterministic index builder

## Routine automation priority

Paper-library maintenance is a first-class update target alongside Recent Activity.

At each scheduled intelligence/update run:

1. Scan the configured local research root for `*.pdf`.
2. Rebuild `papers-data.js` and `paper-summary.js` with `tools/build_paper_index.py --source <runtime-source> --output papers-data.js --summary-output paper-summary.js`.
3. Never copy third-party publisher PDFs into the public repository unless the user explicitly marks the file as their own or confirms redistribution rights.
4. Preserve stable paper IDs. IDs derive from the relative path, so browser-local notes survive ordinary index rebuilds.
5. If the index materially changes, add one concise verified item to `activity-data.js` describing the updated paper count/categories.
6. Do not publish absolute Windows paths, credentials, private notes or browser-local note content.
7. Routine paper-index commits should include `papers-data.js`, `paper-summary.js`, and, when warranted, `activity-data.js` only.
8. Before push, inspect the staged diff and ensure no PDF binaries or unrelated files are included.

## Notes model

Paper notes are stored only in the user's browser `localStorage` under stable paper IDs. They are not part of the public Git repository.

The Reading Desk can load a local PDF through the browser file picker and display it next to the note editor. On browsers with the File System Access API, the user can also connect the local research root once and let the desk match indexed papers by stable relative-path hash. The directory handle may be retained in browser IndexedDB; file contents and absolute paths are never published or uploaded.

The user can export any note as Markdown for later archival or deliberate Git publication.
