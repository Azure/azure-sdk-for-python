"""The untrusted intake cannot authorize or select privileged review execution."""

import copy
from pathlib import Path
import unittest
from unittest import mock

from test_mgmt_sdk_review_context import MODULE as collector
import mgmt_sdk_review_routing as routing

HEAD = "b" * 40
ROOT = f"/repos/{routing.REPOSITORY}"


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.run = {
            "id": 123,
            "workflow_id": 456,
            "event": "pull_request",
            "status": "completed",
            "conclusion": "success",
            "repository": {"full_name": routing.REPOSITORY},
            "head_repository": {"id": 789},
            "head_sha": HEAD,
            "run_attempt": 1,
            "created_at": "2026-11-26T08:42:05Z",
            "actor": {"id": 42},
            "pull_requests": [],
        }
        self.pull = {
            "number": 49107,
            "state": "open",
            "base": {"repo": {"full_name": routing.REPOSITORY}},
            "head": {"sha": HEAD, "repo": {"id": 789, "full_name": "personal/sdk"}},
            "labels": [{"name": routing.REVIEW_LABEL}],
        }
        self.events = [
            {
                "id": 321,
                "event": "labeled",
                "created_at": "2026-11-26T08:42:03Z",
                "label": {"name": routing.REVIEW_LABEL},
                "actor": {"id": 42, "login": "maintainer", "type": "User"},
            }
        ]
        self.jobs = {"total_count": 1, "jobs": [{"name": "request", "status": "completed", "conclusion": "success"}]}
        self.workflow = {"id": 456}
        self.permission = {"permission": "write"}
        self.pulls = [self.pull]
        self.truncated = False
        self.client = mock.Mock(repository=routing.REPOSITORY)
        self.client.get.side_effect = lambda path: {
            f"{ROOT}/actions/runs/123": self.run,
            f"{ROOT}/actions/workflows/pr-review-intake.yml": self.workflow,
            f"{ROOT}/actions/runs/123/attempts/1/jobs?per_page=100": self.jobs,
            f"{ROOT}/pulls/49107": self.pull,
            f"{ROOT}/collaborators/maintainer/permission": self.permission,
        }[path]
        self.client.paged_get.side_effect = lambda path, max_items: (
            self.pulls if "/commits/" in path else self.events,
            self.truncated,
        )

    def authorize(self, **kwargs):
        return routing.authorized_request(self.client, "123", **kwargs)

    def resolve(self, **inputs):
        return collector.resolve_review_target(
            self.client,
            {
                "inputs": {
                    "pr_number": "49107",
                    "head_sha": HEAD,
                    "request_run_id": "123",
                    "request_event_id": "321",
                    **inputs,
                }
            },
            "workflow_dispatch",
            "github-actions[bot]",
            "github-actions[bot]",
            routing.DEFAULT_REF,
        )

    def test_fork_with_empty_workflow_run_prs_routes_and_revalidates(self):
        request = self.authorize()
        self.assertEqual(
            {"pr_number": "49107", "head_sha": HEAD, "request_run_id": "123", "request_event_id": "321"}, request
        )
        self.assertEqual({"pr_number": "49107", "head_sha": HEAD}, self.resolve())
        self.client.paged_get.assert_any_call(f"{ROOT}/commits/{HEAD}/pulls", max_items=100)
        with mock.patch.object(routing.subprocess, "run") as dispatch:
            routing.route_review(self.client, {"workflow_run": {"id": 123}}, routing.DEFAULT_REF)
        command = dispatch.call_args.args[0]
        self.assertEqual(
            ["gh", "workflow", "run", routing.REVIEW_WORKFLOW, "--repo", routing.REPOSITORY, "--ref", "main"],
            command[:8],
        )
        for key, value in request.items():
            self.assertIn(f"{key}={value}", command)

    def test_wrong_workflow_repository_event_and_run_fail_closed(self):
        for key, value in (
            ("id", 124),
            ("workflow_id", 999),
            ("event", "push"),
            ("status", "in_progress"),
            ("conclusion", "failure"),
            ("repository", {"full_name": "personal/sdk"}),
            ("head_sha", "main"),
        ):
            with self.subTest(key=key):
                original = self.run[key]
                self.run[key] = value
                with self.assertRaises(ValueError):
                    self.authorize()
                self.run[key] = original

    def test_skipped_or_incomplete_request_job_is_not_authorization(self):
        for conclusion in ("skipped", "failure", "cancelled"):
            self.jobs["jobs"][0]["conclusion"] = conclusion
            self.assertIsNone(self.authorize())
        self.jobs["jobs"] = []
        self.assertIsNone(self.authorize())

    def test_stale_closed_unlabeled_or_deleted_fork_is_not_routed(self):
        for key, value in (
            ("state", "closed"),
            ("labels", []),
            ("head", {"sha": "a" * 40, "repo": {"id": 789}}),
            ("head", {"sha": HEAD, "repo": None}),
            ("head", {"sha": HEAD, "repo": {"id": 790}}),
            ("base", {"repo": {"full_name": "personal/sdk"}}),
        ):
            with self.subTest(key=key, value=value):
                original = self.pull[key]
                self.pull[key] = value
                self.assertIsNone(self.authorize())
                self.pull[key] = original

    def test_ambiguous_or_truncated_associations_fail_closed(self):
        self.pulls.append(copy.deepcopy(self.pull))
        with self.assertRaisesRegex(ValueError, "unambiguous"):
            self.authorize()
        self.pulls.pop()
        self.truncated = True
        with self.assertRaises(ValueError):
            self.authorize()

    def test_stale_replaced_removed_or_unattributable_labels_do_not_authorize(self):
        for key, value in (
            ("event", "unlabeled"),
            ("actor", {"id": 43}),
            ("created_at", "2026-11-26T08:37:04Z"),
            ("created_at", "2026-11-26T08:42:06Z"),
        ):
            with self.subTest(key=key):
                original = self.events[0][key]
                self.events[0][key] = value
                self.assertIsNone(self.authorize())
                self.events[0][key] = original
        self.assertIsNone(self.authorize(event_id="322"))
        self.events = []
        self.assertIsNone(self.authorize())

    def test_latest_label_event_wins_even_with_out_of_order_history(self):
        self.events.insert(0, {**self.events[0], "id": 322, "event": "unlabeled"})
        self.assertIsNone(self.authorize())

    def test_unprivileged_requester_and_bot_identity_are_insufficient(self):
        self.permission["permission"] = "read"
        with self.assertRaisesRegex(ValueError, "write access"):
            self.authorize()
        self.permission["permission"] = "write"
        self.events[0]["actor"]["type"] = "Bot"
        with self.assertRaises(ValueError):
            self.authorize()
        for field in ("request_run_id", "request_event_id", "head_sha"):
            with self.subTest(field=field):
                with self.assertRaises(collector.GitHubApiError):
                    self.resolve(**{field: ""})

    def test_dispatch_cannot_substitute_target_or_head(self):
        for inputs in ({"pr_number": "49108"}, {"head_sha": "a" * 40}, {"request_event_id": "322"}):
            with self.subTest(inputs=inputs):
                with self.assertRaises(collector.GitHubApiError):
                    self.resolve(**inputs)

    def test_untrusted_ref_or_repository_rejects_before_api_or_dispatch(self):
        with mock.patch.object(routing.subprocess, "run") as dispatch:
            for ref in ("refs/heads/feature", "refs/pull/1/merge", "refs/tags/main"):
                with self.assertRaises(ValueError):
                    routing.route_review(self.client, {"workflow_run": {"id": 123}}, ref)
            self.client.repository = "personal/sdk"
            with self.assertRaises(ValueError):
                routing.route_review(self.client, {"workflow_run": {"id": 123}}, routing.DEFAULT_REF)
            dispatch.assert_not_called()
        self.client.get.assert_not_called()

    def test_unrelated_label_skips_without_dispatch(self):
        self.pull["labels"] = [{"name": "other"}]
        with mock.patch.object(routing.subprocess, "run") as dispatch:
            routing.route_review(self.client, {"workflow_run": {"id": 123}}, routing.DEFAULT_REF)
            dispatch.assert_not_called()

    def test_intake_is_inert_and_router_only_executes_trusted_tooling(self):
        workflows = Path(__file__).parents[1]
        intake = (workflows / "pr-review-intake.yml").read_text(encoding="utf-8")
        router = (workflows / "pr-review-router.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", intake)
        self.assertIn("permissions: {}", intake)
        for unsafe in ("uses:", "secrets.", "checkout", "upload-artifact"):
            self.assertNotIn(unsafe, intake)
        self.assertIn("workflow_run:", router)
        self.assertIn("actions: write", router)
        self.assertIn("ref: ${{ github.workflow_sha }}", router)
        self.assertIn("persist-credentials: false", router)
        self.assertNotIn("download-artifact", router)
        self.assertNotIn("pull_request_target", intake + router)


if __name__ == "__main__":
    unittest.main()
