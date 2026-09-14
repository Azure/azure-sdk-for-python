import importlib.util
import json
from pathlib import Path
import textwrap
import unittest


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