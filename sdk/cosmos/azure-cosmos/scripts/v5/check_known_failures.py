# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Gate the full v4-on-rust run: fail only on UNEXPLAINED failures.

The broad suite isn't all-green — some reds are known-unsupported features
(resource-token auth, partitionless, query/feed, ...). This diffs a pytest
transcript against ``tests/known_rust_failures.txt``: any FAILED/ERROR test
whose node id contains none of the listed substrings is a real regression.

Usage:
    python scripts/v5/check_known_failures.py run.txt [tests/known_rust_failures.txt]
Exit 0 = every failure explained; 1 = unexplained failures (listed); 2 = bad args.
"""
from __future__ import annotations

import re
import sys
from typing import List, Tuple

_FAILED = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)")


def load_patterns(text: str) -> List[str]:
    """Lower-cased, non-empty, non-comment lines from the known-failures file."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s.lower())
    return out


def classify(failed_ids: List[str], patterns: List[str]) -> Tuple[List[str], List[str]]:
    """Split failures into (explained, unexplained) by substring match on node id."""
    explained, unexplained = [], []
    for nid in failed_ids:
        low = nid.lower()
        (explained if any(p in low for p in patterns) else unexplained).append(nid)
    return explained, unexplained


def failed_ids_from_transcript(text: str) -> List[str]:
    """Node ids from pytest FAILED/ERROR summary lines."""
    return [m.group(1) for m in (_FAILED.match(l) for l in text.splitlines()) if m]


def main(argv: List[str]) -> int:
    if not argv:
        print("usage: check_known_failures.py <transcript> [known.txt]", file=sys.stderr)
        return 2
    transcript = open(argv[0], encoding="utf-8").read()
    known = argv[1] if len(argv) > 1 else "tests/known_rust_failures.txt"
    patterns = load_patterns(open(known, encoding="utf-8").read())
    _, unexplained = classify(failed_ids_from_transcript(transcript), patterns)
    if unexplained:
        print("UNEXPLAINED rust failures (not in {}):".format(known), file=sys.stderr)
        for nid in unexplained:
            print("  " + nid, file=sys.stderr)
        return 1
    print("All failures match known_rust_failures.txt — gate clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

