"""Parse a parity-run transcript and rewrite the per-op audit markdown.

Default ``--op`` is ``create_item`` so single-arg invocations
(``python docs/_build_parity_audit.py <transcript.txt>``) keep working.
Pass e.g. ``--op delete_item`` to render the delete_item parity audit.
"""
from __future__ import annotations

import ast
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_OP = "create_item"


def _test_file_for(op: str) -> Path:
    """Sync parity test file for the named op."""
    return Path("tests/{op}/sync/test_{op}_parity.py".format(op=op))


def _out_path_for(op: str) -> Path:
    """Output markdown path for the per-op audit doc."""
    return Path("docs/V5/V5_PARITY_AUDIT_{op}.md".format(op=op))


FAILED_LINE_RE = re.compile(r"^FAILED tests[\\/][^:]+::(test_\w+)", re.MULTILINE)
PASSED_LINE_RE = re.compile(r"^PASSED tests[\\/][^:]+::(test_\w+)", re.MULTILINE)
SKIPPED_LINE_RE = re.compile(r"^SKIPPED tests[\\/][^:]+::(test_\w+)", re.MULTILINE)
# pytest -v per-test result line: ``tests/.../test_X PASSED [..%]``.
VERBOSE_RESULT_LINE_RE = re.compile(
    r"^tests[\\/][^:]+::(test_\w+)\s+(PASSED|FAILED|SKIPPED|XFAIL|XPASS|ERROR)",
    re.MULTILINE,
)
# Matches any line that begins with a pytest test id. Used to widen
# "seen" detection when ``-v -s`` lets the test's own prints crowd
# the status word off the line. Only feeds ``seen_in_transcript`` --
# the FAIL / SKIP regexes above stay strict.
SEEN_LINE_RE = re.compile(
    r"^tests[\\/][^:]+::(test_\w+)\b",
    re.MULTILINE,
)
# ``collected N items`` line; lets us flag transcripts that ran fewer
# tests than the source currently defines.
COLLECTED_RE = re.compile(r"^collected\s+(\d+)\s+items?", re.MULTILINE)
SUMMARY_RE = re.compile(r"=+\s*((?:\d+\s+\w+(?:,?\s*)?)+)\s+in\s+\d[\d.]*s(?:\s*\([\d:]+\))?\s*=+", re.IGNORECASE)
PARITY_BLOCK_RE = re.compile(r"=+\s*\nPARITY CALL: (?P<title>.+?)\n=+\s*\n(?P<body>.*?)\n=+\s*", re.DOTALL)
SESSION_START_RE = re.compile(r"=+\s*test session starts\s*=+", re.IGNORECASE)


def _parse_test_order(src: str) -> tuple[list[str], dict[str, list[int]]]:
    """Return ``(test names in source order, duplicate definitions)``.

    If the same test name is defined more than once, only the last
    definition is kept (matches Python's import-time semantics) and
    the earlier line numbers are reported as duplicates.
    """
    order: list[str | None] = []
    index_for: dict[str, int] = {}
    last_lineno_for: dict[str, int] = {}
    duplicates: dict[str, list[int]] = {}

    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        name = node.name
        if name in index_for:
            prev_lineno = last_lineno_for[name]
            duplicates.setdefault(name, [prev_lineno]).append(node.lineno)
            order[index_for[name]] = None
        index_for[name] = len(order)
        last_lineno_for[name] = node.lineno
        order.append(name)

    return [n for n in order if n is not None], duplicates


def _parse_tests_without_parity_call(src: str) -> set[str]:
    """Return test names whose body never calls ``run_on_both_backends``.

    Such tests never print a ``PARITY CALL`` block, so the renderer
    must not hand them an unclaimed block from the transcript. The
    check also follows module-level helpers one step: if a test calls
    a helper that itself calls ``run_on_both_backends``, the test
    counts as a block producer.
    """
    tree = ast.parse(src)

    def _calls_target(node: ast.AST, target_names: set[str]) -> bool:
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            f = sub.func
            if isinstance(f, ast.Name) and f.id in target_names:
                return True
            if isinstance(f, ast.Attribute) and f.attr in target_names:
                return True
        return False

    # Collect module-level helpers that (transitively) call
    # run_on_both_backends.
    producers: set[str] = {"run_on_both_backends"}
    helpers: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            helpers[node.name] = node
    changed = True
    while changed:
        changed = False
        for name, fn in helpers.items():
            if name in producers:
                continue
            if _calls_target(fn, producers):
                producers.add(name)
                changed = True

    # A test is a non-producer iff its body calls no producer.
    non_producers: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        if not _calls_target(node, producers):
            non_producers.add(node.name)
    return non_producers


