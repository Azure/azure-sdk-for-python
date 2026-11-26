"""Offline fixtures for release-rotation queues and conservative activity checks."""

import base64
from copy import deepcopy
import importlib.util
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "triage_prs.py"
SPEC = importlib.util.spec_from_file_location("triage_prs", SCRIPT)
triage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(triage)

REPO = "Azure/azure-sdk-for-python"
PR_URL = f"https://github.com/{REPO}/pull/42"
RUN_URL = f"https://github.com/{REPO}/actions/runs/100"
PLAN_URL = "https://azsdk-releaseplan-dashboard-test.westus-01.azurewebsites.net/?releaseplan=37904"
HEAD = "a" * 40
OLD = "b" * 40
WHEN = "2026-10-26T09:00:00Z"
LATER = "2026-10-26T10:00:00Z"
PR = {
    "number": 42,
    "title": "[AutoPR azure-mgmt-example]-generated",
    "state": "open",
    "draft": False,
    "html_url": PR_URL,
    "updated_at": WHEN,
    "head": {"sha": HEAD},
    "base": {"sha": OLD},
    "changed_files": 1,
    "user": {"login": "author"},
    "labels": [],
    "body": f"[Release plan #37904]({PLAN_URL})",
}
SUMMARY = {"number": 42, "title": PR["title"], "isDraft": False, "updatedAt": WHEN}
FILE = {
    "filename": "sdk/example/azure-mgmt-example/azure/mgmt/example/_version.py",
    "status": "modified",
    "patch": '+VERSION = "1.0.0b1"',
}


def review(state="APPROVED", login="maintainer", when=WHEN, identifier=1, commit=HEAD):
    return {
        "id": identifier,
        "user": {"login": login},
        "state": state,
        "submitted_at": when,
        "commit_id": commit,
        "html_url": PR_URL + f"#pullrequestreview-{identifier}",
        "body": "",
    }


def run(status="completed", head=HEAD, associated=True):
    return {
        "id": 100,
        "workflow_id": 9,
        "status": status,
        "conclusion": "success" if status == "completed" else None,
        "created_at": triage.datetime.now(triage.timezone.utc).isoformat(),
        "html_url": RUN_URL,
        # Deliberately different from the associated PR head.
        "head_sha": OLD,
        "pull_requests": [{"number": 42, "head": {"sha": head}}] if associated else [],
    }


def comment(body="Please check", login="author", when=LATER, identifier=2):
    return {
        "id": identifier,
        "body": body,
        "user": {"login": login},
        "created_at": when,
        "html_url": PR_URL + f"#issuecomment-{identifier}",
    }


def bot(body=None):
    return comment(
        body
        or (
            "## Management SDK PR review\nPartial result; human review required.\n"
            f"<!-- gh-aw-agentic-workflow: test, workflow_id: mgmt-sdk-pr-review, run: {RUN_URL} -->"
        ),
        "github-actions[bot]",
    )


def row(approval=None, bot_comment=None):
    return {
        "pr": deepcopy(PR),
        "name": "azure-mgmt-example",
        "version": "1.0.0b1",
        "approval": approval,
        "owners": ["@maintainer"],
        "ownership_known": True,
        "review_decision": "APPROVED" if approval else "REVIEW_REQUIRED",
        "bot_review": bot_comment,
        "followups": [],
        "release_plans": [PLAN_URL],
        "issues": [],
        "queues": {},
    }


class MemoryRequests:
    def __init__(self):
        self.records = {}

    def status(self, repo, number, head):
        return self.records.get((repo.casefold(), number, head))

    def claim(self, repo, number, head):
        if self.status(repo, number, head):
            return False
        self.finish(repo, number, head, "pending")
        return True

    def finish(self, repo, number, head, status):
        self.records[repo.casefold(), number, head] = status


class FakeGitHub:
    repo = REPO

    def __init__(self):
        self.details = deepcopy(PR)
        self.reviews = [review()]
        self.comments = [bot()]
        self.inline = []
        self.files = [deepcopy(FILE)]
        self.linked_run = run()
        self.workflow_runs = []
        self.ownership_error = False
        self.skipped_team = False
        self.activity_error = False
        self.last_details = None
        self.get_count = 0
        self.requests = MemoryRequests()

    def get(self, endpoint):
        self.get_count += 1
        if self.get_count > 1 and self.last_details is not None:
            return deepcopy(self.last_details)
        return deepcopy(self.details)

    def cached(self, endpoint):
        if "/actions/runs/" in endpoint:
            return deepcopy(self.linked_run)
        return {"id": 9}

    def pages(self, endpoint, key=None):
        if "/actions/workflows/" in endpoint:
            if self.activity_error:
                raise triage.CollectionError("HTTP 403")
            return deepcopy(self.workflow_runs)
        if "/reviews?" in endpoint:
            return deepcopy(self.reviews)
        if "/issues/" in endpoint:
            return deepcopy(self.comments)
        if "/comments?" in endpoint:
            return deepcopy(self.inline)
        return deepcopy(self.files)

    def owners(self, base_sha, files, package):
        if self.ownership_error:
            raise triage.CollectionError("Team membership unreadable")
        return {"maintainer"}, ["@maintainer"], self.skipped_team


