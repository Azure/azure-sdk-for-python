"""Parse a parity-run transcript and rewrite docs/V5_PARITY_AUDIT.md
to contain only per-test reports (no commentary, no historical context)."""
from __future__ import annotations
import ast, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
TEST_FILE = Path("tests/create_item/sync/test_create_item_parity.py")
FAILED_LINE_RE = re.compile(r"^FAILED tests[\\/][^:]+::(test_\w+)", re.MULTILINE)
PASSED_LINE_RE = re.compile(r"^PASSED tests[\\/][^:]+::(test_\w+)", re.MULTILINE)
SKIPPED_LINE_RE = re.compile(r"^SKIPPED tests[\\/][^:]+::(test_\w+)", re.MULTILINE)
# Verbose-mode per-test result lines (``pytest -v``):
#   tests/create_item/sync/test_create_item_parity.py::test_X PASSED [..%]
VERBOSE_RESULT_LINE_RE = re.compile(
    r"^tests[\\/][^:]+::(test_\w+)\s+(PASSED|FAILED|SKIPPED|XFAIL|XPASS|ERROR)",
    re.MULTILINE,
)
# Collection summary line (``collected N items``) so we can compare what
# pytest actually saw against what the test file currently defines and
# warn when the transcript is stale relative to the source.
COLLECTED_RE = re.compile(r"^collected\s+(\d+)\s+items?", re.MULTILINE)
SUMMARY_RE = re.compile(r"=+\s*((?:\d+\s+\w+(?:,?\s*)?)+)\s+in\s+\d[\d.]*s(?:\s*\([\d:]+\))?\s*=+", re.IGNORECASE)
PARITY_BLOCK_RE = re.compile(r"=+\s*\nPARITY CALL: (?P<title>.+?)\n=+\s*\n(?P<body>.*?)\n=+\s*", re.DOTALL)
SESSION_START_RE = re.compile(r"=+\s*test session starts\s*=+", re.IGNORECASE)


def _parse_test_order(src: str) -> tuple[list[str], dict[str, list[int]]]:
    """Return (effective_test_order, duplicate_definitions).

    Test order is based on Python runtime semantics at module import time:
    if the same test function name is defined multiple times, the last
    definition wins and earlier ones are shadowed.
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


def _latest_run_slice(transcript: str) -> str:
    """Best-effort extraction of the latest pytest session from transcript."""
    starts = [m.start() for m in SESSION_START_RE.finditer(transcript)]
    if starts:
        return transcript[starts[-1]:]
    return transcript


def _parse_skip_reasons(src: str) -> dict:
    """Return {test_name: skip_reason} by walking the AST.

    Handles multi-line implicit-concatenated string literals in the
    ``reason=`` kwarg, which the previous regex-based parser missed.
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
    """Return {test_name: short_description} from the first line of each
    test function's docstring. Falls back to '(no description)'."""
    out = {}
    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        doc = ast.get_docstring(node) or ""
        first = doc.strip().splitlines()[0].strip() if doc.strip() else ""
        out[node.name] = first or "(no description)"
    return out


# Mojibake produced when UTF-8 em-dashes / en-dashes get mis-decoded as
# cp1252 during pytest output capture. Map them back to ASCII so the
# audit doc never contains stray ``ΓÇö`` / ``ΓÇô`` sequences.
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
}