def _latest_run_slice(transcript: str) -> str:
    """Return the substring starting at the last pytest session start."""
    starts = [m.start() for m in SESSION_START_RE.finditer(transcript)]
    if starts:
        return transcript[starts[-1]:]
    return transcript


def _parse_skip_reasons(src: str) -> dict:
    """Return ``{test_name: skip_reason}`` for ``@pytest.mark.skip`` decorators.

    Reads the AST so multi-line, implicit-concatenated string literals
    in the ``reason=`` kwarg are picked up cleanly.
    """
    out = {}
    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            # Match @pytest.mark.skip(...)
            f = dec.func
            if (isinstance(f, ast.Attribute) and f.attr == "skip"
                    and isinstance(f.value, ast.Attribute) and f.value.attr == "mark"):
                reason = None
                for kw in dec.keywords:
                    if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                        reason = kw.value.value
                if reason is None and dec.args and isinstance(dec.args[0], ast.Constant):
                    reason = dec.args[0].value
                if reason:
                    out[node.name] = reason.strip()
                break
    return out


def _parse_descriptions(src: str) -> dict:
    """Return ``{test_name: first docstring line}`` for each test function.

    Falls back to ``'(no description)'`` when the test has no docstring.
    """
    out = {}
    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        doc = ast.get_docstring(node) or ""
        first = doc.strip().splitlines()[0].strip() if doc.strip() else ""
        out[node.name] = first or "(no description)"
    return out


# Replacements for typographic punctuation that gets garbled when
# pytest output is captured through a Windows console that re-encodes
# bytes between UTF-8, cp437 and cp1252. Each key is a known
# mis-decoded sequence; the value is the ASCII fallback we want.
_MOJIBAKE_FIXUPS = {
    "ΓÇö": "--",
    "ΓÇô": "-",
    "ΓÇÖ": "'",
    "ΓÇÿ": "'",
    "ΓÇ£": '"',
    "ΓÇ¥": '"',
    "ΓÇª": "...",
    "\u2014": "--",
    "\u2013": "-",
    "\u00f9": "--",
    "\u00f7": "-",
}


def _sanitize(text: str) -> str:
    for bad, good in _MOJIBAKE_FIXUPS.items():
        text = text.replace(bad, good)
    return text


# Verdict line in a PARITY CALL block: the line after ``--- VERDICT ---``,
# indented by two spaces. Used to populate the scoreboard ``Why`` cell.
_VERDICT_LINE_RE = re.compile(r"^---\s*VERDICT\s*---\s*$\s*^\s+(.+)$", re.MULTILINE)


def _extract_verdict(block: str) -> str | None:
    """Return the verdict text from a rendered PARITY CALL block."""
    if not block:
        return None
    m = _VERDICT_LINE_RE.search(block)
    if not m:
        return None
    return m.group(1).strip()


def _scoreboard_why(
    status: str,
    name: str,
    description: str,
    skip_reason: str | None,
    block: str | None,
    is_non_producer: bool = False,
) -> str:
    """Return the ``Why`` cell text for one scoreboard row.

    - FAILED  -> verdict line from the test's PARITY CALL block,
                 falling back to a "no block in transcript" note.
    - SKIPPED -> the ``@pytest.mark.skip(reason=...)`` text from source.
    - STALE   -> a fixed "not in transcript" note.
    - PASSED  -> verdict line if present, else a plain "Passed" note.
                 Non-producer tests get a tailored note because no
                 pytest flag will produce a block for them.
    """
    if status == "FAILED":
        verdict = _extract_verdict(block) if block else None
        if verdict:
            return verdict
        return "(failed -- no PARITY CALL block in transcript)"
    if status == "SKIPPED":
        return "Skipped: " + (skip_reason or "(no reason given in source)")
    if status == "STALE":
        return "Not in transcript -- re-run pytest and rebuild this doc."
    # PASSED
    verdict = _extract_verdict(block) if block else None
    if verdict:
        return verdict
    if is_non_producer:
        return "Passed (test does not invoke the parity harness; see the per-test section for what it actually pins)."
    return "Passed (no PARITY CALL block captured -- re-run with `pytest -s` to populate)."


