"""Version-2 production boundary tests; no network writes or package execution."""

# cspell:ignore mcpscripts

import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import urllib.request

from test_mgmt_sdk_review_comment import (
    HEAD,
    NEW_SPEC,
    PACKAGE,
    REPO,
    SCRIPT,
    SOURCE,
    TOOLING,
    WORKFLOW,
    add_entry,
    context,
    envelope,
    lock_json,
    production_fixture,
    review,
)
import mgmt_sdk_review_contract as contract
import mgmt_sdk_review_context as collector
import mgmt_sdk_review_evidence as evidence
import mgmt_sdk_review_service as service

RULES = WORKFLOW.parents[1] / "copilot-instructions.md"
RULE_TEXT = (
    "## MGMT SDK Code Review Rules"
    + RULES.read_text(encoding="utf-8").split("## MGMT SDK Code Review Rules", 1)[1].split("\n## ", 1)[0]
)


def fixture():
    data, trusted = production_fixture()
    data.pop("preflight")
    data.pop("registrations")
    trusted["mgmtSdkCodeReviewRules"] = RULE_TEXT.strip()
    trusted["sources"].extend(
        [
            record("azure/mgmt/example/_version.py", 'VERSION = "1.0.0b1"\n'),
            record("CHANGELOG.md", "## 1.0.0b1 (2026-09-28)\n\n### Other Changes\n- Initial version.\n"),
            record("_metadata.json", '{"apiVersion": "2026-09-01-preview"}\n'),
            record(
                "pyproject.toml",
                ('[project]\nclassifiers = ["Development Status :: 4 - Beta"]\n' "[packaging]\nis_stable = false\n"),
            ),
        ]
    )
    trusted["deterministicChecks"][PACKAGE] = dict(
        zip(("checks", "findings"), evidence.deterministic_checks(trusted, PACKAGE))
    )
    return data, trusted


def record(path, content, status="available"):
    return evidence.source_record(
        REPO,
        {"path": PACKAGE + "/" + path, "revision": HEAD, "status": status, "content": content, "error": ""},
        PACKAGE,
    )


def reference(record, start=1, end=1, reason=""):
    return {"source_id": record["id"], "start_line": start, "end_line": end, "reason": reason}


def submit(data, trusted):
    result = service.ReviewService(trusted).call({"operation": "preflight", "draft": data})
    if not result["ok"]:
        raise AssertionError(result)
    return envelope(result["submission"]["data"])


