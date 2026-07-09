# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the legacy-folder parity reporter.

The reporter and the capture plugin share one wire format: the plugin
emits ``===PARITY-CAPTURE-<token>-START===\\n{json}\\n===PARITY-CAPTURE-<token>-END===``
blocks into the pytest transcript, and the reporter parses those same
blocks back out. Renaming a field on either side (for example
``nodeid`` to ``test_id``) silently drops every capture, the reporter
produces an empty scoreboard, and the only signal is a human re-running
the audit and noticing the doc went blank.

These tests exercise the reporter against **synthetic transcripts** --
no live Cosmos account, no SDK call, no pytest -- so they run in
milliseconds and gate the wire-format contract.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest


_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_REPORTER_PATH = _REPO_ROOT / "scripts" / "v5" / "build_legacy_parity_audit.py"


def _load_reporter():
    """Import the reporter module by file path."""
    mod_name = "_v5_parity_reporter_under_test"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, str(_REPORTER_PATH))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Register before exec_module so dataclasses' annotation resolver
    # can find the module via ``sys.modules.get(cls.__module__)``.
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_block(token: str, **overrides) -> str:
    """Render one ``===PARITY-CAPTURE-<token>-START===...END===`` block."""
    payload = {
        "nodeid": "tests/somefile.py::TestX::test_y",
        "backend": "core-python",
        "surface": "sync",
        "op": "read_item",
        "ordinal": 0,
        "plugin_version": "v2",
        "status": "ok",
        "test_doc": "Verify something.",
        "request": {"args": [], "kwargs": {"item": "id1", "partition_key": "pk1"}},
        "return_value": {"id": "id1", "pk": "pk1", "value": 1},
        "response_headers": {
            "etag": "\"abc\"",
            "x-ms-request-charge": "1.0",
            "x-ms-activity-id": "act-1",
            "x-ms-session-token": "0:0",
            "x-ms-serviceversion": "v=1",
            "x-ms-gatewayversion": "v=1",
            "x-ms-request-duration-ms": "0.1",
            "x-ms-global-committed-lsn": "1",
            "x-ms-number-of-read-regions": "1",
            "x-ms-transport-request-id": "1",
            "lsn": "1",
            "x-ms-resource-quota": "",
            "x-ms-resource-usage": "",
            "x-ms-documentdb-partitionkeyrangeid": "0",
            "x-ms-cosmos-internal-partition-id": "uuid",
            "x-ms-last-state-change-utc": "Mon, 08 Jun 2026 00:00:00 GMT",
            "x-ms-cosmos-llsn": "1",
            "x-ms-cosmos-item-llsn": "1",
            "x-ms-item-lsn": "1",
        },
        "exception": None,
    }
    payload.update(overrides)
    sentinel_start = f"===PARITY-CAPTURE-{token}-START==="
    sentinel_end = f"===PARITY-CAPTURE-{token}-END==="
    return (
        f"some pytest line\n"
        f"{sentinel_start}\n"
        f"{json.dumps(payload)}\n"
        f"{sentinel_end}\n"
        f"more pytest noise\n"
    )