class ApprovalTests(unittest.TestCase):
    def test_comment_does_not_invalidate_approval(self):
        reviews = [review(), review("COMMENTED", when=LATER, identifier=2)]
        self.assertEqual(triage.effective_approval(reviews, {"maintainer"})["id"], 1)

    def test_changes_requested_or_dismissal_invalidates_approval(self):
        for state in ("CHANGES_REQUESTED", "DISMISSED"):
            with self.subTest(state=state):
                self.assertIsNone(
                    triage.effective_approval([review(), review(state, when=LATER, identifier=2)], {"maintainer"})
                )

    def test_later_approval_and_login_case(self):
        reviews = [review("CHANGES_REQUESTED"), review(login="Maintainer", when=LATER, identifier=2)]
        self.assertEqual(triage.effective_approval(reviews, {"maintainer"})["id"], 2)
        self.assertIsNone(triage.effective_approval(reviews, {"other"}))

    def test_pending_review_ignored(self):
        pending = review("PENDING", identifier=2)
        pending["submitted_at"] = None
        self.assertEqual(triage.effective_approval([pending, review()], {"maintainer"})["id"], 1)


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.client = triage.GitHub(REPO)

    def test_last_rule_and_nested_double_star(self):
        text = "/sdk/ @general\n/**/*mgmt*/ @maintainer\n/sdk/example/azure-mgmt-example/private/ @special\n"
        with patch.object(self.client, "load_rules", return_value=triage.parse_codeowners(text)) as load:
            owners = self.client.owners(OLD, [FILE], "azure-mgmt-example")
            self.assertEqual(owners, ({"maintainer"}, ["@maintainer"], False))
            self.client.owners(OLD, [FILE], "azure-mgmt-example")
            load.assert_called_once()
            special = dict(FILE, filename="sdk/example/azure-mgmt-example/private/client.py")
            self.assertEqual(self.client.owners(OLD, [special], "azure-mgmt-example")[0], {"special"})

    def test_rename_uses_previous_path_and_unrelated_files_ignored(self):
        rules = triage.parse_codeowners("/sdk/ @general\n/sdk/example/azure-mgmt-example/old.py @old")
        renamed = dict(
            FILE,
            status="renamed",
            filename="sdk/example/azure-mgmt-example/new.py",
            previous_filename="sdk/example/azure-mgmt-example/old.py",
        )
        with patch.object(self.client, "load_rules", return_value=rules):
            self.assertEqual(
                self.client.owners(OLD, [renamed, {"filename": "eng/file.py"}], "azure-mgmt-example")[0], {"old"}
            )

    def test_missing_owner_is_unknown(self):
        with patch.object(self.client, "load_rules", return_value=triage.parse_codeowners("/elsewhere/ @other")):
            with self.assertRaises(triage.CollectionError):
                self.client.owners(OLD, [FILE], "azure-mgmt-example")

    def test_team_members_cached_and_casefolded(self):
        rules = triage.parse_codeowners("/sdk/ @Azure/owners")
        with patch.object(self.client, "load_rules", return_value=rules), patch.object(
            self.client, "pages", return_value=[{"login": "Maintainer"}]
        ) as pages:
            self.assertEqual(self.client.owners(OLD, [FILE], "azure-mgmt-example")[0], {"maintainer"})
            self.client.owners(OLD, [FILE], "azure-mgmt-example")
            pages.assert_called_once()

    def test_codeowners_file_precedence(self):
        content = base64.b64encode(b"/sdk/ @maintainer").decode()
        with patch.object(self.client, "cached", return_value={"encoding": "base64", "content": content}) as cached:
            self.client.load_rules(OLD)
            self.assertIn("/contents/.github/CODEOWNERS?", cached.call_args.args[0])
            cached.assert_called_once()

    def test_expected_team_403_skipped_and_cached_without_losing_named_owners(self):
        rules = triage.parse_codeowners("/sdk/ @Azure/azure-arm-sdk-reviewers @maintainer")
        with patch.object(self.client, "load_rules", return_value=rules), patch.object(
            self.client,
            "pages",
            side_effect=triage.CollectionError("Resource not accessible by integration (HTTP 403)"),
        ) as pages:
            for _ in range(2):
                maintainers, owners, skipped = self.client.owners(OLD, [FILE], "azure-mgmt-example")
                self.assertEqual(maintainers, {"maintainer"})
                self.assertIn("@Azure/azure-arm-sdk-reviewers", owners)
                self.assertTrue(skipped)
            pages.assert_called_once()

    def test_other_team_403_or_other_error_still_reported(self):
        for owner, error in (
            ("@Azure/other-team", "HTTP 403"),
            ("@Azure/azure-arm-sdk-reviewers", "HTTP 401"),
            ("@Azure/azure-arm-sdk-reviewers", "HTTP 500"),
        ):
            with self.subTest(owner=owner, error=error):
                client = triage.GitHub(REPO)
                rules = triage.parse_codeowners(f"/sdk/ {owner} @maintainer")
                with patch.object(client, "load_rules", return_value=rules), patch.object(
                    client, "pages", side_effect=triage.CollectionError(error)
                ):
                    with self.assertRaises(triage.CollectionError):
                        client.owners(OLD, [FILE], "azure-mgmt-example")

    def test_empty_override_does_not_fall_back(self):
        rules = triage.parse_codeowners("/sdk/ @maintainer\n/sdk/example/azure-mgmt-example/\n")
        with patch.object(self.client, "load_rules", return_value=rules):
            with self.assertRaises(triage.CollectionError):
                self.client.owners(OLD, [FILE], "azure-mgmt-example")