class EvidenceAndChecksTests(unittest.TestCase):
    def test_source_collection_issues_preserve_checks_and_force_partial(self):
        draft, trusted = fixture()
        for issue in (
            f"{PACKAGE}: source discovery exceeded the 16-file package limit.",
            f"{PACKAGE}/pyproject.toml cannot identify version data: invalid TOML.",
        ):
            with self.subTest(issue=issue):
                trusted["sourceCollectionIssues"] = [issue]
                result = contract.preflight(draft, trusted)
                self.assertTrue(result["ok"], result)
                self.assertEqual("partial", result["reviewCompleteness"])
                body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
                self.assertIn(issue, body)
                self.assertIn("Source collection", body)
                self.assertIn("Version consistency", body)
                self.assertIn("README snippets", body)
                self.assertNotIn("**Unverified checks:** None.", body)
        trusted["sourceCollectionIssues"] = [f"{PACKAGE}-other: source discovery exceeded the limit."]
        result = contract.preflight(draft, trusted)
        self.assertEqual("complete", result["reviewCompleteness"])
        self.assertNotIn(
            "Source collection", contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        )

    def test_checks_and_findings_reject_historical_sdk_evidence(self):
        for revision in ("a" * 40, "c" * 40, "9" * 40):
            for location in ("check", "finding"):
                with self.subTest(revision=revision, location=location):
                    draft, trusted = fixture()
                    trusted["breakingChangeContext"][0]["releaseBaseline"]["revision"] = "9" * 40
                    stale = evidence.source_record(
                        REPO,
                        {
                            "path": PACKAGE + "/pyproject.toml",
                            "revision": revision,
                            "status": "available",
                            "content": '[packaging]\ntitle = "HistoricalClient"\n',
                        },
                        PACKAGE,
                    )
                    trusted["sources"].append(stale)
                    if location == "check":
                        draft["packages"][0]["checks"]["Client name consistency"]["sources"] = [reference(stale)]
                    else:
                        draft["packages"][0]["findings"] = [
                            {
                                "check": "Client name consistency",
                                "severity": "Blocking",
                                "title": "Client names differ",
                                "observation": "The packaging title differs from the client name.",
                                "remediation": "Align the packaging title and client name.",
                                "sources": [reference(stale)],
                            }
                        ]
                    errors = contract.preflight(draft, trusted)["errors"]
                    self.assertIn("wrong_revision", {item["code"] for item in errors})
                    with self.assertRaisesRegex(contract.ReviewError, "wrong_revision"):
                        contract.validate_sources(
                            [evidence.citation(stale, 1, 2)],
                            "test.sources",
                            trusted,
                            trusted["breakingChangeContext"][0],
                            PACKAGE,
                            check="Client name consistency",
                        )
                    # Even a forged success-shaped receipt cannot bypass independent publication validation.
                    data = {**draft, "registrations": []}
                    data["preflight"] = {"attempt": 1, "digest": contract.digest(data)}
                    with self.assertRaisesRegex(contract.ReviewError, "wrong_revision"):
                        contract.prepare_output(envelope(data), trusted)

    def test_attribution_retains_historical_sdk_context(self):
        old, trusted = review(), context()
        add_entry(old, trusted)
        final, trusted = production_fixture(old, trusted)
        draft = {key: value for key, value in final.items() if key not in {"preflight", "registrations"}}
        for revision in (trusted["firstRevision"], trusted["mergeBaseRevision"], "9" * 40):
            trusted["breakingChangeContext"][0]["releaseBaseline"]["revision"] = "9" * 40
            historical = evidence.source_record(
                REPO,
                {
                    "path": PACKAGE + "/pyproject.toml",
                    "revision": revision,
                    "status": "available",
                    "content": '[packaging]\ntitle = "HistoricalClient"\n',
                },
                PACKAGE,
            )
            trusted["sources"].append(historical)
            draft["packages"][0]["attribution"][0]["sdk_context"] = [reference(historical)]
            body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
            self.assertIn(revision, body)
            self.assertIn("Human review", body)

    def test_collector_discovers_clients_from_data_and_bounds_snapshot(self):
        _, trusted = fixture()
        trusted["changedFiles"] = []
        trusted["collectionLimits"] = {}
        client = collector.GitHubClient(REPO, "test")
        path = PACKAGE + "/pyproject.toml"
        client.files[(path, HEAD)] = {
            "path": path,
            "revision": HEAD,
            "status": "available",
            "content": '[tool.setuptools.dynamic.version]\nattr = "azure.mgmt.example._version.VERSION"\n',
        }
        with mock.patch.object(
            client,
            "_read_file",
            side_effect=lambda path, revision: {
                "path": path,
                "revision": revision,
                "status": "missing",
                "error": "Pinned file returned HTTP 404.",
            },
        ):
            collector.collect_review_sources(client, trusted)
        collected = {item["path"] for item in trusted["sources"]}
        for suffix in (
            "azure/mgmt/example/_version.py",
            "azure/mgmt/example/_client.py",
            "azure/mgmt/example/aio/_client.py",
        ):
            self.assertIn(PACKAGE + "/" + suffix, collected)
        self.assertFalse(trusted["sourceCollectionIssues"])
        with mock.patch.object(collector, "MAX_SNAPSHOT_BYTES", 1):
            collector.collect_review_sources(client, trusted)
        project = next(item for item in trusted["sources"] if item["path"] == path)
        self.assertEqual("truncated", project["status"])
        self.assertEqual("", project["content"])
        self.assertEqual(0, project["lineCount"])

    def test_rules_policy_fingerprint_matches_authoritative_rules(self):
        self.assertEqual(evidence.RULES_SHA256, hashlib.sha256(RULE_TEXT.strip().encode()).hexdigest())
        self.assertEqual(tuple(contract.CHECKS), evidence.CHECKS)
        self.assertEqual(
            set(contract.DRAFT_SCHEMA["properties"]["packages"]["items"]["properties"]["checks"]["properties"]),
            set(evidence.SEMANTIC_CHECKS),
        )

    def initial_client_fixture(self, synchronous="ExampleMgmtClient", asynchronous="ExampleMgmtClient"):
        draft, trusted = fixture()
        trusted["breakingChangeContext"][0]["releaseBaseline"] = {
            "status": "not_applicable",
            "reason": "Initial release independently confirmed.",
        }
        for path, name in (
            ("azure/mgmt/example/_client.py", synchronous),
            ("azure/mgmt/example/aio/_client.py", asynchronous),
        ):
            trusted["sources"].append(record(path, f"class {name}:\n    pass\n"))
        return draft, trusted

    def test_initial_client_names_accept_exact_suffix(self):
        for name in ("ExampleMgmtClient", "MgmtClient"):
            with self.subTest(name=name):
                draft, trusted = self.initial_client_fixture(name, name)
                checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
                check = next(item for item in checks if item["name"] == "Initial client name")
                self.assertEqual("completed", check["outcome"])
                self.assertEqual(2, len(check["sources"]))
                self.assertFalse(findings)
                body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
                self.assertIn("Initial client name", body)
                self.assertIn("**Findings:** None.", body)
                self.assertIn("Review completeness: complete", body)

    def test_initial_client_names_block_in_both_sync_and_async_clients(self):
        for name in ("ExampleManagementClient", "ExampleClient", "ExampleMgmtClientExtra", "ExampleMgmtClient".lower()):
            for kind in ("synchronous", "asynchronous"):
                with self.subTest(name=name, kind=kind):
                    draft, trusted = self.initial_client_fixture(**{kind: name})
                    _, findings = evidence.deterministic_checks(trusted, PACKAGE)
                    self.assertEqual(1, len(findings))
                    self.assertEqual("Initial client name", findings[0]["check"])
                    self.assertEqual("Blocking", findings[0]["severity"])
                    self.assertIn(name, findings[0]["observation"])
                    self.assertIn("client.tsp", findings[0]["remediation"])
                    self.assertIn("MgmtClient", findings[0]["remediation"])
                    self.assertIn("regenerate", findings[0]["remediation"])
                    self.assertEqual([], draft["packages"][0]["findings"])
                    # Independent publication derives the blocker even when the model submits no findings.
                    body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
                    self.assertIn("Blocking", body)
                    self.assertIn(name, body)
                    self.assertIn("client.tsp", body)

    def test_initial_naming_does_not_force_renames_for_existing_or_ambiguous_releases(self):
        for status, expected in (("available", "not_applicable"), ("unverified", "unverified")):
            with self.subTest(status=status):
                draft, trusted = self.initial_client_fixture("OldManagementClient", "OldManagementClient")
                trusted["breakingChangeContext"][0]["releaseBaseline"] = {
                    "status": status,
                    "revision": "c" * 40,
                    "error": "Historical package evidence unavailable.",
                }
                checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
                check = next(item for item in checks if item["name"] == "Initial client name")
                self.assertEqual(expected, check["outcome"])
                self.assertFalse(findings)
                self.assertTrue(check["reason"])
                if status == "available":
                    body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
                    self.assertIn("Initial client name ` (not applicable:", body)
                    self.assertNotIn("client.tsp", body)

    def test_initial_client_name_requires_readable_unambiguous_current_evidence(self):
        for mutation in ("missing", "truncated", "access_error", "historical", "syntax", "multiple", "absent"):
            with self.subTest(mutation=mutation):
                draft, trusted = self.initial_client_fixture()
                client = next(item for item in trusted["sources"] if item["path"].endswith("example/_client.py"))
                if mutation in ("missing", "truncated", "access_error"):
                    client["status"] = mutation
                elif mutation == "historical":
                    client["revision"] = trusted["firstRevision"]
                elif mutation == "syntax":
                    client["content"] = "class InvalidSyntax(:\n"
                elif mutation == "multiple":
                    client["content"] = "class OneMgmtClient: pass\nclass TwoMgmtClient: pass\n"
                else:
                    client["content"] = "from somewhere import Client\n"
                checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
                check = next(item for item in checks if item["name"] == "Initial client name")
                self.assertEqual("unverified", check["outcome"])
                self.assertFalse(findings)
                self.assertTrue(check["reason"])
                body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
                self.assertIn("Review completeness: partial", body)

    def test_optional_async_client_absence_differs_from_access_failure(self):
        _, trusted = self.initial_client_fixture()
        client = next(item for item in trusted["sources"] if item["path"].endswith("aio/_client.py"))
        for status, expected in (("missing", "completed"), ("access_error", "unverified")):
            client["status"] = status
            checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
            check = next(item for item in checks if item["name"] == "Initial client name")
            self.assertEqual(expected, check["outcome"])
            self.assertFalse(findings)

    def test_initial_client_ast_check_never_executes_package_code(self):
        _, trusted = self.initial_client_fixture()
        client = next(item for item in trusted["sources"] if item["path"].endswith("example/_client.py"))
        client["content"] = 'raise RuntimeError("must not execute")\nclass ExampleMgmtClient:\n    pass\n'
        checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
        check = next(item for item in checks if item["name"] == "Initial client name")
        self.assertEqual("completed", check["outcome"])
        self.assertTrue(check["sources"][0]["url"].endswith("#L2"))
        self.assertFalse(findings)

    def test_no_findings_and_partial_are_distinct(self):
        draft, trusted = fixture()
        output = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertIn("Review completeness: complete", output)
        self.assertIn("**Findings:** None.", output)
        draft["packages"][0]["checks"]["README snippets"].update(
            outcome="unverified", reason="README sample requires unavailable operation documentation.", sources=[]
        )
        output = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertIn("Review completeness: partial", output)
        self.assertIn("Version consistency", output)
        self.assertIn("Client signature", output)

    def test_rule_change_fails_visible_not_stale_clean(self):
        draft, trusted = fixture()
        trusted["mgmtSdkCodeReviewRules"] += "\nNew requirement."
        checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
        self.assertFalse(findings)
        self.assertEqual(["unverified"] * len(evidence.AUTOMATIC_CHECKS), [item["outcome"] for item in checks])
        self.assertIn("rules changed", checks[0]["reason"])
        self.assertIn("partial", contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"])

    def test_version_preview_and_stability_violations(self):
        _, trusted = fixture()
        version = next(item for item in trusted["sources"] if item["path"].endswith("_version.py"))
        version["content"] = 'VERSION = "1.0.0"\n'
        checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
        self.assertEqual(
            {"Version consistency", "Preview version", "Stability flags"}, {item["check"] for item in findings}
        )
        self.assertEqual(["completed"] * 4 + ["not_applicable"], [item["outcome"] for item in checks])
        self.assertTrue(all(item["severity"] == "Blocking" for item in findings))

    def test_calendar_boundary_and_malformed_latest_heading(self):
        _, trusted = fixture()
        changelog = next(item for item in trusted["sources"] if item["path"].endswith("CHANGELOG.md"))
        today = datetime.date.fromisoformat(trusted["reviewDate"])
        for days in (21, 22):
            changelog["content"] = f"## 1.0.0b1 ({today + datetime.timedelta(days=days)})\n"
            _, findings = evidence.deterministic_checks(trusted, PACKAGE)
            date_findings = [item for item in findings if item["check"] == "Changelog date"]
            self.assertEqual(int(days > 21), len(date_findings))
        for heading in ("Malformed", "1.0.0b1 (2026-02-30)", "1.0.0b1 (Unreleased)", "1.0.0b1 (20260928)"):
            changelog["content"] = f"## {heading}\n## 0.9.0 (2025-01-01)\n"
            checks, _ = evidence.deterministic_checks(trusted, PACKAGE)
            self.assertEqual("unverified", checks[2]["outcome"])

    def test_literal_only_parsing_never_executes(self):
        _, trusted = fixture()
        version = next(item for item in trusted["sources"] if item["path"].endswith("_version.py"))
        version["content"] = 'raise RuntimeError("must not run")\nVERSION = str(1)\n'
        checks, _ = evidence.deterministic_checks(trusted, PACKAGE)
        self.assertEqual("unverified", checks[0]["outcome"])
        version["content"] = 'raise RuntimeError("must not run")\nVERSION = "1.0.0b1"\n'
        checks, _ = evidence.deterministic_checks(trusted, PACKAGE)
        self.assertEqual("completed", checks[0]["outcome"])
        self.assertTrue(checks[0]["sources"][0]["url"].endswith("#L2"))
        project = next(item for item in trusted["sources"] if item["path"].endswith("pyproject.toml"))
        project["content"] = "project = 42\npackaging = false\n"
        checks, _ = evidence.deterministic_checks(trusted, PACKAGE)
        self.assertEqual("unverified", checks[3]["outcome"])

    def test_missing_flags_are_findings_but_unreadable_data_is_unverified(self):
        _, trusted = fixture()
        project = next(item for item in trusted["sources"] if item["path"].endswith("pyproject.toml"))
        project["content"] = "[project]\nname = 'example'\n"
        _, findings = evidence.deterministic_checks(trusted, PACKAGE)
        self.assertEqual("Stability flags", findings[0]["check"])
        for state in ("missing", "truncated", "unverified"):
            project["status"] = state
            checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
            self.assertEqual("unverified", checks[3]["outcome"])
            self.assertFalse(findings)

    def test_source_catalog_distinguishes_access_errors_and_evidence_roles(self):
        item = evidence.source_record(
            REPO,
            {
                "path": PACKAGE + "/README.md",
                "revision": HEAD,
                "status": "unverified",
                "httpStatus": 403,
                "error": "HTTP 403 while fetching pinned evidence.",
            },
            PACKAGE,
        )
        self.assertEqual("access_error", item["status"])
        self.assertEqual(0, item["lineCount"])
        version = record("azure/mgmt/example/_version.py", 'VERSION = "1.0.0"\n')
        self.assertEqual(["Version consistency", "Preview version", "Stability flags"], version["allowedChecks"])

    def test_snapshot_owned_fields_cannot_be_asserted(self):
        draft, trusted = fixture()
        for key, value in (("initial_release", True), ("outcome", "no_entries"), ("release", "invented")):
            changed = copy.deepcopy(draft)
            changed["packages"][0][key] = value
            self.assertFalse(contract.preflight(changed, trusted)["ok"])
        trusted["breakingChangeContext"][0]["releaseBaseline"] = {
            "status": "not_applicable",
            "reason": "Initial release independently confirmed.",
        }
        body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertIn("Initial release independently confirmed", body)

    def test_ranges_states_exclusions_and_multiple_diagnostics(self):
        draft, trusted = fixture()
        checks = draft["packages"][0]["checks"]
        checks["Client signature"]["sources"][0]["end_line"] = 900
        checks["README snippets"]["sources"][0]["reason"] = "Lines unavailable."
        result = contract.preflight(draft, trusted)
        self.assertFalse(result["ok"])
        self.assertTrue(
            {"line_out_of_bounds", "citation_state_conflict"} <= {item["code"] for item in result["errors"]}
        )
        self.assertTrue(all(item["path"].startswith("data.packages[0].checks.") for item in result["errors"]))
        for path in (
            "generated_samples/sample.py",
            "generated_tests/test.py",
            "azure/mgmt/example/_models.py",
            "azure/mgmt/example/operations/_operations.py",
            "azure/mgmt/example/_version.py",
        ):
            draft, trusted = fixture()
            excluded = record(path, "content")
            trusted["sources"].append(excluded)
            draft["packages"][0]["checks"]["README snippets"]["sources"] = [reference(excluded)]
            self.assertIn("excluded_file", {item["code"] for item in contract.preflight(draft, trusted)["errors"]})
        for start, end, why, code in (
            (0, 1, "", "missing_anchor"),
            (2, 1, "", "missing_anchor"),
            (1, 1, "unavailable", "citation_state_conflict"),
        ):
            draft, trusted = fixture()
            ref = draft["packages"][0]["checks"]["README snippets"]["sources"][0]
            ref.update(start_line=start, end_line=end, reason=why)
            self.assertIn(code, {item["code"] for item in contract.preflight(draft, trusted)["errors"]})

    def test_unavailable_evidence_never_silently_becomes_completed(self):
        draft, trusted = fixture()
        ref = draft["packages"][0]["checks"]["README snippets"]["sources"][0]
        ref.update(start_line=0, end_line=0, reason="Exact lines were unavailable.")
        self.assertIn(
            "missing_verified_evidence", {item["code"] for item in contract.preflight(draft, trusted)["errors"]}
        )
        draft["packages"][0]["checks"]["README snippets"]["outcome"] = "unverified"
        draft["packages"][0]["checks"]["README snippets"]["reason"] = "Exact lines were unavailable."
        self.assertTrue(contract.preflight(draft, trusted)["ok"])

    def test_schema_reports_multiple_independent_errors(self):
        draft, trusted = fixture()
        for check in draft["packages"][0]["checks"].values():
            check["outcome"] = "looks_good"
        errors = contract.preflight(draft, trusted)["errors"]
        self.assertEqual(3, len(errors))
        self.assertEqual({"schema_mismatch"}, {item["code"] for item in errors})

    def test_production_publication_budgets_and_no_findings_claims(self):
        draft, trusted = fixture()
        refs = []
        for i in range(42):
            item = record(f"docs/evidence{i}.md", "Verified fixture line.")
            trusted["sources"].append(item)
            refs.append(reference(item))
        draft["packages"][0]["checks"]["README snippets"]["sources"] = refs
        result = contract.preflight(draft, trusted)
        self.assertIn("publication_link_budget", {item["code"] for item in result["errors"]})
        draft, trusted = fixture()
        draft["packages"][0]["findings"] = [
            {
                "check": "README snippets",
                "severity": "Blocking",
                "title": f"Snippet mismatch {i}",
                "observation": "Incorrect snippet " * 600,
                "remediation": "Use the real signature " * 400,
                "sources": draft["packages"][0]["checks"]["README snippets"]["sources"],
            }
            for i in range(4)
        ]
        result = contract.preflight(draft, trusted)
        self.assertIn("publication_size_budget", {item["code"] for item in result["errors"]})
        draft["packages"][0]["findings"] = draft["packages"][0]["findings"][:1]
        result = contract.preflight(draft, trusted)
        self.assertTrue(result["ok"], result)
        body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertIn("Snippet mismatch", body)
        self.assertNotIn("**Findings:** None.", body)


class ServiceAndPublicationTests(unittest.TestCase):
    def test_retained_production_shapes_require_explicit_new_contract(self):
        corpus = json.loads(
            (Path(__file__).parent / "fixtures" / "mgmt-review" / "historical" / "contract-failures.json").read_text()
        )
        self.assertEqual(10, len(corpus["cases"]))
        for case in corpus["cases"]:
            with self.subTest(run=case["run"]):
                self.assertRegex(case["run"], r"^https://github.com/Azure/azure-sdk-for-python/actions/runs/\d+$")
                fragment = case["fragment"]
                kind = case["failure"]
                draft, trusted = fixture()
                if kind.startswith("matching_target"):
                    trusted["pullRequestNumber"] = fragment["item_number"]
                    payload = submit(draft, trusted)
                    payload["items"][0]["item_number"] = fragment["item_number"]
                    self.assertEqual(1, len(contract.prepare_output(payload, trusted)["items"]))
                    if "source" in fragment:
                        with self.assertRaisesRegex(contract.ReviewError, "missing_anchor"):
                            contract.source_identity(fragment["source"], "historical.source")
                elif kind == "five_verified_sources_without_anchors":
                    for source in fragment["sources"]:
                        with self.assertRaisesRegex(contract.ReviewError, "missing_anchor"):
                            contract.source_identity(source, "historical.source")
                    # Explicit fixture migration selects ranges in independently supplied test content.
                    # It neither accepts the legacy payload nor guesses anchors in production.
                    self.assertTrue(contract.preflight(draft, trusted)["ok"])
                    self.assertEqual(
                        len(evidence.AUTOMATIC_CHECKS), len(evidence.deterministic_checks(trusted, PACKAGE)[0])
                    )
                elif kind == "unavailable_with_anchor":
                    with self.assertRaisesRegex(contract.ReviewError, "citation_state_conflict"):
                        contract.source_identity(fragment["source"], "historical.source")
                elif kind == "mixed_attribution_roles":
                    old, old_context = review(), context()
                    add_entry(old, old_context, direct=True)
                    entry = old["packages"][0]["attribution"]["entries"][0]
                    entry["sources"] = [fragment["sources"][0]]
                    entry["sdk_context"] = [fragment["sources"][1]]
                    migrated, trusted = production_fixture(old, old_context)
                    draft = {k: v for k, v in migrated.items() if k not in {"registrations", "preflight"}}
                    self.assertTrue(contract.preflight(draft, trusted)["ok"])
                elif kind == "high_confidence_unavailable_specification":
                    with self.assertRaisesRegex(contract.ReviewError, "verified source lines"):
                        contract.validate_sources(
                            fragment["sources"],
                            "historical.sources",
                            trusted,
                            trusted["breakingChangeContext"][0],
                            PACKAGE,
                            required=True,
                            specification=True,
                        )
                elif kind == "stability_version_evidence":
                    contract.validate_sources(
                        [fragment["source"]],
                        "historical.sources",
                        trusted,
                        trusted["breakingChangeContext"][0],
                        PACKAGE,
                        check=fragment["check"],
                    )
                elif kind == "stale_tooling":
                    self.assertNotIn("github.event.pull_request.base.sha", SOURCE)
                    self.assertIn("ref: ${{ github.workflow_sha }}", SOURCE)
                else:
                    with self.assertRaises(contract.ReviewError):
                        contract.prepare_output({"items": [fragment], "errors": []}, trusted)

    def test_correction_success_then_only_one_envelope(self):
        draft, trusted = fixture()
        host = service.ReviewService(trusted)
        broken = copy.deepcopy(draft)
        broken["packages"][0]["checks"]["README snippets"]["sources"][0]["end_line"] = 999
        self.assertFalse(host.call({"operation": "preflight", "draft": broken})["ok"])
        result = host.call({"operation": "preflight", "draft": draft})
        self.assertTrue(result["ok"])
        self.assertEqual(2, result["attempt"])
        self.assertEqual(1, result["correctionsRemaining"])
        self.assertIn(
            "Management SDK PR review",
            contract.prepare_output(envelope(result["submission"]["data"]), trusted)["items"][0]["body"],
        )
        with self.assertRaisesRegex(contract.ReviewError, "correction_limit"):
            host.call({"operation": "preflight", "draft": draft})

    def test_exhausted_corrections_do_not_produce_publication(self):
        draft, trusted = fixture()
        draft["packages"] = []
        host = service.ReviewService(trusted)
        for number in range(1, 4):
            result = host.call({"operation": "preflight", "draft": draft})
            self.assertFalse(result["ok"])
            self.assertNotIn("submission", result)
            self.assertEqual(number, result["attempt"])
        with self.assertRaisesRegex(contract.ReviewError, "correction_limit"):
            host.call({"operation": "preflight", "draft": fixture()[0]})

    def test_target_is_checked_and_removed(self):
        draft, trusted = fixture()
        payload = submit(draft, trusted)
        payload["items"][0]["item_number"] = trusted["pullRequestNumber"]
        output = contract.prepare_output(payload, trusted)
        self.assertEqual({"type", "body"}, set(output["items"][0]))
        for number in (False, str(trusted["pullRequestNumber"]), trusted["pullRequestNumber"] + 1):
            payload["items"][0]["item_number"] = number
            with self.assertRaisesRegex(contract.ReviewError, "conflicting_target"):
                contract.prepare_output(payload, trusted)
        payload["items"][0].pop("item_number")
        payload["items"][0]["comment_id"] = 123
        with self.assertRaisesRegex(contract.ReviewError, "unsupported_publication_field"):
            contract.prepare_output(payload, trusted)

    def test_modified_payload_and_legacy_schema_are_rejected(self):
        draft, trusted = fixture()
        payload = submit(draft, trusted)
        payload["items"][0]["data"]["outcome"] = "not_applicable"
        payload = envelope(payload["items"][0]["data"])
        with self.assertRaisesRegex(contract.ReviewError, "preflight_changed"):
            contract.prepare_output(payload, trusted)
        with self.assertRaises(contract.ReviewError):
            contract.prepare_output(envelope(review()), trusted)
        with self.assertRaises(contract.ReviewError):
            contract.prepare_output({"items": [{"type": "add_comment", "body": "-"}], "errors": []}, trusted)

    def test_specification_role_registration_and_independent_reread(self):
        old, trusted = review(), context()
        add_entry(old, trusted, direct=True)
        final, trusted = production_fixture(old, trusted)
        draft = {key: value for key, value in final.items() if key not in {"preflight", "registrations"}}
        trusted["sources"] = [item for item in trusted["sources"] if "specification" not in item["roles"]]
        host = service.ReviewService(trusted)
        with mock.patch.object(
            service.GitHubClient,
            "read_file",
            return_value={
                "path": "specification/example/main.tsp",
                "revision": NEW_SPEC,
                "status": "available",
                "content": '// Definition\n@renamedFrom(Versions.v1, "Widget")\nmodel NewWidget {}\n',
            },
        ) as fetch:
            registered = host.call(
                {
                    "operation": "register",
                    "package": PACKAGE,
                    "repository": "Azure/azure-rest-api-specs",
                    "revision": NEW_SPEC,
                    "path": "specification/example/main.tsp",
                }
            )
            self.assertIn("2: @renamedFrom", registered["numberedContent"])
            entry = draft["packages"][0]["attribution"][0]
            entry["sources"] = [reference(registered, 2, 3)]
            entry["sdk_context"] = [draft["packages"][0]["checks"]["README snippets"]["sources"][0]]
            result = host.call({"operation": "preflight", "draft": draft})
            self.assertTrue(result["ok"], result)
            resolver = service.EvidenceRegistry(trusted, "")
            body = contract.prepare_output(envelope(result["submission"]["data"]), trusted, resolver.resolve)["items"][
                0
            ]["body"]
            self.assertIn("TypeSpec/API", body)
            self.assertIn("README.md", body)
            self.assertEqual(2, fetch.call_count)
            changed = copy.deepcopy(result["submission"]["data"])
            changed["registrations"][0]["sha256"] = "0" * 64
            changed["preflight"]["digest"] = contract.digest(
                {key: value for key, value in changed.items() if key != "preflight"}
            )
            with self.assertRaisesRegex(contract.ReviewError, "evidence_changed"):
                contract.prepare_output(envelope(changed), trusted, resolver.resolve)
            entry["sources"], entry["sdk_context"] = entry["sdk_context"], entry["sources"]
            errors = contract.preflight(draft, host.context)["errors"]
            self.assertIn("wrong_evidence_role", {item["code"] for item in errors})

    def test_direct_attribution_needs_verified_spec_not_sdk_context(self):
        old, trusted = review(), context()
        add_entry(old, trusted, direct=True)
        final, trusted = production_fixture(old, trusted)
        draft = {key: value for key, value in final.items() if key not in {"preflight", "registrations"}}
        entry = draft["packages"][0]["attribution"][0]
        entry["sources"][0].update(start_line=0, end_line=0, reason="Specification definition unavailable.")
        self.assertIn(
            "missing_verified_evidence", {item["code"] for item in contract.preflight(draft, trusted)["errors"]}
        )
        entry["cause"] = "human_review"
        self.assertTrue(contract.preflight(draft, trusted)["ok"])

    def test_registration_limits_wrong_revision_and_no_agent_content(self):
        _, trusted = fixture()
        host = service.ReviewService(trusted)
        request = {
            "operation": "register",
            "package": PACKAGE,
            "repository": "Azure/azure-rest-api-specs",
            "revision": NEW_SPEC,
            "path": "specification/example/main.tsp",
        }
        with self.assertRaises(contract.ReviewError):
            host.call({**request, "content": "model Invented {}"})
        with self.assertRaisesRegex(contract.ReviewError, "wrong_revision"):
            host.call({**request, "revision": "0" * 40})
        for path in (
            "../README.md",
            "specification/../README.md",
            "specification/%2e%2e/file.tsp",
            "https://evil.invalid",
        ):
            with self.assertRaisesRegex(contract.ReviewError, "invalid_source_path"):
                host.call({**request, "path": path})
        with mock.patch.object(
            service.GitHubClient,
            "read_file",
            side_effect=lambda path, revision: {
                "path": path,
                "revision": revision,
                "status": "available",
                "content": "x" * (256 * 1024),
            },
        ) as fetch:
            results = [host.call({**request, "path": f"specification/example/file{i}.tsp"}) for i in range(20)]
            self.assertEqual("truncated", results[4]["status"])
            self.assertEqual("", results[4]["numberedContent"])
            with self.assertRaisesRegex(contract.ReviewError, "evidence_budget"):
                host.call({**request, "path": "specification/example/extra.tsp"})
            self.assertEqual(4, fetch.call_count)

    def test_unknown_operations_cannot_execute_commands(self):
        _, trusted = fixture()
        for request in (
            {"operation": "exec", "command": "python"},
            {"operation": "read", "path": "secret"},
            {"operation": "describe", "url": "https://evil.invalid"},
        ):
            with self.assertRaises(contract.ReviewError):
                service.ReviewService(trusted).call(request)

    def test_final_schema_and_host_mount_permissions(self):
        self.assertEqual(contract.SCHEMA, lock_json("GH_AW_VALIDATION_JSON")["add_comment"]["dataSchema"])
        lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
        self.assertIn('"name": "review"', lock)
        self.assertIn("http://127.0.0.1:8765/review", lock)
        self.assertNotRegex(SOURCE, r"(?m)^    - (?:python|curl)(?:\s|$)")
        self.assertNotIn('--mount "${RUNNER_TEMP}/mgmt-review-service', lock)
        self.assertIn('--mount "${RUNNER_TEMP}/gh-aw:${RUNNER_TEMP}/gh-aw:ro"', lock)


@unittest.skipUnless(os.environ.get("GH_AW_RUNTIME"), "Set GH_AW_RUNTIME to v0.88.8 runtime; required for release.")
class PinnedPreflightRuntimeTests(unittest.TestCase):
    def test_actual_compiled_python_tool_and_documented_commands(self):
        harness = Path(__file__).with_name("mgmt_review_runtime.cjs")
        lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
        marker = re.search(r"cat > .*?/review.py\" << '([^']+)'", lock)
        script = textwrap_dedent(lock.split(marker[0], 1)[1].split(marker[1], 1)[0])
        draft, trusted = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / "context.json"
            snapshot.write_text(json.dumps(trusted), encoding="utf-8")
            tool = root / "review.py"
            tool.write_text(script, encoding="utf-8")
            env = {
                **os.environ,
                "GH_REPOSITORY": REPO,
                "PR_NUMBER": str(trusted["pullRequestNumber"]),
                "REVIEW_HEAD_SHA": HEAD,
                "REVIEW_TOOLING_SHA": TOOLING,
                "GH_TOKEN": "test",
            }
            process = subprocess.Popen(
                [sys.executable, str(SCRIPT.with_name("mgmt_sdk_review_service.py")), "--context", str(snapshot)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                for _ in range(40):
                    if process.poll() is not None:
                        self.fail(process.communicate()[1].decode())
                    try:
                        request = urllib.request.Request(
                            "http://127.0.0.1:8765/review",
                            data=b'{"operation":"describe"}',
                            headers={"Content-Type": "application/json"},
                        )
                        with urllib.request.urlopen(request, timeout=1) as response:
                            self.assertEqual("2", json.load(response)["schemaVersion"])
                        break
                    except OSError:
                        time.sleep(0.1)
                else:
                    self.fail("Host service not responsive")
                jq = shutil.which("jq") or os.environ["JQ"]
                expression = re.search(r"(?m)^jq '([^']+)' .* \| mcpscripts review \.$", SOURCE)[1]
                broken = copy.deepcopy(draft)
                broken["packages"][0]["checks"]["README snippets"]["sources"][0]["end_line"] = 999
                for current in (broken, draft):
                    arguments = subprocess.run(
                        [jq, expression], input=json.dumps(current), capture_output=True, text=True, check=True
                    )
                    result = subprocess.run(
                        ["node", str(harness)],
                        input=json.dumps(
                            {
                                "mode": "preflight-tool",
                                "script": str(tool),
                                "arguments": json.loads(arguments.stdout),
                            }
                        ),
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    tool_response = json.loads(result.stdout)
                    answer = json.loads(tool_response["content"][0]["text"])
                    if current is broken:
                        self.assertFalse(answer["ok"])
                        self.assertNotIn("submission", answer)
                self.assertTrue(answer["ok"], answer)
                self.assertEqual(2, answer["attempt"])
                expression = re.search(r"(?m)^jq '([^']+)' .* \| safeoutputs add_comment \.$", SOURCE)[1]
                submission = subprocess.run(
                    [jq, expression], input=json.dumps(answer), capture_output=True, text=True, check=True
                )
                ingested = subprocess.run(
                    ["node", str(harness)],
                    input=json.dumps(
                        {
                            "mode": "submit",
                            "submissions": [json.loads(submission.stdout)] * 2,
                            "schema": contract.SCHEMA,
                            "validation": lock_json("GH_AW_VALIDATION_JSON"),
                        }
                    ),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                ingested = json.loads(ingested.stdout)
                self.assertEqual(1, len(ingested["appended"]))
                self.assertIn("error", ingested["responses"][1])
                ingested = ingested["ingestion"][0]
                self.assertTrue(ingested["isValid"], ingested)
                prepared = contract.prepare_output({"errors": [], "items": [ingested["normalizedItem"]]}, trusted)
                published = subprocess.run(
                    ["node", str(harness)],
                    input=json.dumps({"mode": "publish", "payload": prepared}),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                published = json.loads(published.stdout)
                self.assertEqual(1, published["writes"])
                self.assertEqual(0, published["hides"])
                self.assertIn("Review completeness: complete", published["comment"]["body"])
            finally:
                process.terminate()
                process.communicate(timeout=10)

    def test_exhaustion_leaves_existing_comments_untouched(self):
        draft, trusted = fixture()
        draft["packages"] = []
        host = service.ReviewService(trusted)
        submissions = []
        for _ in range(3):
            result = host.call({"operation": "preflight", "draft": draft})
            if result.get("submission"):
                submissions.append(result["submission"])
        harness = Path(__file__).with_name("mgmt_review_runtime.cjs")
        response = subprocess.run(
            ["node", str(harness)],
            input=json.dumps(
                {
                    "mode": "submit",
                    "submissions": submissions,
                    "schema": contract.SCHEMA,
                    "validation": lock_json("GH_AW_VALIDATION_JSON"),
                }
            ),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual([], json.loads(response.stdout)["appended"])
        response = subprocess.run(
            ["node", str(harness)],
            input=json.dumps(
                {
                    "mode": "publish",
                    "payload": {"items": []},
                    "existing": True,
                }
            ),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(0, json.loads(response.stdout)["hides"])
        self.assertEqual(0, json.loads(response.stdout)["writes"])
        # Positive control: this very same existing comment is hidden after an accepted review.
        draft, trusted = fixture()
        prepared = contract.prepare_output(submit(draft, trusted), trusted)
        response = subprocess.run(
            ["node", str(harness)],
            input=json.dumps(
                {
                    "mode": "publish",
                    "payload": prepared,
                    "existing": True,
                }
            ),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(1, json.loads(response.stdout)["hides"])
        self.assertEqual(1, json.loads(response.stdout)["writes"])


def textwrap_dedent(value):
    import textwrap

    return textwrap.dedent(value).lstrip()
