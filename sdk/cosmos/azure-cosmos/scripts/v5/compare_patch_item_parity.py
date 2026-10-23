# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run or verify the reviewed default patch comparison without accepting its failures."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import os

ROOT = Path(__file__).resolve().parents[2]
PROBES = (
    "no_response", "no_response_rejection", "session_token", "etag_current", "etag_stale",
    "invalid_path", "atomic_patch_control", "atomic_patch_rejection",
    "filter_false", "filter_true", "filter_etag_current", "filter_etag_stale",
    "filter_false_etag_current", "filter_false_etag_stale",
    "stale_self", "stale_self_set", "self_only", "self_different_id",
    "response_hook", "if_none_match", "if_none_match_stale", "ten_operations", "eleven_operations",
    "integer_increment_on_integer", "integer_increment_on_fraction",
    "array_add", "array_set", "array_add_then_remove", "array_remove_then_add",
)
EXPECTED_KEYS = {
    (backend, surface, name)
    for backend in ("core-python", "rust")
    for surface in ("sync", "async")
    for name in (
        *PROBES,
        *(("test_patch_item_none_options", "test_patch_operations", "test_conditional_patching")
          if surface == "sync" else ("test_patch_operations_async", "test_conditional_patching_async")),
    )
}
IF_NONE_MATCH = "NotImplementedError: The Rust patch backend does not support If-None-Match."
FRACTION = (
    "CosmosHttpResponseError: (None) 400: type mismatch at '/n': expected integer number, got fractional number\n"
    "Code: None\nMessage: 400: type mismatch at '/n': expected integer number, got fractional number"
)
KNOWN_FAILURES = {
    ("rust", surface, name): ("AssertionError", detail)
    for surface in ("sync", "async")
    for name, detail in (
        ("if_none_match", IF_NONE_MATCH), ("if_none_match_stale", IF_NONE_MATCH),
        ("eleven_operations", "Expected HTTP 400, got NoneType"),
        ("integer_increment_on_fraction", FRACTION),
    )
}
KNOWN_FAILURES[("rust", "sync", "test_patch_item_none_options")] = (
    "TypeError", "pre_trigger_include is not supported by the Rust-backed APIs.",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_evidence(folder):
    """Check completeness and internal consistency, without claiming cryptographic provenance."""
    report = read_json(folder / "report.json")
    execution = read_json(folder / "execution.json")
    require(isinstance(report, dict) and isinstance(execution, dict), "Invalid report or execution object")
    rows = report["cases"]
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), "Invalid case records")
    keys = [(r["backend"], r["surface"], r["case"]) for r in rows]
    require(len(keys) == len(set(keys)), "Duplicate case identities")
    require(set(keys) == EXPECTED_KEYS,
            f"Selection mismatch: missing={sorted(EXPECTED_KEYS - set(keys))}; extra={sorted(set(keys) - EXPECTED_KEYS)}")
    for row in rows:
        require(row["outcome"] in ("PASS", "FAIL"), "Unsupported case outcome")
        if row["outcome"] == "FAIL":
            require(isinstance(row.get("error"), str) and bool(row["error"]), "Missing failure type")
            require(isinstance(row.get("detail"), str), "Missing failure detail")
        else:
            require("error" not in row and "detail" not in row, "PASS row contains failure fields")
    failures = sum(r["outcome"] == "FAIL" for r in rows)
    require(type(execution["exit_code"]) is int and execution["exit_code"] == int(failures > 0),
            "Runner exit does not match recorded outcomes")
    transcript = (folder / "execution.txt").read_text(encoding="utf-8-sig")
    summary = f"TOTAL 126 cases; {failures} failures; 4 verified database deletions"
    require(transcript.splitlines()[-1:] == [summary], "Missing or inconsistent completion summary")
    emitted = []
    for line in transcript.splitlines():
        if line.startswith("{"):
            value = json.loads(line)
            if isinstance(value, dict) and "case" in value:
                emitted.append(value)
    require(emitted == rows, "Transcript case results disagree with report")
    cleanup = report["cleanup"]
    independent = read_json(folder / "independent_cleanup.json")
    for entries in (cleanup, independent):
        require(isinstance(entries, list) and all(isinstance(row, dict) for row in entries), "Invalid cleanup records")
        require(len(entries) == 4, "Expected four database cleanup records")
        ids = [r["database"] for r in entries]
        require(len(set(ids)) == 4, "Duplicate cleanup database")
        require(all(re.fullmatch(r"patch_review_[0-9a-f]{32}", name) for name in ids),
                "Unexpected owned database identity")
        require(all(type(r["status"]) is int and r["status"] == 404 for r in entries),
                "Database cleanup was not confirmed")
    require({r["database"] for r in cleanup} == {r["database"] for r in independent},
            "Independent cleanup checked different databases")
    require(sha256(folder / "runner_snapshot.py") == execution["runner_sha256"], "Runner snapshot hash mismatch")
    require(execution["native_sha256"] == report["extension_sha256"], "Native identity mismatch")
    for field in ("native_sha256", "runner_sha256"):
        require(isinstance(execution[field], str) and re.fullmatch(r"[0-9a-f]{64}", execution[field]),
                f"Invalid {field}")
    require(re.fullmatch(r"[0-9a-f]{40}", execution["source_head"]), "Invalid source revision")
    require(execution["worktree"] in ("clean", "dirty"), "Missing worktree state")
    require(isinstance(execution["python"], str) and bool(execution["python"]), "Missing Python identity")
    started = datetime.fromisoformat(execution["started_utc"])
    ended = datetime.fromisoformat(execution["completed_utc"])
    require(started.utcoffset() is not None and ended.utcoffset() is not None and ended >= started,
            "Invalid execution interval")
    require(isinstance(report["sources"], dict) and
            set(report["sources"]) == {"test_crud.py", "test_crud_async.py", "test_none_options.py"},
            "Unexpected original-source selection")
    for name, digest in report["sources"].items():
        require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), "Invalid original-source hash")
        require((folder / ("copied_" + name)).is_file(), "Missing copied original")
    return report, execution