def _parse_args(argv: list[str]) -> tuple[str, Path] | None:
    """Return ``(op, transcript_path)`` or ``None`` on a usage error.

    Two accepted forms::

        python docs/_build_parity_audit.py <transcript.txt>
        python docs/_build_parity_audit.py --op <name> <transcript.txt>

    The op name becomes part of a filesystem path, so reject anything
    that contains a path separator or parent-traversal sequence.
    """
    if len(argv) == 2:
        return DEFAULT_OP, Path(argv[1])
    if len(argv) == 4 and argv[1] == "--op":
        op = argv[2]
        if not op or "/" in op or "\\" in op or ".." in op:
            print(
                "error: --op must be a simple identifier (e.g. delete_item); got: {!r}".format(op),
                file=sys.stderr,
            )
            return None
        return op, Path(argv[3])
    return None


def main() -> int:
    parsed = _parse_args(sys.argv)
    if parsed is None:
        print(
            "usage: python docs/_build_parity_audit.py [--op <name>] <transcript.txt>\n"
            "       --op defaults to '{}' (back-compat with the single-arg form).".format(DEFAULT_OP)
        )
        return 2
    op, transcript_path = parsed
    test_file = _test_file_for(op)
    if not test_file.is_file():
        print(
            "error: parity test file not found for op={!r}: {} does not exist"
            .format(op, test_file.as_posix()),
            file=sys.stderr,
        )
        return 2
    raw = transcript_path.read_bytes()
    # PowerShell's ``Tee-Object`` writes UTF-16 LE with a BOM by default.
    # Handle the common BOM-tagged encodings explicitly so the regexes
    # below see real text instead of NUL-separated bytes.
    if raw.startswith(b"\xff\xfe"):
        transcript = raw.decode("utf-16-le", errors="replace")
    elif raw.startswith(b"\xfe\xff"):
        transcript = raw.decode("utf-16-be", errors="replace")
    elif raw.startswith(b"\xef\xbb\xbf"):
        transcript = raw.decode("utf-8-sig", errors="replace")
    else:
        transcript = raw.decode("utf-8", errors="replace")
    transcript = _sanitize(transcript)
    transcript = _latest_run_slice(transcript)
    src = test_file.read_text(encoding="utf-8")
    tests, duplicate_defs = _parse_test_order(src)
    if duplicate_defs:
        rendered = ", ".join(
            "{}@{}".format(name, "->".join(str(ln) for ln in lines))
            for name, lines in sorted(duplicate_defs.items())
        )
        print(
            "warning: duplicate test function definitions found; using runtime "
            f"last-definition order: {rendered}",
            file=sys.stderr,
        )
    skipped = _parse_skip_reasons(src)
    descriptions = _parse_descriptions(src)
    # Tests whose body never calls ``run_on_both_backends`` (directly or
    # via a helper). They will never produce a PARITY CALL block, so the
    # source-order fallback below must not consume an unclaimed block
    # on their behalf -- doing so would steal it from the next real
    # producer and mis-render both rows.
    non_producer_tests = _parse_tests_without_parity_call(src)
    failed = set(FAILED_LINE_RE.findall(transcript))
    # Tests pytest actually exercised in this transcript. A test missing
    # from every regex below is marked STALE rather than silently
    # defaulting to PASSED. ``SEEN_LINE_RE`` is added last and only
    # widens "seen" -- the FAIL / SKIP sets stay strict so a missing
    # FAIL can never be silently upgraded to a PASS.
    seen_in_transcript: set[str] = set()
    seen_in_transcript.update(FAILED_LINE_RE.findall(transcript))
    seen_in_transcript.update(PASSED_LINE_RE.findall(transcript))
    seen_in_transcript.update(SKIPPED_LINE_RE.findall(transcript))
    seen_in_transcript.update(name for name, _ in VERBOSE_RESULT_LINE_RE.findall(transcript))
    seen_in_transcript.update(SEEN_LINE_RE.findall(transcript))
    collected_match = COLLECTED_RE.search(transcript)
    collected_count = int(collected_match.group(1)) if collected_match else None
    summary_matches = list(SUMMARY_RE.finditer(transcript))
    summary = summary_matches[-1].group(1).strip(" ,") if summary_matches else "(unknown)"
    blocks = []
    title_to_block = {}
    title_blocks = []
    for m in PARITY_BLOCK_RE.finditer(transcript):
        title = m.group("title").strip()
        rendered = "PARITY CALL: " + title + "\n" + ("=" * 78) + "\n" + m.group("body").rstrip() + "\n" + ("=" * 78)
        rendered = _sanitize(rendered)
        if title not in title_to_block:
            title_blocks.append(title)
        title_to_block[title] = rendered
    blocks = [title_to_block[t] for t in title_blocks]
    statuses = {}
    for n in tests:
        if n in skipped:
            statuses[n] = "SKIPPED"
        elif n in failed:
            statuses[n] = "FAILED"
        elif n in seen_in_transcript:
            statuses[n] = "PASSED"
        else:
            # No evidence pytest ran this test; mark explicitly so the
            # reader does not mistake silence for success.
            statuses[n] = "STALE"
    stale_tests = [n for n in tests if statuses[n] == "STALE"]
    block_for = {}
    # Pass 1: match blocks whose title embeds the test name
    # (e.g. ``test_duplicate_id_raises_typed_exception: insert id=...``).
    name_to_block = {}
    for title, rendered in zip(title_blocks, blocks):
        for n in tests:
            if title.startswith(n + ':') or title.startswith(n + ' '):
                name_to_block[n] = rendered
                break
    used_titles = set()
    for n, rendered in name_to_block.items():
        block_for[n] = rendered
        for title, r2 in zip(title_blocks, blocks):
            if r2 == rendered:
                used_titles.add(title)
                break
    remaining = [(t, r) for t, r in zip(title_blocks, blocks) if t not in used_titles]

    # Pass 2: match unclaimed blocks to tests by their ``[Lx]`` level
    # tag. Block titles like ``[L5] duplicate-id 409: ...`` carry no
    # test name, so the name-match in pass 1 misses them.
    level_re = re.compile(r"^\[(L\d+)]")
    still_remaining = []
    for title, rendered in remaining:
        m_lvl = level_re.match(title)
        assigned = False
        if m_lvl:
            tag = "_" + m_lvl.group(1) + "_"  # e.g. "_L5_"
            for n in tests:
                if (
                    tag in n
                    and n not in block_for
                    and statuses[n] != "SKIPPED"
                    and n not in non_producer_tests
                ):
                    block_for[n] = rendered
                    assigned = True
                    break
        if not assigned:
            still_remaining.append(rendered)
    remaining = still_remaining

    # Pass 3: source-order fallback. Only match a leftover block to a
    # test whose ``[Lx]`` level prefix matches the block's title; never
    # to a non-producer. Leaves the row unmatched (so the doc renders
    # the honest "No PARITY CALL block" note) rather than silently
    # attaching the wrong block.
    for n in tests:
        if statuses[n] == 'SKIPPED' or n in block_for:
            continue
        if n in non_producer_tests:
            continue
        if not remaining:
            continue
        m_name_lvl = re.match(r"^test_(L\d+)_", n)
        if not m_name_lvl:
            continue
        want_tag = "[" + m_name_lvl.group(1) + "]"
        for idx, (title, rendered) in enumerate(
            zip(title_blocks, blocks)
        ):
            if rendered in remaining and title.startswith(want_tag):
                block_for[n] = rendered
                remaining.remove(rendered)
                break
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    account = os.environ.get("ACCOUNT_URI") or os.environ.get("ACCOUNT_HOST") or "(env not set)"
    out = []
    out.append("# `{}` parity test results".format(op))
    out.append("")
    out.append(f"**Generated:** {now}")
    out.append(f"**Source:** `{test_file.as_posix()}`")
    out.append(f"**Account:** `{account}`")
    out.append("")
    out.append(f"**Summary:** {summary}")
    out.append("")
    if stale_tests or (collected_count is not None and collected_count != len(tests)):
        out.append(
            "> ⚠ **Transcript / source mismatch.** The test file currently "
            f"defines **{len(tests)}** tests"
            + (
                f", but the transcript records pytest collecting **{collected_count}**"
                if collected_count is not None
                else ""
            )
            + ". The transcript is stale relative to the source -- re-run "
              f"`pytest {test_file.as_posix()} -v -s` "
              "and rebuild this doc to get a faithful report. Tests with no "
              "evidence in the transcript are marked `_STALE_` in the "
              "scoreboard below (they did **not** silently pass; they were "
              "simply not exercised by the captured run)."
        )
        if stale_tests:
            out.append("")
            out.append("> Missing from transcript: "
                       + ", ".join("`{}`".format(n) for n in stale_tests))
        out.append("")
    out.append("Each test runs the same `{}` call against both backends".format(op))
    out.append("(core-python and rust) and diffs the outcomes. This document is")
    out.append("the verbatim per-test report from the most recent run \u2014 no")
    out.append("commentary, no historical context. The `PARITY CALL` blocks are")
    out.append("produced by")
    out.append("`tests/common/_parity_helpers.py::BackendComparison.format_report`.")
    out.append("")
    out.append("**How to read a PARITY CALL block.** Each block is one test's")
    out.append("structured report and has five sections:")
    out.append("")
    out.append("- `REQUEST` \u2014 the body and kwargs the test sent to *both*")
    out.append("  backends (identical inputs by construction).")
    out.append("- `CORE-PYTHON` \u2014 the legacy v4.x backend's outcome:")
    out.append("  status (`OK` or `RAISED`), response body, and the response")
    out.append("  headers it surfaced.")
    out.append("- `RUST` \u2014 the same three things from the rust path.")
    out.append("- `DIFFS` \u2014 normalised differences between the two outcomes.")
    out.append("  Headers are bucketed into three populations before the diff")
    out.append("  runs, each with a different contract:")
    out.append("")
    out.append("  | Population | Value diff | Presence diff | Examples |")
    out.append("  | --- | --- | --- | --- |")
    out.append("  | value-volatile required | skipped | **enforced** | `x-ms-request-charge`, `etag`, `date`, `server`, `x-ms-resource-quota`, the LSN family, the topology / diagnostic IDs |")
    out.append("  | fully ignored | skipped | skipped | `_etag` body-field leftover (structurally not a header name) |")
    out.append("  | everything else | **enforced** | **enforced** | intended-collection-rid echo, indexing-progress, retry-after, sub-status, any header the driver newly starts surfacing |")
    out.append("")
    out.append("  The Rust binding rewrites a small set of `cosmos-`-prefixed")
    out.append("  LSN-family headers (`x-ms-cosmos-llsn` and friends) to their")
    out.append("  un-prefixed legacy spellings inside")
    out.append("  `azure/cosmos/_backend/base.py::normalize_response_headers`")
    out.append("  *before* the response reaches the diff, so each LSN header is")
    out.append("  presence-checked under a single canonical name. The exact sets")
    out.append("  live in `_VALUE_VOLATILE_REQUIRED_HEADERS` and")
    out.append("  `_FULLY_IGNORED_HEADERS` in `tests/common/_parity_helpers.py`.")
    out.append("- `VERDICT` \u2014 plain-English summary of what the diff means")
    out.append("  (`FULL PARITY`, `FUNCTIONAL PARITY, REPORTING GAP`,")
    out.append("  `FUNCTIONAL DIVERGENCE`, or `EXCEPTION DIVERGENCE`).")
    out.append("")
    out.append("If a row in the scoreboard says \u201CNo PARITY CALL block found")
    out.append("in transcript for this test\u201D it means the test ran but its")
    out.append("printed report was not in the captured pytest stdout \u2014 most")
    out.append("often because pytest was invoked without `-s`, so per-test")
    out.append("stdout was swallowed for passing tests. Re-run with")
    out.append("`pytest -s ...` to populate every row.")
    out.append("")
    out.append("## Scoreboard")
    out.append("")
    out.append(
        "Rows are sorted by status: failed tests first (so regressions are "
        "the first thing the reader sees), then skipped, then stale, then "
        "passed. The **Per-test reports** section below follows the same "
        "order, so scrolling down reads top-to-bottom in the same priority. "
        "The `#` column is the test's index in the source file -- click "
        "through to the matching section in **Per-test reports** below for "
        "the full PARITY CALL block. The `Description` column is the "
        "test's docstring summary -- a short, customer-focused statement of "
        "what scenario the test exercises -- and is filled in for every "
        "row regardless of outcome. The `Why` column is the *outcome* "
        "reason for this run: the verdict line from the parity helper on "
        "passes and failures, the `@pytest.mark.skip(reason=...)` text from "
        "the source on skips, and a stale-transcript note on stale rows."
    )
    out.append("")
    out.append("| # | Test | Description | Outcome | Why |")
    out.append("| --- | --- | --- | --- | --- |")
    marker_for = {
        "PASSED": "**PASS**",
        "FAILED": "**FAIL**",
        "SKIPPED": "_SKIP_",
        "STALE": "_STALE_",
    }
    # Group order: failures first, then skips, then stale, then passes.
    # Within each group keep source order so the # column reads
    # monotonically per group and matches the per-test reports section.
    status_order = {"FAILED": 0, "SKIPPED": 1, "STALE": 2, "PASSED": 3}
    source_index = {n: i for i, n in enumerate(tests, 1)}
    sortable = [(status_order[statuses[n]], source_index[n], n) for n in tests]
    sortable.sort()

    def _cell(text: str) -> str:
        """Escape pipes and collapse newlines so the cell stays on one row."""
        return (text or "").replace("|", "\\|").replace("\n", " ")

    for _, i, n in sortable:
        s = statuses[n]
        desc = _cell(descriptions.get(n, "(no description)"))
        why = _cell(_scoreboard_why(
            s,
            n,
            descriptions.get(n, ""),
            skipped.get(n),
            block_for.get(n),
            is_non_producer=n in non_producer_tests,
        ))
        out.append(f"| {i} | `{n}` | {desc} | {marker_for[s]} | {why} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Per-test reports")
    out.append("")
    # Per-test reports use the same failed -> skipped -> stale -> passed
    # ordering as the scoreboard so the doc reads top-to-bottom in the
    # same priority. The heading number ``i`` stays the source-file
    # index so the scoreboard's ``#`` column links unambiguously.
    for _, i, n in sortable:
        s = statuses[n]
        out.append(f"### {i}. `{n}` \u2014 {s}")
        out.append("")
        desc = descriptions.get(n, "")
        if desc and desc != "(no description)":
            out.append(f"> **What this test exercises:** {desc}")
            out.append("")
        if s == "SKIPPED":
            out.append(f"> **Skip reason:** {skipped.get(n, '(no reason)')}")
            out.append("")
            out.append("_No backend call was made; nothing to diff._")
            out.append("")
            continue
        if s == "STALE":
            out.append(
                "> **Not in transcript.** This test exists in the source but "
                "was not exercised by the captured pytest run -- the "
                "transcript predates this test definition (or rename). "
                "Re-run the suite and rebuild this doc."
            )
            out.append("")
            out.append("_No PARITY CALL block available -- the test did not run in this transcript._")
            out.append("")
            continue
        b = block_for.get(n)
        if b is None:
            if n in non_producer_tests:
                out.append(
                    "_No PARITY CALL block: this test deliberately bypasses "
                    "the parity harness (``run_on_both_backends``) -- it pins "
                    "a single-backend wrapper-level contract rather than a "
                    "cross-backend behavioural diff. See the test's docstring "
                    "above for what it actually asserts._"
                )
            else:
                out.append("_No PARITY CALL block found in transcript for this test._")
        else:
            out.append("```text")
            out.append(b)
            out.append("```")
        out.append("")
    # Filename carries the op name as a suffix so per-op runs do not
    # overwrite each other (``..._create_item.md``, ``..._delete_item.md``).
    out_path = _out_path_for(op)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out_path.as_posix()} ({sum(len(x)+1 for x in out)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
