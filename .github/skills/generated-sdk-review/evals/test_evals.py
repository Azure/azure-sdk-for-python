"""Evals for the generated SDK review report.

Historical cases replay published review findings.
Rule cases lock the behavior those reviews depended on, including known false alarms.
"""

import json
import pathlib
import sys
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from review_report import ReviewError, build_report, validate_report

CASES = pathlib.Path(__file__).resolve().parent / "cases"


def load_cases():
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(CASES.glob("*.json"))]


class HistoricalFindings(unittest.TestCase):
    def test_cases_cover_three_published_reviews(self):
        cases = load_cases()
        self.assertGreaterEqual(len(cases), 3)
        self.assertEqual(
            [case["id"] for case in cases],
            ["48637-api-versions", "48997-api-versions", "48997-changelog"],
        )

    def test_each_case_matches_the_known_finding(self):
        for case in load_cases():
            with self.subTest(case=case["id"]):
                report = build_report(case["context"])
                self.assertEqual([], validate_report(report, case["context"]))
                findings = report["reviews"][0]["findings"]
                self.assertEqual(case["expectedTitles"], [item["title"] for item in findings])
                self.assertTrue(all(item["severity"] == "high" for item in findings))
                self.assertTrue(all(item["line"] == case["expectedLine"] for item in findings))
                description = "\n".join(item["description"] for item in findings)
                for needle in case["descriptionMustContain"]:
                    self.assertIn(needle, description)
                for title in case["forbiddenTitles"]:
                    self.assertNotIn(title, [item["title"] for item in findings])


class RuleGuards(unittest.TestCase):
    def test_singular_api_version_difference_is_not_a_finding(self):
        # The first review of SDK PR 48997 missed the real map and then treated a missing
        # singular apiVersion as unverified. A singular field must not create a finding on its own.
        context = _context(
            changed=["sdk/example/azure-mgmt-example/_metadata.json"],
            files={
                "sdk/example/azure-mgmt-example/_metadata.json": {
                    "baseline": json.dumps({"apiVersion": "2026-01-01", "apiVersions": {"Example": "2026-01-01"}}),
                    "head": json.dumps({"apiVersion": "2026-02-01", "apiVersions": {"Example": "2026-01-01"}}),
                }
            },
        )
        self.assertEqual([], build_report(context)["reviews"][0]["findings"])

    def test_service_name_containing_preview_is_not_a_preview_api(self):
        context = _context(
            changed=["sdk/example/azure-mgmt-example/_metadata.json"],
            files={
                "sdk/example/azure-mgmt-example/_metadata.json": {
                    "head": json.dumps({"apiVersions": {"PreviewWidget": "2026-01-01"}})
                },
                "sdk/example/azure-mgmt-example/azure/mgmt/example/_version.py": {"head": 'VERSION = "1.0.0"\n'},
            },
        )
        self.assertEqual([], build_report(context)["reviews"][0]["findings"])

    def test_preview_api_on_a_stable_version_is_a_finding(self):
        context = _context(
            changed=["sdk/example/azure-mgmt-example/_metadata.json"],
            files={
                "sdk/example/azure-mgmt-example/_metadata.json": {
                    "head": json.dumps({"apiVersions": {"Example": "2026-01-01-preview"}}, indent=2)
                },
                "sdk/example/azure-mgmt-example/azure/mgmt/example/_version.py": {"head": 'VERSION = "1.0.0"\n'},
            },
        )
        findings = build_report(context)["reviews"][0]["findings"]
        self.assertEqual(["Preview API requires a beta package version"], [item["title"] for item in findings])

    def test_old_changelog_placeholder_is_not_the_latest_release(self):
        context = _context(
            changed=["sdk/example/azure-mgmt-example/CHANGELOG.md"],
            files={
                "sdk/example/azure-mgmt-example/CHANGELOG.md": {
                    "head": "# Release History\n\n## 1.2.0 (2026-01-01)\n\nReal notes.\n\n## 1.1.0 (2025-01-01)\n\ntool can't generate changelog for this release, please update manually.\n"
                }
            },
        )
        self.assertEqual([], build_report(context)["reviews"][0]["findings"])

    def test_existing_release_keeps_compute_management_client(self):
        # SDK PR 48997 recorded Initial client name as not applicable because Compute already
        # had a release. ComputeManagementClient does not end in MgmtClient, and that is not a finding.
        context = _context(
            package="azure-mgmt-compute",
            first_release=False,
            changed=["sdk/compute/azure-mgmt-compute/azure/mgmt/compute/_client.py"],
            files={
                "sdk/compute/azure-mgmt-compute/azure/mgmt/compute/_client.py": {
                    "head": "class ComputeManagementClient:\n    def __init__(self, credential, subscription_id, base_url=None, **kwargs):\n        pass\n"
                }
            },
        )
        self.assertEqual([], build_report(context)["reviews"][0]["findings"])

    def test_data_plane_package_is_rejected(self):
        context = _context(package="azure-storage-blob", changed=["sdk/storage/azure-storage-blob/README.md"])
        with self.assertRaises(ReviewError):
            build_report(context)

    def test_report_rejects_a_finding_outside_the_changed_files(self):
        context = _context()
        report = build_report(context)
        report["reviews"][0]["findings"] = [
            {
                "severity": "high",
                "file": "sdk/example/azure-mgmt-example/README.md",
                "line": 1,
                "title": "Invented",
                "description": "This file was not changed.",
            }
        ]
        self.assertTrue(validate_report(report, context))


def _context(package="azure-mgmt-example", first_release=False, changed=None, files=None):
    return {
        "specPrNumber": 1,
        "specHeadSha": "a" * 40,
        "skillRevision": "eval",
        "baselineCommitSha": "b" * 40,
        "packageName": package,
        "firstRelease": first_release,
        "changedFiles": changed or ["sdk/example/azure-mgmt-example/_metadata.json"],
        "files": files or {},
    }


if __name__ == "__main__":
    unittest.main()