class ActivityTests(unittest.TestCase):
    def test_all_active_states_including_old_head(self):
        for status in triage.ACTIVE_STATUSES:
            with self.subTest(status=status):
                item = row()
                triage.classify(item, FakeGitHub(), 9, [run(status, OLD)], [])
                self.assertIn(2, item["queues"])
                self.assertNotIn(1, item["queues"])
                self.assertIn("older/different head", item["queues"][2])

    def test_unassociated_run_prevents_trigger_recommendation(self):
        client = FakeGitHub()
        client.workflow_runs = [run("queued", associated=False)]
        runs, issues = triage.recent_reviews(client)
        item = row()
        triage.classify(item, client, 9, runs, issues)
        self.assertNotIn(1, item["queues"])
        self.assertIn("Review activity unknown", " ".join(item["issues"]))
        self.assertIn(RUN_URL, " ".join(issues))

    def test_activity_access_failure_is_unknown(self):
        client = FakeGitHub()
        client.activity_error = True
        runs, issues = triage.recent_reviews(client)
        item = row()
        triage.classify(item, client, 9, runs, issues)
        self.assertNotIn(1, item["queues"])
        self.assertTrue(issues)

    def test_other_pr_active_run_does_not_block(self):
        other = run("queued")
        other["pull_requests"][0]["number"] = 43
        item = row()
        triage.classify(item, FakeGitHub(), 9, [other], [])
        self.assertIn(1, item["queues"])
        self.assertNotIn(2, item["queues"])

    def test_label_presence_only_changes_trigger_instruction(self):
        for labeled in (False, True):
            with self.subTest(labeled=labeled):
                item = row()
                item["pr"]["labels"] = [{"name": "mgmt-review-needed"}] if labeled else []
                triage.classify(item, FakeGitHub(), 9, [], [])
                self.assertIn("Remove and reapply" if labeled else "Add", item["queues"][1])

    def test_status_independent_request_retains_completed_attempts(self):
        client = FakeGitHub()
        client.workflow_runs = [run("in_progress"), dict(run(), id=101)]
        with patch.object(client, "pages", wraps=client.pages) as pages:
            runs, issues = triage.recent_reviews(client)
            endpoint, key = pages.call_args.args
            self.assertTrue(endpoint.startswith(f"repos/{REPO}/actions/workflows/{triage.WORKFLOW}/runs?"))
            self.assertNotIn("created=", endpoint)
            self.assertNotIn("status=", endpoint)
            self.assertEqual(key, "workflow_runs")
            pages.assert_called_once()
        self.assertEqual(len(runs), 2)
        self.assertFalse(issues)

    def test_waiting_to_in_progress_transition_cannot_hide_active_run(self):
        client = FakeGitHub()
        active = run("waiting")

        def transition(endpoint, key=None):
            if "?status=waiting&" in endpoint or "?status=" not in endpoint:
                active["status"] = "in_progress"
            if "?status=" not in endpoint or f"status={active['status']}&" in endpoint:
                return [deepcopy(active)]
            return []

        with patch.object(client, "pages", side_effect=transition):
            runs, issues = triage.recent_reviews(client)
        item = row()
        triage.classify(item, client, 9, runs, issues)
        self.assertFalse(issues)
        self.assertEqual(runs[0]["status"], "in_progress")
        self.assertIn(2, item["queues"])
        self.assertNotIn(1, item["queues"])

    def test_active_run_on_later_page_is_found(self):
        client = triage.GitHub(REPO)
        pages = [
            {"total_count": 2, "workflow_runs": [run()]},
            {
                "total_count": 2,
                "workflow_runs": [dict(run("queued"), id=101, created_at="2026-01-01T00:00:00Z")],
            },
        ]
        with patch.object(triage, "gh", return_value=pages):
            runs, issues = triage.recent_reviews(client)
        self.assertFalse(issues)
        self.assertEqual([item["status"] for item in runs], ["completed", "queued"])

    def test_three_day_boundary_applies_only_to_completed_attempts(self):
        now = triage.timestamp("2026-11-26T09:00:00Z")
        for status in (*triage.ACTIVE_STATUSES, "completed"):
            for created, expected in (
                ("2026-11-23T08:59:59Z", False),
                ("2026-11-23T09:00:00Z", True),
                ("2026-11-23T09:00:01Z", True),
            ):
                with self.subTest(status=status, created=created):
                    client = FakeGitHub()
                    client.workflow_runs = [
                        dict(
                            run(status, associated=False),
                            created_at=created,
                            conclusion="failure" if status == "completed" else None,
                        )
                    ]
                    runs, issues = triage.recent_reviews(client, now=now)
                    self.assertEqual(bool(runs), expected or status != "completed")
                    self.assertEqual(bool(issues), status != "completed")

    def test_old_active_run_blocks_new_trigger_with_or_without_association(self):
        for status in triage.ACTIVE_STATUSES:
            for associated in (True, False):
                with self.subTest(status=status, associated=associated):
                    client = FakeGitHub()
                    client.workflow_runs = [
                        dict(run(status, OLD, associated=associated), created_at="2026-01-01T00:00:00Z")
                    ]
                    runs, issues = triage.recent_reviews(client)
                    item = row()
                    triage.classify(item, client, 9, runs, issues)
                    self.assertNotIn(1, item["queues"])
                    if associated:
                        self.assertIn(2, item["queues"])
                        self.assertIn(RUN_URL, item["queues"][2])
                        self.assertFalse(item["issues"])
                    else:
                        self.assertIn("Review activity unknown", " ".join(item["issues"]))
                        self.assertIn(RUN_URL, " ".join(issues))

    def test_missing_run_timestamp_is_unknown_not_silently_ignored(self):
        for value in (None, "invalid", "2026-11-26T09:00:00"):
            with self.subTest(value=value):
                client = FakeGitHub()
                client.workflow_runs = [dict(run(), created_at=value)]
                _, issues = triage.recent_reviews(client)
                self.assertIn("creation time unavailable", " ".join(issues))

    def test_failed_current_head_is_reported_without_retry_even_with_current_comment(self):
        for bot_comment in (None, bot()):
            with self.subTest(bot_comment=bot_comment):
                item = row(bot_comment=bot_comment)
                failed = dict(run(), conclusion="failure")
                triage.classify(item, FakeGitHub(), 9, [failed], [])
                self.assertNotIn(1, item["queues"])
                self.assertNotIn(2, item["queues"])
                self.assertIn("Review failed for the current head", " ".join(item["issues"]))
                self.assertIn(RUN_URL, " ".join(item["issues"]))

    def test_completed_attempt_without_comment_does_not_trigger_duplicate(self):
        for conclusion in ("success", "cancelled"):
            with self.subTest(conclusion=conclusion):
                item = row()
                triage.classify(item, FakeGitHub(), 9, [dict(run(), conclusion=conclusion)], [])
                self.assertNotIn(1, item["queues"])
                self.assertNotIn(2, item["queues"])
                self.assertIn("already attempted for the current head", " ".join(item["issues"]))

    def test_skipped_workflow_does_not_count_as_review_attempt(self):
        for head in (HEAD, None):
            with self.subTest(head=head):
                item = row()
                triage.classify(item, FakeGitHub(), 9, [dict(run(head=head), conclusion="skipped")], [])
                self.assertIn(1, item["queues"])
                self.assertFalse(item["issues"])

    def test_failed_older_head_allows_review_of_new_head(self):
        item = row()
        triage.classify(item, FakeGitHub(), 9, [dict(run(head=OLD), conclusion="failure")], [])
        self.assertIn(1, item["queues"])
        self.assertFalse(item["issues"])

    def test_later_success_supersedes_failure_for_same_head(self):
        item = row(bot_comment=bot())
        failed = dict(run(), conclusion="failure", created_at=WHEN)
        succeeded = dict(run(), id=101, created_at=LATER)
        triage.classify(item, FakeGitHub(), 9, [failed, succeeded], [])
        self.assertFalse(item["issues"])
        self.assertNotIn(1, item["queues"])

    def test_completed_attempt_with_unknown_pr_head_does_not_allow_duplicate(self):
        item = row()
        triage.classify(item, FakeGitHub(), 9, [run(head=None)], [])
        self.assertNotIn(1, item["queues"])
        self.assertIn("no PR head", " ".join(item["issues"]))


