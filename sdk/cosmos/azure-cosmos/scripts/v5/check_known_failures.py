# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check a completed Rust-default pytest run against exact known-failure IDs.

Pass the captured process exit code with --pytest-exit-code. Empty, incomplete,
inconsistent and entirely skipped runs are invalid, not successful comparisons.
Exit 0 = no unexplained failures; 1 = unexplained failures; 2 = invalid input.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import List, Tuple

_FAILED = re.compile(r"^(?:FAILED|ERROR)\s+(.+?)(?:\s+-\s+.*)?$")
_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_SUMMARY = re.compile(
    r"=*\s*(?P<body>.+?)\s+in\s+\d+(?:\.\d+)?s"
    r"(?:\s+\(\d+:\d{2}(?::\d{2})?\))?\s*=*"
)
_COUNT = re.compile(
    r"(?P<count>\d+)\s+"
    r"(?P<kind>passed|failed|skipped|errors?|xfailed|xpassed|warnings?|deselected)"
)


def _normalize_nodeid(nodeid: str) -> str:
    path, separator, test = nodeid.partition("::")
    return path.replace("\\", "/") + separator + test


def load_known_ids(text: str) -> List[str]:
    """Load exact, case-sensitive node IDs; reject broad feature-name entries."""
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        nodeid = _normalize_nodeid(line.strip())
        if not nodeid or nodeid.startswith("#"):
            continue
        path, separator, test = nodeid.partition("::")
        if (
            not path.startswith("tests/")
            or not path.endswith(".py")
            or not separator
            or not test
        ):
            raise ValueError(
                "known-failures line {} must be an exact tests/...py::... node ID, not {!r}".format(
                    number, nodeid
                )
            )
        out.append(nodeid)
    return out


def classify(failed_ids: List[str], known_ids: List[str]) -> Tuple[List[str], List[str]]:
    """Split failures into (explained, unexplained) by exact node ID."""
    known = set(known_ids)
    explained, unexplained = [], []
    for nid in failed_ids:
        (explained if _normalize_nodeid(nid) in known else unexplained).append(nid)
    return explained, unexplained


def failed_ids_from_transcript(text: str) -> List[str]:
    """Node ids from pytest FAILED/ERROR summary lines."""
    return [
        match.group(1).strip()
        for line in _ANSI.sub("", text).splitlines()
        if (match := _FAILED.fullmatch(line.strip()))
    ]


def validate_run(text: str, pytest_exit_code: int) -> List[str]:
    """Require completion evidence consistent with the real pytest exit code."""
    if pytest_exit_code not in (0, 1):
        raise ValueError("pytest did not complete normally (exit {})".format(pytest_exit_code))
    lines = _ANSI.sub("", text).strip().splitlines()
    summary = _SUMMARY.fullmatch(lines[-1].strip()) if lines else None
    if summary is None:
        raise ValueError("transcript has no final pytest completion summary")
    counts: dict[str, int] = {}
    for part in summary.group("body").split(","):
        match = _COUNT.fullmatch(part.strip())
        if match is None:
            raise ValueError("unrecognized pytest summary count: {!r}".format(part))
        kind = match.group("kind")
        if kind in ("errors", "warnings"):
            kind = kind[:-1]
        if kind in counts:
            raise ValueError("duplicate pytest summary count: {}".format(kind))
        counts[kind] = int(match.group("count"))
    if not sum(counts.get(kind, 0) for kind in ("passed", "failed", "error", "xfailed", "xpassed")):
        raise ValueError("pytest recorded no executed tests (empty or entirely skipped run)")
    failed_ids = failed_ids_from_transcript(text)
    failures = counts.get("failed", 0) + counts.get("error", 0)
    if failures != len(failed_ids):
        raise ValueError(
            "pytest summary reports {} failures/errors but {} FAILED/ERROR node IDs were captured".format(
                failures, len(failed_ids)
            )
        )
    if bool(failures) != (pytest_exit_code == 1):
        raise ValueError("pytest exit code and transcript failure count disagree")
    return failed_ids


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript")
    parser.add_argument("known", nargs="?", default="tests/known_rust_failures.txt")
    parser.add_argument("--pytest-exit-code", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        raw = Path(args.transcript).read_bytes()
        encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        failed_ids = validate_run(raw.decode(encoding), args.pytest_exit_code)
        known_ids = load_known_ids(Path(args.known).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        print("INVALID Rust test run: {}".format(exc), file=sys.stderr)
        return 2
    explained, unexplained = classify(failed_ids, known_ids)
    if unexplained:
        print("UNEXPLAINED Rust failures (not in {}):".format(args.known), file=sys.stderr)
        for nid in unexplained:
            print("  " + nid, file=sys.stderr)
        return 1
    print("Completed pytest run; {} explicitly exempt failures, no unexplained failures.".format(len(explained)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
