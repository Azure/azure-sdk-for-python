import copy
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock
from urllib.parse import quote

WORKFLOW = Path(__file__).parents[1] / "mgmt-sdk-pr-review.md"
SCRIPT = WORKFLOW.parent / "scripts" / "mgmt_sdk_review_contract.py"
SPEC = importlib.util.spec_from_file_location("mgmt_sdk_review_contract", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SOURCE = WORKFLOW.read_text(encoding="utf-8")
FIXTURES = Path(__file__).parent / "fixtures" / "mgmt-review"
PACKAGE = "sdk/example/azure-mgmt-example"
REPO = "Azure/azure-sdk-for-python"
FIRST, HEAD, BASE, TOOLING, OLD_SPEC, NEW_SPEC = (char * 40 for char in "abcdef")


def reference(path="README.md", revision=HEAD, repo=REPO, package=PACKAGE):
    return {
        "url": f"https://github.com/{repo}/blob/{revision}/{package}/{path}#L2-L3",
        "line_status": "verified",
        "reason": "",
    }


def context():
    return {
        "repository": REPO,
        "pullRequestNumber": 49107,
        "toolingRevision": TOOLING,
        "firstRevision": FIRST,
        "latestRevision": HEAD,
        "mergeBaseRevision": BASE,
        "affectedPackages": [PACKAGE],
        "packageDiscovery": {"status": "complete", "error": None},
        "commitDiscovery": {"status": "complete", "error": None},
        "apiVersionDrift": [
            {
                "packagePath": PACKAGE,
                "metadataPath": PACKAGE + "/_metadata.json",
                "firstRevision": FIRST,
                "latestRevision": HEAD,
                "firstApiVersion": "2026-01-01",
                "latestApiVersion": "2026-01-01",
                "status": "unchanged",
                "error": None,
            }
        ],
        "breakingChangeContext": [
            {
                "packagePath": PACKAGE,
                "changelogPath": PACKAGE + "/CHANGELOG.md",
                "status": "complete",
                "collectionIssues": [],
                "introducedEntries": [],
                "emptyBreakingChangeSections": [],
                "releaseBaseline": {"status": "available", "revision": BASE},
                "specificationSources": {
                    "mergeBase": {
                        "status": "available",
                        "repository": "Azure/azure-rest-api-specs",
                        "revision": OLD_SPEC,
                    },
                    "latest": {"status": "available", "repository": "Azure/azure-rest-api-specs", "revision": NEW_SPEC},
                },
            }
        ],
    }


def review():
    return {
        "schema_version": "1",
        "outcome": "reviewed",
        "packages": [
            {
                "package": PACKAGE,
                "checks": [
                    {"name": name, "outcome": "completed", "reason": "", "sources": [reference()]}
                    for name in MODULE.CHECKS
                ],
                "findings": [],
                "attribution": {"outcome": "no_entries", "initial_release": False, "reason": "", "entries": []},
            }
        ],
    }


def envelope(data):
    return {
        "items": [
            {
                "type": "add_comment",
                "data": data,
                "temporary_id": "aw_fixture",
                "body": MODULE.SUBMISSION
                + "\n\nStructured data:\n```json\n"
                + json.dumps(data, ensure_ascii=False, indent=2)
                + "\n```",
            }
        ],
        "errors": [],
    }


def add_entry(data, trusted, *, direct=False, release="2.0.0 (2026-09-22)"):
    entries = trusted["breakingChangeContext"][0]["introducedEntries"]
    index = len(entries)
    entries.append(
        {
            "text": "Removed `Widget`.\nUse `NewWidget` | instead.",
            "release": release,
            "startLine": 5 + index * 3,
            "endLine": 6 + index * 3,
            "changeKind": "added",
        }
    )
    attribution = data["packages"][0]["attribution"]
    attribution["outcome"] = "entries"
    attribution["entries"].append(
        {
            "entry_index": index,
            "release": release,
            "cause": "typespec_api" if direct else "human_review",
            "confidence": "high" if direct else "not_applicable",
            "explanation": (
                'The @renamedFrom(Versions.v1, "Widget") annotation explains the rename.'
                if direct
                else "The old definition could not be located in the pinned specification."
            ),
            "sources": (
                [reference("main.tsp", NEW_SPEC, "Azure/azure-rest-api-specs", "specification/example")]
                if direct
                else []
            ),
        }
    )


def lock_json(name):
    lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
    block = lock.split(name + ": |\n", 1)[1]
    return json.JSONDecoder().raw_decode(textwrap.dedent(block).lstrip())[0]


class StructuredReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = review()
        self.context = context()
        self.package = self.data["packages"][0]
        self.breaking = self.context["breakingChangeContext"][0]

    def render(self):
        return MODULE.prepare_output(envelope(self.data), self.context)["items"][0]["body"]

    def reject(self, field):
        with self.assertRaisesRegex(ValueError, re.escape(field)):
            self.render()

    def test_no_findings_deterministic(self):
        body = self.render()
        self.assertEqual(body, self.render())
        self.assertIn("**Findings:** None.", body)
        self.assertIn("**Unverified checks:** None.", body)
        self.assertIn("No newly added or modified entries.", body)
        self.assertTrue(body.startswith(MODULE.MARKER))
        self.assertIn("API-version drift", body)
        self.assertNotIn("Structured data:", body)
        self.package["checks"].reverse()
        self.assertEqual(body, self.render())

    def test_ordinary_findings_and_partial_checks(self):
        self.package["findings"] = [
            {
                "severity": "Blocking",
                "check": "Version consistency",
                "title": "Versions differ",
                "observation": "Changelog has 2.0.0 but package metadata has 1.0.0.",
                "remediation": "Align package and changelog versions.",
                "sources": [reference("CHANGELOG.md")],
            }
        ]
        check = self.package["checks"][-1]
        check.update(outcome="unverified", reason="README was truncated before the examples.", sources=[])
        body = self.render()
        self.assertIn("Versions differ", body)
        self.assertIn("README was truncated", body)
        check.update(outcome="not_applicable", reason="The README has no code examples.", sources=[reference()])
        self.assertIn("not applicable:", self.render())
        self.package["checks"][0]["outcome"] = "unverified"
        self.package["checks"][0]["reason"] = "Version metadata inaccessible"
        self.reject(".findings[0].check")

    def test_confirmed_initial_release(self):
        self.breaking["releaseBaseline"] = {
            "status": "not_applicable",
            "reason": "Initial release independently confirmed.",
        }
        self.package["attribution"]["initial_release"] = True
        body = self.render()
        self.assertIn("Initial release independently confirmed", body)
        self.assertNotIn("Needs human review", body)
        self.package["attribution"]["initial_release"] = False
        self.reject(".initial_release")

    def test_agent_cannot_invent_initial_release(self):
        self.package["attribution"]["initial_release"] = True
        self.reject(".initial_release")

    def test_initial_release_collector_snapshot_reaches_renderer(self):
        from test_mgmt_sdk_review_context import CollectionTests

        self.context = CollectionTests().collect_initial_release()
        name = self.context["affectedPackages"][0]
        self.package["package"] = name
        for check in self.package["checks"]:
            check["sources"] = [reference(package=name)]
        self.package["attribution"]["initial_release"] = True
        body = self.render()
        self.assertIn("Initial release:", body)
        self.assertIn("1.0.0b1 (2026-09-22)", body)
        self.assertNotIn("Needs human review", body)

    def test_version_metadata_is_allowed_only_for_required_version_checks(self):
        source = reference("azure/mgmt/example/_version.py")
        self.package["checks"][0]["sources"] = [source]
        self.render()
        self.package["checks"][-1]["sources"] = [source]
        self.reject("excluded")

    def test_no_entries_requires_all_trusted_collection_complete(self):
        alterations = [
            lambda c: c["breakingChangeContext"][0].update(status="unverified"),
            lambda c: c["breakingChangeContext"][0].update(collectionIssues=["Tag baseline could not be retrieved"]),
            lambda c: c["breakingChangeContext"][0].update(emptyBreakingChangeSections=[{"release": "2.0.0"}]),
            lambda c: c["commitDiscovery"].update(status="unverified", error="Commit list truncated"),
            lambda c: c["packageDiscovery"].update(status="unverified", error="File list truncated"),
        ]
        for alteration in alterations:
            with self.subTest(alteration=alteration):
                self.context = context()
                alteration(self.context)
                self.reject(".outcome")
                self.package["attribution"].update(
                    outcome="incomplete", reason="Collection did not finish for this package."
                )
                self.assertIn("**Needs human review:**", self.render())
                self.package["attribution"].update(outcome="no_entries", reason="")

    def test_entries_cannot_be_omitted_or_invented(self):
        add_entry(self.data, self.context)
        entry = self.package["attribution"]["entries"].pop()
        self.reject(".entries")
        self.package["attribution"]["entries"] = [entry, entry]
        self.reject("duplicate")
        self.package["attribution"]["entries"] = [entry]
        entry["entry_index"] = 8
        self.reject(".entries")
        entry["entry_index"] = 0
        entry["release"] = "another release"
        self.reject(".release")

    def test_multiple_releases_and_packages(self):
        add_entry(self.data, self.context, direct=True)
        add_entry(self.data, self.context, release="3.0.0 (2026-09-23)")
        second = copy.deepcopy(self.package)
        other = PACKAGE.replace("example", "another")
        second["package"] = other
        for check in second["checks"]:
            check["sources"] = [reference(package=other)]
        self.data["packages"].append(second)
        self.context["affectedPackages"].append(other)
        for key in ("breakingChangeContext", "apiVersionDrift"):
            record = copy.deepcopy(self.context[key][0])
            record["packagePath"] = other
            if key == "breakingChangeContext":
                record["changelogPath"] = other + "/CHANGELOG.md"
            self.context[key].append(record)
        body = self.render()
        for expected in ("2.0.0", "3.0.0", "another", "TypeSpec/API", "Human review", "Change:"):
            self.assertIn(expected, body)
        self.assertIn("#L5-L6", body)
        self.assertIn("<br>", body)

    def test_partial_collection_keeps_available_entries_and_exact_diagnostics(self):
        add_entry(self.data, self.context)
        self.breaking.update(status="unverified", collectionIssues=["Missing historical provenance: HTTP 404"])
        self.package["attribution"].update(outcome="incomplete", reason="One source could not be retrieved.")
        body = self.render()
        self.assertIn("Removed", body)
        self.assertIn("Missing historical provenance: HTTP 404", body)
        self.assertIn("One source could not be retrieved", body)

    def test_cause_confidence_matrix(self):
        add_entry(self.data, self.context, direct=True)
        entry = self.package["attribution"]["entries"][0]
        for cause, confidence in (
            ("typespec_api", "not_applicable"),
            ("human_review", "high"),
            ("generator", "high"),
            ("typespec_api", "low"),
        ):
            with self.subTest(cause=cause, confidence=confidence):
                entry.update(cause=cause, confidence=confidence)
                self.reject(".")
        entry.update(cause="typespec_api", confidence="high", sources=[])
        self.reject(".sources")

    def test_typespec_requires_trusted_source_baseline_and_lines(self):
        add_entry(self.data, self.context, direct=True)
        entry = self.package["attribution"]["entries"][0]
        source = entry["sources"][0]
        source["url"] = source["url"].replace(NEW_SPEC, "1" * 40)
        self.reject(".sources")
        source["url"] = source["url"].replace("1" * 40, NEW_SPEC).split("#")[0]
        source.update(line_status="unavailable", reason="Source was truncated before the definition.")
        self.reject(".sources")
        source.update(url=source["url"] + "#L2-L3", line_status="verified", reason="")
        self.breaking["releaseBaseline"] = {"status": "unverified"}
        self.reject(".cause")

    def test_schema_rejects_missing_extra_fields_and_wrong_types(self):
        for mutate in (
            lambda d: d.pop("schema_version"),
            lambda d: d.update(schema_version=True),
            lambda d: d.update(schema_version="2"),
            lambda d: d.update(packages=None),
            lambda d: d.update(outcome="looks_good"),
            lambda d: d.update(context=self.context),
            lambda d: d["packages"][0].update(findings={}),
            lambda d: d["packages"][0]["attribution"].update(initial_release="true"),
            lambda d: d["packages"][0]["checks"][0].update(name="Everything looks fine"),
        ):
            with self.subTest(mutate=mutate):
                self.data = review()
                mutate(self.data)
                self.reject("data")

    def test_package_coverage_and_duplicate_checks(self):
        self.data["packages"].append(copy.deepcopy(self.package))
        self.reject("duplicate")
        self.data["packages"].pop()
        self.context["affectedPackages"].append("sdk/another/azure-mgmt-another")
        self.reject("affectedPackages")
        self.context["affectedPackages"].pop()
        self.package["checks"].append(copy.deepcopy(self.package["checks"][0]))
        self.reject("duplicate")
        self.package["checks"].pop()
        self.package["checks"].pop()
        self.reject("account for every rule")

    def test_not_applicable_requires_trusted_discovery(self):
        self.data = {"schema_version": "1", "outcome": "not_applicable", "packages": []}
        self.reject("affectedPackages")
        self.context["affectedPackages"] = []
        self.assertIn("review not applicable", self.render())
        self.context["packageDiscovery"].update(status="unverified", error="File list incomplete")
        self.reject("not_applicable")

    def test_placeholders_and_reason_free_diagnostics(self):
        for placeholder in (
            "-",
            "None!",
            "`None.`",
            "_Done_",
            "**`None.`**",
            "~~None~~",
            "<strong>None.</strong>",
            "&#78;one&#33;",
            "[None.](https://example.invalid)",
            "TBD",
            "Full review is pending",
            "The full review is pending",
            "pending review: see logs",
            "Unable to complete review because ...",
        ):
            with self.subTest(placeholder=placeholder):
                check = self.package["checks"][0]
                check.update(outcome="unverified", reason=placeholder, sources=[])
                self.reject(".reason")
        check["reason"] = "Unable to complete review because the pinned file returned HTTP 404."
        self.assertIn("HTTP 404", self.render())

    def test_literal_type_names_are_not_html_placeholders(self):
        for value in ("<Widget>", "`<Widget>`", "value & other", "None is the documented return value"):
            MODULE.substantive(value, "analysis")

    def test_placeholder_validation_uses_the_rendered_entity_fixed_point(self):
        for placeholder in (
            "&amp;#70;ull review is pending",
            "&amp;amp;#78;one!",
            "&amp;lt;strong&amp;gt;None&amp;lt;/strong&amp;gt;",
            "\uff26ull review is pending",
        ):
            with self.subTest(placeholder=placeholder):
                self.package["checks"][0].update(outcome="unverified", reason=placeholder, sources=[])
                self.reject(".reason")
        MODULE.reason("Baseline&#32;unavailable", "reason")

    def test_excessive_entity_nesting_is_rejected_by_validator_and_renderer(self):
        value = "&#70;ull review pending"
        for _ in range(12):
            value = html.escape(value)
        for function in (lambda: MODULE.substantive(value, "reason"), lambda: MODULE.text(value)):
            with self.assertRaisesRegex(ValueError, "excessively nested"):
                function()

    def test_diagnostic_only_review_rejected(self):
        for check in self.package["checks"]:
            check.update(outcome="unverified", reason="Pinned file was inaccessible.", sources=[])
        self.reject("diagnostic-only")

    def test_immutable_sources_line_anchors_and_exclusions(self):
        source = self.package["checks"][0]["sources"][0]
        original = source["url"]
        for url in (
            original.replace(HEAD, "main"),
            original.replace("#L2-L3", "#L9-L2"),
            original.replace("github.com", "evil.invalid"),
            original.replace(HEAD, "1" * 40),
            original.replace("/README.md", "/../README.md"),
            original.replace("/README.md", "/generated_samples/sample.py"),
            original.replace("/README.md", "/azure/mgmt/example/_models.py"),
        ):
            with self.subTest(url=url):
                source["url"] = url
                self.reject(".sources")
        source["url"] = original.split("#")[0]
        self.reject(".sources")
        source.update(line_status="unavailable", reason="Exact source lines could not be verified.")
        self.assertIn("lines unverified", self.render())

    def test_escaping_multiline_mentions_html_and_delimiters(self):
        add_entry(self.data, self.context)
        explanation = (
            '@renamedFrom(Versions.v1, "OldWidget") @@Azure.ClientGenerator.Core.clientName\n'
            '<Widget> | **bold** `code` ``more``\n\n@copilot "quoted" \\ path & values'
        )
        self.package["attribution"]["entries"][0]["explanation"] = explanation
        body = self.render()
        self.assertIn("@renamedFrom", body)
        self.assertIn("@@Azure", body)
        self.assertIn(r"\|", body)
        self.assertIn("<br><br>", body)
        self.assertIn("<Widget>", body)
        self.assertEqual(body, self.render())

    def test_pipe_escaping_is_independent_of_adjacent_backslashes(self):
        for count in range(5):
            value = "value" + "\\" * count + "|next"
            rendered = MODULE.text(value)
            self.assertEqual(1, len(re.findall(r"(?<!\\)\\\|", rendered)))
            self.assertIn("`\\|`", rendered)
        self.assertEqual(MODULE.text("`name`|value"), MODULE.text("\uff40name\uff40\uff5cvalue"))

    def test_publication_link_budget_is_checked_before_rewriting(self):
        self.package["checks"][0]["sources"] = [reference(f"evidence{index}.md") for index in range(42)]
        self.assertEqual(48, len(re.findall(r"https?://", self.render())))
        self.package["checks"][0]["sources"].append(reference("extra.md"))
        self.reject("48-link budget")

    def test_complete_outcomes_cannot_carry_incomplete_reasons(self):
        self.package["checks"][0]["reason"] = "Version metadata was inaccessible."
        self.reject(".reason")
        self.package["checks"][0]["reason"] = ""
        self.package["attribution"]["reason"] = "No newly added entries. This is an initial release."
        self.reject(".reason")

    def test_api_drift_is_rendered_only_from_trusted_results(self):
        drift = self.context["apiVersionDrift"][0]
        drift.update(status="changed", latestApiVersion="2026-09-22-preview")
        body = self.render()
        for expected in ("API version changed", "Blocking", FIRST, HEAD, "2026-01-01", "2026-09-22-preview"):
            self.assertIn(expected, body)
        drift.update(status="unverified", error="Metadata file returned HTTP 404.")
        self.assertIn("Metadata file returned HTTP 404", self.render())
        self.assertNotIn("API version changed", self.render())

    def test_trusted_context_bound_to_workflow_event(self):
        MODULE.validate_context(self.context, REPO, 49107, HEAD, TOOLING)
        for key in ("repository", "pullRequestNumber", "latestRevision", "toolingRevision"):
            changed = copy.deepcopy(self.context)
            changed[key] = "untrusted"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                MODULE.validate_context(changed, REPO, 49107, HEAD, TOOLING)

    def test_collector_errors_and_missing_duplicate_mixed_outputs(self):
        valid = envelope(self.data)
        for errors in (None, False, 0, "", {}, ["Line 2: Invalid JSON"]):
            with self.subTest(errors=errors), self.assertRaisesRegex(ValueError, "output.errors"):
                MODULE.prepare_output({**valid, "errors": errors}, self.context)
        for items in (None, [], [None], valid["items"] * 2):
            with self.subTest(items=items), self.assertRaises(ValueError):
                MODULE.prepare_output({"errors": [], "items": items}, self.context)
        for kind in ("noop", "missing_tool", "missing_data", "report_incomplete"):
            diagnostic = {"type": kind, "reason": "Failed to submit review"}
            for items in ([diagnostic], [*valid["items"], diagnostic]):
                with self.subTest(kind=kind, items=items), self.assertRaises(ValueError):
                    MODULE.prepare_output({"errors": [], "items": items}, self.context)
        for field, value in (("item_number", 123), ("comment_id", 123), ("body", "Some handwritten Markdown")):
            payload = copy.deepcopy(valid)
            payload["items"][0][field] = value
            with self.assertRaises(ValueError):
                MODULE.prepare_output(payload, self.context)

    def test_size_and_duplicate_json_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.json"
            for raw in ('{"outcome":"reviewed","outcome":"not_applicable"}', "{" + " " * MODULE.MAX_BYTES + "}"):
                path.write_text(raw, encoding="utf-8")
                with self.assertRaises(ValueError):
                    MODULE.load_json(path)
        add_entry(self.data, self.context)
        self.package["attribution"]["entries"][0]["explanation"] = "x" * 12001
        self.reject("size limit")

    def test_actual_failure_payloads_and_equivalent_structured_scenarios(self):
        files = sorted(FIXTURES.glob("run-*.json"))
        self.assertEqual(5, len(files))
        for path in files:
            with self.subTest(run=path.stem):
                payload = json.loads(path.read_text(encoding="utf-8"))
                old_body = payload["items"][0]["body"]
                self.assertIn("### Breaking-change attribution", old_body)
                with self.assertRaisesRegex(ValueError, "body"):
                    MODULE.prepare_output(payload, self.context)
                data, trusted = review(), context()
                if "\nNeeds human review:" in old_body:
                    explanation = (
                        old_body.split("\nNeeds human review:", 1)[1].split("\n\n### Review summary", 1)[0].strip()
                    )
                    trusted["breakingChangeContext"][0].update(
                        status="unverified",
                        collectionIssues=["No previous release heading was found at the merge base"],
                    )
                    data["packages"][0]["attribution"].update(outcome="incomplete", reason=explanation)
                    body = MODULE.prepare_output(envelope(data), trusted)["items"][0]["body"]
                    self.assertIn("**Needs human review:**", body)
                else:
                    trusted["breakingChangeContext"][0]["releaseBaseline"] = {
                        "status": "not_applicable",
                        "reason": "Initial release confirmed by complete added-file and absent-directory evidence.",
                    }
                    data["packages"][0]["attribution"]["initial_release"] = True
                    body = MODULE.prepare_output(envelope(data), trusted)["items"][0]["body"]
                    self.assertIn("No newly added or modified entries.", body)
                self.assertTrue(body.startswith(MODULE.MARKER))


class PublicationIntegrationTests(unittest.TestCase):
    def run_publisher(self, directory, payload, trusted):
        directory = Path(directory)
        output = directory / "agent_output.json"
        output.write_text(json.dumps(payload), encoding="utf-8")
        snapshot = directory / "trusted.json"
        snapshot.write_text(json.dumps(trusted), encoding="utf-8")
        env = {
            **os.environ,
            "GH_AW_AGENT_OUTPUT": str(output),
            "REVIEW_CONTEXT": str(snapshot),
            "GH_REPOSITORY": REPO,
            "PR_NUMBER": "49107",
            "REVIEW_HEAD_SHA": HEAD,
            "REVIEW_TOOLING_SHA": TOOLING,
        }
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "publish"], env=env, cwd=directory, capture_output=True, text=True, timeout=10
        )
        return result, json.loads(output.read_text(encoding="utf-8"))

    def test_cli_replaces_data_before_builtin_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            result, output = self.run_publisher(directory, envelope(review()), context())
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual({"type", "body"}, set(output["items"][0]))
            self.assertIn("## Management SDK PR review", output["items"][0]["body"])

    def test_rejected_submission_never_reaches_publisher_or_hides_existing_review(self):
        with tempfile.TemporaryDirectory() as directory:
            useful_comment = mock.Mock()
            useful_comment.body = "Existing useful review"
            payload = envelope(review())
            payload["errors"] = ["Rejected second tool call"]
            result, output = self.run_publisher(directory, payload, context())
            if result.returncode == 0:
                useful_comment.hide()
                useful_comment.publish(output)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("No review will be published or hidden", result.stderr)
            self.assertEqual(payload, output)
            useful_comment.hide.assert_not_called()
            useful_comment.publish.assert_not_called()
            self.assertEqual("Existing useful review", useful_comment.body)

    def test_agent_workspace_context_cannot_override_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            trusted = context()
            trusted["breakingChangeContext"][0].update(status="unverified", collectionIssues=["Missing baseline"])
            Path(directory, "review-context.json").write_text(json.dumps(context()), encoding="utf-8")
            result, _ = self.run_publisher(directory, envelope(review()), trusted)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("trusted collection requires 'incomplete'", result.stderr)

    def test_generated_contract_matches_publisher_schema(self):
        meta = lock_json("GH_AW_TOOLS_META_JSON")
        self.assertEqual(MODULE.SCHEMA, meta["property_injections"]["add_comment"]["data"])
        validation = lock_json("GH_AW_VALIDATION_JSON")
        self.assertEqual(MODULE.SCHEMA, validation["add_comment"]["dataSchema"])

    def test_compiled_job_trust_and_publication_order(self):
        lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
        agent = re.split(r"\n  [a-z_]+:\n", lock.split("\n  agent:\n", 1)[1])[0]
        job = lock.split("\n  safe_outputs:\n", 1)[1]
        collector = lock.split("\n  review_context:\n", 1)[1].split("\n  safe_outputs:", 1)[0]
        self.assertIn("- review_context", agent)
        self.assertIn("- review_context", job.split("runs-on:", 1)[0])
        self.assertNotIn("pull-requests: write", agent)
        self.assertNotIn("pull-requests: write", collector)
        self.assertIn("ref: ${{ github.workflow_sha }}", collector)
        self.assertNotIn("github.event.pull_request.base.sha", SOURCE)
        self.assertIn("checkout: false", SOURCE)
        for job_part in (agent, job):
            self.assertIn("artifact-ids: ${{ needs.review_context.outputs.artifact_id }}", job_part)
        self.assertIn("persist-credentials: false", collector)
        self.assertLess(job.index("id: setup-agent-output-env"), job.index("name: Validate and render"))
        self.assertLess(job.index("name: Download independently trusted"), job.index("name: Validate and render"))
        self.assertLess(job.index("name: Validate and render"), job.index("name: Process Safe Outputs"))
        step = job[job.index("name: Validate and render") : job.index("name: Process Safe Outputs")]
        self.assertNotIn("continue-on-error", step)
        self.assertNotIn("if:", step)
        self.assertIn("mgmt-review-trusted/mgmt_sdk_review_contract.py", step)
        self.assertIn('\\"hide_older_comments\\":true', job)
        self.assertIn('\\"max\\":1', job)
        self.assertIn("process_safe_outputs.cjs", job)

    def test_actual_documented_jq_command_preserves_structured_data(self):
        jq = shutil.which("jq") or os.environ.get("JQ")
        self.assertTrue(jq, "Install jq or set JQ to test the workflow's submission command.")
        expression = re.search(r"(?m)^jq '([^']+)' .* \| safeoutputs add_comment \.$", SOURCE)[1]
        data = review()
        add_entry(data, context())
        data["packages"][0]["attribution"]["entries"][0][
            "explanation"
        ] = '@renamedFrom("a") @@clientName <Widget> | `name`\n\n"quoted" \\ path & value'
        result = subprocess.run([jq, expression], input=json.dumps(data), capture_output=True, text=True, check=True)
        self.assertEqual({"body": MODULE.SUBMISSION, "data": data}, json.loads(result.stdout))

    @unittest.skipUnless(os.environ.get("GH_AW_RUNTIME"), "Set GH_AW_RUNTIME to pinned gh-aw actions/setup/js")
    def test_pinned_ingestion_and_builtin_handler(self):
        data, trusted = review(), context()
        add_entry(data, trusted, direct=True)
        entry = data["packages"][0]["attribution"]["entries"][0]
        entry["sources"][0]["url"] = entry["sources"][0]["url"].replace(
            "main.tsp", "@renamedFrom(Widget)&\uff21Widget.tsp"
        )
        entry["explanation"] = "\n".join(
            '@renamedFrom("a") @@clientName <Widget> \\| `name` "quoted" \\ path' for _ in range(15)
        )
        script = Path(__file__).parent / "mgmt_review_runtime.cjs"
        request = {
            "mode": "ingest",
            "item": {"type": "add_comment", "body": MODULE.SUBMISSION, "data": data},
            "validation": lock_json("GH_AW_VALIDATION_JSON"),
        }
        result = subprocess.run(
            ["node", str(script)],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=30,
        )
        ingested = json.loads(result.stdout)
        self.assertTrue(ingested["isValid"], ingested)
        self.assertEqual(data, ingested["normalizedItem"]["data"])
        prepared = MODULE.prepare_output({"items": [ingested["normalizedItem"]], "errors": []}, trusted)
        result = subprocess.run(
            ["node", str(script)],
            input=json.dumps({"mode": "publish", "payload": prepared}),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=30,
        )
        published = json.loads(result.stdout)
        self.assertTrue(published["result"]["success"], published)
        self.assertEqual(49107, published["comment"]["issue_number"])
        self.assertIn(NEW_SPEC, published["comment"]["body"])
        self.assertIn(quote(entry["sources"][0]["url"], safe="/:%#._-~"), published["comment"]["body"])
        self.assertIn("<Widget>", published["comment"]["body"])
        self.assertEqual(15, published["comment"]["body"].count('@renamedFrom("a")'))
        self.assertNotIn("Structured data:", published["comment"]["body"])
        # The built-in handler replaces our stripped marker with its own searchable XML marker.
        self.assertEqual(1, published["comment"]["body"].count("workflow_id: mgmt-sdk-pr-review"))


if __name__ == "__main__":
    unittest.main()
