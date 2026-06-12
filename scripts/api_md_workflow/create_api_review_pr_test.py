import json
import unittest
from unittest.mock import MagicMock, patch

from scripts.api_md_workflow import create_api_review_pr as workflow


def command_result(stdout="", status=0):
    return workflow.CommandResult(status=status, stdout=stdout, stderr="")


def stub_git_branches(branches):
    branch_set = set(branches)

    def runner(args, check):
        if args[0] == "fetch" and len(args) > 2 and args[2].split(":", 1)[0] in branch_set:
            return command_result()
        return command_result(status=1)

    return runner


class StubGithubApi:
    def __init__(self, head_results=None, search_results=None, on_lookup=None):
        self.head_results = head_results or []
        self.search_results = search_results or []
        self.on_lookup = on_lookup

    def _lookup(self, results):
        if self.on_lookup:
            self.on_lookup()
        return results

    def list_pull_requests_by_head(self, _head, _limit):
        return self._lookup(self.head_results)

    def search_pull_requests(self, _query, _limit):
        return self._lookup(self.search_results)

    def list_pull_requests_by_branches(self, _base, _head, _limit):
        return []

    def update_pull_request_body(self, _number, _body):
        return None

    def create_draft_pull_request(self, _base, _head, _title, _body):
        return {"html_url": "https://github.com/Azure/azure-sdk-for-python/pull/1"}


