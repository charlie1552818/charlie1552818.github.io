from __future__ import annotations

import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "index.html",
    "papers.html",
    "activity-data.js",
    "papers-data.js",
    "paper-summary.js",
    "AUTOMATION_ACTIVITY_CONTRACT.md",
    "PAPER_LIBRARY_CONTRACT.md",
}
PUBLIC_TEXT_SUFFIXES = {".html", ".css", ".js"}
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, str | None]] = []
        self.ids: set[str] = set()
        self.blank_links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        element_id = data.get("id")
        if element_id:
            self.ids.add(element_id)

        for attr in ("href", "src"):
            value = data.get(attr)
            if value:
                self.refs.append((tag, attr, value))

        if tag == "a" and data.get("target") == "_blank":
            self.blank_links.append((data.get("href") or "", data.get("rel") or ""))


def tracked_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / item.decode("utf-8") for item in proc.stdout.split(b"\0") if item]


def load_assigned_json(path: Path, variable: str) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    prefix = f"window.{variable} = "
    if not text.startswith(prefix) or not text.endswith(";"):
        raise ValueError(f"{path.name}: expected assignment to window.{variable}")
    payload = text[len(prefix) : -1]
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected an object payload")
    return value


def resolve_local_reference(document: Path, raw: str) -> tuple[Path | None, str | None]:
    value = raw.strip()
    if not value or value.startswith("//"):
        return None, None

    parts = urlsplit(value)
    if parts.scheme.lower() in SKIP_SCHEMES or parts.netloc:
        return None, None

    fragment = unquote(parts.fragment) if parts.fragment else None
    if not parts.path:
        return document, fragment

    path_text = unquote(parts.path)
    if path_text.startswith("/"):
        candidate = ROOT / path_text.lstrip("/")
    else:
        candidate = document.parent / path_text

    return candidate.resolve(), fragment


def main() -> int:
    errors: list[str] = []

    for name in sorted(REQUIRED):
        if not (ROOT / name).is_file():
            errors.append(f"missing required file: {name}")

    try:
        tracked = tracked_files()
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"unable to read tracked files: {exc}")
        tracked = []

    for path in tracked:
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if path.suffix.lower() == ".pdf":
            errors.append(f"PDF is not allowed in this public repo: {rel.as_posix()}")

    parsed: dict[Path, DocumentParser] = {}
    for document in sorted(ROOT.rglob("*.html")):
        if ".git" in document.parts:
            continue
        parser = DocumentParser()
        try:
            parser.feed(document.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            errors.append(f"{document.relative_to(ROOT)}: unable to parse: {exc}")
            continue
        parsed[document.resolve()] = parser

        for href, rel in parser.blank_links:
            rel_tokens = {token.lower() for token in rel.split()}
            if not ({"noopener", "noreferrer"} & rel_tokens):
                errors.append(
                    f"{document.relative_to(ROOT)}: target=_blank link lacks noopener/noreferrer: {href}"
                )

    for document, parser in parsed.items():
        for _tag, _attr, raw in parser.refs:
            try:
                candidate, fragment = resolve_local_reference(document, raw)
            except ValueError:
                errors.append(f"{document.relative_to(ROOT)}: invalid local URL: {raw}")
                continue
            if candidate is None:
                continue

            try:
                candidate.relative_to(ROOT)
            except ValueError:
                errors.append(f"{document.relative_to(ROOT)}: local reference escapes repository: {raw}")
                continue

            if not candidate.exists():
                errors.append(f"{document.relative_to(ROOT)}: missing local target: {raw}")
                continue

            if fragment and candidate.suffix.lower() == ".html":
                target_parser = parsed.get(candidate.resolve())
                if target_parser is None:
                    errors.append(f"{document.relative_to(ROOT)}: cannot inspect anchor target: {raw}")
                elif fragment not in target_parser.ids:
                    errors.append(f"{document.relative_to(ROOT)}: missing anchor #{fragment} in {candidate.relative_to(ROOT)}")

    leaked_path = re.compile(r"(?i)(?:[a-z]:\\users\\|file:///)")
    for path in tracked:
        if path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if leaked_path.search(text):
            errors.append(f"{path.relative_to(ROOT)}: contains an absolute local/file URL pattern")

    activity_path = ROOT / "activity-data.js"
    if activity_path.is_file():
        activity_text = activity_path.read_text(encoding="utf-8")
        activity_ids = re.findall(r'\bid:\s*["\']([^"\']+)["\']', activity_text)
        if not 3 <= len(activity_ids) <= 6:
            errors.append(f"activity-data.js: expected 3-6 activity items, found {len(activity_ids)}")
        if len(activity_ids) != len(set(activity_ids)):
            errors.append("activity-data.js: duplicate activity id detected")

    try:
        library = load_assigned_json(ROOT / "papers-data.js", "PAPER_LIBRARY")
        summary = load_assigned_json(ROOT / "paper-summary.js", "PAPER_LIBRARY_SUMMARY")
        items = library.get("items")
        total = library.get("total")
        summary_total = summary.get("total")
        if not isinstance(items, list):
            errors.append("papers-data.js: items must be an array")
        else:
            if total != len(items):
                errors.append(f"papers-data.js: total={total!r} but items={len(items)}")
        if summary_total != total:
            errors.append(f"paper-summary.js: total={summary_total!r} does not match library total={total!r}")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"paper metadata validation failed: {exc}")

    if errors:
        print(f"Site validation FAILED with {len(errors)} issue(s):", file=sys.stderr)
        for issue in errors:
            print(f" - {issue}", file=sys.stderr)
        return 1

    print("Site validation passed.")
    print(f"Checked {len(parsed)} HTML document(s) and {len(tracked)} repository file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
