"""Version-2 production boundary tests; no network writes or package execution."""

# cspell:ignore mcpscripts

import copy
import datetime
import hashlib
import io
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
import urllib.parse
import urllib.error
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

RULES = WORKFLOW.parents[1] / "instructions" / "reviewer" / "management.instructions.md"
RULE_TEXT = RULES.read_text(encoding="utf-8")


def fixture():
    data, trusted = production_fixture()
    data.pop("preflight")
    data.pop("registrations")
    trusted["mgmtSdkCodeReviewRules"] = RULE_TEXT.strip()
    trusted["sources"].extend(
        [
            record("azure/mgmt/example/_version.py", 'VERSION = "1.0.0b1"\n'),
            record("CHANGELOG.md", "## 1.0.0b1 (2026-09-28)\n\n### Other Changes\n- Initial version.\n"),
            record("_metadata.json", '{"apiVersion": null, "apiVersions": {"Example": "2026-09-01-preview"}}\n'),
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


def multipackage_fixture(count=7):
    draft, trusted = fixture()
    result, context = copy.deepcopy(draft), copy.deepcopy(trusted)
    result["packages"] = []
    for key in ("affectedPackages", "sources", "apiVersionDrift", "breakingChangeContext"):
        context[key] = []
    for index in range(count):
        name = PACKAGE + f"-{index}"

        def clone(value):
            return json.loads(json.dumps(value).replace(PACKAGE, name))

        package = json.dumps(clone(draft["packages"][0]))
        for source in trusted["sources"]:
            copied = clone(source)
            copied["id"] = evidence.source_id(copied["repository"], copied["revision"], copied["path"])
            package = package.replace(source["id"], copied["id"])
            context["sources"].append(copied)
        result["packages"].append(json.loads(package))
        context["affectedPackages"].append(name)
        for key in ("apiVersionDrift", "breakingChangeContext"):
            context[key].extend(clone(trusted[key]))
    context["deterministicChecks"] = {
        name: dict(zip(("checks", "findings"), evidence.deterministic_checks(context, name)))
        for name in context["affectedPackages"]
    }
    return result, context


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
    payload = envelope(result["submission"]["data"])
    payload["items"][0]["item_number"] = result["submission"]["item_number"]
    return payload


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

    def test_cold_cache_handoff_discovers_same_sources_as_warm_cache(self):
        for cached in (False, True):
            with self.subTest(cached=cached):
                _, trusted = fixture()
                contents = {item["path"]: item["content"] for item in trusted["sources"]}
                project = PACKAGE + "/pyproject.toml"
                contents[
                    project
                ] += '\n[tool.setuptools.dynamic.version]\nattr = "azure.mgmt.example._version.VERSION"\n'
                for suffix in ("_client.py", "aio/_client.py"):
                    contents[PACKAGE + "/azure/mgmt/example/" + suffix] = "class ExampleMgmtClient:\n    pass\n"
                trusted.update(changedFiles=[{"filename": PACKAGE + "/README.md"}], collectionLimits={})
                client = collector.GitHubClient(REPO, "test")
                client.request_count = collector.MAX_API_REQUESTS - 20
                self.assertLess(20, collector.MAX_PACKAGE_API_REQUESTS)

                def fetch(path, revision):
                    client.request_count += 1
                    return {
                        "path": path,
                        "revision": revision,
                        "status": "available" if path in contents else "missing",
                        "content": contents.get(path, ""),
                        "error": "",
                    }

                with mock.patch.object(client, "_read_file", side_effect=fetch) as reads:
                    if cached:
                        client.read_file(project, HEAD)
                    collector.collect_review_sources(client, trusted)
                self.assertEqual(8, reads.call_count)
                self.assertEqual(1, reads.call_args_list.count(mock.call(project, HEAD)))
                self.assertEqual(mock.call(project, HEAD), reads.call_args_list[0])
                self.assertEqual(collector.MAX_API_REQUESTS - 12, client.request_count)
                self.assertEqual([], trusted["sourceCollectionIssues"])
                paths = {item["path"] for item in trusted["sources"]}
                for suffix in ("_version.py", "_client.py", "aio/_client.py"):
                    self.assertIn(PACKAGE + "/azure/mgmt/example/" + suffix, paths)
                self.assertEqual("completed", trusted["deterministicChecks"][PACKAGE]["checks"][0]["outcome"])

    def test_project_discovery_preserves_last_request_and_cached_evidence(self):
        for remaining in (1, 2):
            with self.subTest(remaining=remaining):
                _, trusted = fixture()
                trusted.update(changedFiles=[], collectionLimits={})
                client = collector.GitHubClient(REPO, "test")
                client.request_count = collector.MAX_API_REQUESTS - remaining
                readme = PACKAGE + "/README.md"
                client.files[(readme, HEAD)] = {
                    "path": readme,
                    "revision": HEAD,
                    "status": "available",
                    "content": "Retained evidence.",
                }

                def fetch(path, revision):
                    client.request_count += 1
                    return {
                        "path": path,
                        "revision": revision,
                        "status": "available",
                        "content": '[tool.setuptools.dynamic.version]\nattr = "azure.mgmt.example._version.VERSION"\n',
                    }

                with mock.patch.object(client, "_read_file", side_effect=fetch) as reads:
                    collector.collect_review_sources(client, trusted)
                self.assertEqual(remaining - 1, reads.call_count)
                self.assertEqual(collector.MAX_API_REQUESTS - 1, client.request_count)
                preserved = next(item for item in trusted["sources"] if item["path"] == readme)
                self.assertEqual("Retained evidence.", preserved["content"])
                self.assertEqual("available", preserved["status"])
                self.assertTrue(any(item["status"] == "unverified" for item in trusted["sources"]))
                self.assertEqual("unverified", trusted["deterministicChecks"][PACKAGE]["checks"][0]["outcome"])

    def test_unavailable_project_does_not_invent_source_paths(self):
        for status, content in (("missing", ""), ("unverified", ""), ("available", "malformed = [")):
            with self.subTest(status=status):
                _, trusted = fixture()
                trusted.update(changedFiles=[], collectionLimits={})
                client = collector.GitHubClient(REPO, "test")
                with mock.patch.object(
                    client,
                    "_read_file",
                    side_effect=lambda path, revision: {
                        "path": path,
                        "revision": revision,
                        "status": status,
                        "content": content,
                        "error": "Project unavailable." if status != "available" else "",
                    },
                ):
                    collector.collect_review_sources(client, trusted)
                self.assertTrue(trusted["sourceCollectionIssues"])
                self.assertFalse(any(item["path"].endswith("/_version.py") for item in trusted["sources"]))
                self.assertEqual("unverified", trusted["deterministicChecks"][PACKAGE]["checks"][0]["outcome"])

    def test_project_discovery_counts_toward_package_file_limit(self):
        _, trusted = fixture()
        trusted.update(
            changedFiles=[{"filename": f"{PACKAGE}/azure/mgmt/example/extra{index}/_client.py"} for index in range(20)],
            collectionLimits={},
        )
        client = collector.GitHubClient(REPO, "test")
        with mock.patch.object(
            client,
            "_read_file",
            side_effect=lambda path, revision: {
                "path": path,
                "revision": revision,
                "status": "missing",
                "error": "Pinned file missing.",
            },
        ) as reads:
            collector.collect_review_sources(client, trusted)
        self.assertEqual(16, reads.call_count)
        self.assertEqual(16, len(trusted["sources"]))
        self.assertIn((PACKAGE + "/pyproject.toml", HEAD), client.files)
        self.assertTrue(any("16-file package limit" in issue for issue in trusted["sourceCollectionIssues"]))

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

    def api_provenance(self, versions, singular=None):
        return collector.summarize_provenance(
            [
                {
                    "status": "available",
                    "path": PACKAGE + "/_metadata.json",
                    "content": json.dumps({"apiVersion": singular, "apiVersions": versions}),
                }
            ]
        )

    def test_api_version_drift_compares_complete_maps_not_order_or_flattened_versions(self):
        first = {"Example": "2026-01-01", "Other": "2026-02-01"}
        for latest, expected in (
            ({"Other": "2026-02-01", "Example": "2026-01-01"}, "unchanged"),
            ({"Example": "2026-02-01", "Other": "2026-01-01"}, "changed"),
            ({**first, "Added": "2026-01-01"}, "changed"),
            ({"Example": "2026-01-01"}, "changed"),
        ):
            with self.subTest(latest=latest):
                result = collector.api_version_drift(
                    PACKAGE,
                    "a" * 40,
                    HEAD,
                    self.api_provenance(first, "ignored-preview"),
                    self.api_provenance(latest, "ignored-stable"),
                )
                self.assertEqual(expected, result["status"])
                self.assertEqual(first, result["firstApiVersions"])
                self.assertEqual(latest, result["latestApiVersions"])
                self.assertEqual(sorted(latest), list(result["latestApiVersions"]))
                self.assertIsNone(result["error"])

    def test_preview_check_uses_any_map_value_and_ignores_singular_api_version(self):
        for versions, singular, sdk_version, blocking in (
            ({"Example": "2026-01-01"}, "2026-01-01-preview", "1.0.0", False),
            ({"PreviewService": "2026-01-01"}, None, "1.0.0", False),
            ({"Example": "2026-01-01-preview"}, "2026-01-01", "1.0.0", True),
            ({"Stable": "2026-01-01", "Preview": "2026-02-01-Preview"}, None, "1.0.0", True),
            ({"Stable": "2026-01-01", "Preview": "2026-02-01-preview"}, None, "1.0.0b1", False),
        ):
            with self.subTest(versions=versions, sdk_version=sdk_version):
                _, trusted = fixture()
                metadata = next(item for item in trusted["sources"] if item["path"].endswith("_metadata.json"))
                metadata["content"] = json.dumps({"apiVersion": singular, "apiVersions": versions})
                version = next(item for item in trusted["sources"] if item["path"].endswith("_version.py"))
                version["content"] = f'VERSION = "{sdk_version}"\n'
                checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
                check = next(item for item in checks if item["name"] == "Preview version")
                self.assertEqual("completed", check["outcome"])
                preview_findings = [item for item in findings if item["check"] == "Preview version"]
                self.assertEqual(int(blocking), len(preview_findings))
                if blocking:
                    self.assertEqual("Blocking", preview_findings[0]["severity"])
                    self.assertIn("preview", preview_findings[0]["observation"].lower())

    def test_invalid_api_maps_remain_unverified_in_both_checks_without_fallback(self):
        for versions in (
            None,
            {},
            [],
            "2026-01-01",
            {"Example": None},
            {"Example": ""},
            {"Example": 2026},
            {"Example": ["2026-01-01"]},
            {"Example": " 2026-01-01"},
            {"": "2026-01-01"},
            {" Example": "2026-01-01"},
            {"Stable": "2026-01-01", "Invalid": None},
        ):
            with self.subTest(versions=versions):
                _, trusted = fixture()
                metadata = next(item for item in trusted["sources"] if item["path"].endswith("_metadata.json"))
                metadata["content"] = json.dumps({"apiVersion": "2026-01-01-preview", "apiVersions": versions})
                checks, findings = evidence.deterministic_checks(trusted, PACKAGE)
                check = next(item for item in checks if item["name"] == "Preview version")
                self.assertEqual("unverified", check["outcome"])
                self.assertIn("apiVersions", check["reason"])
                self.assertFalse([item for item in findings if item["check"] == "Preview version"])
                provenance = self.api_provenance(versions, "2026-01-01-preview")
                drift = collector.api_version_drift(PACKAGE, "a" * 40, HEAD, provenance, provenance)
                self.assertEqual("unverified", drift["status"])
                self.assertIn(check["reason"], drift["error"])

    def test_null_api_version_with_valid_map_is_not_incomplete(self):
        draft, trusted = fixture()
        provenance = self.api_provenance({"Example": "2026-09-01-preview"})
        trusted["apiVersionDrift"] = [
            collector.api_version_drift(PACKAGE, trusted["firstRevision"], HEAD, provenance, provenance)
        ]
        body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertIn("Review completeness: complete", body)
        self.assertIn("**Findings:** None.", body)

    def test_compute_null_scalar_regression_detects_gallery_change(self):
        # Actual API maps from the revisions cited in:
        # https://github.com/Azure/azure-sdk-for-python/pull/48997#issuecomment-5770214235
        first = {
            "Compute": "2026-04-01",
            "ComputeDisk": "2026-03-02",
            "ComputeGallery": "2025-12-03",
            "ComputeSku": "2021-07-01",
        }
        latest = {**first, "ComputeGallery": "2026-03-03"}
        draft, trusted = fixture()
        drift = collector.api_version_drift(
            PACKAGE, trusted["firstRevision"], HEAD, self.api_provenance(first), self.api_provenance(latest)
        )
        self.assertEqual("changed", drift["status"])
        trusted["apiVersionDrift"] = [drift]
        body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        for expected in ("Blocking", "API versions changed", "ComputeGallery", "2025-12-03", "2026-03-03"):
            self.assertIn(expected, body)
        self.assertIn("service-to-API-version mapping", body)

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

    def test_multi_package_reviews_share_links_without_dropping_checks(self):
        draft, trusted = multipackage_fixture()
        result = contract.preflight(draft, trusted)
        self.assertTrue(result["ok"], result)
        self.assertEqual("complete", result["reviewCompleteness"])
        self.assertEqual(35, result["links"])
        body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertIn("### Evidence references", body)
        for check in evidence.CHECKS:
            self.assertEqual(7, body.count(check))
        urls = re.findall(r"https?://[^)]+", body)
        self.assertEqual(35, len(set(urls)))
        for number in range(1, 36):
            self.assertIn(f"[E{number}]", body)
            self.assertIn(f"| E{number} |", body)
        # Existing single-package formatting and repeated inline links are unchanged.
        draft, trusted = fixture()
        body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertNotIn("### Evidence references", body)
        self.assertEqual(11, len(re.findall(r"https?://", body)))

    def test_shared_references_preserve_findings_partial_checks_and_distinct_ranges(self):
        draft, trusted = multipackage_fixture(2)
        package = draft["packages"][0]
        ref = package["checks"]["README snippets"]["sources"][0]
        package["findings"] = [
            {
                "check": "README snippets",
                "severity": "Blocking",
                "title": "Snippet mismatch",
                "observation": "Incorrect signature.",
                "remediation": "Use the real signature.",
                "sources": [ref],
            }
        ]
        check = package["checks"]["Client name consistency"]
        check.update(
            outcome="unverified",
            reason="No precise lines.",
            sources=[{**ref, "start_line": 0, "end_line": 0, "reason": "Exact lines unavailable."}],
        )
        package["checks"]["Client signature"]["sources"] = [{**ref, "start_line": 1, "end_line": 1}]
        trusted["apiVersionDrift"][0].update(status="changed", latestApiVersions={"Example": "2026-02-01"})
        result = contract.preflight(draft, trusted)
        self.assertTrue(result["ok"], result)
        self.assertEqual("partial", result["reviewCompleteness"])
        body = contract.prepare_output(submit(draft, trusted), trusted)["items"][0]["body"]
        self.assertIn("Snippet mismatch", body)
        self.assertIn("API versions changed", body)
        self.assertIn("lines unverified", body)
        self.assertIn("Exact lines unavailable.", body)
        urls = re.findall(r"https?://[^)]+", body)
        self.assertEqual(len(urls), len(set(urls)))
        readme = next(item for item in trusted["sources"] if item["id"] == ref["source_id"])
        for start, end in ((0, 0), (1, 1), (2, 3)):
            self.assertIn(evidence.citation(readme, start, end)["url"], urls)
        for revision in (trusted["firstRevision"], trusted["latestRevision"]):
            self.assertIn(f"/blob/{revision}/{package['package']}/_metadata.json", body)

    def test_unique_multi_package_evidence_still_enforces_link_budget(self):
        draft, trusted = multipackage_fixture(10)
        result = service.ReviewService(trusted).call({"operation": "preflight", "draft": draft})
        self.assertFalse(result["ok"])
        self.assertNotIn("submission", result)
        self.assertIn("publication_link_budget", {item["code"] for item in result["errors"]})
        final = {**draft, "registrations": []}
        final["preflight"] = {"attempt": 1, "digest": contract.digest(final)}
        with self.assertRaisesRegex(contract.ReviewError, "publication_link_budget"):
            contract.prepare_output(envelope(final), trusted)


class BoundedAttributionTests(unittest.TestCase):
    FILTER = SCRIPT.with_name("mgmt_sdk_review_request.jq")

    def breaking_fixture(self, count=42):
        draft, trusted = fixture()
        entries = trusted["breakingChangeContext"][0]["introducedEntries"]
        for index in range(count):
            entries.append(
                {
                    "text": f"Removed operation {index}.",
                    "release": "2.0.0",
                    "startLine": index + 5,
                    "endLine": index + 5,
                    "changeKind": "added",
                }
            )
        package = contract.draft_template(trusted)["packages"][0]
        draft["packages"][0].update(
            attribution=package["attribution"], attribution_omitted=package["attribution_omitted"]
        )
        for entry in draft["packages"][0]["attribution"]:
            entry["explanation"] = "The removed operation could not be located in the pinned specification."
        return draft, trusted

    def bound(self, draft, operation="preflight", check=True):
        result = subprocess.run(
            ["jq", "--arg", "operation", operation, "-f", str(self.FILTER)],
            input=json.dumps(draft, ensure_ascii=False),
            capture_output=True,
            encoding="utf-8",
            check=check,
            timeout=10,
        )
        if not check:
            return result
        wrapper = json.loads(result.stdout)
        self.assertLessEqual(
            len(json.dumps(wrapper, separators=(",", ":"), ensure_ascii=False).encode()),
            contract.MAX_REVIEW_REQUEST_BYTES,
        )
        request = json.loads(wrapper["request"])
        self.assertEqual(operation, request["operation"])
        return request["draft"]

    def test_describe_caps_work_and_preserves_full_trusted_snapshot(self):
        for count in (0, 1, 8, 9, 42, 43):
            with self.subTest(count=count):
                draft, trusted = self.breaking_fixture(count)
                host = service.ReviewService(trusted)
                description = host.call({"operation": "describe"})
                selected = min(count, contract.MAX_INITIAL_ATTRIBUTION_ENTRIES)
                self.assertEqual(selected, len(description["packages"][0]["entries"]))
                self.assertEqual(count - selected, description["packages"][0]["omittedEntries"])
                self.assertEqual(count, description["packages"][0]["totalEntries"])
                self.assertEqual(count, len(host.context["breakingChangeContext"][0]["introducedEntries"]))
                self.assertEqual(draft["packages"][0]["attribution_omitted"], count - selected)
                self.assertEqual([], contract.schema_errors(description["draft"]))

    def test_selection_is_round_robin_and_uses_each_packages_prefix(self):
        _, trusted = multipackage_fixture(3)
        for package in trusted["breakingChangeContext"]:
            package["introducedEntries"] = [
                {"text": str(i), "release": "2.0.0", "startLine": i + 1, "endLine": i + 1, "changeKind": "added"}
                for i in range(10)
            ]
        draft = contract.draft_template(trusted)
        self.assertEqual([3, 3, 2], [len(item["attribution"]) for item in draft["packages"]])
        self.assertEqual([7, 7, 8], [item["attribution_omitted"] for item in draft["packages"]])
        for package, breaking in zip(draft["packages"], trusted["breakingChangeContext"]):
            self.assertEqual(
                [evidence.entry_id(item) for item in breaking["introducedEntries"][:len(package["attribution"])]],
                [item["entry_id"] for item in package["attribution"]],
            )

    def test_partial_review_publishes_checked_prefix_and_explicit_omissions(self):
        draft, trusted = self.breaking_fixture()
        bounded = self.bound(draft)
        result = service.ReviewService(trusted).call({"operation": "preflight", "draft": bounded})
        self.assertTrue(result["ok"], result)
        self.assertEqual("partial", result["reviewCompleteness"])
        body = contract.prepare_output(envelope(result["submission"]["data"]), trusted)["items"][0]["body"]
        self.assertIn("34 of 42 breaking-change entries were not reviewed", body)
        self.assertIn("Breaking-change attribution truncated", body)
        self.assertIn("Unreviewed breaking changes", body)
        self.assertIn("Omitted changelog entries", body)
        self.assertIn("CHANGELOG.md#L13-L46", body)
        self.assertIn("Removed operation 7.", body)
        self.assertNotIn("Removed operation 8.", body)
        self.assertIn("README snippets", body)
        self.assertNotIn("Review completeness: complete", body)
        for count in (0, 1):
            complete, context = self.breaking_fixture(count)
            if count:
                complete["packages"][0]["attribution"][0]["cause"] = "human_review"
            answer = contract.preflight(self.bound(complete), context)
            self.assertTrue(answer["ok"], answer)
            if not count:
                self.assertEqual("complete", answer["reviewCompleteness"])

    def test_incorrect_counts_gaps_and_forged_post_preflight_omissions_are_rejected(self):
        draft, trusted = self.breaking_fixture()
        for mutation in ("count", "gap", "duplicate", "negative", "overflow"):
            current = copy.deepcopy(draft)
            package = current["packages"][0]
            if mutation == "count":
                package["attribution_omitted"] -= 1
            elif mutation == "gap":
                package["attribution"][0]["entry_id"] = evidence.entry_id(
                    trusted["breakingChangeContext"][0]["introducedEntries"][8]
                )
            elif mutation == "duplicate":
                package["attribution"][0] = copy.deepcopy(package["attribution"][1])
            elif mutation == "negative":
                package["attribution_omitted"] = -1
            else:
                package["attribution_omitted"] = 43
            with self.subTest(mutation=mutation):
                self.assertFalse(contract.preflight(current, trusted)["ok"])
        payload = submit(draft, trusted)
        payload["items"][0]["data"]["packages"][0]["attribution_omitted"] = 0
        with self.assertRaises(contract.ReviewError):
            contract.prepare_output(payload, trusted)

    def test_encoded_boundary_trims_whole_rows_without_changing_findings_or_evidence(self):
        draft, _ = self.breaking_fixture(1)
        package = draft["packages"][0]
        package["findings"] = [
            {
                "check": "README snippets", "severity": "Warning", "title": "Snippet mismatch",
                "observation": "", "remediation": "Use the documented signature.",
                "sources": copy.deepcopy(package["checks"]["README snippets"]["sources"]),
            }
        ]
        request = {"operation": "preflight", "draft": draft}
        wrapper = {"request": json.dumps(request, separators=(",", ":"), ensure_ascii=False)}
        base_bytes = len(json.dumps(wrapper, separators=(",", ":"), ensure_ascii=False).encode())
        for size in (8999, 9000, 9001, 10240, 10241):
            current = copy.deepcopy(draft)
            current["packages"][0]["findings"][0]["observation"] = "x" * (size - base_bytes)
            if size > 9001:
                failure = self.bound(current, check=False)
                self.assertNotEqual(0, failure.returncode)
                self.assertIn("Checks and findings exceed", failure.stderr)
                continue
            bounded = self.bound(current)
            self.assertEqual(current["packages"][0]["checks"], bounded["packages"][0]["checks"])
            self.assertEqual(current["packages"][0]["findings"], bounded["packages"][0]["findings"])
            if size <= contract.MAX_REVIEW_REQUEST_BYTES:
                self.assertEqual(current, bounded)
            elif size == 9001:
                self.assertEqual([], bounded["packages"][0]["attribution"])
                self.assertEqual(1, bounded["packages"][0]["attribution_omitted"])

    def test_unicode_and_string_escaping_are_counted_and_fixed_content_fails_explicitly(self):
        draft, _ = self.breaking_fixture()
        draft["packages"][0]["attribution"][0]["explanation"] = '"\\\u00e9' * 2000
        bounded = self.bound(draft)
        self.assertEqual([], bounded["packages"][0]["attribution"])
        self.assertEqual(42, bounded["packages"][0]["attribution_omitted"])
        self.assertEqual(draft["packages"][0]["checks"], bounded["packages"][0]["checks"])
        draft["packages"][0]["checks"]["README snippets"]["reason"] = "x" * 10000
        failure = self.bound(draft, check=False)
        self.assertNotEqual(0, failure.returncode)
        self.assertIn("Checks and findings exceed", failure.stderr)
        self.assertEqual("", failure.stdout)


class PublicSpecificationReadsTests(unittest.TestCase):
    def read(self):
        return service.read_public_specification_file(
            "Azure/azure-rest-api-specs", NEW_SPEC, "specification/example/@Widget (preview).tsp"
        )

    def test_public_reads_never_use_tokens_or_global_authenticated_opener(self):
        with mock.patch.dict(
            os.environ, {"GH_TOKEN": "repository-token", "GITHUB_TOKEN": "publisher-token"}
        ), mock.patch.object(service.urllib.request, "build_opener") as build, mock.patch.object(
            service.urllib.request, "urlopen"
        ) as global_open:
            response = build.return_value.open.return_value.__enter__.return_value
            response.headers = {"Content-Length": "15"}
            response.read.return_value = b"model Widget {}"
            result = self.read()
            self.assertEqual("available", result["status"])
            self.assertEqual("model Widget {}", result["content"])
            request = build.return_value.open.call_args.args[0]
            self.assertEqual(
                f"https://raw.githubusercontent.com/Azure/azure-rest-api-specs/{NEW_SPEC}/"
                "specification/example/%40Widget%20%28preview%29.tsp",
                request.full_url,
            )
            self.assertEqual("GET", request.get_method())
            self.assertEqual({"User-agent": "azure-sdk-python-mgmt-review"}, dict(request.header_items()))
            self.assertIsInstance(build.call_args.args[0], service.NoSpecificationRedirects)
            self.assertEqual(service.API_TIMEOUT_SECONDS, build.return_value.open.call_args.kwargs["timeout"])
            response.read.assert_called_once_with(service.MAX_TEXT_FILE_BYTES + 1)
            global_open.assert_not_called()

    def test_size_limit_applies_with_absent_or_misleading_headers(self):
        limit = service.MAX_TEXT_FILE_BYTES
        for header, payload, expected, reads in (
            (str(limit + 1), b"", "truncated", 0),
            (None, b"x" * (limit + 1), "truncated", 1),
            ("1", b"x" * (limit + 1), "truncated", 1),
            (str(limit), b"x" * limit, "available", 1),
        ):
            with self.subTest(header=header), mock.patch.object(service.urllib.request, "build_opener") as build:
                response = build.return_value.open.return_value.__enter__.return_value
                response.headers = {} if header is None else {"Content-Length": header}
                response.read.return_value = payload
                result = self.read()
                self.assertEqual(expected, result["status"])
                self.assertEqual(reads, response.read.call_count)
                if expected == "truncated":
                    self.assertNotIn("content", result)
                else:
                    self.assertEqual(limit, len(result["content"]))

    def test_http_errors_are_explicit_without_authenticated_retry(self):
        for code in (301, 302, 307, 308, 401, 403, 404, 429, 500):
            with self.subTest(code=code), mock.patch.object(service.urllib.request, "build_opener") as build:
                error = urllib.error.HTTPError(
                    "https://raw.githubusercontent.com/", code, "Unavailable", {}, io.BytesIO()
                )
                build.return_value.open.side_effect = error
                result = self.read()
                record = evidence.source_record("Azure/azure-rest-api-specs", result, PACKAGE, "specification")
                self.assertEqual("missing" if code == 404 else "access_error", record["status"])
                self.assertIsNone(record["sha256"])
                self.assertEqual(0, record["lineCount"])
                self.assertIn(f"HTTP {code}", record["error"])
                self.assertIn("no authenticated fallback", record["error"])
                self.assertEqual(1, build.return_value.open.call_count)

    def test_redirect_handler_rejects_changed_hosts_and_mutable_revisions(self):
        handler = service.NoSpecificationRedirects()
        for target in (
            "https://evil.invalid/content",
            "http://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/file",
            "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/file",
        ):
            self.assertIsNone(handler.redirect_request(None, None, 302, "Redirect", {}, target))

    def test_invalid_content_headers_and_network_errors_remain_unverified(self):
        for header, content, error in (
            (None, b"\xff", None),
            ("invalid", b"model Widget {}", None),
            ("-1", b"model Widget {}", None),
            ("30", b"model Widget {}", None),
            (None, b"", TimeoutError("Read timed out")),
            (None, b"", urllib.error.URLError("Connection unavailable")),
            (None, b"", service.http.client.IncompleteRead(b"partial", 20)),
        ):
            with self.subTest(header=header, error=error), mock.patch.object(
                service.urllib.request, "build_opener"
            ) as build:
                response = build.return_value.open.return_value.__enter__.return_value
                response.headers = {} if header is None else {"Content-Length": header}
                response.read.return_value = content
                response.read.side_effect = error
                result = self.read()
                self.assertEqual("unverified", result["status"])
                self.assertNotIn("content", result)
                self.assertIn("Could not read public specification", result["error"])
                self.assertEqual(1, build.return_value.open.call_count)

    def test_untrusted_identities_never_reach_public_reader(self):
        for repository, revision in (
            ("Azure/azure-rest-api-specs", "main"),
            ("evil.invalid/path/extra", NEW_SPEC),
            ("Azure/azure-rest-api-specs?query", NEW_SPEC),
        ):
            _, trusted = fixture()
            trusted["breakingChangeContext"][0]["specificationSources"]["latest"].update(
                repository=repository, revision=revision
            )
            with mock.patch.object(service, "read_public_specification_file") as read:
                with self.assertRaisesRegex(contract.ReviewError, "wrong_revision"):
                    service.EvidenceRegistry(trusted).register(
                        PACKAGE, repository, revision, "specification/example/main.tsp"
                    )
                read.assert_not_called()

    def test_only_sdk_collection_receives_repository_credentials(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        collector_job = source.split("  review_context:\n", 1)[1].split("\n  safe_outputs:", 1)[0]
        self.assertIn("GH_TOKEN: ${{ github.token }}", collector_job)
        for label in ("Validate and render management SDK review", "Start read-only evidence and preflight service"):
            env = source.split("name: " + label, 1)[0].rsplit("- env:", 1)[1]
            self.assertNotIn("GH_TOKEN", env)
        lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
        publisher = lock.split("\n  safe_outputs:\n", 1)[1].split("\n    timeout-minutes:", 1)[0]
        self.assertIn("permissions:\n      pull-requests: write", publisher)
        self.assertNotIn("contents: read", publisher)


class ServiceAndPublicationTests(unittest.TestCase):
    def test_canonical_draft_covers_packages_checks_and_entry_ids_without_claiming_review(self):
        _, trusted = multipackage_fixture(2)
        trusted["breakingChangeContext"][0]["introducedEntries"] = [
            {"text": "Removed an operation.", "release": "2.0.0", "startLine": 4, "endLine": 4, "changeKind": "added"}
        ]
        host = service.ReviewService(trusted)
        draft = host.call({"operation": "describe"})["draft"]
        self.assertEqual([], contract.schema_errors(draft))
        self.assertEqual(trusted["affectedPackages"], [item["package"] for item in draft["packages"]])
        for package in draft["packages"]:
            self.assertEqual(set(evidence.SEMANTIC_CHECKS), set(package["checks"]))
            self.assertTrue(all(check["outcome"] == "unverified" for check in package["checks"].values()))
        self.assertEqual(
            evidence.entry_id(trusted["breakingChangeContext"][0]["introducedEntries"][0]),
            draft["packages"][0]["attribution"][0]["entry_id"],
        )
        self.assertFalse(contract.preflight(draft, trusted)["ok"])
        draft["packages"].clear()
        self.assertEqual(2, len(host.call({"operation": "describe"})["draft"]["packages"]))

    def test_empty_canonical_draft_still_requires_complete_discovery(self):
        _, trusted = fixture()
        trusted["affectedPackages"] = []
        trusted["breakingChangeContext"] = []
        draft = contract.draft_template(trusted)
        self.assertEqual({"schema_version": "2", "outcome": "not_applicable", "packages": []}, draft)
        trusted["packageDiscovery"] = {"status": "unverified", "error": "Changed-file pagination was incomplete."}
        self.assertFalse(contract.preflight(draft, trusted)["ok"])

    def test_pinned_file_lines_do_not_require_a_changed_file_or_diff_anchor(self):
        # Run 36515583252 mislabeled an unchanged README citation as unavailable.
        draft, trusted = fixture()
        source = draft["packages"][0]["checks"]["README snippets"]["sources"][0]
        record = next(item for item in trusted["sources"] if item["id"] == source["source_id"])
        old = evidence.citation(record, source["start_line"], source["end_line"])
        old.update(line_status="unavailable", reason="README was not changed in the PR.")
        with self.assertRaisesRegex(contract.ReviewError, "citation_state_conflict"):
            contract.source_identity(old, "readme")
        self.assertTrue(contract.preflight(draft, trusted)["ok"])

    def test_production_shape_failures_leave_semantic_budget_for_correction(self):
        # Run 36528442672 spent all three attempts on these successive draft errors.
        draft, trusted = fixture()
        host = service.ReviewService(trusted)
        broken = copy.deepcopy(draft)
        broken["attributions"] = []
        broken["packages"][0].pop("attribution")
        for current in (broken, {key: value for key, value in broken.items() if key != "attributions"}):
            result = host.call({"operation": "preflight", "draft": current})
            self.assertFalse(result["ok"])
            self.assertEqual("format", result["phase"])
            self.assertEqual(0, result["attempt"])
            self.assertEqual(3, result["correctionsRemaining"])
            self.assertNotIn("submission", result)
        broken = copy.deepcopy(draft)
        for check in broken["packages"][0]["checks"].values():
            check["reason"] = "The signature was checked."
            for source in check["sources"]:
                source["reason"] = "The source supports this check."
        result = host.call({"operation": "preflight", "draft": broken})
        self.assertFalse(result["ok"])
        self.assertEqual(1, result["attempt"])
        self.assertEqual({"citation_state_conflict"}, {error["code"] for error in result["errors"]})
        result = host.call({"operation": "preflight", "draft": draft})
        self.assertTrue(result["ok"], result)
        self.assertEqual(2, result["attempt"])
        self.assertEqual(1, len(contract.prepare_output(envelope(result["submission"]["data"]), trusted)["items"]))

    def test_shape_checks_are_bounded_and_never_authorize_publication(self):
        draft, trusted = fixture()
        host = service.ReviewService(trusted)
        for number in range(10):
            result = host.call({"operation": "check", "draft": draft})
            self.assertTrue(result["ok"])
            self.assertEqual(0, result["attempt"])
            self.assertEqual(9 - number, result["formatChecksRemaining"])
            self.assertNotIn("submission", result)
        for operation in ("check", "preflight"):
            with self.assertRaisesRegex(contract.ReviewError, "format_check_limit"):
                host.call({"operation": operation, "draft": draft})
        result = host.call({"operation": "incomplete", "reason": "Format correction budget was exhausted."})
        self.assertIn("incompleteSubmission", result)
        self.assertNotIn("submission", result)

    def test_incomplete_is_terminal_and_not_a_clean_review(self):
        draft, trusted = fixture()
        host = service.ReviewService(trusted)
        for value in ("", "todo", "Review pending", "x" * 12001, False):
            with self.subTest(value=str(value)[:20]), self.assertRaises(contract.ReviewError):
                host.call({"operation": "incomplete", "reason": value})
        result = host.call({"operation": "incomplete", "reason": "Required source could not be retrieved."})
        payload = {"items": [{"type": "noop", **result["incompleteSubmission"]}], "errors": []}
        self.assertEqual(payload, contract.prepare_output(payload, trusted))
        with self.assertRaisesRegex(contract.ReviewError, "correction_limit"):
            host.call({"operation": "preflight", "draft": draft})
        accepted = service.ReviewService(trusted)
        self.assertTrue(accepted.call({"operation": "preflight", "draft": draft})["ok"])
        with self.assertRaisesRegex(contract.ReviewError, "correction_limit"):
            accepted.call({"operation": "incomplete", "reason": "Discard the accepted review."})

    def test_incomplete_does_not_bypass_transport_validation(self):
        draft, trusted = fixture()
        item = {"type": "noop", **contract.incomplete_submission("Three semantic attempts were exhausted.")}
        for payload in (
            {"items": [item], "errors": ["Rejected extra submission"]},
            {"items": [item, item], "errors": []},
            {"items": [item, *submit(draft, trusted)["items"]], "errors": []},
            {"items": [{**item, "item_number": 123}], "errors": []},
            {"items": [{**item, "body": "Publish this instead"}], "errors": []},
            {"items": [{**item, "message": "No issues found."}], "errors": []},
            {"items": [{**item, "message": contract.INCOMPLETE + "todo"}], "errors": []},
            {"items": [{**item, "message": None}], "errors": []},
        ):
            with self.subTest(payload=payload), self.assertRaises(contract.ReviewError):
                contract.prepare_output(payload, trusted)

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
        expected = trusted["pullRequestNumber"]
        self.assertEqual(str(expected), payload["items"][0]["item_number"])
        for number in (expected, str(expected)):
            payload["items"][0]["item_number"] = number
            output = contract.prepare_output(payload, trusted)
            self.assertEqual({"type", "body"}, set(output["items"][0]))
        for number in (
            False,
            True,
            float(expected),
            None,
            expected + 1,
            str(expected + 1),
            f"0{expected}",
            f"+{expected}",
            f" {expected}",
            f"{expected} ",
            f"{expected}.0",
            f"{expected}e0",
            "４９１０７",
            "#aw_example",
            "",
            [],
            {},
        ):
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
        with mock.patch.object(service.urllib.request, "build_opener") as build:
            response = build.return_value.open.return_value.__enter__.return_value
            response.headers = {}
            response.read.return_value = b'// Definition\n@renamedFrom(Versions.v1, "Widget")\nmodel NewWidget {}\n'
            fetch = build.return_value.open
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
            resolver = service.EvidenceRegistry(trusted)
            body = contract.prepare_output(envelope(result["submission"]["data"]), trusted, resolver.resolve)["items"][
                0
            ]["body"]
            self.assertIn("TypeSpec/API", body)
            self.assertIn("README.md", body)
            self.assertEqual(2, fetch.call_count)
            for call in fetch.call_args_list:
                request = call.args[0]
                self.assertEqual(
                    f"https://raw.githubusercontent.com/Azure/azure-rest-api-specs/{NEW_SPEC}/specification/example/main.tsp",
                    request.full_url,
                )
                self.assertIsNone(request.get_header("Authorization"))
            fetch.side_effect = urllib.error.HTTPError(
                "https://raw.githubusercontent.com/", 403, "Forbidden", {}, io.BytesIO()
            )
            with self.assertRaisesRegex(contract.ReviewError, "evidence_changed"):
                contract.prepare_output(
                    envelope(result["submission"]["data"]), trusted, service.EvidenceRegistry(trusted).resolve
                )
            fetch.side_effect = None
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
            service,
            "read_public_specification_file",
            side_effect=lambda repository, revision, path: {
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
    def test_bounded_attribution_survives_ingestion_and_publication(self):
        helper = BoundedAttributionTests()
        draft, trusted = helper.breaking_fixture()
        draft = helper.bound(draft)
        result = service.ReviewService(trusted).call({"operation": "preflight", "draft": draft})
        self.assertTrue(result["ok"], result)
        harness = Path(__file__).with_name("mgmt_review_runtime.cjs")
        response = subprocess.run(
            ["node", str(harness)],
            input=json.dumps(
                {
                    "mode": "submit",
                    "submissions": [result["submission"]],
                    "toolConfig": lock_json("GH_AW_SAFE_OUTPUTS_CONFIG")["add_comment"],
                    "validation": lock_json("GH_AW_VALIDATION_JSON"),
                }
            ),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        ingested = json.loads(response.stdout)["ingestion"][0]
        self.assertTrue(ingested["isValid"], ingested)
        self.assertEqual(34, ingested["normalizedItem"]["data"]["packages"][0]["attribution_omitted"])
        prepared = contract.prepare_output({"items": [ingested["normalizedItem"]], "errors": []}, trusted)
        response = subprocess.run(
            ["node", str(harness)],
            input=json.dumps({"mode": "publish", "payload": prepared}),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        published = json.loads(response.stdout)
        self.assertEqual(1, published["writes"])
        self.assertIn("Review completeness: partial", published["comment"]["body"])
        self.assertIn("34 of 42 breaking-change entries were not reviewed", published["comment"]["body"])
        self.assertIn("Omitted changelog entries", published["comment"]["body"])

    def test_live_manual_targets_survive_tool_ingestion_and_publication(self):
        harness = Path(__file__).with_name("mgmt_review_runtime.cjs")
        tool_config = lock_json("GH_AW_SAFE_OUTPUTS_CONFIG")["add_comment"]
        # Activation cannot resolve needs.review_context.outputs.pr_number yet.
        self.assertEqual("", tool_config["target"])
        for pr in (49229, 49247):
            for event in ("workflow_dispatch", "pull_request_target"):
                for as_integer in (False, True):
                    with self.subTest(pr=pr, event=event, as_integer=as_integer):
                        draft, trusted = fixture()
                        trusted["pullRequestNumber"] = pr
                        result = service.ReviewService(trusted).call({"operation": "preflight", "draft": draft})
                        submission = result["submission"]
                        self.assertEqual(str(pr), submission["item_number"])
                        if as_integer:
                            submission["item_number"] = pr
                        submissions = [submission]
                        if event == "workflow_dispatch":
                            submissions.insert(
                                0, {key: value for key, value in submission.items() if key != "item_number"}
                            )
                        response = subprocess.run(
                            ["node", str(harness)],
                            input=json.dumps(
                                {
                                    "mode": "submit",
                                    "eventName": event,
                                    "prNumber": pr,
                                    "submissions": submissions,
                                    "toolConfig": tool_config,
                                    "validation": lock_json("GH_AW_VALIDATION_JSON"),
                                }
                            ),
                            capture_output=True,
                            text=True,
                            check=True,
                            timeout=30,
                        )
                        transport = json.loads(response.stdout)
                        if event == "workflow_dispatch":
                            self.assertTrue(transport["responses"][0]["isError"], transport)
                        self.assertEqual(1, len(transport["appended"]), transport)
                        ingested = transport["ingestion"][0]
                        self.assertTrue(ingested["isValid"], ingested)
                        self.assertEqual(submission["item_number"], ingested["normalizedItem"]["item_number"])
                        prepared = contract.prepare_output(
                            {"items": [ingested["normalizedItem"]], "errors": []}, trusted
                        )
                        self.assertNotIn("item_number", prepared["items"][0])
                        config = lock_json("GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG")["add_comment"]
                        self.assertEqual("${{ needs.review_context.outputs.pr_number }}", config["target"])
                        config["target"] = str(pr)
                        response = subprocess.run(
                            ["node", str(harness)],
                            input=json.dumps(
                                {
                                    "mode": "publish",
                                    "eventName": event,
                                    "prNumber": pr,
                                    "payload": prepared,
                                    "handlerConfig": config,
                                    "existing": True,
                                }
                            ),
                            capture_output=True,
                            text=True,
                            check=True,
                            timeout=30,
                        )
                        published = json.loads(response.stdout)
                        self.assertTrue(published["result"]["success"], published)
                        self.assertEqual(pr, published["comment"]["issue_number"])
                        self.assertEqual(1, published["writes"])
                        self.assertEqual(1, published["hides"])

    def publish_multi_package(self, draft, trusted):
        payload = submit(draft, trusted)
        payload["items"][0]["body"] = contract.SUBMISSION
        harness = Path(__file__).with_name("mgmt_review_runtime.cjs")
        result = subprocess.run(
            ["node", str(harness)],
            input=json.dumps(
                {"mode": "ingest", "item": payload["items"][0], "validation": lock_json("GH_AW_VALIDATION_JSON")}
            ),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        ingested = json.loads(result.stdout)
        self.assertTrue(ingested["isValid"], ingested)
        prepared = contract.prepare_output({"items": [ingested["normalizedItem"]], "errors": []}, trusted)
        result = subprocess.run(
            ["node", str(harness)],
            input=json.dumps({"mode": "publish", "payload": prepared, "existing": True}),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        published = json.loads(result.stdout)
        self.assertTrue(published["result"]["success"], published)
        self.assertEqual(1, published["writes"])
        self.assertEqual(1, published["hides"])
        self.assertEqual(49107, published["comment"]["issue_number"])
        body = published["comment"]["body"]
        for url in re.findall(r"https?://[^)]+", prepared["items"][0]["body"]):
            self.assertIn(url, body)
        for name in trusted["affectedPackages"]:
            self.assertIn(name, body)
        return body

    def test_multi_package_citations_survive_ingestion_and_publication(self):
        draft, trusted = multipackage_fixture()
        body = self.publish_multi_package(draft, trusted)
        for number in range(1, 36):
            self.assertIn(f"[E{number}]", body)
            self.assertIn(f"| E{number} |", body)

    def test_multi_package_attribution_keeps_shared_specification_and_historical_evidence(self):
        draft, trusted = multipackage_fixture(2)
        expected_urls = set()
        for package, breaking in zip(draft["packages"], trusted["breakingChangeContext"]):
            name = package["package"]
            entry = {
                "text": "Renamed <Widget> | @clientName.",
                "release": "1.0.0b1 (2026-09-28)",
                "startLine": 1,
                "endLine": 1,
                "changeKind": "added",
            }
            breaking["introducedEntries"] = [entry]
            spec_refs = []
            for revision in (NEW_SPEC, breaking["specificationSources"]["mergeBase"]["revision"]):
                spec = evidence.source_record(
                    "Azure/azure-rest-api-specs",
                    {
                        "path": "specification/example/@renamedFrom(Widget)&\uff21Widget file.tsp",
                        "revision": revision,
                        "status": "available",
                        "content": "model Widget {}",
                    },
                    name,
                    "specification",
                )
                trusted["sources"].append(spec)
                spec_refs.append(reference(spec))
                expected_urls.add(evidence.citation(spec, 1, 1)["url"])
            sdk = next(
                item for item in trusted["sources"] if item["package"] == name and item["path"].endswith("/README.md")
            )
            historical = evidence.source_record(REPO, {**sdk, "revision": trusted["mergeBaseRevision"]}, name)
            trusted["sources"].append(historical)
            expected_urls.add(evidence.citation(historical, 1, 1)["url"])
            package["attribution"] = [
                {
                    "entry_id": evidence.entry_id(entry),
                    "cause": "typespec_api",
                    "explanation": '@renamedFrom("Widget") explains the <Widget> rename.',
                    "sources": spec_refs,
                    "sdk_context": [reference(historical)],
                }
            ]
        body = self.publish_multi_package(draft, trusted)
        for url in expected_urls:
            self.assertEqual(1, body.count(urllib.parse.quote(url, safe="/:%#._-~")))
        self.assertEqual(2, body.count('@renamedFrom("Widget")'))
        self.assertIn("<Widget>", body)
        self.assertNotIn("%2520", body)
        self.assertIn("TypeSpec/API", body)

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
                broken = copy.deepcopy(draft)
                broken["packages"][0]["checks"]["README snippets"]["sources"][0]["end_line"] = 999
                for operation, current in (("check", draft), ("preflight", broken), ("preflight", draft)):
                    command = re.search(rf"(?m)^jq --arg operation {operation} -f (\S+) ", SOURCE)
                    self.assertIsNotNone(command)
                    filter_path = SCRIPT.with_name(Path(command[1]).name)
                    arguments = subprocess.run(
                        [jq, "--arg", "operation", operation, "-f", str(filter_path)],
                        input=json.dumps(current),
                        capture_output=True,
                        text=True,
                        check=True,
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
                    if operation == "check":
                        self.assertTrue(answer["ok"])
                        self.assertEqual("format", answer["phase"])
                        self.assertEqual(0, answer["attempt"])
                        self.assertNotIn("submission", answer)
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
                            "toolConfig": lock_json("GH_AW_SAFE_OUTPUTS_CONFIG")["add_comment"],
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
                    "toolConfig": lock_json("GH_AW_SAFE_OUTPUTS_CONFIG")["add_comment"],
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
        incomplete = host.call(
            {"operation": "incomplete", "reason": "Three semantic attempts failed to cover the trusted packages."}
        )
        expression = re.search(r"(?m)^jq '([^']+)' .* \| safeoutputs noop \.$", SOURCE)[1]
        result = subprocess.run(
            [shutil.which("jq") or os.environ["JQ"], expression],
            input=json.dumps(incomplete),
            capture_output=True,
            text=True,
            check=True,
        )
        response = subprocess.run(
            ["node", str(harness)],
            input=json.dumps(
                {
                    "mode": "ingest",
                    "item": {"type": "noop", **json.loads(result.stdout)},
                    "validation": lock_json("GH_AW_VALIDATION_JSON"),
                }
            ),
            capture_output=True,
            text=True,
            check=True,
        )
        ingested = json.loads(response.stdout)
        self.assertTrue(ingested["isValid"], ingested)
        prepared = contract.prepare_output({"items": [ingested["normalizedItem"]], "errors": []}, trusted)
        response = subprocess.run(
            ["node", str(harness)],
            input=json.dumps({"mode": "publish", "payload": prepared, "existing": True}),
            capture_output=True,
            text=True,
            check=True,
        )
        recorded = json.loads(response.stdout)
        self.assertTrue(recorded["result"]["success"], recorded)
        self.assertIn(contract.INCOMPLETE, recorded["result"]["message"])
        self.assertEqual(0, recorded["hides"])
        self.assertEqual(0, recorded["writes"])
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