class ReporterParserTests(unittest.TestCase):
    """``parse_captures`` is the contract surface between plugin and reporter."""

    def setUp(self):
        self.reporter = _load_reporter()

    def _write_temp(self, text: str) -> str:
        fh = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        fh.write(text)
        fh.close()
        self.addCleanup(os.unlink, fh.name)
        return fh.name

    def test_parses_v2_tokenised_sentinels(self):
        """v2 sentinels (per-session 8-hex token) must round-trip."""
        path = self._write_temp(_make_block(token="a1b2c3d4"))
        blocks = self.reporter.parse_captures(path)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].nodeid, "tests/somefile.py::TestX::test_y")
        self.assertEqual(blocks[0].plugin_version, "v2")
        self.assertEqual(blocks[0].op, "read_item")
        self.assertEqual(blocks[0].status, "ok")
        self.assertEqual(blocks[0].test_doc, "Verify something.")

    def test_parses_v1_legacy_sentinels(self):
        """Old token-less ``===PARITY-CAPTURE-START===`` blocks still parse."""
        payload = {
            "nodeid": "tests/somefile.py::TestX::test_y",
            "backend": "core-python",
            "surface": "sync",
            "op": "read_item",
            "ordinal": 0,
            "status": "ok",
            "request": {"args": [], "kwargs": {}},
            "return_value": None,
            "response_headers": {},
            "exception": None,
        }
        text = (
            "===PARITY-CAPTURE-START===\n"
            f"{json.dumps(payload)}\n"
            "===PARITY-CAPTURE-END===\n"
        )
        path = self._write_temp(text)
        blocks = self.reporter.parse_captures(path)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].plugin_version, "v1")

    def test_unique_tokens_in_same_transcript_dont_cross_match(self):
        """Two blocks with different tokens must each pair to their OWN end marker."""
        text = _make_block(token="aaaaaaaa") + _make_block(token="bbbbbbbb")
        path = self._write_temp(text)
        blocks = self.reporter.parse_captures(path)
        self.assertEqual(len(blocks), 2)

    def test_collision_string_in_payload_does_not_confuse_parser(self):
        """Bug 6: a literal sentinel string inside a test's stdout must not
        derail the parser. The v2 tokenised sentinels make this safe by
        construction; this test pins the guarantee."""
        # First block uses token "11111111". Then we have a noise line
        # that contains the OLD v1 literal sentinel (which the parser
        # also accepts), followed by garbage and no matching end.
        # The v2 block above should still parse cleanly.
        text = (
            _make_block(token="11111111")
            + "test output: '===PARITY-CAPTURE-START===' was logged here\n"
            + "more output, no end marker for the noise line\n"
        )
        path = self._write_temp(text)
        # The parser should yield the v2 block plus (potentially) try
        # the v1 noise; the v1 noise has no end marker so it's
        # silently skipped by ``_find_next_capture_block``.
        blocks = self.reporter.parse_captures(path)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].nodeid, "tests/somefile.py::TestX::test_y")

    def test_malformed_json_is_skipped_not_fatal(self):
        """A malformed block warns to stderr but the run continues."""
        text = (
            "===PARITY-CAPTURE-deadbeef-START===\n"
            "not json at all {{{\n"
            "===PARITY-CAPTURE-deadbeef-END===\n"
            + _make_block(token="11112222")
        )
        path = self._write_temp(text)
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            blocks = self.reporter.parse_captures(path)
        finally:
            sys.stderr = old_stderr
        # The malformed block is dropped; the good block survives.
        self.assertEqual(len(blocks), 1)

    def test_parse_transcript_disambiguates_same_class_method_by_file(self):
        """Rows with the same class::method in different files must not collide."""
        text = (
            "tests/test_alpha.py::TestDup::test_same PASSED [ 50%]\n"
            "tests/test_beta.py::TestDup::test_same FAILED [100%]\n"
        )
        path = self._write_temp(text)
        rows = self.reporter.parse_transcript(path)
        self.assertEqual(len(rows), 2)
        keys = {(r.file_key, r.class_name, r.method_name, r.outcome) for r in rows}
        self.assertIn(("test_alpha", "TestDup", "test_same", "PASSED"), keys)
        self.assertIn(("test_beta", "TestDup", "test_same", "FAILED"), keys)

    def test_index_captures_disambiguates_same_class_method_by_file(self):
        """Capture indexing must keep file-level separation for duplicate names."""
        text = (
            _make_block(token="11111111", nodeid="tests/test_alpha.py::TestDup::test_same")
            + _make_block(token="22222222", nodeid="tests/test_beta.py::TestDup::test_same")
        )
        path = self._write_temp(text)
        blocks = self.reporter.parse_captures(path)
        idx = self.reporter.index_captures(blocks)
        self.assertEqual(len(idx), 2)
        self.assertIn(("sync", "test_alpha", "TestDup", "test_same"), idx)
        self.assertIn(("sync", "test_beta", "TestDup", "test_same"), idx)