class FreshnessTests(unittest.TestCase):
    def test_current_comment_with_different_run_head_sha(self):
        self.assertEqual(triage.review_freshness(FakeGitHub(), 9, PR, bot()), "current")
        item = row(review(), bot())
        triage.classify(item, FakeGitHub(), 9, [], [])
        self.assertFalse(item["queues"])

    def test_older_linked_pr_head_is_outdated(self):
        client = FakeGitHub()
        client.linked_run = run(head=OLD)
        item = row(bot_comment=bot())
        triage.classify(item, client, 9, [], [])
        self.assertIn("outdated", item["queues"][1])

    def test_unverifiable_link_never_recommends_trigger(self):
        for linked in (dict(run(), workflow_id=8), run(associated=False), run(head=None)):
            with self.subTest(linked=linked):
                client = FakeGitHub()
                client.linked_run = linked
                item = row(bot_comment=bot())
                triage.classify(item, client, 9, [], [])
                self.assertNotIn(1, item["queues"])
                self.assertIn("freshness unknown", item["issues"][0])

    def test_missing_run_link_is_unknown(self):
        with self.assertRaises(triage.CollectionError):
            triage.review_freshness(FakeGitHub(), 9, PR, bot("No linked run"))

    def test_heading_alone_does_not_identify_automated_review(self):
        self.assertIsNone(triage.bot_review([comment("## Management SDK PR review")]))
        fake = bot()
        fake["user"]["login"] = "someone"
        self.assertIsNone(triage.bot_review([fake]))
        self.assertEqual(triage.bot_review([bot()])["id"], 2)

    def test_old_workflow_marker_supported(self):
        item = bot("<!-- gh-aw-workflow-id: mgmt-sdk-pr-review -->\n## Management SDK PR review")
        self.assertEqual(triage.bot_review([item]), item)


class CollectionTests(unittest.TestCase):
    def test_skipped_team_preserves_named_approval_changes_and_followups(self):
        client = FakeGitHub()
        client.skipped_team = True
        client.reviews = [review(commit=OLD)]
        client.comments.append(comment())
        item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="APPROVED"))
        triage.classify(item, client, 9, [], [])
        self.assertIsNotNone(item["approval"])
        self.assertFalse(item["issues"])
        self.assertNotIn(3, item["queues"])
        self.assertIn(4, item["queues"])
        self.assertIn(5, item["queues"])

    def test_skipped_team_uses_github_decision_without_missing_approval_claim(self):
        for decision in ("APPROVED", "REVIEW_REQUIRED", "CHANGES_REQUESTED"):
            with self.subTest(decision=decision):
                client = FakeGitHub()
                client.skipped_team = True
                client.reviews = [review(login="team-only-reviewer")]
                item = triage.collect_pr(client, dict(SUMMARY, reviewDecision=decision))
                triage.classify(item, client, 9, [], [])
                self.assertFalse(item["issues"])
                if decision == "APPROVED":
                    self.assertNotIn(3, item["queues"])
                else:
                    self.assertIn(f"GitHub review decision: {decision}", item["queues"][3])

    def test_skipped_team_without_github_decision_is_still_unverified(self):
        client = FakeGitHub()
        client.skipped_team = True
        client.reviews = []
        item = triage.collect_pr(client, SUMMARY)
        self.assertIn("GitHub review decision unavailable", item["issues"][0])

    def test_first_beta_and_author_followups_in_all_comment_channels(self):
        client = FakeGitHub()
        client.comments.append(comment())
        client.inline = [comment(identifier=3)]
        author_review = review("COMMENTED", "author", LATER, 4)
        author_review["body"] = "Ready now?"
        client.reviews.append(author_review)
        item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="APPROVED"))
        self.assertEqual(item["version"], "1.0.0b1")
        self.assertEqual(len(item["followups"]), 3)
        triage.classify(item, client, 9, [], [])
        self.assertIn(5, item["queues"])
        self.assertNotIn(4, item["queues"])

    def test_comments_before_approval_or_by_other_people_not_followups(self):
        client = FakeGitHub()
        client.comments += [comment(when=WHEN), comment(login="other")]
        item = triage.collect_pr(client, SUMMARY)
        self.assertFalse(item["followups"])

    def test_old_commit_timestamps_cannot_hide_changed_head(self):
        item = row(review(commit=OLD), bot())
        triage.classify(item, FakeGitHub(), 9, [], [])
        self.assertIn(4, item["queues"])

    def test_missing_commit_is_verification_warning(self):
        item = row(review(commit=None), bot())
        triage.classify(item, FakeGitHub(), 9, [], [])
        self.assertTrue(item["issues"])
        self.assertNotIn(4, item["queues"])

    def test_ownership_failure_is_not_missing_approval(self):
        client = FakeGitHub()
        client.ownership_error = True
        item = triage.collect_pr(client, SUMMARY)
        triage.classify(item, client, 9, [], [])
        self.assertNotIn(3, item["queues"])
        self.assertIn("Approval verification incomplete", item["issues"][0])

    def test_github_review_requirement_even_with_approval(self):
        item = row(review(), bot())
        item["review_decision"] = "CHANGES_REQUESTED"
        triage.classify(item, FakeGitHub(), 9, [], [])
        self.assertIn(3, item["queues"])

    def test_changed_pr_requires_rescan(self):
        client = FakeGitHub()
        client.last_details = deepcopy(PR)
        client.last_details["head"]["sha"] = OLD
        with self.assertRaises(triage.CollectionError):
            triage.collect_pr(client, SUMMARY)

    def test_changes_requested_since_listing_rejects_stale_approval(self):
        client = FakeGitHub()
        client.details["updated_at"] = LATER
        client.reviews = [review(), review("CHANGES_REQUESTED", "second", LATER, 2)]
        with self.assertRaisesRegex(triage.CollectionError, "changed since initial listing"):
            triage.collect_pr(client, dict(SUMMARY, reviewDecision="APPROVED"))
        self.assertEqual(client.get_count, 1)

    def test_missing_listing_timestamp_cannot_bypass_snapshot_guard(self):
        with self.assertRaisesRegex(triage.CollectionError, "changed since initial listing"):
            triage.collect_pr(FakeGitHub(), {"number": 42, "reviewDecision": "APPROVED"})

    def test_timestamp_change_during_collection_rejects_snapshot(self):
        client = FakeGitHub()
        client.last_details = dict(PR, updated_at=LATER)
        with self.assertRaisesRegex(triage.CollectionError, "changed during collection"):
            triage.collect_pr(client, SUMMARY)

    def test_newly_closed_or_draft_pr_skipped(self):
        for changes in ({"state": "closed"}, {"draft": True}):
            client = FakeGitHub()
            client.details.update(changes)
            self.assertIsNone(triage.collect_pr(client, SUMMARY))

    def test_truncated_files_not_treated_as_complete(self):
        client = FakeGitHub()
        client.details["changed_files"] = 3001
        with self.assertRaises(triage.CollectionError):
            triage.collect_pr(client, SUMMARY)

    def test_version_changelog_fallback(self):
        file = dict(FILE, filename="sdk/example/azure-mgmt-example/CHANGELOG.md", patch="+## 2.0.0 (Unreleased)")
        self.assertEqual(triage.sdk_version([file]), "2.0.0")


