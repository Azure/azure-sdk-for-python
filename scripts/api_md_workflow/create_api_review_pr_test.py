import json
import tempfile
import unittest
from pathlib import Path
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
        workflow.set_github_api_for_test(
            StubGithubApi(
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
            )
        )

        self.assertEqual(
            workflow.target_reference_info("example:users/example/direct-feature"),
            {
                "label": "Working PR",
                "markdown": "[PR #45678](https://github.com/Azure/azure-sdk-for-python/pull/45678)",
            },
        )

    def test_target_reference_info_keeps_origin_main_as_branch(self):
        workflow.set_command_runner_for_test(stub_git_branches(["main"]))
        workflow.set_github_api_for_test(
            StubGithubApi(
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
            )
        )

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
        workflow.set_github_api_for_test(
            StubGithubApi(
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
            )
        )

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

    def test_package_version_major_minor(self):
        self.assertEqual(workflow.package_version_major_minor("1.2.3b1"), "1.2")
        self.assertEqual(workflow.package_version_major_minor("12"), "12.0")

    def test_parse_package_work_item_id(self):
        self.assertEqual(workflow.parse_package_work_item_id("Work Item ID: 31370\n"), 31370)
        self.assertEqual(workflow.parse_package_work_item_id('{"work_item_id":31371}'), 31371)

    def test_pkg_work_item_value_no_shell(self):
        with (
            patch.object(workflow, "resolve_azsdk_executable", return_value="azsdk") as resolve_azsdk,
            patch.object(workflow, "run", return_value=workflow.CommandResult(0, "Work Item ID: 31370\n")) as run,
        ):
            self.assertEqual(workflow.package_work_item_metadata_value("azure-example", "1.2.3b1"), "31370")

        resolve_azsdk.assert_called_once_with()
        run.assert_called_once_with(
            [
                "azsdk",
                "package",
                "find-work-item",
                "--package-name",
                "azure-example",
                "--package-version",
                "1.2",
                "--language",
                "Python",
            ],
            check=False,
            capture=True,
        )

    def test_pkg_work_item_value_error(self):
        with (
            patch.object(workflow, "resolve_azsdk_executable", return_value="azsdk"),
            patch.object(workflow, "run", return_value=workflow.CommandResult(1, "", "Unexpected failure")),
            patch.object(workflow, "log_warning") as log_warning,
        ):
            self.assertEqual(workflow.package_work_item_metadata_value("azure-example", "1.2.3b1"), '"ERROR"')

        log_warning.assert_called_once()
        self.assertIn('packageWorkItemId: "ERROR"', log_warning.call_args.args[0])

    def test_pkg_work_item_value_unknown_missing(self):
        with (
            patch.object(workflow, "resolve_azsdk_executable", return_value="azsdk"),
            patch.object(
                workflow,
                "run",
                return_value=workflow.CommandResult(
                    1, "[ERROR] No package work item found for package 'azure-example'.\n", ""
                ),
            ),
            patch.object(workflow, "log_warning") as log_warning,
        ):
            self.assertEqual(workflow.package_work_item_metadata_value("azure-example", "1.2.3b1"), '"Unknown"')

        log_warning.assert_called_once()
        self.assertIn('packageWorkItemId: "Unknown"', log_warning.call_args.args[0])

    def test_pkg_work_item_value_unknown_no_id(self):
        with (
            patch.object(workflow, "resolve_azsdk_executable", return_value="azsdk"),
            patch.object(workflow, "run", return_value=workflow.CommandResult(0, "No package work item found\n", "")),
            patch.object(workflow, "log_warning") as log_warning,
        ):
            self.assertEqual(workflow.package_work_item_metadata_value("azure-example", "1.2.3b1"), '"Unknown"')

        log_warning.assert_called_once()
        self.assertIn('packageWorkItemId: "Unknown"', log_warning.call_args.args[0])

    def test_azsdk_preflight_checks_help(self):
        with (
            patch.object(workflow, "resolve_azsdk_executable", return_value="azsdk") as resolve_azsdk,
            patch.object(workflow, "run", return_value=workflow.CommandResult(0, "help")) as run,
        ):
            workflow.ensure_azsdk_find_work_item_available()

        resolve_azsdk.assert_called_once_with()
        run.assert_called_once_with(["azsdk", "package", "find-work-item", "--help"], check=False, capture=True)

    def test_azsdk_preflight_fails_if_stale(self):
        with (
            patch.object(workflow, "resolve_azsdk_executable", return_value="azsdk"),
            patch.object(workflow, "run", return_value=workflow.CommandResult(1, "", "Unknown command")),
        ):
            with self.assertRaisesRegex(RuntimeError, "package find-work-item"):
                workflow.ensure_azsdk_find_work_item_available()

    def test_main_preflights_azsdk_first(self):
        with (
            patch.object(
                workflow, "ensure_azsdk_find_work_item_available", side_effect=RuntimeError("missing command")
            ),
            patch.object(workflow, "find_package_dir") as find_package_dir,
        ):
            with self.assertRaisesRegex(RuntimeError, "missing command"):
                workflow.main(["--package-name", "azure-example", "--base", "azure-example_1.0.0"])

        find_package_dir.assert_not_called()

    def test_resolve_azsdk_uses_path_first(self):
        with patch.object(workflow.shutil, "which", return_value="C:/tools/azsdk.exe"):
            self.assertEqual(workflow.resolve_azsdk_executable(), "C:/tools/azsdk.exe")

    def test_resolve_azsdk_uses_common_dir(self):
        def is_file(candidate):
            return str(candidate).replace("\\", "/").endswith("/bin/azsdk.exe")

        with (
            patch.object(workflow.shutil, "which", return_value=None),
            patch.object(workflow.Path, "home", return_value=Path("C:/Users/example")),
            patch.object(workflow.Path, "is_file", is_file),
        ):
            self.assertEqual(
                workflow.resolve_azsdk_executable().replace("\\", "/"),
                "C:/Users/example/bin/azsdk.exe",
            )

    def test_resolve_azsdk_uses_mcp_dir(self):
        def is_file(candidate):
            return str(candidate).replace("\\", "/").endswith("/.azure-sdk-mcp/azsdk.exe")

        with (
            patch.object(workflow.shutil, "which", return_value=None),
            patch.object(workflow.Path, "home", return_value=Path("C:/Users/example")),
            patch.object(workflow.Path, "is_file", is_file),
        ):
            self.assertEqual(
                workflow.resolve_azsdk_executable().replace("\\", "/"),
                "C:/Users/example/.azure-sdk-mcp/azsdk.exe",
            )

    def test_resolve_azsdk_missing_errors(self):
        with (
            patch.object(workflow.shutil, "which", return_value=None),
            patch.object(workflow.Path, "home", return_value=Path("C:/Users/example")),
            patch.object(workflow.Path, "is_file", return_value=False),
        ):
            with self.assertRaisesRegex(RuntimeError, "azure-sdk-mcp.ps1"):
                workflow.resolve_azsdk_executable()

    def test_add_package_work_item_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir)
            metadata_file = package_dir / "api.metadata.yml"
            metadata_file.write_text(
                "apiMdSha256: abc123\r\nparserVersion: 1.0\r\n",
                encoding="utf-8",
            )

            with patch.object(workflow, "package_work_item_metadata_value", return_value="31370") as package_work_item:
                workflow.add_package_work_item_metadata("azure-example", "1.2.3b1", package_dir)

            package_work_item.assert_called_once_with("azure-example", "1.2.3b1")
            self.assertEqual(
                metadata_file.read_text(encoding="utf-8"),
                "apiMdSha256: abc123\npackageWorkItemId: 31370\nparserVersion: 1.0\n",
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
        json_text = (
            block.replace("<!-- api-md-review-sync\n", "")
            .replace("DO NOT MODIFY THESE CONTENTS!\n", "")
            .replace("\n-->", "")
        )
        self.assertEqual(json.loads(json_text), {"schemaVersion": 1, "workingPrNumber": None})


if __name__ == "__main__":
    unittest.main()