class ReporterVerdictTests(unittest.TestCase):
    """``_build_comparison`` -> ``BackendComparison._verdict`` is the
    other place where a contract change between plugin and helper
    could silently mis-label a row."""

    def setUp(self):
        self.reporter = _load_reporter()

    def _block(self, **overrides):
        text = _make_block(token="cafebabe", **overrides)
        path = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        path.write(text)
        path.close()
        self.addCleanup(os.unlink, path.name)
        return self.reporter.parse_captures(path.name)[0]

    def test_full_parity_when_blocks_match(self):
        """Two identical capture blocks must produce FULL PARITY."""
        cp = self._block(backend="core-python")
        rs = self._block(backend="rust")
        cmp = self.reporter._build_comparison("TestX", "test_y", cp, rs)
        verdict = cmp._verdict()
        self.assertTrue(
            verdict.startswith("FULL PARITY"),
            f"expected FULL PARITY, got: {verdict!r}",
        )

    def test_same_exception_name_does_not_falsely_diverge(self):
        """Two captures that recorded ``ValueError`` on both sides
        must NOT register as EXCEPTION DIVERGENCE. This is the
        bug we fixed by memoising ``_synthesise_exception_class``."""
        exc_payload = {
            "type": "ValueError",
            "message": "bad parameter",
            "status_code": None,
            "sub_status": None,
        }
        cp = self._block(
            backend="core-python",
            status="raised",
            return_value=None,
            exception=exc_payload,
        )
        rs = self._block(
            backend="rust",
            status="raised",
            return_value=None,
            exception=exc_payload,
        )
        cmp = self.reporter._build_comparison("TestX", "test_y", cp, rs)
        verdict = cmp._verdict()
        self.assertTrue(
            verdict.startswith("FULL PARITY"),
            f"expected FULL PARITY for same-named exception on both sides, "
            f"got: {verdict!r}",
        )

    def test_wire_nondeterministic_headers_do_not_fire_header_gap(self):
        """``x-ms-cosmos-quorum-acked-llsn`` is gateway-emitted
        non-deterministically; presence-missing on one side must NOT
        produce a HEADER GAP. This is Bug 2 of the
        principal-engineer review."""
        # Build two captures with the SAME headers except the rust
        # side has the quorum-acked header and the core-python side
        # does not. With the wire-nondeterministic bucket in place,
        # this should still be FULL PARITY (header skipped entirely).
        cp = self._block(backend="core-python")
        rs_headers = dict(cp.response_headers)
        rs_headers["x-ms-cosmos-quorum-acked-llsn"] = "5"
        rs = self._block(backend="rust", response_headers=rs_headers)
        cmp = self.reporter._build_comparison("TestX", "test_y", cp, rs)
        verdict = cmp._verdict()
        self.assertTrue(
            verdict.startswith("FULL PARITY"),
            f"expected FULL PARITY for wire-nondeterministic quorum-acked "
            f"header difference, got: {verdict!r}",
        )


class ReporterRenderingTests(unittest.TestCase):
    """End-to-end smoke: parse synthetic transcripts and render the
    markdown audit doc. Asserts on key strings rather than the full
    output so it's not brittle to whitespace changes."""

    def setUp(self):
        self.reporter = _load_reporter()
        # Pin the helpers import path so the reporter finds the same
        # ``_parity_helpers`` the running test process is using.
        self.reporter._load_parity_helpers()  # noqa: SLF001

    def test_emit_markdown_includes_verdict_categories_and_fallback_labels(self):
        """Bug 5 fix: the 'How to read this report' section must
        list BOTH the four primary verdicts and the fallback labels."""
        # Render a doc against empty transcripts -- enough to fire
        # the static section emitters.
        with tempfile.TemporaryDirectory() as td:
            cp_path = os.path.join(td, "cp.txt")
            rs_path = os.path.join(td, "rs.txt")
            out_path = os.path.join(td, "audit.md")
            for p in (cp_path, rs_path):
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write("")  # empty transcript
            rc = self.reporter.main([
                "--op", "read_item",
                "--corepy", cp_path,
                "--rust", rs_path,
                "--out", out_path,
                "--account-host", "https://test.documents.azure.com/",
            ])
            self.assertEqual(rc, 0)
            with open(out_path, "r", encoding="utf-8") as fh:
                md = fh.read()
        for s in (
            "FULL PARITY",
            "FUNCTIONAL PARITY, HEADER GAP",
            "FUNCTIONAL DIVERGENCE",
            "EXCEPTION DIVERGENCE",
            "RUST REGRESSION",
            "SHARED FAILURE",
            "BOTH SKIPPED",
            "UNPAIRED",
        ):
            self.assertIn(s, md, f"expected {s!r} in audit markdown")


if __name__ == "__main__":
    unittest.main()
