# charlie1552818.github.io

Personal research portfolio for control, robotics, autonomous systems, and a local-first research-paper reading desk.

## Public surfaces

- `index.html` — portfolio homepage
- `work/*.html` — long-form case studies
- `papers.html` — research-paper index and reading desk
- `activity-data.js` — machine-updated recent activity
- `papers-data.js` / `paper-summary.js` — machine-generated paper metadata
- `paper-index-excludes.txt` — narrow denylist for generated PDF artifacts that are not literature
- `robots.txt` / `sitemap.xml` / `404.html` — search/discovery and fallback surfaces

The site is static and is published with GitHub Pages from `main`.

## Safe maintenance workflow

1. Start from a clean `main` synchronized with `origin/main`.
2. Keep routine automation inside its documented update surfaces:
   - `AUTOMATION_ACTIVITY_CONTRACT.md`
   - `PAPER_LIBRARY_CONTRACT.md`
3. Run the repository health check:

   ```bash
   python tools/validate_site.py
   ```

4. Inspect the diff before committing.
5. Never commit credentials, private notes, absolute local paths, browser-local notes, or third-party PDF binaries.
6. Push only reviewed changes; GitHub Pages publishes the static site after the branch update.

## Repository validation

`tools/validate_site.py` provides a local pre-push health check for:

- required public files;
- local HTML links and asset references;
- same-page anchors;
- `target="_blank"` link protection;
- accidental public absolute Windows/file URLs;
- accidental tracked PDF binaries;
- Recent Activity IDs/count;
- paper-library and summary count consistency;
- SEO metadata, 404 behavior, sitemap/robots coverage, and excluded-artifact leakage.

The validator uses only the Python standard library.

## Paper library

The public repository stores metadata only. The deterministic index builder is:

```bash
python tools/build_paper_index.py --source <research-root> --output papers-data.js --summary-output paper-summary.js
```

The local source path is runtime-only and must never be written into public output.

Known generated reports/results are filtered through `paper-index-excludes.txt`; keep exclusions narrow and evidence-backed so real literature is not hidden. Browser-local research notes can be backed up/restored as JSON from Paper Desk.

## GitHub connectivity note

On the Windows maintenance host, GitHub HTTPS may require a local proxy. Keep proxy settings in the user's Git configuration rather than in this repository. If fetch/pull/clone fails while DNS still works, verify the active proxy endpoint and Git's GitHub-specific proxy configuration before recloning or modifying repository history.
