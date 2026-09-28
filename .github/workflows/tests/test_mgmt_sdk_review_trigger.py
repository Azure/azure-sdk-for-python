"""Manual and label triggers share trusted target resolution and publication."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from test_mgmt_sdk_review_context import MODULE as collector
from test_mgmt_sdk_review_comment import HEAD, REPO, WORKFLOW, envelope, production_fixture
import mgmt_sdk_review_contract as contract


def pull_request():
    return {
        "number": 49107,
        "state": "open",
        "base": {"repo": {"full_name": REPO}},
        "head": {
            "sha": HEAD,
            "ref": "sdkauto/example",
            "repo": {"full_name": REPO, "owner": {"login": "Azure", "type": "Organization"}},
        },
    }


class ReviewTriggerTests(unittest.TestCase):
    def setUp(self):
        self.client = mock.Mock(repository=REPO)
        self.client.get.return_value = pull_request()
        self.event = {"inputs": {"pr_number": "49107"}}

    def resolve(self, **kwargs):
        values = {
            "client": self.client,
            "event": self.event,
            "event_name": "workflow_dispatch",
            "actor": "msyyc",
            "triggering_actor": "msyyc",
            "ref": "refs/heads/main",
            **kwargs,
        }
        return collector.resolve_review_target(**values)

    def test_main_and_feature_branch_resolve_same_pr_head(self):
        for branch in ("main", "mgmt-review-reliability"):
            with self.subTest(branch=branch):
                self.client.get.reset_mock()
                target = self.resolve(ref="refs/heads/" + branch)
                self.assertEqual({"pr_number": "49107", "head_sha": HEAD}, target)
                self.client.get.assert_called_once_with(f"/repos/{REPO}/pulls/49107")

    def test_manual_permissions_reject_before_api_access(self):
        cases = [
            ({"actor": "someone-else"}, "manual_actor_forbidden"),
            ({"triggering_actor": "someone-else"}, "manual_actor_forbidden"),
            ({"actor": ""}, "manual_actor_forbidden"),
            ({"triggering_actor": ""}, "manual_actor_forbidden"),
            ({"ref": "refs/tags/main"}, "manual_ref_forbidden"),
            ({"ref": "refs/pull/49223/head"}, "manual_ref_forbidden"),
            ({"ref": "refs/heads/"}, "manual_ref_forbidden"),
        ]
        for arguments, code in cases:
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(collector.GitHubApiError, code):
                    self.resolve(**arguments)
        self.client.repository = "msyyc/azure-sdk-for-python"
        with self.assertRaisesRegex(collector.GitHubApiError, "manual_repository_forbidden"):
            self.resolve()
        self.client.get.assert_not_called()

    def test_invalid_numbers_cannot_select_arbitrary_targets(self):
        for number in (None, True, 49107, "", "0", "-1", "01", "1.0", "1e3", "49107\n", "1/../2", "1" * 11):
            with self.subTest(number=number):
                self.event["inputs"]["pr_number"] = number
                with self.assertRaisesRegex(collector.GitHubApiError, "invalid_pr_number"):
                    self.resolve()
        self.client.get.assert_not_called()

    def test_personal_forks_deleted_and_lookalike_owners_rejected(self):
        sources = [
            None,
            {"full_name": "msyyc/azure-sdk-for-python", "owner": {"login": "msyyc", "type": "User"}},
            {"full_name": "Azure-personal/sdk", "owner": {"login": "Azure-personal", "type": "Organization"}},
            {"full_name": "Azure/sdk", "owner": {"login": "Azure", "type": "User"}},
            {"full_name": "personal/sdk", "owner": {"login": "Azure", "type": "Organization"}},
        ]
        for source in sources:
            with self.subTest(source=source):
                self.client.get.return_value["head"]["repo"] = source
                with self.assertRaisesRegex(collector.GitHubApiError, "manual_source_forbidden"):
                    self.resolve()

    def test_azure_organization_sources_and_closed_prs_supported(self):
        self.client.get.return_value["head"]["repo"]["full_name"] = "Azure/another-sdk-fork"
        self.client.get.return_value["state"] = "closed"
        self.assertEqual(HEAD, self.resolve(actor="MSYYC", triggering_actor="MSYYC")["head_sha"])

    def test_wrong_api_target_and_missing_head_fail_closed(self):
        for change, code in (
            ({"number": 123}, "wrong_review_target"),
            ({"base": {"repo": {"full_name": "personal/sdk"}}}, "wrong_review_target"),
            ({"head": None}, "invalid_head_revision"),
            ({"head": {"sha": "main"}}, "invalid_head_revision"),
        ):
            with self.subTest(change=change):
                self.client.get.return_value = {**pull_request(), **change}
                with self.assertRaisesRegex(collector.GitHubApiError, code):
                    self.resolve()
        self.client.get.side_effect = collector.GitHubApiError("Forbidden", status=403)
        with self.assertRaisesRegex(collector.GitHubApiError, "Forbidden"):
            self.resolve()

    def test_label_trigger_preserves_eligibility_and_rejects_stale_heads(self):
        self.client.get.return_value["head"]["repo"]["owner"] = {"login": "personal", "type": "User"}
        self.client.get.return_value["head"]["repo"]["full_name"] = "personal/sdk"
        event = {
            "action": "labeled",
            "label": {"name": "mgmt-review-needed"},
            "pull_request": {"number": 49107, "head": {"sha": HEAD}},
        }
        arguments = {"event": event, "event_name": "pull_request_target", "actor": "other", "triggering_actor": "other"}
        self.assertEqual(HEAD, self.resolve(**arguments)["head_sha"])
        event["pull_request"]["head"]["sha"] = "a" * 40
        with self.assertRaisesRegex(collector.GitHubApiError, "stale_event_head"):
            self.resolve(**arguments)
        event["label"]["name"] = "other"
        with self.assertRaisesRegex(collector.GitHubApiError, "invalid_trigger"):
            self.resolve(**arguments)
        with self.assertRaisesRegex(collector.GitHubApiError, "invalid_trigger"):
            self.resolve(event_name="push")

    def test_environment_resolver_exports_only_authorized_target(self):
        with tempfile.TemporaryDirectory() as directory:
            event_path = Path(directory, "event.json")
            output_path = Path(directory, "output.txt")
            event_path.write_text(json.dumps(self.event), encoding="utf-8")
            env = {
                "GH_REPOSITORY": REPO,
                "GH_TOKEN": "test",
                "GITHUB_EVENT_PATH": str(event_path),
                "GITHUB_OUTPUT": str(output_path),
                "GITHUB_EVENT_NAME": "workflow_dispatch",
                "GITHUB_ACTOR": "msyyc",
                "GITHUB_TRIGGERING_ACTOR": "msyyc",
                "GITHUB_REF": "refs/heads/main",
            }
            with mock.patch.dict(os.environ, env), mock.patch.object(
                collector, "GitHubClient", return_value=self.client
            ):
                collector.resolve_target()
                self.assertEqual(f"pr_number=49107\nhead_sha={HEAD}\n", output_path.read_text(encoding="utf-8"))
                output_path.unlink()
                os.environ["GITHUB_TRIGGERING_ACTOR"] = "other"
                with self.assertRaisesRegex(collector.GitHubApiError, "manual_actor_forbidden"):
                    collector.resolve_target()
                self.assertFalse(output_path.exists())

    def test_partial_reruns_reauthorize_agent_and_publisher(self):
        scripts = WORKFLOW.parent / "scripts"
        for script, arguments in (
            ("mgmt_sdk_review_service.py", ["--context", "must-not-be-read.json"]),
            ("mgmt_sdk_review_contract.py", ["publish"]),
        ):
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(scripts / script), *arguments],
                    env={
                        **os.environ,
                        "GH_REPOSITORY": REPO,
                        "GITHUB_EVENT_NAME": "workflow_dispatch",
                        "GITHUB_ACTOR": "msyyc",
                        "GITHUB_TRIGGERING_ACTOR": "other",
                        "GITHUB_REF": "refs/heads/main",
                    },
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=10,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("manual_actor_forbidden", result.stderr)
                self.assertNotIn("No such file", result.stderr)
                if script == "mgmt_sdk_review_contract.py":
                    self.assertIn("No review will be published or hidden", result.stderr)

    def test_compiled_pipeline_uses_one_resolved_target_without_test_bypass(self):
        lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", lock)
        self.assertIn("pull_request_target:", lock)
        self.assertIn("inputs.pr_number", lock)
        self.assertIn("job-discriminator:", source)
        self.assertNotIn("publish:", source)
        self.assertNotIn("staged:", source)
        collector_job = lock.split("\n  review_context:\n", 1)[1].split("\n  safe_outputs:", 1)[0]
        self.assertLess(collector_job.index("id: target"), collector_job.index("Collect immutable"))
        self.assertIn("head_sha: ${{ steps.target.outputs.head_sha }}", collector_job)
        self.assertIn("pr_number: ${{ steps.target.outputs.pr_number }}", collector_job)
        self.assertIn("ref: ${{ github.workflow_sha }}", collector_job)
        for job_name in ("agent", "safe_outputs"):
            job = re.split(r"\n  [a-z_]+:\n", lock.split(f"\n  {job_name}:\n", 1)[1])[0]
            self.assertIn("- review_context", job)
            self.assertIn("PR_NUMBER: ${{ needs.review_context.outputs.pr_number }}", job)
            self.assertIn("REVIEW_HEAD_SHA: ${{ needs.review_context.outputs.head_sha }}", job)
            self.assertNotIn("REVIEW_HEAD_SHA: ${{ github.event.pull_request.head.sha }}", job)
        self.assertEqual(1, lock.count("name: Validate and render management SDK review"))
        self.assertEqual(1, lock.count("name: Process Safe Outputs"))

    @unittest.skipUnless(os.environ.get("GH_AW_RUNTIME"), "Set GH_AW_RUNTIME to pinned gh-aw actions/setup/js")
    def test_pinned_runtime_publishes_manual_and_label_reviews_identically(self):
        data, trusted = production_fixture()
        prepared = contract.prepare_output(envelope(data), trusted)
        lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
        encoded = re.search(r'GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG: (".*")', lock)[1]
        config = json.loads(json.loads(encoded))["add_comment"]
        self.assertEqual("${{ needs.review_context.outputs.pr_number }}", config["target"])
        self.assertEqual(1, config["max"])
        config["target"] = self.resolve()["pr_number"]
        results = []
        for event_name in ("pull_request_target", "workflow_dispatch"):
            result = subprocess.run(
                ["node", str(Path(__file__).with_name("mgmt_review_runtime.cjs"))],
                input=json.dumps(
                    {
                        "mode": "publish",
                        "eventName": event_name,
                        "payload": prepared,
                        "handlerConfig": config,
                        "existing": True,
                    }
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=30,
            )
            published = json.loads(result.stdout)
            self.assertTrue(published["result"]["success"], published)
            self.assertEqual(1, published["writes"])
            self.assertEqual(1, published["hides"])
            self.assertEqual(49107, published["comment"]["issue_number"])
            results.append(published["comment"]["body"])
        self.assertEqual(results[0], results[1])


if __name__ == "__main__":
    unittest.main()