class ReportAndCliTests(unittest.TestCase):
    def test_partial_scan_never_claims_no_action(self):
        report, incomplete = triage.render_report(REPO, [], ["HTTP 403"])
        self.assertTrue(incomplete)
        self.assertNotIn("No PRs need action", report)
        self.assertIn("verification incomplete", report)

    def test_queue_numbers_preserved_and_rows_sorted(self):
        first, second = row(), row()
        second["pr"]["number"] = 43
        second["pr"]["html_url"] = PR_URL.replace("42", "43")
        second["pr"]["updated_at"] = LATER
        first["queues"][4] = second["queues"][4] = "Inspect changes."
        report, incomplete = triage.render_report(REPO, [first, second], [])
        self.assertFalse(incomplete)
        self.assertIn("## 2. Changes after approval and need review again", report)
        self.assertNotIn("## 1.", report)
        self.assertLess(report.index(f"{REPO}#43"), report.index(f"{REPO}#42"))

    def test_paginated_lists_and_incomplete_objects(self):
        client = triage.GitHub(REPO)
        with patch.object(triage, "gh", return_value=[[{"id": 1}], [{"id": 2}]]):
            self.assertEqual(len(client.pages("endpoint")), 2)
        with patch.object(triage, "gh", return_value=[{"total_count": 2, "workflow_runs": [run()]}]):
            with self.assertRaises(triage.CollectionError):
                client.pages("endpoint", "workflow_runs")

    def test_cli_default_includes_first_beta(self):
        listing = [dict(SUMMARY, reviewDecision="APPROVED")]
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=FakeGitHub()
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main([]), 0)
            self.assertIn("Scanned 1", output.getvalue())
            self.assertIn("No PRs need action", output.getvalue())

    def test_cli_stale_listing_never_claims_no_action(self):
        listing = [dict(SUMMARY, reviewDecision="APPROVED")]
        client = FakeGitHub()
        client.details["updated_at"] = LATER
        client.reviews = [review(), review("CHANGES_REQUESTED", "second", LATER, 2)]
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=client
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main([]), 2)
            self.assertIn("changed since initial listing", output.getvalue())
            self.assertNotIn("No PRs need action", output.getvalue())

    def test_cli_limit_marks_partial(self):
        listing = [dict(SUMMARY)]
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=FakeGitHub()
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main(["--limit", "1"]), 2)
            self.assertIn("reached --limit", output.getvalue())
            self.assertNotIn("No PRs need action", output.getvalue())

    def test_cli_exact_package_filter_and_drafts(self):
        listing = [
            dict(SUMMARY),
            dict(SUMMARY, number=43, title="[AutoPR azure-mgmt-other]-generated"),
            dict(SUMMARY, number=44, isDraft=True),
        ]
        client = FakeGitHub()
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=client
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main(["--package", "azure-mgmt-example"]), 0)
            self.assertIn("Scanned 1", output.getvalue())

    def test_cli_unknown_version_cannot_silently_match_filter(self):
        listing = [dict(SUMMARY)]
        client = FakeGitHub()
        client.files[0]["patch"] = ""
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=client
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main(["--version", "1.0.0b1"]), 2)
            self.assertIn("cannot apply --version", output.getvalue())

    def test_cli_collection_failure_reports_partial(self):
        listing = [dict(SUMMARY)]
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "collect_pr", side_effect=triage.CollectionError("HTTP 403")
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main([]), 2)
            self.assertIn("collection incomplete", output.getvalue())
            self.assertNotIn("No PRs need action", output.getvalue())


