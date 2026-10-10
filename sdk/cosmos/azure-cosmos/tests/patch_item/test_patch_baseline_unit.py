# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""The reviewed failure baseline must not hide changed or incomplete executions."""
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

PATH = Path(__file__).resolve().parents[2] / "scripts" / "v5" / "compare_patch_item_parity.py"
SPEC = importlib.util.spec_from_file_location("patch_baseline", PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def save_run(folder, report, execution):
    folder.mkdir(exist_ok=True)
    write_json(folder / "report.json", report)
    write_json(folder / "execution.json", execution)
    failures = sum(row["outcome"] == "FAIL" for row in report["cases"])
    (folder / "execution.txt").write_text(
        "\n".join(json.dumps(row) for row in report["cases"])
        + f"\nTOTAL 126 cases; {failures} failures; 4 verified database deletions\n",
        encoding="utf-8",
    )
    write_json(folder / "independent_cleanup.json", report["cleanup"])
    (folder / "runner_snapshot.py").write_text("pass\n", encoding="utf-8")
    for filename in report["sources"]:
        (folder / ("copied_" + filename)).write_text("def test_example():\n    pass\n", encoding="utf-8")


@pytest.fixture
def evidence(tmp_path):
    baseline, current = tmp_path / "baseline", tmp_path / "current"
    rows = []
    for key in sorted(VERIFIER.EXPECTED_KEYS):
        row = dict(zip(("backend", "surface", "case"), key), outcome="PASS")
        if key in VERIFIER.KNOWN_FAILURES:
            error, detail = VERIFIER.KNOWN_FAILURES[key]
            row.update(outcome="FAIL", error=error, detail=detail)
        rows.append(row)
    report = {
        "cases": rows, "extension_sha256": "a" * 64,
        "sources": {name: "b" * 64 for name in ("test_crud.py", "test_crud_async.py", "test_none_options.py")},
        "cleanup": [{"database": "patch_review_" + f"{i:032x}", "status": 404} for i in range(4)],
    }
    execution = {
        "exit_code": 1, "native_sha256": "a" * 64, "runner_sha256": "",
        "source_head": "c" * 40, "worktree": "dirty", "python": "controlled",
        "started_utc": "2026-10-10T00:00:00+00:00", "completed_utc": "2026-10-10T00:01:00+00:00",
    }
    save_run(baseline, report, execution)
    execution["runner_sha256"] = VERIFIER.sha256(baseline / "runner_snapshot.py")
    save_run(baseline, report, execution)
    save_run(current, report, execution)
    return baseline, current, copy.deepcopy(report), dict(execution)


def test_unchanged_failures_are_not_parity(evidence):
    baseline, current, _, _ = evidence
    result = VERIFIER.compare(baseline, current)
    assert len(VERIFIER.EXPECTED_KEYS) == result["total_cases"] == 126
    assert result["failure_count"] == 9
    assert result["strict_parity"] == "FAIL"
    assert result["baseline_comparison"] == result["build_identity"] == "UNCHANGED"


@pytest.mark.parametrize("mutation,expected", [
    ("regression", ["REGRESSION"]), ("improvement", ["IMPROVEMENT_REQUIRES_REVIEW"]),
    ("same_count", ["REGRESSION", "IMPROVEMENT_REQUIRES_REVIEW"]),
    ("error_type", ["CHANGED_FAILURE"]), ("error_detail", ["CHANGED_FAILURE"]),
])
def test_outcome_changes_require_review(evidence, mutation, expected):
    baseline, current, report, execution = evidence
    passing = next(r for r in report["cases"] if r["outcome"] == "PASS")
    failing = next(r for r in report["cases"] if r["outcome"] == "FAIL")
    if mutation in ("regression", "same_count"):
        passing.update(outcome="FAIL", error="AssertionError", detail="new bug")
    if mutation in ("improvement", "same_count"):
        failing["outcome"] = "PASS"
        del failing["error"], failing["detail"]
    if mutation == "error_type":
        failing["error"] = "ValueError"
    if mutation == "error_detail":
        failing["detail"] += " changed"
    save_run(current, report, execution)
    result = VERIFIER.compare(baseline, current)
    assert result["baseline_comparison"] == "CHANGED"
    assert sorted(row["change"] for row in result["changes"]) == sorted(expected)
    if mutation == "same_count":
        assert result["failure_count"] == 9


@pytest.mark.parametrize("mutation", [
    "missing", "duplicate", "extra", "skip", "error_absent", "detail_absent", "pass_error",
    "exit", "summary", "transcript", "cleanup_missing", "cleanup_duplicate", "cleanup_status",
    "cleanup_target", "independent_different", "independent_missing", "snapshot", "native",
    "source_missing", "source_hash", "copy_missing", "time", "timezone", "python", "head",
])
def test_incomplete_or_inconsistent_evidence_is_invalid(evidence, mutation):
    baseline, current, report, execution = evidence
    failing = next(r for r in report["cases"] if r["outcome"] == "FAIL")
    if mutation == "missing":
        report["cases"].pop()
    elif mutation == "duplicate":
        report["cases"].append(copy.deepcopy(report["cases"][0]))
    elif mutation == "extra":
        report["cases"].append({"backend": "rust", "surface": "sync", "case": "unknown", "outcome": "PASS"})
    elif mutation == "skip":
        report["cases"][0]["outcome"] = "SKIP"
    elif mutation == "error_absent":
        del failing["error"]
    elif mutation == "detail_absent":
        del failing["detail"]
    elif mutation == "pass_error":
        next(r for r in report["cases"] if r["outcome"] == "PASS")["error"] = "hidden"
    elif mutation == "exit":
        execution["exit_code"] = 0
    elif mutation == "cleanup_missing":
        report["cleanup"].pop()
    elif mutation == "cleanup_duplicate":
        report["cleanup"][1] = report["cleanup"][0]
    elif mutation == "cleanup_status":
        report["cleanup"][0]["status"] = 503
    elif mutation == "cleanup_target":
        report["cleanup"][0]["database"] = "not_owned"
    elif mutation == "native":
        report["extension_sha256"] = "d" * 64
    elif mutation == "source_missing":
        del report["sources"]["test_crud.py"]
    elif mutation == "source_hash":
        report["sources"]["test_crud.py"] = ""
    elif mutation == "time":
        execution["completed_utc"] = "2025-01-01T00:00:00+00:00"
    elif mutation == "timezone":
        execution["started_utc"] = "2026-10-10T00:00:00"
    elif mutation == "python":
        execution["python"] = ""
    elif mutation == "head":
        execution["source_head"] = "missing"
    save_run(current, report, execution)
    if mutation == "summary":
        with (current / "execution.txt").open("a", encoding="utf-8") as stream:
            stream.write("interrupted\n")
    elif mutation == "transcript":
        text = (current / "execution.txt").read_text(encoding="utf-8")
        (current / "execution.txt").write_text(text.replace('"outcome": "PASS"', '"outcome": "FAIL"', 1), encoding="utf-8")
    elif mutation == "independent_different":
        independent = copy.deepcopy(report["cleanup"])
        independent[0]["database"] = "patch_review_" + "f" * 32
        write_json(current / "independent_cleanup.json", independent)
    elif mutation == "independent_missing":
        (current / "independent_cleanup.json").unlink()
    elif mutation == "snapshot":
        (current / "runner_snapshot.py").write_text("changed\n", encoding="utf-8")
    elif mutation == "copy_missing":
        (current / "copied_test_crud.py").unlink()
    with pytest.raises((ValueError, OSError)):
        VERIFIER.compare(baseline, current)


@pytest.mark.parametrize("field", ["native_sha256", "source_head", "python", "original_sources", "copied_source"])
def test_identity_change_is_separate_from_outcome(evidence, field):
    baseline, current, report, execution = evidence
    if field == "original_sources":
        report["sources"]["test_crud.py"] = "e" * 64
    elif field == "native_sha256":
        report["extension_sha256"] = execution[field] = "e" * 64
    elif field == "source_head":
        execution[field] = "e" * 40
    elif field == "python":
        execution[field] = "different interpreter"
    save_run(current, report, execution)
    if field == "copied_source":
        (current / "copied_test_crud.py").write_text("different\n", encoding="utf-8")
    result = VERIFIER.compare(baseline, current)
    assert result["baseline_comparison"] == "UNCHANGED"
    assert result["strict_parity"] == "FAIL"
    assert result["build_identity"] == "CHANGED"


def test_baseline_cannot_silently_accept_another_failure(evidence):
    baseline, current, report, execution = evidence
    next(r for r in report["cases"] if r["outcome"] == "FAIL")["detail"] = "different baseline"
    save_run(baseline, report, execution)
    with pytest.raises(ValueError, match="reviewed nine"):
        VERIFIER.compare(baseline, current)


def test_verify_cli_never_runs_live(evidence, monkeypatch, capsys):
    baseline, current, _, _ = evidence
    monkeypatch.setattr(VERIFIER, "run_comparison", lambda *_: pytest.fail("unexpected live run"))
    assert VERIFIER.main(["--baseline", str(baseline), "--verify", str(current)]) == 0
    assert json.loads(capsys.readouterr().out)["strict_parity"] == "FAIL"
    (current / "report.json").write_text("{", encoding="utf-8")
    assert VERIFIER.main(["--baseline", str(baseline), "--verify", str(current)]) == 2
    assert json.loads(capsys.readouterr().out)["baseline_comparison"] == "INVALID"


def test_live_run_refuses_existing_directory(evidence):
    _, current, _, _ = evidence
    with pytest.raises(ValueError, match="already exists"):
        VERIFIER.run_comparison(current)


def test_all_improvements_still_require_baseline_review(evidence, capsys):
    baseline, current, report, execution = evidence
    for row in report["cases"]:
        row["outcome"] = "PASS"
        row.pop("error", None)
        row.pop("detail", None)
    execution["exit_code"] = 0
    save_run(current, report, execution)
    assert VERIFIER.main(["--baseline", str(baseline), "--verify", str(current)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["strict_parity"] == "PASS"
    assert len(result["changes"]) == 9


@pytest.mark.parametrize("filename,value", [
    ("report.json", []), ("execution.json", []), ("independent_cleanup.json", {}),
])
def test_malformed_objects_are_invalid(evidence, filename, value, capsys):
    baseline, current, _, _ = evidence
    write_json(current / filename, value)
    assert VERIFIER.main(["--baseline", str(baseline), "--verify", str(current)]) == 2
    assert json.loads(capsys.readouterr().out)["baseline_comparison"] == "INVALID"


@pytest.mark.parametrize("complete", [True, False])
def test_live_wrapper_preserves_actual_execution(evidence, monkeypatch, complete):
    baseline, current, report, execution = evidence
    root = current.parent / "package"
    runner = root / "scripts" / "v5" / "run_patch_item_parity.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("pass\n", encoding="utf-8")
    native = root / "controlled.pyd"
    native.write_bytes(b"controlled")
    report["extension_sha256"] = VERIFIER.sha256(native)
    output = current.parent / "live"
    monkeypatch.setattr(VERIFIER, "ROOT", root)
    monkeypatch.setenv("ACCOUNT_HOST", "https://unused.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    monkeypatch.setenv("PATCH_REVIEW_SUPPLEMENTAL", "1")
    monkeypatch.setenv("PATCH_REVIEW_NONE_OPTIONS", "1")
    check_output = MagicMock(side_effect=["c" * 40 + "\n", "dirty"])
    monkeypatch.setattr(VERIFIER.subprocess, "check_output", check_output)

    class NotFound(Exception):
        status_code = 404

    client = MagicMock()
    owner = client.return_value.__enter__.return_value
    owner.get_database_client.return_value.read.side_effect = NotFound()
    monkeypatch.setitem(VERIFIER.sys.modules, "azure.cosmos", SimpleNamespace(
        CosmosClient=client, exceptions=SimpleNamespace(CosmosResourceNotFoundError=NotFound),
        _rust=SimpleNamespace(__file__=str(native)),
    ))

    def execute(command, **kwargs):
        assert command == [VERIFIER.sys.executable, str(runner)]
        assert kwargs["cwd"] == root
        assert kwargs["env"]["PATCH_REVIEW_OUTPUT"] == str(output)
        assert "PATCH_REVIEW_SUPPLEMENTAL" not in kwargs["env"]
        assert "PATCH_REVIEW_NONE_OPTIONS" not in kwargs["env"]
        if not complete:
            return SimpleNamespace(returncode=7, stdout=b"setup failed\n")
        save_run(output, report, execution)
        return SimpleNamespace(returncode=1, stdout=(output / "execution.txt").read_bytes())

    monkeypatch.setattr(VERIFIER.subprocess, "run", execute)
    if complete:
        VERIFIER.run_comparison(output)
        loaded, metadata = VERIFIER.load_evidence(output)
        assert len(loaded["cases"]) == 126
        assert metadata["exit_code"] == 1
        assert metadata["native_sha256"] == VERIFIER.sha256(native)
        assert [c.args[0] for c in owner.get_database_client.call_args_list] == [
            r["database"] for r in report["cleanup"]
        ]
    else:
        with pytest.raises(FileNotFoundError):
            VERIFIER.run_comparison(output)
        assert (output / "execution.txt").read_bytes() == b"setup failed\n"
        assert VERIFIER.read_json(output / "execution.json")["exit_code"] == 7
        client.assert_not_called()
    assert (output / "comparison_tool_snapshot.py").read_bytes() == PATH.read_bytes()