def compare(baseline, evidence):
    reference, old_execution = load_evidence(baseline)
    actual, new_execution = load_evidence(evidence)
    old = {(r["backend"], r["surface"], r["case"]): r for r in reference["cases"]}
    known = {key: (row["error"], row["detail"]) for key, row in old.items() if row["outcome"] == "FAIL"}
    require(known == KNOWN_FAILURES, "Baseline does not match the reviewed nine failure signatures")
    changes = []
    for row in actual["cases"]:
        key = row["backend"], row["surface"], row["case"]
        previous = old[key]
        if row["outcome"] != previous["outcome"]:
            kind = "REGRESSION" if row["outcome"] == "FAIL" else "IMPROVEMENT_REQUIRES_REVIEW"
        elif row["outcome"] == "FAIL" and (row["error"], row["detail"]) != (previous["error"], previous["detail"]):
            kind = "CHANGED_FAILURE"
        else:
            continue
        changes.append({"identity": list(key), "change": kind, "before": previous, "after": row})
    identity_changes = {}
    for field in ("source_head", "worktree", "python", "native_sha256", "runner_sha256"):
        if old_execution[field] != new_execution[field]:
            identity_changes[field] = {"before": old_execution[field], "after": new_execution[field]}
    if reference["sources"] != actual["sources"]:
        identity_changes["original_sources"] = {"before": reference["sources"], "after": actual["sources"]}
    for name in reference["sources"]:
        old_hash = sha256(baseline / ("copied_" + name))
        new_hash = sha256(evidence / ("copied_" + name))
        if old_hash != new_hash:
            identity_changes["copied_" + name] = {"before": old_hash, "after": new_hash}
    failures = [r for r in actual["cases"] if r["outcome"] == "FAIL"]
    return {
        "strict_parity": "FAIL" if failures else "PASS",
        "baseline_comparison": "CHANGED" if changes else "UNCHANGED",
        "build_identity": "CHANGED" if identity_changes else "UNCHANGED",
        "total_cases": len(actual["cases"]), "failure_count": len(failures),
        "changes": changes, "identity_changes": identity_changes,
        "failures": failures, "runner_exit": new_execution["exit_code"],
        "limits": "Outcome baseline only, not full body/header parity. Historical hashes identify recorded "
                  "builds, not proof that dirty source was compiled. Offline cleanup records are not fresh reads.",
    }


def run_comparison(output):
    """Use the unchanged runner, save its actual exit, then independently check only its owned databases."""
    require(not output.exists(), "Output directory already exists")
    require(bool(os.environ.get("ACCOUNT_HOST")) and bool(os.environ.get("ACCOUNT_KEY")), "Missing account credentials")
    runner = ROOT / "scripts" / "v5" / "run_patch_item_parity.py"
    snapshot = runner.read_bytes()
    sys.path.insert(0, str(ROOT))
    from azure.cosmos import CosmosClient, exceptions, _rust
    native = sha256(Path(_rust.__file__))
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    env = dict(os.environ, PATCH_REVIEW_OUTPUT=str(output))
    env.pop("PATCH_REVIEW_NONE_OPTIONS", None)
    env.pop("PATCH_REVIEW_SUPPLEMENTAL", None)
    started = datetime.now(timezone.utc).isoformat()
    process = subprocess.run([sys.executable, str(runner)], cwd=ROOT, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output.mkdir(parents=True, exist_ok=True)
    (output / "execution.txt").write_bytes(process.stdout)
    (output / "runner_snapshot.py").write_bytes(snapshot)
    (output / "comparison_tool_snapshot.py").write_bytes(Path(__file__).read_bytes())
    (output / "execution.json").write_text(json.dumps({
        "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": process.returncode, "source_head": head, "worktree": "dirty" if dirty else "clean",
        "python": sys.version, "native_sha256": native,
        "runner_sha256": hashlib.sha256(snapshot).hexdigest(),
    }, indent=2) + "\n", encoding="utf-8")
    report = read_json(output / "report.json")
    checked = []
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python") as owner:
        for row in report["cleanup"]:
            require(re.fullmatch(r"patch_review_[0-9a-f]{32}", row["database"]), "Unexpected cleanup target")
            try:
                owner.get_database_client(row["database"]).read()
            except exceptions.CosmosResourceNotFoundError as error:
                require(error.status_code == 404, "Unexpected cleanup status")
                checked.append({"database": row["database"], "status": 404})
            else:
                raise ValueError("Owned database still exists")
    (output / "independent_cleanup.json").write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
    require(runner.read_bytes() == snapshot, "Runner changed during execution")
    require(sha256(Path(_rust.__file__)) == native, "Native binary changed during execution")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path, help="Reviewed default-run evidence directory")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", type=Path, help="Run default comparison into a NEW evidence directory")
    mode.add_argument("--verify", type=Path, help="Verify an existing evidence directory without live requests")
    args = parser.parse_args(argv)
    try:
        baseline = args.baseline.resolve()
        compare(baseline, baseline)
        evidence = (args.run or args.verify).resolve()
        if args.run:
            run_comparison(evidence)
        result = compare(baseline, evidence)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"baseline_comparison": "INVALID", "error": str(error)}))
        return 2
    if args.run:
        (evidence / "baseline_comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["baseline_comparison"] == "UNCHANGED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