class RotatorTests(unittest.TestCase):
    def test_configuration_is_repository_scoped_and_case_insensitive(self):
        text = '{"repositories":{"Azure/azure-sdk-for-python":{"rotators":["Rotator","rotator"]}}}'
        with patch.object(Path, "read_text", return_value=text):
            self.assertEqual(triage.load_rotators("config.json", REPO.lower()), {"rotator"})
            self.assertEqual(triage.load_rotators("config.json", "other/repo"), set())

    def test_invalid_or_missing_configuration_stops_collection(self):
        for text in (
            "not JSON",
            "{}",
            '{"repositories":[]}',
            '{"repositories":{"Azure/azure-sdk-for-python":{"rotators":"rotator"}}}',
            '{"repositories":{"Azure/azure-sdk-for-python":{"rotators":["@rotator"]}}}',
        ):
            with self.subTest(text=text), patch.object(Path, "read_text", return_value=text):
                with self.assertRaises(triage.CollectionError):
                    triage.load_rotators("config.json", REPO)
        with patch.object(Path, "read_text", side_effect=FileNotFoundError):
            with self.assertRaises(triage.CollectionError):
                triage.load_rotators("config.json", REPO)

    def test_configured_rotator_approval_removes_review_requests(self):
        client = FakeGitHub()
        client.rotators = {"rotator"}
        client.reviews = [review(login="Rotator")]
        client.comments = []
        item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="APPROVED"))
        triage.classify(item, client, 9, [], [])
        self.assertEqual(item["approval"]["user"]["login"], "Rotator")
        self.assertFalse(item["queues"])

    def test_rotator_dismissal_and_changes_requested_invalidate_approval(self):
        for state in ("DISMISSED", "CHANGES_REQUESTED"):
            with self.subTest(state=state):
                client = FakeGitHub()
                client.rotators = {"rotator"}
                client.reviews = [review(login="rotator"), review(state, "rotator", LATER, 2)]
                item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="REVIEW_REQUIRED"))
                triage.classify(item, client, 9, [], [])
                self.assertIsNone(item["approval"])
                self.assertIn(3, item["queues"])

    def test_rotator_approval_does_not_override_github_requirements(self):
        client = FakeGitHub()
        client.rotators = {"rotator"}
        client.reviews = [review(login="rotator")]
        item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="REVIEW_REQUIRED"))
        triage.classify(item, client, 9, [], [])
        self.assertIn("GitHub review decision", item["queues"][3])

    def test_rotator_approval_survives_unreadable_owners_with_warning(self):
        client = FakeGitHub()
        client.ownership_error = True
        client.rotators = {"rotator"}
        client.reviews = [review(login="rotator", commit=OLD)]
        item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="APPROVED"))
        triage.classify(item, client, 9, [], [])
        self.assertIsNotNone(item["approval"])
        self.assertIn(4, item["queues"])
        self.assertIn("Approval verification incomplete", item["issues"][0])


class AdditionalQueueTests(unittest.TestCase):
    def test_holds_are_exclusive_even_with_missing_plan_and_old_approval(self):
        for label in ("HoldOn", "holdon", "blocking-release"):
            with self.subTest(label=label):
                item = row(review(when="2026-01-01T00:00:00Z"))
                item["pr"]["labels"] = [{"name": label}]
                item["release_plans"] = []
                item["followups"] = [comment()]
                triage.classify(item, FakeGitHub(), 9, [run("queued")], [])
                self.assertEqual(set(item["queues"]), {6})
                self.assertIn("Release plan: missing", item["queues"][6])

    def test_release_plan_link_is_detected_in_markdown_and_plain_text(self):
        self.assertEqual(triage.release_plan_links(f"[Release plan]({PLAN_URL})"), [PLAN_URL])
        self.assertEqual(triage.release_plan_links(f"{PLAN_URL}\n{PLAN_URL}"), [PLAN_URL])

    def test_release_plan_url_label_and_destination_are_separate_urls(self):
        other_plan = PLAN_URL.replace("37904", "36087")
        for body, expected in (
            (f"**Release plan link:** [{PLAN_URL}]({PLAN_URL})", [PLAN_URL]),
            (f"[{PLAN_URL}]({other_plan})", [PLAN_URL, other_plan]),
            (f"[Release plan]({PLAN_URL})[Release plan]({other_plan})", [PLAN_URL, other_plan]),
        ):
            with self.subTest(body=body):
                self.assertEqual(triage.release_plan_links(body), expected)

    def test_url_labeled_release_plan_is_omitted_from_invalid_queue(self):
        client = FakeGitHub()
        client.details["body"] = f"**Release plan link:** [{PLAN_URL}]({PLAN_URL})"
        item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="APPROVED"))
        triage.classify(item, client, 9, [], [])
        self.assertEqual(item["release_plans"], [PLAN_URL])
        self.assertNotIn(7, item["queues"])
        report, _ = triage.render_report(REPO, [item], [])
        self.assertNotIn("## 7. Invalid PRs without release-plan link", report)

    def test_missing_non_plan_and_malformed_links_are_invalid(self):
        for body in (
            None,
            "No plan",
            "https://example.com/?releaseplan=37904",
            "https://azsdk-releaseplan-dashboard.azurewebsites.net/?releaseplan=unknown",
            "https://[bad",
        ):
            with self.subTest(body=body):
                self.assertEqual(triage.release_plan_links(body), [])
        client = FakeGitHub()
        client.details["body"] = ""
        item = triage.collect_pr(client, dict(SUMMARY, reviewDecision="APPROVED"))
        triage.classify(item, client, 9, [], [])
        report, _ = triage.render_report(REPO, [item], [])
        section = report.split("## 7. Invalid PRs without release-plan link\n\n")[1]
        self.assertEqual(section.strip(), f"- [{REPO}#42]({PR_URL})")
        self.assertNotIn("azure-mgmt-example", section)

    def test_aged_approval_uses_strict_calendar_month_boundary(self):
        now = triage.timestamp("2026-11-25T10:00:00Z")
        for when, expected in (
            ("2026-09-25T10:00:00Z", False),
            ("2026-09-25T09:59:59Z", True),
            ("2026-09-26T10:00:00Z", False),
        ):
            with self.subTest(when=when):
                item = row(review(when=when))
                triage.classify(item, FakeGitHub(), 9, [], [], now=now)
                self.assertEqual(8 in item["queues"], expected)

    def test_calendar_cutoff_clamps_month_end_and_crosses_year(self):
        self.assertEqual(
            triage.two_months_before(triage.timestamp("2026-04-30T00:00:00Z")),
            triage.timestamp("2026-02-28T00:00:00Z"),
        )
        self.assertEqual(
            triage.two_months_before(triage.timestamp("2026-01-31T00:00:00Z")),
            triage.timestamp("2025-11-30T00:00:00Z"),
        )

    def test_old_head_approval_is_not_an_aged_current_approval(self):
        item = row(review(when="2026-01-01T00:00:00Z", commit=OLD))
        triage.classify(item, FakeGitHub(), 9, [], [])
        self.assertIn(4, item["queues"])
        self.assertNotIn(8, item["queues"])

    def test_current_approval_skips_missing_bot_review_and_active_queue(self):
        for runs in ([], [run("queued")]):
            with self.subTest(runs=runs):
                item = row(review())
                triage.classify(item, FakeGitHub(), 9, runs, [])
                self.assertNotIn(1, item["queues"])
                self.assertNotIn(2, item["queues"])
                self.assertNotIn(3, item["queues"])

    def test_exact_report_order_and_empty_sections_omitted(self):
        item = row()
        item["queues"] = {number: "evidence" for number in range(1, 9)}
        report, _ = triage.render_report(REPO, [item], [])
        expected = [
            "## 1. First review needed",
            "## 2. Changes after approval and need review again",
            "## 3. Author follow-up after approval",
            "## 4. Automated review needs triggering",
            "## 5. Automated review active",
            "## 6. HoldOn PRs",
            "## 7. Invalid PRs without release-plan link",
            "## 8. Approved but unmerged for over two months",
        ]
        self.assertEqual([line for line in report.splitlines() if line.startswith("## ")], expected)
        item["queues"] = {7: ""}
        report, _ = triage.render_report(REPO, [item], [])
        self.assertNotIn("## 4.", report)


