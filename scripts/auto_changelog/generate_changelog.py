#!/usr/bin/env python
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Auto-generate changelog entries for Azure SDK Python packages.

Combines three sources of changelog information:
  1. Chronus change files (.chronus/changes/*.md)
  2. Git commit history (PR numbers, diffs)
  3. AI-powered generation/polishing (Azure OpenAI or OpenAI)

Usage:
  # Basic: show changelog from Chronus change files
  python scripts/auto_changelog/generate_changelog.py --package-path sdk/storage/azure-storage-blob

  # AI-generate from git diffs (no Chronus files needed)
  python scripts/auto_changelog/generate_changelog.py --package-path sdk/storage/azure-storage-blob --ai-generate

  # AI-polish existing Chronus entries
  python scripts/auto_changelog/generate_changelog.py --package-path sdk/storage/azure-storage-blob --ai-polish

  # Write to CHANGELOG.md
  python scripts/auto_changelog/generate_changelog.py --package-path sdk/storage/azure-storage-blob --write

  # Full pipeline: AI-generate + breaking changes detection + write
  python scripts/auto_changelog/generate_changelog.py --package-path sdk/storage/azure-storage-blob \\
      --ai-generate --detect-breaking --write --clean

AI setup (for --ai-generate / --ai-polish):
  Azure OpenAI: set AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY  (optionally AZURE_OPENAI_DEPLOYMENT)
  OpenAI:       set OPENAI_API_KEY  (optionally OPENAI_MODEL)
  Requires:     pip install openai
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

logging.basicConfig(stream=sys.stderr, format="[%(levelname)s] %(message)s")
_LOGGER = logging.getLogger("auto_changelog")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GITHUB_PR_URL = "https://github.com/Azure/azure-sdk-for-python/pull"
SECTION_ORDER = ["Features Added", "Breaking Changes", "Bugs Fixed", "Other Changes"]
VERSION_RE = re.compile(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]')

CHANGE_KIND_MAP: Dict[str, tuple] = {
    # changeKind -> (changelog section, semver bump)
    "breaking":     ("Breaking Changes", "major"),
    "feature":      ("Features Added",   "minor"),
    "fix":          ("Bugs Fixed",       "patch"),
    "deprecation":  ("Other Changes",    "minor"),
    "dependencies": ("Other Changes",    "patch"),
    "internal":     ("Other Changes",    "none"),
}

# ---------------------------------------------------------------------------
# AI prompts
# ---------------------------------------------------------------------------

_AI_SYSTEM = """\
You are an expert changelog writer for the Azure SDK for Python. You write clear,
concise changelog entries following Azure SDK conventions.

RULES:
- Each entry is a single bullet point starting with "- "
- Use backticks around class names, method names, parameter names, and module paths
- Be specific: mention the exact API names, parameters, or behaviors changed
- Write from the user's perspective (what they can now do, what changed for them)
- Use past tense for fixes ("Fixed an issue where...") and additions ("Added support for...")
- Do NOT include PR numbers or commit hashes (those are added separately)
- Do NOT include version numbers
- Keep entries to 1-3 lines max

SECTION DEFINITIONS:
- "Features Added": New functionality, new APIs, new parameters, new supported scenarios
- "Breaking Changes": Removed/renamed APIs, changed signatures, behavioral changes that break existing code
- "Bugs Fixed": Bug fixes, error handling improvements, correctness fixes
- "Other Changes": Dependency bumps, internal refactors, documentation, deprecations

OUTPUT FORMAT — JSON object, section names as keys, arrays of entry strings as values.
Only include sections that have entries. Example:
{
  "Features Added": ["Added support for `new_param` in `BlobClient.upload_blob`"],
  "Bugs Fixed": ["Fixed `TypeError` in `ContainerClient.list_blobs` with pagination"]
}
"""

_POLISH_TMPL = """\
Improve the following changelog entries for the Azure SDK Python package "{package_name}".
Keep the same meaning but make them clearer, more specific, and
following Azure SDK conventions.

Current entries by section:
{entries_json}

Return improved entries in the same JSON format. Keep the same sections.
If an entry is already well-written, keep it as-is.
"""

_GEN_COMMITS_TMPL = """\
Generate changelog entries for the Azure SDK Python package "{package_name}"
based on these git commits and diffs.

Commits (most recent first):
{commits_text}

Code diffs (summarized):
{diffs_text}

Categorize each change into the correct section.
Ignore test-only, CI config, and internal tooling changes unless they affect the public API.
Return a JSON object with section names as keys and arrays of entry strings as values.
"""

_GEN_DIFF_TMPL = """\
Generate changelog entries for the Azure SDK Python package "{package_name}"
based on this code diff against the main branch.

Code diff:
{diff_text}

Focus on public API surfaces (classes, methods, parameters in non-underscore modules).
Ignore test, CI, generated code, and internal tooling changes.
Return a JSON object with section names as keys and arrays of entry strings as values.
"""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ChronusChange:
    change_kind: str
    packages: List[str]
    description: str
    section: str
    file_path: str
    bump_type: str


@dataclass
class CommitInfo:
    commit_hash: str
    author: str
    pr_number: Optional[int]
    commit_message: str


# ---------------------------------------------------------------------------
# Chronus parsing
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> tuple:
    parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        raise ValueError("Missing --- frontmatter delimiters")
    raw, body = parts[1].strip(), parts[2].strip()
    if yaml is not None:
        fm = yaml.safe_load(raw)
    else:
        fm: dict = {}
        m = re.search(r"changeKind:\s*(\w+)", raw)
        if m:
            fm["changeKind"] = m.group(1)
        pkgs = re.findall(r"^\s*-\s*(.+)$", raw, re.MULTILINE)
        fm["packages"] = [p.strip() for p in pkgs if "changeKind" not in p]
    return fm, body


def _parse_change_file(path: str) -> Optional[ChronusChange]:
    try:
        with open(path, encoding="utf-8") as f:
            fm, body = _parse_frontmatter(f.read())
        kind = fm.get("changeKind", "")
        pkgs = fm.get("packages", [])
        if not kind or kind not in CHANGE_KIND_MAP or not pkgs:
            return None
        section, bump = CHANGE_KIND_MAP[kind]
        return ChronusChange(kind, pkgs, body, section, str(path), bump)
    except Exception as exc:
        _LOGGER.error("Failed to parse %s: %s", path, exc)
        return None


def _find_changes(repo_root: str, package_path: str) -> List[ChronusChange]:
    d = os.path.join(repo_root, ".chronus", "changes")
    if not os.path.isdir(d):
        return []
    norm = package_path.replace("\\", "/").strip("/")
    out: List[ChronusChange] = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        c = _parse_change_file(os.path.join(d, fn))
        if c and any(p.replace("\\", "/").strip("/") == norm for p in c.packages):
            out.append(c)
    _LOGGER.info("Found %d Chronus change(s) for %s", len(out), package_path)
    return out


# ---------------------------------------------------------------------------
# Git utilities
# ---------------------------------------------------------------------------

def _git(args: List[str], cwd: str) -> str:
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _pr_number(msg: str) -> Optional[int]:
    m = re.search(r"\(#(\d+)\)", msg)
    return int(m.group(1)) if m else None


def _commit_for_file(path: str, repo_root: str) -> Optional[CommitInfo]:
    if os.path.isabs(path):
        try:
            path = os.path.relpath(path, repo_root)
        except ValueError:
            pass
    out = _git(["log", "--diff-filter=A", "--format=%H|%an|%s", "--follow", "--", path], repo_root)
    if not out:
        return None
    parts = out.split("\n")[0].split("|", 2)
    if len(parts) < 3:
        return None
    h, a, m = parts
    return CommitInfo(h.strip(), a.strip(), _pr_number(m), m.strip())


def _recent_commits(pkg: str, repo: str, since: Optional[str], branch: str) -> List[CommitInfo]:
    if since:
        args = ["log", f"--since={since}", "--format=%H|%an|%s", "--", pkg]
    else:
        args = ["log", f"{branch}..HEAD", "--format=%H|%an|%s", "--", pkg]
    out = _git(args, repo)
    if not out:
        return []
    commits = []
    for line in out.split("\n"):
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        h, a, m = parts
        commits.append(CommitInfo(h.strip(), a.strip(), _pr_number(m), m.strip()))
    return commits


def _diff_for_commit(h: str, pkg: str, repo: str) -> str:
    return _git(["diff", f"{h}~1..{h}", "--", pkg], repo)


def _diff_against_branch(pkg: str, repo: str, branch: str) -> str:
    return _git(["diff", branch, "--", pkg], repo)


def _pr_link(n: int) -> str:
    return f"([#{n}]({GITHUB_PR_URL}/{n}))"


def _enrich(desc: str, pr: Optional[int]) -> str:
    if pr is None or f"#{pr}" in desc:
        return desc
    return f"{desc} {_pr_link(pr)}"


# ---------------------------------------------------------------------------
# AI generation
# ---------------------------------------------------------------------------

def _get_ai_client():
    try:
        import openai
    except ImportError:
        raise ImportError("Install the openai package: pip install openai")

    ep = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_API_KEY")
    if ep and key:
        dep = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        ver = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        return openai.AzureOpenAI(azure_endpoint=ep, api_key=key, api_version=ver), dep

    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return openai.OpenAI(api_key=key), os.environ.get("OPENAI_MODEL", "gpt-4o")

    raise EnvironmentError(
        "Set AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY, or OPENAI_API_KEY"
    )


def _call_ai(prompt: str, max_tokens: int = 2000) -> Dict[str, List[str]]:
    client, model = _get_ai_client()
    _LOGGER.info("Calling AI model...")
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _AI_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    body = resp.choices[0].message.content or ""
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        _LOGGER.error("AI returned invalid JSON")
        return {}

    valid = {"Features Added", "Breaking Changes", "Bugs Fixed", "Other Changes"}
    result: Dict[str, List[str]] = {}
    for sec, entries in data.items():
        sec = sec if sec in valid else "Other Changes"
        if isinstance(entries, list):
            clean = [e.strip().removeprefix("- ") for e in entries if isinstance(e, str)]
            result.setdefault(sec, []).extend(clean)
    return result


def _truncate_diff(diff: str, max_lines: int = 500) -> str:
    lines = diff.split("\n")
    if len(lines) <= max_lines:
        return diff
    kept, skip = [], 0
    for line in lines:
        if line.startswith(("diff --git", "---", "+++")) or line.startswith(("+", "-")):
            if skip:
                kept.append(f"  ... ({skip} lines skipped)")
                skip = 0
            kept.append(line)
        else:
            skip += 1
        if len(kept) >= max_lines:
            kept.append(f"\n... ({len(lines) - len(kept)} more lines)")
            break
    return "\n".join(kept)


def _ai_generate(repo: str, pkg: str, name: str, branch: str, since: Optional[str]) -> Dict[str, List[str]]:
    commits = _recent_commits(pkg, repo, since, branch)
    if commits:
        _LOGGER.info("Found %d commits for AI analysis", len(commits))
        diffs = {}
        for c in commits[:15]:
            d = _diff_for_commit(c.commit_hash, pkg, repo)
            if d:
                diffs[c.commit_hash] = d
        ct = "\n".join(
            f"- [{c.commit_hash[:8]}] {c.commit_message}"
            + (f" (PR #{c.pr_number})" if c.pr_number else "")
            + f" by {c.author}"
            for c in commits[:15]
        )
        dt = "\n\n".join(f"=== {h[:8]} ===\n{_truncate_diff(d)}" for h, d in diffs.items() if d.strip())
        return _call_ai(
            _GEN_COMMITS_TMPL.format(package_name=name, commits_text=ct, diffs_text=dt),
            max_tokens=3000,
        )

    diff = _diff_against_branch(pkg, repo, branch)
    if not diff:
        _LOGGER.warning("No diff found")
        return {}
    if len(diff) > 50_000:
        diff = diff[:50_000] + "\n\n... [truncated] ..."
    return _call_ai(_GEN_DIFF_TMPL.format(package_name=name, diff_text=diff), max_tokens=3000)


def _ai_polish(name: str, sections: Dict[str, List[str]]) -> Dict[str, List[str]]:
    if not sections:
        return sections
    r = _call_ai(_POLISH_TMPL.format(
        package_name=name, entries_json=json.dumps(sections, indent=2),
    ))
    return r or sections


# ---------------------------------------------------------------------------
# Version calculation
# ---------------------------------------------------------------------------

def _read_version(pkg: str, repo: str) -> Optional[str]:
    for root, dirs, files in os.walk(os.path.join(repo, pkg)):
        dirs[:] = [d for d in dirs if d not in ("tests", "samples", "__pycache__", ".tox")]
        if "_version.py" in files:
            with open(os.path.join(root, "_version.py"), encoding="utf-8") as f:
                for line in f:
                    m = VERSION_RE.match(line.strip())
                    if m:
                        return m.group(1)
    return None


def _next_version(cur: str, sections: Dict[str, List[str]], stable: bool) -> str:
    if not cur:
        return "1.0.0b1"
    preview = "b" in cur or "rc" in cur
    label = "b"

    def _bump(v: str) -> str:
        has_brk = "Breaking Changes" in sections
        has_fix = "Bugs Fixed" in sections
        n = v.split(".")
        if has_brk:
            return f"{int(n[0])+1}.0.0"
        if has_fix:
            return f"{n[0]}.{n[1]}.{int(n[2])+1}"
        return f"{n[0]}.{int(n[1])+1}.0"

    if preview and not stable:
        parts = cur.split(label)
        return f"{parts[0]}{label}{int(parts[1])+1}"
    if preview and stable:
        return cur.split(label)[0]
    if not preview and not stable:
        return _bump(cur) + label + "1"
    return _bump(cur)


# ---------------------------------------------------------------------------
# Changelog formatting / writing
# ---------------------------------------------------------------------------

def _format_entry(version: str, sections: Dict[str, List[str]], date: Optional[str]) -> str:
    status = date or "Unreleased"
    lines = [f"## {version} ({status})", ""]
    for sec in SECTION_ORDER:
        entries = sections.get(sec)
        if entries:
            lines.append(f"### {sec}")
            for e in entries:
                e = e.strip()
                lines.append(e if e.startswith("- ") else f"- {e}")
            lines.append("")
    return "\n".join(lines)


def _write_changelog(pkg: str, repo: str, entry: str) -> str:
    path = os.path.join(repo, pkg, "CHANGELOG.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"CHANGELOG.md not found at {path}")
    with open(path, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    hdr = next((i for i, l in enumerate(lines) if l.strip() == "# Release History"), -1)
    if hdr == -1:
        updated = f"# Release History\n\n{entry}\n{content}"
    else:
        first_ver = next((i for i in range(hdr + 1, len(lines)) if lines[i].strip().startswith("## ")), -1)
        if first_ver == -1:
            updated = f"# Release History\n\n{entry}\n"
        elif "(Unreleased)" in lines[first_ver]:
            end = next((i for i in range(first_ver + 1, len(lines)) if lines[i].strip().startswith("## ")), len(lines))
            updated = "\n".join(lines[:first_ver]) + "\n" + entry + "\n" + "\n".join(lines[end:])
        else:
            updated = "\n".join(lines[:first_ver]) + "\n" + entry + "\n" + "\n".join(lines[first_ver:])

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    _LOGGER.info("Updated %s", path)
    return path


def _merge(*dicts: Dict[str, List[str]]) -> Dict[str, List[str]]:
    merged: Dict[str, List[str]] = {}
    for d in dicts:
        for sec, entries in d.items():
            merged.setdefault(sec, []).extend(entries)
    # Deduplicate by substring match
    for sec in merged:
        seen, uniq = [], []
        for e in merged[sec]:
            lo = e.lower().strip()
            if not any(lo in s or s in lo for s in seen):
                seen.append(lo)
                uniq.append(e)
        merged[sec] = uniq
    return merged


# ---------------------------------------------------------------------------
# Breaking changes checker integration
# ---------------------------------------------------------------------------

def _detect_breaking(repo: str, pkg: str) -> Dict[str, List[str]]:
    script = os.path.join(repo, "scripts", "breaking_changes_checker", "detect_breaking_changes.py")
    if not os.path.isfile(script):
        return {}
    _LOGGER.info("Running breaking changes checker...")
    try:
        r = subprocess.run(
            [sys.executable, script, "-t", os.path.join(repo, pkg), "-c"],
            capture_output=True, text=True, timeout=300, cwd=repo,
        )
        out = r.stdout
        s, e = out.find("===== changelog start ====="), out.find("===== changelog end =====")
        if s == -1 or e == -1:
            return {}
        text = out[s + len("===== changelog start ====="):e].strip()
        sections: Dict[str, List[str]] = {}
        cur = None
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("### "):
                cur = line[4:].strip()
            elif line.startswith("- ") and cur:
                sections.setdefault(cur, []).append(line[2:].strip())
        return sections
    except Exception as exc:
        _LOGGER.warning("Breaking changes checker failed: %s", exc)
        return {}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _detect_repo_root() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    cur = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise RuntimeError("Could not detect repo root. Use --repo-root.")


def main():
    ap = argparse.ArgumentParser(
        description="Auto-generate changelog entries for Azure SDK Python packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--package-path", required=True, help="e.g. sdk/storage/azure-storage-blob")
    ap.add_argument("--repo-root", default=None, help="Repo root (auto-detected)")
    ap.add_argument("--write", action="store_true", help="Update CHANGELOG.md in-place")
    ap.add_argument("--clean", action="store_true", help="Delete consumed Chronus change files")
    ap.add_argument("--detect-breaking", action="store_true", help="Run breaking changes checker")
    ap.add_argument("--ai-generate", action="store_true", help="AI-generate entries from git diffs")
    ap.add_argument("--ai-polish", action="store_true", help="AI-polish existing entries")
    ap.add_argument("--version", default=None, help="Explicit version (auto-calculated)")
    ap.add_argument("--release-date", default=None, help="YYYY-MM-DD (default: Unreleased)")
    ap.add_argument("--stable", action="store_true", help="Tag as stable release")
    ap.add_argument("--base-branch", default="main", help="Base branch (default: main)")
    ap.add_argument("--since", default=None, help="Git date for commit lookback")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    repo = os.path.abspath(args.repo_root or _detect_repo_root())
    pkg = args.package_path.replace("\\", "/").strip("/")
    name = os.path.basename(pkg)

    _LOGGER.info("Package: %s (%s)", name, pkg)

    # --- Collect from all sources ---
    all_dicts: list = []

    # 1) Chronus change files
    changes = _find_changes(repo, pkg)
    if changes:
        secs: Dict[str, List[str]] = {}
        for ch in changes:
            ci = _commit_for_file(ch.file_path, repo)
            desc = _enrich(ch.description, ci.pr_number if ci else None)
            secs.setdefault(ch.section, []).append(desc)
        _LOGGER.info("Chronus: %d entries", sum(len(v) for v in secs.values()))
        all_dicts.append(secs)

    # 2) Breaking changes checker
    if args.detect_breaking:
        bs = _detect_breaking(repo, pkg)
        if bs:
            _LOGGER.info("Detected: %d entries", sum(len(v) for v in bs.values()))
            all_dicts.append(bs)

    # 3) AI generation
    if args.ai_generate:
        ai = _ai_generate(repo, pkg, name, args.base_branch, args.since)
        if ai:
            _LOGGER.info("AI-generated: %d entries", sum(len(v) for v in ai.values()))
            all_dicts.append(ai)

    if not all_dicts:
        print("No changelog entries found from any source.\n", file=sys.stderr)
        print("Tips:", file=sys.stderr)
        print("  - Add Chronus change files: npx chronus add <package-path>", file=sys.stderr)
        print("  - Use --ai-generate to create entries from git diffs", file=sys.stderr)
        print("  - Use --detect-breaking to auto-detect API changes", file=sys.stderr)
        sys.exit(1)

    sections = _merge(*all_dicts)

    # --- AI polish ---
    if args.ai_polish:
        _LOGGER.info("Polishing entries with AI...")
        sections = _ai_polish(name, sections)

    # --- Validate ---
    if not set(sections) & {"Features Added", "Breaking Changes", "Bugs Fixed", "Other Changes"}:
        print("ERROR: No valid changelog sections.", file=sys.stderr)
        sys.exit(1)

    # --- Version ---
    if args.version:
        version = args.version
    else:
        cur_ver = _read_version(pkg, repo)
        if cur_ver:
            version = _next_version(cur_ver, sections, args.stable)
            _LOGGER.info("Version: %s -> %s", cur_ver, version)
        else:
            version = "0.0.0"

    # --- Format ---
    entry = _format_entry(version, sections, args.release_date)

    # --- Output ---
    if args.write:
        path = _write_changelog(pkg, repo, entry)
        print(f"Updated {path}", file=sys.stderr)
        if args.clean:
            n = 0
            for ch in _find_changes(repo, pkg):
                try:
                    os.remove(ch.file_path)
                    n += 1
                except OSError:
                    pass
            if n:
                print(f"Deleted {n} Chronus change file(s)", file=sys.stderr)
    else:
        print(entry)
        if args.clean:
            print("WARNING: --clean ignored without --write", file=sys.stderr)

    total = sum(len(v) for v in sections.values())
    summary = ", ".join(f"{k}: {len(v)}" for k, v in sections.items())
    print(f"\nChangelog: {version} — {total} entries ({summary})", file=sys.stderr)


if __name__ == "__main__":
    main()
