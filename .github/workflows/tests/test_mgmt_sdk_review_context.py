import base64
import importlib.util
import io
import json
from pathlib import Path
import textwrap
import unittest
from unittest import mock
import urllib.error
import urllib.parse


SCRIPT = Path(__file__).parents[1] / "scripts" / "mgmt_sdk_review_context.py"
SPEC = importlib.util.spec_from_file_location("mgmt_sdk_review_context", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorkflowBootstrapTests(unittest.TestCase):
    def test_single_trusted_collector_has_valid_python(self):
        workflow = (SCRIPT.parents[1] / "mgmt-sdk-pr-review.md").read_text(encoding="utf-8")
        blocks = workflow.split("python - <<'PY'")[1:]
        self.assertEqual(1, len(blocks))
        source = textwrap.dedent(blocks[0].split("\n      PY", 1)[0])
        compile(source, "collector-bootstrap", "exec")
        self.assertIn('revision = os.environ["TRUSTED_BASE_SHA"]', source)
        self.assertIn("TRUSTED_BASE_SHA: ${{ github.event.pull_request.base.sha }}", workflow)
        self.assertEqual(1, workflow.count("      python mgmt_sdk_review_context.py"))

    def test_generated_bootstrap_has_valid_python(self):
        workflow = (SCRIPT.parents[1] / "mgmt-sdk-pr-review.lock.yml").read_text(encoding="utf-8")
        runs = [
            json.loads(line.strip().removeprefix("run: "))
            for line in workflow.splitlines()
            if line.strip().startswith('run: "python - ')
        ]
        self.assertEqual(1, len(runs))
        source = runs[0].split("python - <<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
        compile(source, "generated-collector-bootstrap", "exec")


class BreakingChangeParserTests(unittest.TestCase):
    def test_date_correction_preserves_exact_and_modified_matching(self):
        old = MODULE.parse_breaking_changes(
            "## 2.0.0 (2026-01-01)\n### Breaking Changes\n"
            "- Deleted model `OldWidget`.\n- Method `Widgets.get` was renamed.\n"
        )
        corrected = MODULE.parse_breaking_changes(
            "## 2.0.0 (2026-01-02)\n### Breaking Changes\n"
            "- Deleted model `OldWidget`.\n- Method `Widgets.get` was renamed.\n"
        )
        self.assertEqual([], MODULE.introduced_breaking_changes(old["entries"], corrected["entries"]))

        corrected["entries"][1]["text"] = "Method `Widgets.get` was renamed to `Widgets.fetch`."
        introduced = MODULE.introduced_breaking_changes(old["entries"], corrected["entries"])
        self.assertEqual(1, len(introduced))
        self.assertEqual("modified", introduced[0]["changeKind"])
        self.assertEqual("2.0.0 (2026-01-02)", introduced[0]["release"])
        self.assertEqual(old["entries"][1]["text"], introduced[0]["previousText"])

    def test_identical_entry_in_different_version_is_added(self):
        old = MODULE.parse_breaking_changes("## 1.0.0 (2026-01-01)\n### Breaking Changes\n- Deleted model.\n")
        new = MODULE.parse_breaking_changes("## 2.0.0 (2026-01-02)\n### Breaking Changes\n- Deleted model.\n")
        self.assertEqual("added", MODULE.introduced_breaking_changes(old["entries"], new["entries"])[0]["changeKind"])

    def test_added_modified_multiline_and_historical_entries(self):
        old = MODULE.parse_breaking_changes(
            """# Release History

## 2.0.0 (2026-01-01)
### Breaking Changes
  - Method `Widgets.get` was renamed.

## 1.0.0 (2025-01-01)
### Breaking Changes
  - Historical entry.
"""
        )
        new = MODULE.parse_breaking_changes(
            """# Release History

## 2.0.0 (2026-01-01)
### Breaking Changes
  - Method `Widgets.get` was renamed to `Widgets.fetch`.
    Use `fetch` for new calls.
  - Deleted model `OldWidget`.

## 1.0.0 (2025-01-01)
### Breaking Changes
  - Historical entry.
"""
        )

        introduced = MODULE.introduced_breaking_changes(old["entries"], new["entries"])

        self.assertEqual(["modified", "added"], [entry["changeKind"] for entry in introduced])
        self.assertIn("Use `fetch`", introduced[0]["text"])
        self.assertEqual(5, introduced[0]["startLine"])
        self.assertNotIn("Historical entry.", [entry["text"] for entry in introduced])

    def test_empty_section_is_recorded(self):
        parsed = MODULE.parse_breaking_changes(
            """## 3.0.0 (2026-02-02)
### Breaking Changes

### Features Added
- A feature
"""
        )

        self.assertEqual([], parsed["entries"])
        self.assertEqual([{"release": "3.0.0 (2026-02-02)", "sectionLine": 2}], parsed["emptySections"])

    def test_multiple_releases_remain_separate(self):
        parsed = MODULE.parse_breaking_changes(
            """## 3.0.0 (2026-02-02)
### Breaking Changes
- New break
## 2.0.0 (2026-01-01)
### Breaking Changes
- Old break
"""
        )

        self.assertEqual(
            ["3.0.0 (2026-02-02)", "2.0.0 (2026-01-01)"],
            [entry["release"] for entry in parsed["entries"]],
        )

    def test_latest_release_uses_all_headings_and_skips_placeholder(self):
        parsed = MODULE.parse_breaking_changes(
            """## 0.0.0 (Unreleased)
### Features Added
- Pending
## 1.2.0b1 (2026-01-02)
### Features Added
- Released
## 1.0.0 (2025-01-01)
### Breaking Changes
- Old break
"""
        )

        self.assertEqual("1.2.0b1", MODULE.latest_release_version(parsed))


class ProvenanceTests(unittest.TestCase):
    def test_ranges_are_not_reported_as_resolved_versions(self):
        metadata = {
            "status": "available",
            "path": "pkg/_metadata.json",
            "revision": "a" * 40,
            "content": json.dumps(
                {
                    "emitterVersion": "0.63.6",
                    "httpClientPythonVersion": "^0.37.1",
                }
            ),
        }
        lock = {
            "status": "available",
            "path": "pkg/TempTypeSpecFiles/package-lock.json",
            "revision": "a" * 40,
            "content": json.dumps(
                {
                    "packages": {
                        "node_modules/@azure-tools/typespec-python": {"version": "0.63.6"},
                        "node_modules/@typespec/compiler": {"version": "1.4.0"},
                    }
                }
            ),
        }

        summary = MODULE.summarize_provenance([metadata, lock])

        self.assertEqual("range", summary["metadata"]["httpClientPythonVersion"]["kind"])
        self.assertEqual("resolved", summary["metadata"]["emitterVersion"]["kind"])
        self.assertEqual(2, len(summary["resolvedDependencies"]))

    def test_missing_and_truncated_evidence_are_explicit(self):
        summary = MODULE.summarize_provenance(
            [
                {"status": "missing", "path": "pkg/tsp-location.yaml", "revision": "a" * 40, "error": "404"},
                {
                    "status": "truncated",
                    "path": "pkg/TempTypeSpecFiles/package-lock.json",
                    "revision": "a" * 40,
                    "error": "too large",
                },
            ]
        )

        self.assertEqual(["too large"], summary["issues"])
        self.assertEqual(["missing", "truncated"], [item["status"] for item in summary["files"]])

    def test_source_reference_requires_github_url_and_full_sha(self):
        invalid = {"metadata": {"repository_url": {"value": "https://example.com/specs"}, "commit": {"value": "main"}}}
        valid = {
            "metadata": {
                "repository_url": {"value": "https://github.com/Azure/azure-rest-api-specs"},
                "commit": {"value": "a" * 40},
            }
        }

        self.assertEqual("unverified", MODULE.validated_source_reference(invalid)["status"])
        self.assertEqual("available", MODULE.validated_source_reference(valid)["status"])

    def test_tsp_location_supplies_release_provenance_and_reports_conflicts(self):
        tsp_location = {
            "status": "available",
            "path": "pkg/tsp-location.yaml",
            "revision": "a" * 40,
            "content": (
                "directory: specification/contoso/New\n"
                f"commit: {'b' * 40}\n"
                "repo: Azure/azure-rest-api-specs\n"
                "additionalDirectories:\n"
                "  - specification/common-types/resource-management\n"
            ),
        }
        metadata = {
            "status": "available",
            "path": "pkg/_metadata.json",
            "revision": "a" * 40,
            "content": json.dumps(
                {
                    "typespec_src": "specification/contoso/Old",
                    "commit": "c" * 40,
                    "repository_url": "https://github.com/Azure/different-specs",
                }
            ),
        }

        release_summary = MODULE.summarize_provenance([tsp_location])
        conflicted = MODULE.summarize_provenance([metadata, tsp_location])

        self.assertEqual("available", MODULE.validated_source_reference(release_summary)["status"])
        self.assertEqual(
            ["specification/common-types/resource-management"],
            release_summary["tspLocation"]["additionalDirectories"],
        )
        self.assertEqual(3, len(conflicted["issues"]))
        self.assertEqual("unverified", MODULE.validated_source_reference(conflicted)["status"])


class CollectionTests(unittest.TestCase):
    def collect_context(
        self, *, old_status=200, changelog_status="modified", commit_count=1, package_count=1, annotated_tag=False
    ):
        packages = [f"sdk/contoso/azure-mgmt-contoso{index}" for index in range(package_count)]
        changelog = "## 1.0.0 (2026-01-01)\n### Breaking Changes\n- Historical entry.\n"

        def respond(request, timeout):
            parsed = urllib.parse.urlparse(request.full_url)
            path = parsed.path.removeprefix("/repos/Azure/azure-sdk-for-python")
            query = urllib.parse.parse_qs(parsed.query)
            if not path:
                data = {"default_branch": "main"}
            elif path == "/branches/main":
                data = {"commit": {"sha": "f" * 40}}
            elif path == "/pulls/1":
                data = {
                    "changed_files": package_count,
                    "commits": commit_count,
                    "head": {"sha": "b" * 40},
                    "base": {"sha": "e" * 40},
                }
            elif path.startswith("/compare/"):
                data = {"merge_base_commit": {"sha": "c" * 40}}
            elif path == "/pulls/1/files":
                data = [{"filename": f"{package}/CHANGELOG.md", "status": changelog_status} for package in packages]
            elif path == "/pulls/1/commits":
                offset = (int(query["page"][0]) - 1) * 100
                data = [{"sha": "a" * 40}] * max(0, min(100, min(commit_count, 250) - offset))
            elif path.startswith("/git/ref/tags/"):
                data = {"object": {"type": "tag" if annotated_tag else "commit", "sha": "d" * 40}}
            elif path.startswith("/git/tags/"):
                data = {"object": {"type": "commit", "sha": "d" * 40}}
            elif path.startswith("/contents/"):
                filename = urllib.parse.unquote(path.removeprefix("/contents/"))
                if filename == ".github/copilot-instructions.md":
                    content = "## MGMT SDK Code Review Rules\nReview the package.\n"
                elif filename.endswith("/CHANGELOG.md"):
                    if query["ref"][0] == "c" * 40 and old_status != 200:
                        raise urllib.error.HTTPError(request.full_url, old_status, "baseline unavailable", {}, None)
                    content = changelog
                elif filename.endswith("/_metadata.json"):
                    content = json.dumps({"apiVersion": "2026-01-01"})
                else:
                    content = "{}"
                data = {
                    "type": "file",
                    "encoding": "base64",
                    "content": base64.b64encode(content.encode()).decode(),
                }
            else:
                raise AssertionError(f"Unexpected API call: {request.full_url}")
            response = io.BytesIO(json.dumps(data).encode())
            response.headers = {}
            return response

        output = mock.mock_open()
        with (
            mock.patch.dict(MODULE.os.environ, {"GH_REPOSITORY": "Azure/azure-sdk-for-python", "GH_TOKEN": "test", "PR_NUMBER": "1"}),
            mock.patch.object(MODULE.urllib.request, "urlopen", side_effect=respond) as requests,
            mock.patch("builtins.open", output),
        ):
            MODULE.collect()
        output.assert_called_once_with("review-context.json", "w", encoding="utf-8")
        context = json.loads("".join(call.args[0] for call in output().write.call_args_list))
        self.assertEqual(requests.call_count, context["collectionLimits"]["githubApiRequests"])
        return context

    def test_unavailable_baseline_never_emits_historical_deltas(self):
        for status in (403, 404, 503):
            with self.subTest(status=status):
                package = self.collect_context(old_status=status)["breakingChangeContext"][0]
                self.assertEqual("unverified", package["status"])
                self.assertEqual([], package["introducedEntries"])
                self.assertTrue(any(str(status) in issue for issue in package["collectionIssues"]))

    def test_added_changelog_can_use_missing_baseline(self):
        package = self.collect_context(old_status=404, changelog_status="added")["breakingChangeContext"][0]
        self.assertEqual(1, len(package["introducedEntries"]))
        self.assertEqual("added", package["introducedEntries"][0]["changeKind"])
        self.assertFalse(any("404" in issue for issue in package["collectionIssues"]))

    def test_available_baseline_excludes_unchanged_history(self):
        package = self.collect_context()["breakingChangeContext"][0]
        self.assertEqual("complete", package["status"])
        self.assertEqual([], package["introducedEntries"])

    def test_commit_discovery_checks_declared_count_at_endpoint_cap(self):
        for count, expected in ((249, "complete"), (250, "complete"), (251, "unverified"), (400, "unverified")):
            with self.subTest(count=count):
                context = self.collect_context(commit_count=count)
                discovery = context["commitDiscovery"]
                self.assertEqual(expected, discovery["status"])
                self.assertEqual(count, discovery["expectedCommits"])
                self.assertEqual(min(count, 250), discovery["returnedCommits"])
                self.assertEqual("a" * 40, context["firstRevision"])
                if expected == "unverified":
                    self.assertIn(f"expected {count}, returned 250", discovery["error"])
                else:
                    self.assertIsNone(discovery["error"])

    def test_budget_preserves_completed_packages_and_hands_off_remainder(self):
        with mock.patch.object(MODULE, "MAX_API_REQUESTS", 40):
            context = self.collect_context(package_count=3, annotated_tag=True)
        packages = context["breakingChangeContext"]
        self.assertEqual("complete", context["packageDiscovery"]["status"])
        self.assertEqual(3, len(context["affectedPackages"]))
        self.assertEqual(["complete", "unverified", "unverified"], [package["status"] for package in packages])
        self.assertEqual(["unchanged", "unverified", "unverified"], [drift["status"] for drift in context["apiVersionDrift"]])
        self.assertEqual(31, context["collectionLimits"]["githubApiRequests"])
        for package in packages[1:]:
            self.assertEqual([], package["introducedEntries"])
            self.assertIn("Needs human review", package["collectionIssues"][0])
            self.assertIn("only 9 API requests remain", package["collectionIssues"][0])

    def test_budget_boundary_allows_full_package_or_explicit_handoff(self):
        for limit, expected in ((30, "unverified"), (31, "complete")):
            with self.subTest(limit=limit), mock.patch.object(MODULE, "MAX_API_REQUESTS", limit):
                context = self.collect_context(annotated_tag=True)
                self.assertEqual(expected, context["breakingChangeContext"][0]["status"])
                self.assertLessEqual(context["collectionLimits"]["githubApiRequests"], limit)


class FailureHandlingTests(unittest.TestCase):
    def test_drift_reports_missing_or_invalid_api_version(self):
        for metadata in ({}, [], None, {"apiVersion": ""}, {"apiVersion": 42}):
            with self.subTest(metadata=metadata):
                provenance = MODULE.summarize_provenance(
                    [{"status": "available", "path": "pkg/_metadata.json", "content": json.dumps(metadata)}]
                )
                result = MODULE.api_version_drift("pkg", "a" * 40, "b" * 40, provenance, provenance)

                self.assertEqual("unverified", result["status"])
                self.assertIn(f"first revision {'a' * 40}", result["error"])
                self.assertIn(f"latest revision {'b' * 40}", result["error"])
                self.assertIn("non-empty string apiVersion", result["error"])
                self.assertEqual([], provenance["issues"])

    def test_drift_preserves_valid_comparisons_and_failure_details(self):
        first = {"metadata": {"apiVersion": {"value": "2026-01-01"}}, "issues": []}
        latest = {"metadata": {"apiVersion": {"value": "2026-02-01"}}, "issues": []}
        for provenance, expected in ((first, "unchanged"), (latest, "changed")):
            result = MODULE.api_version_drift("pkg", "a" * 40, "b" * 40, first, provenance)
            self.assertEqual(expected, result["status"])
            self.assertIsNone(result["error"])

        result = MODULE.api_version_drift(
            "pkg", "a" * 40, "b" * 40, first, {"metadata": None, "issues": ["rate limited"]}
        )
        self.assertEqual("unverified", result["status"])
        self.assertIn("rate limited", result["error"])
        self.assertNotIn("first revision", result["error"])

    def test_invalid_repository_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.GitHubClient("https://github.com/Azure/repo", "token")

    def test_read_file_records_api_failure(self):
        client = MODULE.GitHubClient("Azure/azure-sdk-for-python", "token")

        def fail(_):
            raise MODULE.GitHubApiError("rate limited", status=403)

        client.get = fail
        evidence = client.read_file("CHANGELOG.md", "a" * 40)

        self.assertEqual("unverified", evidence["status"])
        self.assertIn("rate limited", evidence["error"])

    def test_read_file_records_malformed_success_payload(self):
        client = MODULE.GitHubClient("Azure/azure-sdk-for-python", "token")
        client.get = lambda _: []

        evidence = client.read_file("CHANGELOG.md", "a" * 40)

        self.assertEqual("unverified", evidence["status"])
        self.assertIn("not an object", evidence["error"])

    def test_request_limit_fails_before_network_access(self):
        client = MODULE.GitHubClient("Azure/azure-sdk-for-python", "token")
        client.request_count = MODULE.MAX_API_REQUESTS

        with self.assertRaisesRegex(MODULE.GitHubApiError, "request limit"):
            client.get("/repos/Azure/azure-sdk-for-python")


if __name__ == "__main__":
    unittest.main()