class LabelGitHub(FakeGitHub):
    def __init__(self):
        super().__init__()
        self.details["user"] = {"login": "azure-sdk-automation[bot]", "type": "Bot"}
        self.details["head"]["repo"] = {"full_name": REPO, "owner": {"type": "Organization"}}
        self.reviews = []
        self.comments = []
        self.actions = []
        self.on_remove = None

    def summary(self, number):
        return dict(SUMMARY, updatedAt=self.details["updated_at"], reviewDecision="REVIEW_REQUIRED")

    def change_label(self, number, remove=False):
        self.actions.append((number, remove))
        self.details["updated_at"] = LATER
        if remove:
            self.details["labels"] = []
            if self.on_remove:
                self.on_remove()
        else:
            self.details["labels"].append({"name": triage.REVIEW_LABEL})

    def trigger_row(self):
        item = triage.collect_pr(self, self.summary(42))
        triage.classify(item, self, 9, [], [])
        return item


class AutomaticLabelTests(unittest.TestCase):
    def test_add_and_reapply_are_automatic_and_verified(self):
        for labeled in (False, True):
            with self.subTest(labeled=labeled):
                client = LabelGitHub()
                client.details["labels"] = [{"name": triage.REVIEW_LABEL}] if labeled else []
                item = client.trigger_row()
                triage.apply_labels(client, [item], 9)
                self.assertEqual(client.actions, [(42, True), (42, False)] if labeled else [(42, False)])
                self.assertEqual(item["label_status"], "succeeded")
                self.assertIn("automatically; label presence verified", item["queues"][1])
                report, incomplete = triage.render_report(REPO, [item], [], apply=True)
                self.assertIn("1 succeeded", report)
                self.assertFalse(incomplete)

    def test_repeated_scan_does_not_repeat_label_write_before_run_appears(self):
        client = LabelGitHub()
        item = client.trigger_row()
        triage.apply_labels(client, [item], 9)
        again = client.trigger_row()
        triage.apply_labels(client, [again], 9)
        self.assertEqual(client.actions, [(42, False)])
        self.assertNotIn(1, again["queues"])
        self.assertIn("No duplicate label update", " ".join(again["issues"]))

    def test_new_automation_head_is_retriggered_once_with_existing_label(self):
        client = LabelGitHub()
        triage.apply_labels(client, [client.trigger_row()], 9)
        client.details["head"]["sha"] = OLD
        client.details["updated_at"] = LATER
        triage.apply_labels(client, [client.trigger_row()], 9)
        triage.apply_labels(client, [client.trigger_row()], 9)
        self.assertEqual(client.actions, [(42, False), (42, True), (42, False)])
        self.assertEqual(client.requests.status(REPO, 42, HEAD), "requested")
        self.assertEqual(client.requests.status(REPO, 42, OLD), "requested")

    def test_existing_attempt_or_failure_prevents_writes_at_fresh_check(self):
        for conclusion in ("success", "failure", "timed_out"):
            with self.subTest(conclusion=conclusion):
                client = LabelGitHub()
                item = client.trigger_row()
                client.workflow_runs = [dict(run(), conclusion=conclusion)]
                triage.apply_labels(client, [item], 9)
                self.assertEqual(client.actions, [])

    def test_uncertain_write_is_not_retried_on_later_scan(self):
        client = LabelGitHub()
        with patch.object(client, "change_label", side_effect=triage.CollectionError("request timed out")):
            triage.apply_labels(client, [client.trigger_row()], 9)
        self.assertEqual(client.requests.status(REPO, 42, HEAD), "uncertain")
        triage.apply_labels(client, [client.trigger_row()], 9)
        self.assertEqual(client.actions, [])

    def test_request_claimed_by_another_scan_prevents_writes(self):
        client = LabelGitHub()
        item = client.trigger_row()
        with patch.object(client.requests, "claim", return_value=False):
            triage.apply_labels(client, [item], 9)
        self.assertEqual(client.actions, [])
        self.assertEqual(item["label_status"], "skipped")

    def test_request_state_failure_prevents_writes(self):
        client = LabelGitHub()
        item = client.trigger_row()
        with patch.object(client.requests, "claim", side_effect=triage.CollectionError("Cannot record state")):
            triage.apply_labels(client, [item], 9)
        self.assertEqual(client.actions, [])

    def test_other_authors_and_non_azure_sources_are_not_modified(self):
        for change in ("author", "source"):
            with self.subTest(change=change):
                client = LabelGitHub()
                if change == "author":
                    client.details["user"] = {"login": "someone", "type": "User"}
                else:
                    client.details["head"]["repo"]["full_name"] = "someone/fork"
                item = client.trigger_row()
                triage.apply_labels(client, [item], 9)
                self.assertEqual(client.actions, [])
                self.assertEqual(item["label_status"], "skipped")

    def test_fresh_active_or_unassociated_run_prevents_writes(self):
        for active in (
            run("queued"),
            run("waiting", associated=False),
            dict(run("waiting"), created_at="2026-01-01T00:00:00Z"),
            dict(run("queued", associated=False), created_at="2026-01-01T00:00:00Z"),
        ):
            with self.subTest(active=active):
                client = LabelGitHub()
                item = client.trigger_row()
                client.workflow_runs = [active]
                triage.apply_labels(client, [item], 9)
                self.assertEqual(client.actions, [])
                self.assertEqual(item["label_status"], "skipped")

    def test_changed_snapshot_or_unknown_identity_prevents_writes(self):
        for change in ("head", "updated", "hold", "draft", "closed", "identity"):
            with self.subTest(change=change):
                client = LabelGitHub()
                item = client.trigger_row()
                workflow = 9
                if change == "head":
                    client.details["head"]["sha"] = OLD
                elif change == "updated":
                    client.details["updated_at"] = LATER
                elif change == "hold":
                    client.details["labels"] = [{"name": "HoldOn"}]
                elif change == "draft":
                    client.details["draft"] = True
                elif change == "closed":
                    client.details["state"] = "closed"
                else:
                    workflow = None
                triage.apply_labels(client, [item], workflow)
                self.assertEqual(client.actions, [])
                self.assertEqual(item["label_status"], "skipped")

    def test_new_current_approval_prevents_writes(self):
        client = LabelGitHub()
        item = client.trigger_row()
        client.reviews = [review()]
        with patch.object(client, "summary", return_value=dict(SUMMARY, reviewDecision="APPROVED")):
            triage.apply_labels(client, [item], 9)
        self.assertEqual(client.actions, [])

    def test_recheck_after_removal_stops_when_review_starts_or_head_changes(self):
        for change in ("active", "old-active", "head"):
            with self.subTest(change=change):
                client = LabelGitHub()
                client.details["labels"] = [{"name": triage.REVIEW_LABEL}]
                item = client.trigger_row()
                if change == "active":
                    client.on_remove = lambda: client.workflow_runs.append(run("queued"))
                elif change == "old-active":
                    client.on_remove = lambda: client.workflow_runs.append(
                        dict(run("waiting"), created_at="2026-01-01T00:00:00Z")
                    )
                else:
                    client.on_remove = lambda: client.details["head"].update(sha=OLD)
                triage.apply_labels(client, [item], 9)
                self.assertEqual(client.actions, [(42, True)])
                self.assertEqual(item["label_status"], "failed/unknown")
                self.assertIn("No automatic retry", item["issues"][0])

    def test_write_failures_are_not_retried(self):
        for error in ("HTTP 403", "request timed out"):
            with self.subTest(error=error):
                client = LabelGitHub()
                item = client.trigger_row()
                with patch.object(client, "change_label", side_effect=triage.CollectionError(error)) as write:
                    triage.apply_labels(client, [item], 9)
                    write.assert_called_once()
                self.assertEqual(item["label_status"], "failed/unknown")
                self.assertIn(error, item["issues"][0])

    def test_missing_label_after_write_is_not_reported_as_success(self):
        client = LabelGitHub()
        item = client.trigger_row()
        with patch.object(client, "change_label"):
            triage.apply_labels(client, [item], 9)
        self.assertEqual(item["label_status"], "failed/unknown")

    def test_holds_and_current_approvals_are_not_write_candidates(self):
        for held in (False, True):
            with self.subTest(held=held):
                client = LabelGitHub()
                if held:
                    client.details["labels"] = [{"name": "HoldOn"}]
                else:
                    client.reviews = [review()]
                    client.summary = lambda number: dict(SUMMARY, reviewDecision="APPROVED")
                item = client.trigger_row()
                triage.apply_labels(client, [item], 9)
                self.assertEqual(client.actions, [])

    def test_cli_is_read_only_by_default_and_apply_mode_invokes_actions(self):
        for apply in (False, True):
            with self.subTest(apply=apply):
                client = LabelGitHub()
                with patch.object(triage, "gh", return_value=[client.summary(42)]), patch.object(
                    triage, "GitHub", return_value=client
                ), patch("sys.stdout", new_callable=io.StringIO):
                    self.assertEqual(triage.main(["--apply-labels"] if apply else []), 0)
                self.assertEqual(client.actions, [(42, False)] if apply else [])

    def test_delete_empty_response_and_post_array_payload(self):
        client = triage.GitHub(REPO)
        response = type("Response", (), {"stdout": "", "stderr": "", "returncode": 0})()
        with patch.object(triage.subprocess, "run", return_value=response):
            self.assertIsNone(client.change_label(42, remove=True))
            with self.assertRaises(triage.CollectionError):
                client.get("empty")
        with patch.object(triage, "gh", return_value=[]) as command:
            client.change_label(42)
            command.assert_called_once_with(
                "api", "--method", "POST", f"repos/{REPO}/issues/42/labels", "-f", "labels[]=mgmt-review-needed"
            )


