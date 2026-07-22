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
        "plugin_version": "v3",
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
    if "executed_engine" not in overrides:
        payload["executed_engine"] = payload["backend"]
    if "rust_operation_delta" not in overrides:
        payload["rust_operation_delta"] = 1 if payload["backend"] == "rust" else 0
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
        path = self._write_temp(
            _make_block(token="a1b2c3d4", plugin_version="v2")
        )
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

    def test_unmatched_start_does_not_hide_later_valid_capture(self):
        """A truncated early block must not stop parsing the rest of the file."""
        text = (
            "===PARITY-CAPTURE-deadbeef-START===\n"
            "truncated payload\n"
            + _make_block(token="11112222")
        )
        path = self._write_temp(text)
        blocks = self.reporter.parse_captures(path)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].nodeid, "tests/somefile.py::TestX::test_y")

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

    def _block(self, **overrides):
        text = _make_block(token="feedface", **overrides)
        path = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        path.write(text)
        path.close()
        self.addCleanup(os.unlink, path.name)
        return self.reporter.parse_captures(path.name)[0]

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
                "--expected-count", "1",
                "--account-host", "https://test.documents.azure.com/",
            ])
            self.assertEqual(rc, 1)
            with open(out_path, "r", encoding="utf-8") as fh:
                md = fh.read()
        self.assertIn("INVALID OR INCOMPLETE INPUT", md)
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

    def test_main_returns_zero_only_for_valid_matching_evidence(self):
        """A complete v3 core/Rust pair with matching calls is a successful check."""
        with tempfile.TemporaryDirectory() as td:
            cp_path = os.path.join(td, "cp.txt")
            rs_path = os.path.join(td, "rs.txt")
            out_path = os.path.join(td, "audit.md")
            result_line = (
                "tests/somefile.py::TestX::test_y PASSED [100%]\n"
            )
            with open(cp_path, "w", encoding="utf-8") as fh:
                fh.write(
                    result_line
                    + _make_block("11111111", backend="core-python")
                    + "================ 1 passed in 0.10s ================\n"
                )
            with open(rs_path, "w", encoding="utf-8") as fh:
                fh.write(
                    result_line
                    + _make_block("22222222", backend="rust")
                    + "================ 1 passed in 0.10s ================\n"
                )

            rc = self.reporter.main([
                "--op", "read_item",
                "--corepy", cp_path,
                "--rust", rs_path,
                "--out", out_path,
                "--expected-count", "1",
            ])

            self.assertEqual(rc, 0)

    def test_main_returns_nonzero_for_functional_difference(self):
        """A response difference must produce a failing process exit code."""
        with tempfile.TemporaryDirectory() as td:
            cp_path = os.path.join(td, "cp.txt")
            rs_path = os.path.join(td, "rs.txt")
            out_path = os.path.join(td, "audit.md")
            result_line = (
                "tests/somefile.py::TestX::test_y PASSED [100%]\n"
            )
            with open(cp_path, "w", encoding="utf-8") as fh:
                fh.write(
                    result_line
                    + _make_block(
                        "11111111",
                        backend="core-python",
                        return_value={"value": 1},
                    )
                    + "================ 1 passed in 0.10s ================\n"
                )
            with open(rs_path, "w", encoding="utf-8") as fh:
                fh.write(
                    result_line
                    + _make_block(
                        "22222222", backend="rust", return_value={"value": 2}
                    )
                    + "================ 1 passed in 0.10s ================\n"
                )

            rc = self.reporter.main([
                "--op", "read_item",
                "--corepy", cp_path,
                "--rust", rs_path,
                "--out", out_path,
                "--expected-count", "1",
            ])

            self.assertEqual(rc, 1)

    def test_second_call_divergence_controls_scoreboard_verdict(self):
        """A multi-call test must not be labelled from only its first call."""
        cp_first = self.reporter.CaptureBlock(
            nodeid="tests/test_x.py::TestX::test_y",
            backend="core-python",
            surface="sync",
            op="read_item",
            ordinal=0,
            status="ok",
            return_value={"value": 1},
        )
        rs_first = self.reporter.CaptureBlock(
            nodeid="tests/test_x.py::TestX::test_y",
            backend="rust",
            surface="sync",
            op="read_item",
            ordinal=0,
            status="ok",
            return_value={"value": 1},
        )
        cp_second = self.reporter.CaptureBlock(
            nodeid="tests/test_x.py::TestX::test_y",
            backend="core-python",
            surface="sync",
            op="read_item",
            ordinal=1,
            status="ok",
            return_value={"value": 2},
        )
        rs_second = self.reporter.CaptureBlock(
            nodeid="tests/test_x.py::TestX::test_y",
            backend="rust",
            surface="sync",
            op="read_item",
            ordinal=1,
            status="ok",
            return_value={"value": 999},
        )
        result = self.reporter.TestResult(
            surface="sync",
            file_key="test_x",
            class_name="TestX",
            method_name="test_y",
            outcome="PASSED",
            raw_path="tests/test_x.py",
        )
        key = ("sync", "test_x", "TestX", "test_y")
        md = self.reporter.emit_markdown(
            op="read_item",
            pairs=[(result, result)],
            corepy_path="core.txt",
            rust_path="rust.txt",
            account_host="https://example",
            corepy_captures={key: [cp_first, cp_second]},
            rust_captures={key: [rs_first, rs_second]},
        )
        scoreboard = md.split("## Per-test PARITY CALL blocks", 1)[0]
        self.assertIn("**FUNCTIONAL DIVERGENCE**", scoreboard)

    def test_failed_pytest_outcome_cannot_be_overridden_by_matching_capture(self):
        """A Rust test failure must remain a regression even if its SDK call matched."""
        cp = self.reporter.TestResult(
            "sync", "test_x", "TestX", "test_y", "PASSED", "tests/test_x.py"
        )
        rs = self.reporter.TestResult(
            "sync", "test_x", "TestX", "test_y", "FAILED", "tests/test_x.py"
        )
        cp_block = self.reporter.CaptureBlock(
            nodeid="tests/test_x.py::TestX::test_y",
            backend="core-python",
            surface="sync",
            op="read_item",
            ordinal=0,
            status="ok",
            return_value={"value": 1},
        )
        rs_block = self.reporter.CaptureBlock(
            nodeid="tests/test_x.py::TestX::test_y",
            backend="rust",
            surface="sync",
            op="read_item",
            ordinal=0,
            status="ok",
            return_value={"value": 1},
        )
        key = ("sync", "test_x", "TestX", "test_y")
        md = self.reporter.emit_markdown(
            op="read_item",
            pairs=[(cp, rs)],
            corepy_path="core.txt",
            rust_path="rust.txt",
            account_host="https://example",
            corepy_captures={key: [cp_block]},
            rust_captures={key: [rs_block]},
        )
        scoreboard = md.split("## Per-test PARITY CALL blocks", 1)[0]
        self.assertIn("**RUST REGRESSION**", scoreboard)

    def test_request_difference_is_a_functional_difference(self):
        """Missing or differently typed operation arguments must be compared."""
        cp = self._block(
            backend="core-python",
            request={"args": [], "kwargs": {"partition_key": "pk"}},
        )
        rs = self._block(
            backend="rust",
            request={"args": [], "kwargs": {}},
        )
        comparison = self.reporter._build_comparison(
            "TestX", "test_y", cp, rs
        )
        self.assertTrue(
            any(diff.startswith("request:") for diff in comparison.diffs)
        )

    def test_request_scalar_difference_is_not_hidden(self):
        """Different item ids or partition keys must not normalize to the same type."""
        cp = self._block(
            backend="core-python",
            request={"args": [], "kwargs": {"item": "alpha"}},
        )
        rs = self._block(
            backend="rust",
            request={"args": [], "kwargs": {"item": "bravo"}},
        )
        comparison = self.reporter._build_comparison(
            "TestX", "test_y", cp, rs
        )
        self.assertTrue(
            any(diff.startswith("request:") for diff in comparison.diffs)
        )

    def test_embedded_generated_uuid_is_normalized(self):
        """Independent resource UUIDs must not create false request or proxy diffs."""
        cp_id = "responses_test11111111-1111-1111-1111-111111111111"
        rs_id = "responses_test22222222-2222-2222-2222-222222222222"
        cp = self._block(
            backend="core-python",
            request={"args": [], "kwargs": {"id": cp_id}},
            return_value="<DatabaseProxy [dbs/{}]>".format(cp_id),
        )
        rs = self._block(
            backend="rust",
            request={"args": [], "kwargs": {"id": rs_id}},
            return_value="<DatabaseProxy [dbs/{}]>".format(rs_id),
        )

        comparison = self.reporter._build_comparison(
            "TestX", "test_y", cp, rs
        )

        self.assertFalse(
            any(
                diff.startswith(("request:", "return_value:"))
                for diff in comparison.diffs
            )
        )

    def test_validation_rejects_wrong_backend_label(self):
        """A rust-vs-rust transcript pair must never be accepted as parity."""
        result = self.reporter.TestResult(
            "sync", "somefile", "TestX", "test_y", "PASSED", "tests/somefile.py"
        )
        cp = self._block(backend="rust")
        rs = self._block(backend="rust")
        errors = self.reporter._validate_audit_inputs(
            op="read_item",
            corepy=[result],
            rust=[result],
            corepy_blocks=[cp],
            rust_blocks=[rs],
        )
        self.assertTrue(any("core-python transcript captured backend" in e for e in errors))

    def test_validation_rejects_rust_selected_call_that_fell_back(self):
        """A Rust client running the legacy engine is not Rust execution evidence."""
        result = self.reporter.TestResult(
            "sync", "somefile", "TestX", "test_y", "PASSED", "tests/somefile.py"
        )
        cp = self._block(backend="core-python")
        rs = self._block(
            backend="rust",
            executed_engine="core-python",
            rust_operation_delta=0,
        )
        errors = self.reporter._validate_audit_inputs(
            op="read_item",
            corepy=[result],
            rust=[result],
            corepy_blocks=[cp],
            rust_blocks=[rs],
        )
        self.assertTrue(any("actually executed 'core-python'" in e for e in errors))

    def test_validation_rejects_unmaterialized_query_capture(self):
        """A pager repr is not evidence that query iteration matched."""
        result = self.reporter.TestResult(
            "sync", "somefile", "TestX", "test_y", "PASSED", "tests/somefile.py"
        )
        cp = self._block(
            backend="core-python",
            op="query_items",
            return_value="<azure.core.paging.ItemPaged object>",
        )
        rs = self._block(
            backend="rust",
            op="query_items",
            return_value="<azure.core.paging.ItemPaged object>",
        )
        errors = self.reporter._validate_audit_inputs(
            op="query_items",
            corepy=[result],
            rust=[result],
            corepy_blocks=[cp],
            rust_blocks=[rs],
        )
        self.assertTrue(any("lazy pager object" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