def _sanitize(text: str) -> str:
    for bad, good in _MOJIBAKE_FIXUPS.items():
        text = text.replace(bad, good)
    return text


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python docs/_build_parity_audit.py <transcript.txt>")
        return 2
    transcript_path = Path(sys.argv[1])
    raw = transcript_path.read_bytes()
    # PowerShell's `Tee-Object` writes UTF-16 LE on Windows by default,
    # which prepends a BOM. Detect and decode accordingly so the regexes
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
    src = TEST_FILE.read_text(encoding="utf-8")
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
    failed = set(FAILED_LINE_RE.findall(transcript))
    # Tests pytest *actually saw* in this transcript. We harvest evidence
    # from every per-test signal pytest can emit: explicit PASSED /
    # FAILED / SKIPPED summary lines (``pytest -ra`` / ``-rA``), the
    # verbose result lines (``pytest -v``), plus the AST-derived skip
    # set (those *are* in the source even if the transcript predates
    # them, so we deliberately do NOT count AST skips as "seen"). A
    # test name absent from all of these is one the transcript did not
    # exercise -- almost always because the transcript was captured
    # against an older revision of the test file than the one we're
    # rendering against now. Such tests get a STALE marker rather
    # than silently defaulting to PASSED.
    seen_in_transcript: set[str] = set()
    seen_in_transcript.update(FAILED_LINE_RE.findall(transcript))
    seen_in_transcript.update(PASSED_LINE_RE.findall(transcript))
    seen_in_transcript.update(SKIPPED_LINE_RE.findall(transcript))
    seen_in_transcript.update(name for name, _ in VERBOSE_RESULT_LINE_RE.findall(transcript))
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
            # No evidence in the transcript that pytest ran this test --
            # it was added (or renamed) after the transcript was
            # captured. Mark explicitly so the reader does not mistake
            # silence for success.
            statuses[n] = "STALE"
    stale_tests = [n for n in tests if statuses[n] == "STALE"]
    block_for = {}
    # First, claim by name for tests whose title embeds the test name
    # (e.g. test_duplicate_id_raises_typed_exception: insert id=...).
    name_to_block = {}
    for title, rendered in zip(title_blocks, blocks):
        for n in tests:
            if title.startswith(n + ':') or title.startswith(n + ' '):
                name_to_block[n] = rendered
                break
    # Then fill the remaining ran tests in source order, consuming any
    # block not already claimed by name (skip tests that produce no block,
    # like test_response_hook_fires_once which runs its own loop).
    used_titles = set()
    for n, rendered in name_to_block.items():
        block_for[n] = rendered
        # Find the title of this block to mark it used.
        for title, r2 in zip(title_blocks, blocks):
            if r2 == rendered:
                used_titles.add(title)
                break
    remaining = [(t, r) for t, r in zip(title_blocks, blocks) if t not in used_titles]

    # Second pass: match unclaimed blocks to tests by their [Lx] level
    # tag. The L5 block's title is "[L5] duplicate-id 409: ..." (no test
    # name), so name-based matching above misses it. Without this pass
    # the source-order fallback below would hand the L5 block to L4
    # (which produces no block of its own because it runs its own loop
    # instead of going through ``_run``).
    level_re = re.compile(r"^\[(L\d+)\]")
    still_remaining = []
    for title, rendered in remaining:
        m_lvl = level_re.match(title)
        assigned = False
        if m_lvl:
            tag = "_" + m_lvl.group(1) + "_"  # e.g. "_L5_"
            for n in tests:
                if tag in n and n not in block_for and statuses[n] != "SKIPPED":
                    block_for[n] = rendered
                    assigned = True
                    break
        if not assigned:
            still_remaining.append(rendered)
    remaining = still_remaining

    for n in tests:
        if statuses[n] == 'SKIPPED' or n in block_for:
            continue
        if not remaining:
            continue
        # Source-order fallback used to consume ``remaining[0]``
        # unconditionally. That mis-maps freely when the transcript's
        # block order doesn't match the source's test order (added /
        # reordered / renamed tests between transcript capture and doc
        # render). Constrain the fallback to only consume a block
        # whose ``[Lx]`` level tag matches this test's level prefix
        # (e.g. ``test_L2_*`` only consumes a ``[L2]``-titled block);
        # leave the test unmatched otherwise so the doc renders the
        # honest "No PARITY CALL block found" notice rather than
        # silently attaching the wrong block.
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
    out.append("# `create_item` parity test results")
    out.append("")
    out.append(f"**Generated:** {now}")
    out.append(f"**Source:** `tests/create_item/sync/test_create_item_parity.py`")
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
              "`pytest tests/create_item/sync/test_create_item_parity.py -v -s` "
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
    out.append("Each test runs the same `create_item` call against both backends")
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
    out.append("| # | Test | Outcome | Description |")
    out.append("| --- | --- | --- | --- |")
    for i, n in enumerate(tests, 1):
        marker = {
            "PASSED": "**PASS**",
            "FAILED": "**FAIL**",
            "SKIPPED": "_SKIP_",
            "STALE": "_STALE_",
        }[statuses[n]]
        desc = descriptions.get(n, "").replace("|", "\\|")
        out.append(f"| {i} | `{n}` | {marker} | {desc} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Per-test reports")
    out.append("")
    for i, n in enumerate(tests, 1):
        s = statuses[n]
        out.append(f"### {i}. `{n}` \u2014 {s}")
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
            out.append("_No PARITY CALL block found in transcript for this test._")
        else:
            out.append("```text")
            out.append(b)
            out.append("```")
        out.append("")
    Path("docs/V5_PARITY_AUDIT.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote docs/V5_PARITY_AUDIT.md ({sum(len(x)+1 for x in out)} chars)")
    return 0
if __name__ == "__main__":
    sys.exit(main())