class ReviewRequestStateTests(unittest.TestCase):
    def test_claim_survives_new_instance_and_is_scoped_to_repository_pr_and_head(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state" / "requests.sqlite3"
            first = triage.ReviewRequests(path)
            self.assertIsNone(first.status(REPO, 42, HEAD))
            self.assertFalse(path.exists())
            self.assertTrue(first.claim(REPO, 42, HEAD))
            second = triage.ReviewRequests(path)
            self.assertEqual(second.status(REPO.lower(), 42, HEAD), "pending")
            self.assertFalse(second.claim(REPO.lower(), 42, HEAD))
            self.assertTrue(second.claim(REPO, 42, OLD))
            self.assertTrue(second.claim(REPO, 43, HEAD))
            self.assertTrue(second.claim("Azure/other", 42, HEAD))
            first.finish(REPO, 42, HEAD, "requested")
            self.assertEqual(second.status(REPO, 42, HEAD), "requested")

    def test_invalid_state_is_reported_instead_of_reset(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "requests.sqlite3"
            path.write_text("invalid database", encoding="utf-8")
            state = triage.ReviewRequests(path)
            with self.assertRaises(triage.CollectionError):
                state.status(REPO, 42, HEAD)
            with self.assertRaises(triage.CollectionError):
                state.claim(REPO, 42, HEAD)
            self.assertEqual(path.read_text(encoding="utf-8"), "invalid database")


if __name__ == "__main__":
    unittest.main()