class ApiReviewPrTests(unittest.TestCase):
    def tearDown(self):
        workflow.set_command_runner_for_test(None)
        workflow.set_github_api_for_test(None)

    def test_github_api_request_uses_timeout(self):
        response = MagicMock()
        response.read.return_value = b'{"ok": true}'
        response_context = MagicMock()
        response_context.__enter__.return_value = response

        with patch.object(workflow, "urlopen", return_value=response_context) as urlopen:
            self.assertEqual(workflow.GitHubApi(None)._request("GET", "https://example.test"), {"ok": True})

        urlopen.assert_called_once()
        self.assertEqual(urlopen.call_args.kwargs["timeout"], workflow.GITHUB_API_TIMEOUT_SECONDS)

    def test_target_reference_info_links_matching_open_pr_from_direct_head_query(self):
        workflow.set_command_runner_for_test(stub_git_branches(["users/example/direct-feature"]))
        workflow.set_github_api_for_test(StubGithubApi(
            head_results=[
                {
                    "number": 45678,
                    "url": "https://github.com/Azure/azure-sdk-for-python/pull/45678",
                    "state": "OPEN",
                    "updatedAt": "2026-06-05T00:00:00Z",
                    "headRefName": "users/example/direct-feature",
                    "headRepositoryOwner": {"login": "example"},
                }
            ]
        ))

        self.assertEqual(
            workflow.target_reference_info("example:users/example/direct-feature"),
            {
                "label": "Working PR",
                "markdown": "[PR #45678](https://github.com/Azure/azure-sdk-for-python/pull/45678)",
            },
        )

    def test_target_reference_info_keeps_origin_main_as_branch(self):
        workflow.set_command_runner_for_test(stub_git_branches(["main"]))
        workflow.set_github_api_for_test(StubGithubApi(
            search_results=[
                {
                    "number": 23456,
                    "url": "https://github.com/Azure/azure-sdk-for-python/pull/23456",
                    "state": "OPEN",
                    "updatedAt": "2026-06-05T00:00:00Z",
                    "headRefName": "main",
                    "headRepositoryOwner": {"login": "example"},
                }
            ]
        ))

        self.assertEqual(
            workflow.target_reference_info("origin/main"),
            {
                "label": "Working branch",
                "markdown": "[branch `origin/main`](https://github.com/Azure/azure-sdk-for-python/tree/main)",
            },
        )

    def test_target_reference_info_treats_existing_target_tag_as_tag(self):
        pr_lookup_count = 0

        def runner(args, check):
            if args[0] == "rev-parse" and "refs/tags/azure-example_1.2.3" in args:
                return command_result()
            if args[0] == "rev-list":
                return command_result("abc123def456\n")
            return command_result(status=1)

        def on_lookup():
            nonlocal pr_lookup_count
            pr_lookup_count += 1

        workflow.set_command_runner_for_test(runner)
        workflow.set_github_api_for_test(StubGithubApi(on_lookup=on_lookup))

        self.assertEqual(
            workflow.target_reference_info("azure-example_1.2.3"),
            {
                "label": "Target tag",
                "markdown": "[tag `azure-example_1.2.3`](https://github.com/Azure/azure-sdk-for-python/commit/abc123def456)",
            },
        )
        self.assertEqual(pr_lookup_count, 0)

    def test_explicit_package_tag_target_wins_over_same_named_remote_branch(self):
        pr_lookup_count = 0

        def runner(args, check):
            if args == ["rev-parse", "--verify", "--quiet", "refs/tags/azure-example_1.2.3"]:
                return command_result()
            if args == ["rev-list", "-n", "1", "azure-example_1.2.3"]:
                return command_result("abc123def456\n")
            if args == ["fetch", "origin", "azure-example_1.2.3:refs/remotes/origin/azure-example_1.2.3"]:
                return command_result()
            return command_result(status=1)

        def on_lookup():
            nonlocal pr_lookup_count
            pr_lookup_count += 1

        workflow.set_command_runner_for_test(runner)
        workflow.set_github_api_for_test(StubGithubApi(on_lookup=on_lookup))

        self.assertEqual(workflow.resolve_target_ref("azure-example_1.2.3", "azure-example"), "azure-example_1.2.3")
        self.assertIsNone(workflow.sync_working_branch_info("azure-example_1.2.3", "azure-example"))
        self.assertEqual(
            workflow.target_reference_info("azure-example_1.2.3", "azure-example"),
            {
                "label": "Target tag",
                "markdown": "[tag `azure-example_1.2.3`](https://github.com/Azure/azure-sdk-for-python/commit/abc123def456)",
            },
        )
        self.assertEqual(pr_lookup_count, 0)

    def test_build_sync_metadata_object_records_fork_owner_and_branch(self):
        workflow.set_command_runner_for_test(stub_git_branches(["users/example/feature"]))
        workflow.set_github_api_for_test(StubGithubApi(
            search_results=[
                {
                    "number": 47204,
                    "url": "https://github.com/Azure/azure-sdk-for-python/pull/47204",
                    "state": "OPEN",
                    "updatedAt": "2026-06-05T00:00:00Z",
                    "headRefName": "users/example/feature",
                    "headRepositoryOwner": {"login": "example"},
                }
            ]
        ))

        metadata = workflow.build_sync_metadata_object(
            package_name="azure-example",
            package_dir="sdk/service/azure-example",
            base_branch="apireview/base_azure-example_1.0.0",
            review_branch="apireview/review_azure-example_1.1.0",
            head_selector="example:users/example/feature",
        )

        self.assertEqual(metadata["workingOwner"], "example")
        self.assertEqual(metadata["workingBranch"], "users/example/feature")
        self.assertEqual(metadata["workingPrNumber"], 47204)

    def test_build_sync_metadata_object_omits_metadata_for_tag_targets(self):
        pr_lookup_count = 0

        def runner(args, check):
            if args[0] == "rev-parse" and "refs/tags/azure-example_1.2.3" in args:
                return command_result()
            return command_result(status=1)

        def on_lookup():
            nonlocal pr_lookup_count
            pr_lookup_count += 1

        workflow.set_command_runner_for_test(runner)
        workflow.set_github_api_for_test(StubGithubApi(on_lookup=on_lookup))

        self.assertIsNone(
            workflow.build_sync_metadata_object(
                package_name="azure-example",
                package_dir="sdk/service/azure-example",
                base_branch="apireview/base_azure-example_1.0.0",
                review_branch="apireview/review_azure-example_1.1.0",
                head_selector="azure-example_1.2.3",
            )
        )
        self.assertEqual(pr_lookup_count, 0)

    def test_build_review_pr_body_calls_out_static_tag_to_tag_reviews(self):
        body = workflow.build_review_pr_body(
            package_name="azure-example",
            target_version="1.2.3",
            base_version="1.2.2",
            working_reference={
                "label": "Target tag",
                "markdown": "[tag `azure-example_1.2.3`](https://github.com/Azure/azure-sdk-for-python/commit/abc123)",
            },
            baseline_ref="[tag `azure-example_1.2.2`](https://github.com/Azure/azure-sdk-for-python/commit/def456)",
            sync_metadata_block=None,
        )

        self.assertIn(
            "> [!WARNING]\n"
            "> Static tag-to-tag review; this PR cannot be automatically updated from a working branch.",
            body,
        )
        self.assertNotIn("Update behavior", body)
        self.assertNotIn("api-md-review-sync", body)

    def test_build_review_pr_body_includes_sync_metadata_for_working_branch_reviews(self):
        metadata_block = workflow.build_sync_metadata_block(
            {
                "schemaVersion": 1,
                "repository": "Azure/azure-sdk-for-python",
                "packageName": "azure-example",
                "packageDir": "sdk/service/azure-example",
                "baseBranch": "apireview/base_azure-example_1.0.0",
                "reviewBranch": "apireview/review_azure-example_1.1.0",
                "workingOwner": "Azure",
                "workingBranch": "main",
                "workingPrNumber": None,
            }
        )

        body = workflow.build_review_pr_body(
            package_name="azure-example",
            target_version="1.1.0b1",
            base_version="1.0.0",
            working_reference={
                "label": "Working branch",
                "markdown": "[branch `main`](https://github.com/Azure/azure-sdk-for-python/tree/main)",
            },
            baseline_ref="[tag `azure-example_1.0.0`](https://github.com/Azure/azure-sdk-for-python/commit/def456)",
            sync_metadata_block=metadata_block,
        )

        self.assertIn("- **Working branch:**", body)
        self.assertNotIn("Static tag-to-tag review", body)
        self.assertIn("<!-- api-md-review-sync", body)
        self.assertIn('"workingBranch": "main"', body)

    def test_api_results_have_api_diff_ignores_metadata_only_changes(self):
        self.assertFalse(
            workflow.api_results_have_api_diff(
                workflow.ApiResult(b"# API\n\nclass Same\n", b"apiMdSha256: old", "1.0.0"),
                workflow.ApiResult(b"# API\n\nclass Same\n", b"apiMdSha256: new", "1.0.1"),
            )
        )

    def test_replace_sync_metadata_block_replaces_stale_hidden_metadata(self):
        old_block = workflow.build_sync_metadata_block(
            {
                "schemaVersion": 1,
                "repository": "Azure/azure-sdk-for-python",
                "packageName": "old-package",
                "packageDir": "sdk/service/old-package",
                "baseBranch": "apireview/base_old-package_1.0.0",
                "reviewBranch": "apireview/review_old-package_1.1.0",
                "workingOwner": "Azure",
                "workingBranch": "old-feature",
            }
        )
        new_block = workflow.build_sync_metadata_block(
            {
                "schemaVersion": 1,
                "repository": "Azure/azure-sdk-for-python",
                "packageName": "azure-example",
                "packageDir": "sdk/service/azure-example",
                "baseBranch": "apireview/base_azure-example_1.0.0",
                "reviewBranch": "apireview/review_azure-example_1.1.0",
                "workingOwner": "Azure",
                "workingBranch": "feature/api-change",
            }
        )

        body = workflow.replace_sync_metadata_block(f"Review body\n\n{old_block}", new_block)

        self.assertTrue(body.startswith("Review body\n\n<!-- api-md-review-sync"))
        self.assertIn("DO NOT MODIFY THESE CONTENTS!", body)
        self.assertIn('"packageName": "azure-example"', body)
        self.assertNotIn("old-package", body)
        self.assertEqual(body.count("api-md-review-sync"), 1)

    def test_sync_metadata_block_json_is_parseable(self):
        block = workflow.build_sync_metadata_block({"schemaVersion": 1, "workingPrNumber": None})
        json_text = block.replace("<!-- api-md-review-sync\n", "").replace("DO NOT MODIFY THESE CONTENTS!\n", "").replace("\n-->", "")
        self.assertEqual(json.loads(json_text), {"schemaVersion": 1, "workingPrNumber": None})


if __name__ == "__main__":
    unittest.main()