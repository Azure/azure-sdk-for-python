#!/usr/bin/env python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Warm the Azure SDK Central Feed Services (CFS) feed with every third-party
dependency declared anywhere in this repository.

Background
----------
This repository installs all packages from the CFS feed
(``https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/``)
instead of directly from PyPI. CFS is an *upstream pull-through* cache: an
**authenticated** request for a package version that CFS has not seen yet causes
CFS to fetch (and permanently cache) it from PyPI. **Unauthenticated** pipelines
(for example CI runs for pull requests from forks) can only read versions that
CFS has *already* cached -- they cannot trigger a pull-through.

That asymmetry is the failure mode this script exists to prevent. A tool such as
``mypy`` has transitive dependencies that are not strictly pinned. When one of
those transitive dependencies publishes a new release, an unauthenticated CI job
that resolves ``mypy`` to that brand-new (uncached) transitive version fails,
because CFS does not have it and the job cannot authenticate to pull it through.

Running this script on a daily authenticated schedule keeps CFS warm: for every
dependency declared in the repo we run ``pip download`` (which resolves and
downloads the **full transitive closure**) against the CFS feed. Because we do
*not* pass ``--no-deps``, the current-latest transitive versions get pulled
through and cached, so the next unauthenticated CI run finds them already present.

What counts as a "declared dependency"
--------------------------------------
The script aggregates requirement specifiers from:

* every ``dev_requirements.txt`` in the repo,
* every package's ``pyproject.toml`` (``[project].dependencies`` and
  ``[project.optional-dependencies]``),
* the shared/engineering requirement files
  (``shared_requirements.txt``, ``eng/ci_tools.txt``, ``eng/test_tools.txt``,
  ``eng/dependency_tools.txt``, ``eng/release_requirements.txt``),
