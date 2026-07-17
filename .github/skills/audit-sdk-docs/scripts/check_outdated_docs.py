#!/usr/bin/env python
"""Audit an Azure SDK repo for outdated documentation references.

Scans Markdown/reStructuredText docs (excluding the auto-generated ``sdk/`` tree
by default) and reports three classes of high-signal staleness for an agent to
judge and fix:

1. BROKEN_RELATIVE_LINK  - ``[text](relative/path.md)`` whose target is missing.
2. DEAD_REPO_URL         - ``https://github.com/<org>/<repo>/blob|tree/main/<path>``
                           pointing at a file/dir that no longer exists locally.
3. MISSING_PATH_REF      - an inline-code token like ``eng/foo.yml`` that looks
                           like a repo-relative path but does not exist.

The script only *reports*; it never edits. Many hits are legitimate placeholders
(e.g. ``sdk/path-to-your-package/_version.py``) or code snippets, so the agent
must read each candidate in context before deciding to update or delete.

Usage:
    python check_outdated_docs.py [REPO_ROOT] [--scan-dir DIR ...] [--include-sdk]

Defaults:
    REPO_ROOT   the repo this script lives in (../../../.. from the script)
    scan dirs   repo-root-level *.md/*.rst files + doc/ + eng/  (recursive)
"""
import argparse
import os
import re
import sys

# repo root = <root>/.github/skills/audit-sdk-docs/scripts/check_outdated_docs.py
DEFAULT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
)

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
INLINE = re.compile(r"`([^`\n]+)`")
PATH_PREFIXES = ("sdk/", "eng/", "scripts/", "doc/", "common/", "tools/", "conda/")
# repo url matcher is built at runtime from --org/--repo

DOC_EXT = (".md", ".rst")


def collect_docs(root, scan_dirs, include_sdk):
    targets = []
    # top-level doc files
    for f in os.listdir(root):
        full = os.path.join(root, f)
        if os.path.isfile(full) and f.lower().endswith(DOC_EXT):
            targets.append(full)
    for d in scan_dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dp, dn, fns in os.walk(base):
            low = dp.lower()
            if (os.sep + "node_modules") in low:
                continue
            # eng/common* is centrally synced from azure-sdk-tools; do not hand-edit
            if (os.sep + "eng" + os.sep + "common") in low:
                continue
            if not include_sdk and (os.sep + "sdk" + os.sep) in (low + os.sep):
                continue
            for fn in fns:
                if fn.lower().endswith(DOC_EXT):
                    targets.append(os.path.join(dp, fn))
    # de-dup preserving order
    seen, out = set(), []
    for t in targets:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def check_broken_links(doc, text, root):
    base = os.path.dirname(doc)
    hits = []
    for m in MD_LINK.finditer(text):
        link = m.group(1).strip().split(" ")[0].strip("<>")
        if not link or link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path_part = link.split("#")[0]
        if not path_part:
            continue
        # skip obvious code-snippet noise (parens, quotes, commas, equals)
        if any(c in path_part for c in "\"'=,"):
            continue
        tgt = os.path.normpath(os.path.join(base, path_part))
        if not os.path.exists(tgt):
            hits.append(("BROKEN_RELATIVE_LINK", link, os.path.relpath(tgt, root)))
    return hits


def check_repo_urls(doc, text, root, url_re):
    hits = []
    for m in url_re.finditer(text):
        rel = m.group(1).rstrip("/")
        local = os.path.normpath(os.path.join(root, rel))
        if not os.path.exists(local):
            hits.append(("DEAD_REPO_URL", rel, rel))
    return hits


def check_path_refs(doc, text, root):
    hits = []
    for m in INLINE.finditer(text):
        tok = m.group(1).strip()
        if " " in tok or not any(tok.lower().startswith(p) for p in PATH_PREFIXES):
            continue
        if any(c in tok for c in "*?<>|{}\"'"):
            continue
        cand = tok.split("#")[0].split(":")[0]
        if not os.path.exists(os.path.normpath(os.path.join(root, cand))):
            hits.append(("MISSING_PATH_REF", tok, cand))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=DEFAULT_ROOT)
    ap.add_argument("--scan-dir", action="append", default=None,
                    help="Directory (relative to root) to scan recursively. Repeatable.")
    ap.add_argument("--include-sdk", action="store_true",
                    help="Also scan the auto-generated sdk/ tree (off by default).")
    ap.add_argument("--org", default="Azure")
    ap.add_argument("--repo", default="azure-sdk-for-python")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: repo root not found: {root}", file=sys.stderr)
        return 2
    scan_dirs = args.scan_dir if args.scan_dir else ["doc", "eng"]
    url_re = re.compile(
        r"https://github\.com/" + re.escape(args.org) + "/" + re.escape(args.repo)
        + r"/(?:blob|tree)/main/([^)\s\"'>#]+)")

    docs = collect_docs(root, scan_dirs, args.include_sdk)
    all_hits = []
    for doc in docs:
        with open(doc, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        rel_doc = os.path.relpath(doc, root)
        for kind, shown, tgt in (
            check_broken_links(doc, text, root)
            + check_repo_urls(doc, text, root, url_re)
            + check_path_refs(doc, text, root)
        ):
            all_hits.append((kind, rel_doc, shown, tgt))

    if not all_hits:
        print("No outdated doc references found.")
    else:
        for kind in ("BROKEN_RELATIVE_LINK", "DEAD_REPO_URL", "MISSING_PATH_REF"):
            group = [h for h in all_hits if h[0] == kind]
            if not group:
                continue
            print(f"\n=== {kind} ({len(group)}) ===")
            for _, doc, shown, tgt in group:
                print(f"{doc}\n    ref: {shown}\n    missing: {tgt}")
    print(f"\nScanned {len(docs)} doc files. Total candidates: {len(all_hits)}")
    print("NOTE: candidates are NOT auto-fixed. Read each in context; many are "
          "intentional placeholders or code snippets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