* the ``azpysdk`` static-analysis tool pins in ``eng/tool_requirements/*.txt``
  (mypy, pylint, pyright, sphinx, black, bandit, ... -- this is precisely the set
  that used to be invisible because it was hardcoded in Python).

First-party / local entries (editable installs, relative paths, and the
first-party ``azure-*`` packages that live in this repo) are skipped: they are
built and published by our own pipelines and are not pulled from PyPI upstream.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Set, Tuple

from packaging.requirements import InvalidRequirement, Requirement

from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup
from ci_tools.parsing.parse_functions import get_pyproject_dict
from ci_tools.variables import discover_repo_root

CFS_INDEX_URL = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"

# Requirement files at well-known locations that are not attached to a single package.
SHARED_REQUIREMENT_FILES = [
    "shared_requirements.txt",
    os.path.join("eng", "ci_tools.txt"),
    os.path.join("eng", "test_tools.txt"),
    os.path.join("eng", "dependency_tools.txt"),
    os.path.join("eng", "release_requirements.txt"),
]

# Directory names that never contain declared dependencies we care about.
_PRUNE_DIRS = {
    ".git",
    ".venv",
    ".tox",
    "node_modules",
    "build",
    "dist",
    ".eggs",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}


class RequirementSource:
    """A single requirement specifier and where it came from (for reporting)."""

    __slots__ = ("spec", "name", "origin")

    def __init__(self, spec: str, name: str, origin: str) -> None:
        self.spec = spec
        self.name = name
        self.origin = origin


def _looks_like_local(line: str) -> bool:
    """Return True for editable installs, path installs, and pip control flags.

    These are first-party or local references that are not pulled from PyPI and
    therefore should not be sent to ``pip download`` against the CFS feed.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return True
    # editable installs / nested-or-constraint file includes
    if stripped.startswith(("-e ", "--editable")):
        return True
    if stripped.startswith(("-r ", "--requirement", "-c ", "--constraint", "-f ", "--find-links")):
        return True
    # bare pip options (e.g. --index-url=...); the caller controls the index
    if stripped.startswith("-"):
        return True
    # relative / absolute path references (../../core/azure-core, ./foo, C:\...)
    if stripped.startswith((".", "/")) or (len(stripped) > 1 and stripped[1] == ":"):
        return True
    # URL / VCS installs
    if "://" in stripped:
        return True
    return False


def _parse_requirement_line(line: str) -> Optional[Requirement]:
    """Parse a single requirements-file line into a Requirement, or None to skip."""
    # strip inline comments and environment-marker-safe trailing whitespace
    content = line.split(" #", 1)[0].strip()
    if _looks_like_local(content):
        return None
    try:
        return Requirement(content)
    except InvalidRequirement:
        return None


def _is_first_party(name: str, first_party: Set[str]) -> bool:
    return name.lower() in first_party


def iter_requirement_files(repo_root: str) -> Iterable[str]:
    """Yield the absolute path of every ``dev_requirements.txt`` in the repo."""
    for current, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in _PRUNE_DIRS]
        if "dev_requirements.txt" in filenames:
            yield os.path.join(current, "dev_requirements.txt")


def collect_from_requirement_file(path: str, origin: str) -> List[RequirementSource]:
    sources: List[RequirementSource] = []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                requirement = _parse_requirement_line(line)
                if requirement is not None:
                    sources.append(RequirementSource(str(requirement), requirement.name, origin))
    except OSError as exc:
        print(f"[warn] could not read {path}: {exc}", file=sys.stderr)
    return sources


def collect_from_pyproject(package_dir: str) -> List[RequirementSource]:
    """Collect [project].dependencies and [project.optional-dependencies]."""
    sources: List[RequirementSource] = []
    pyproject_path = os.path.join(package_dir, "pyproject.toml")
    if not os.path.exists(pyproject_path):
        return sources
    try:
        pyproject = get_pyproject_dict(pyproject_path)
    except Exception as exc:  # pragma: no cover - malformed toml
        print(f"[warn] could not parse {pyproject_path}: {exc}", file=sys.stderr)
        return sources

    project = pyproject.get("project", {}) if isinstance(pyproject, dict) else {}
    if not project:
        return sources
    origin = pyproject_path

    def _add(specifiers: Iterable[str]) -> None:
        for spec in specifiers:
            requirement = _parse_requirement_line(spec)
            if requirement is not None:
                sources.append(RequirementSource(str(requirement), requirement.name, origin))

    _add(project.get("dependencies", []) or [])
    for extra_specs in (project.get("optional-dependencies", {}) or {}).values():
        _add(extra_specs or [])
    return sources


def discover_first_party_names(repo_root: str) -> Set[str]:
    """Return the lowercased names of every package built from this repo.

    These are skipped because they are published by our own pipelines, not pulled
    from PyPI upstream.
    """
    names: Set[str] = set()
    sdk_root = os.path.join(repo_root, "sdk")
    search_root = sdk_root if os.path.isdir(sdk_root) else repo_root
    try:
        for package_dir in discover_targeted_packages("azure*", search_root, compatibility_filter=False):
            try:
                names.add(ParsedSetup.from_path(package_dir).name.lower())
            except Exception:  # pragma: no cover - best effort discovery
                continue
    except Exception as exc:  # pragma: no cover - best effort discovery
        print(f"[warn] first-party discovery failed: {exc}", file=sys.stderr)
    return names


def collect_all_sources(repo_root: str) -> List[RequirementSource]:
    sources: List[RequirementSource] = []

    # 1) dev_requirements.txt everywhere
    for req_file in iter_requirement_files(repo_root):
        sources.extend(collect_from_requirement_file(req_file, req_file))

    # 2) pyproject.toml dependencies for every discovered package
    sdk_root = os.path.join(repo_root, "sdk")
    search_root = sdk_root if os.path.isdir(sdk_root) else repo_root
    try:
        package_dirs = discover_targeted_packages("azure*", search_root, compatibility_filter=False)
    except Exception as exc:  # pragma: no cover - best effort discovery
        print(f"[warn] package discovery failed: {exc}", file=sys.stderr)
        package_dirs = []
    for package_dir in package_dirs:
        sources.extend(collect_from_pyproject(package_dir))

    # 3) shared / engineering requirement files
    for relative in SHARED_REQUIREMENT_FILES:
        absolute = os.path.join(repo_root, relative)
        if os.path.exists(absolute):
            sources.extend(collect_from_requirement_file(absolute, absolute))

    # 4) azpysdk static-analysis tool pins (formerly hardcoded in Python)
    tool_requirements_dir = os.path.join(repo_root, "eng", "tool_requirements")
    if os.path.isdir(tool_requirements_dir):
        for entry in sorted(os.listdir(tool_requirements_dir)):
            if entry.endswith(".txt"):
                path = os.path.join(tool_requirements_dir, entry)
                sources.extend(collect_from_requirement_file(path, path))

    return sources


def dedupe_specs(sources: List[RequirementSource], first_party: Set[str]) -> Tuple[Dict[str, List[str]], List[str]]:
    """Return (spec -> [origins]) for third-party specs, and the skipped first-party names.

    Specs are de-duplicated on their exact text so that distinct version
    constraints for the same distribution are all warmed.
    """
    spec_to_origins: Dict[str, List[str]] = {}
    skipped_first_party: Set[str] = set()
    for source in sources:
        if _is_first_party(source.name, first_party):
            skipped_first_party.add(source.name.lower())
            continue
        spec_to_origins.setdefault(source.spec, [])
        if source.origin not in spec_to_origins[source.spec]:
            spec_to_origins[source.spec].append(source.origin)
    return spec_to_origins, sorted(skipped_first_party)


def pip_download(spec: str, dest: str, index_url: str, python_executable: str) -> Tuple[bool, str]:
    """Download *spec* and its full transitive closure into *dest* from *index_url*.

    Dependencies are intentionally included (no ``--no-deps``) so the whole
    closure is pulled through into the CFS cache.
    """
    command = [
        python_executable,
        "-m",
        "pip",
        "download",
        spec,
        "--dest",
        dest,
        "--index-url",
        index_url,
        # allow pre-releases; some tool pins (and their deps) are pre-release
        "--pre",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout).strip()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--index-url",
        default=os.environ.get("PIP_INDEX_URL", CFS_INDEX_URL),
        help="Feed to warm. Defaults to $PIP_INDEX_URL (set by the pipeline auth step) or the public CFS URL.",
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Directory to download into. Defaults to a temporary directory that is removed afterwards.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Optional path to write a JSON summary report (published as a pipeline artifact).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and print the requirement set without downloading anything.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit non-zero if any requirement failed to download. By default the daily job exits 0 and just reports.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    repo_root = discover_repo_root()

    print(f"[info] scanning repository for declared dependencies: {repo_root}")
    first_party = discover_first_party_names(repo_root)
    print(f"[info] discovered {len(first_party)} first-party packages (these are skipped)")

    sources = collect_all_sources(repo_root)
    spec_to_origins, skipped_first_party = dedupe_specs(sources, first_party)
    specs = sorted(spec_to_origins)

    print(f"[info] collected {len(sources)} requirement references")
    print(f"[info] {len(specs)} unique third-party specifiers to warm")

    if args.dry_run:
        for spec in specs:
            print(f"  {spec}")
        print(f"[info] dry-run: skipped {len(skipped_first_party)} first-party distributions")
        return 0

    dest_context: Optional[tempfile.TemporaryDirectory] = None
    if args.dest:
        os.makedirs(args.dest, exist_ok=True)
        dest = args.dest
    else:
        dest_context = tempfile.TemporaryDirectory(prefix="cfs-warm-")
        dest = dest_context.name

    succeeded: List[str] = []
    failed: List[Dict[str, str]] = []
    try:
        for index, spec in enumerate(specs, start=1):
            print(f"[{index}/{len(specs)}] pip download {spec}")
            ok, error = pip_download(spec, dest, args.index_url, sys.executable)
            if ok:
                succeeded.append(spec)
            else:
                print(f"[warn] failed to warm {spec}: {error.splitlines()[-1] if error else 'unknown error'}")
                failed.append({"spec": spec, "origins": spec_to_origins[spec], "error": error})
    finally:
        if dest_context is not None:
            dest_context.cleanup()

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "index_url": args.index_url,
        "total_unique_specs": len(specs),
        "succeeded": len(succeeded),
        "failed": len(failed),
        "skipped_first_party": len(skipped_first_party),
        "failures": failed,
    }

    print(
        f"[info] done: {len(succeeded)} warmed, {len(failed)} failed, "
        f"{len(skipped_first_party)} first-party skipped"
    )

    if args.report:
        with open(args.report, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        print(f"[info] wrote report to {args.report}")

    if failed and args.fail_on_error:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
