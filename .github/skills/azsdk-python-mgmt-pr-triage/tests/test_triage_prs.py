"""Offline fixtures for release-rotation queues and conservative activity checks."""

import base64
from copy import deepcopy
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "triage_prs.py"
SPEC = importlib.util.spec_from_file_location("triage_prs", SCRIPT)
triage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(triage)

REPO = "Azure/azure-sdk-for-python"
PR_URL = f"https://github.com/{REPO}/pull/42"
RUN_URL = f"https://github.com/{REPO}/actions/runs/100"
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
}
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
        "issues": [],
        "queues": {},
    }


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
            return [deepcopy(item) for item in self.workflow_runs if f"status={item['status']}" in endpoint]
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
        runs, issues = triage.active_reviews(client)
        item = row()
        triage.classify(item, client, 9, runs, issues)
        self.assertNotIn(1, item["queues"])
        self.assertIn("Review activity unknown", " ".join(item["issues"]))
        self.assertIn(RUN_URL, " ".join(issues))

    def test_activity_access_failure_is_unknown(self):
        client = FakeGitHub()
        client.activity_error = True
        runs, issues = triage.active_reviews(client)
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

    def test_status_requests_paginate_once_each(self):
        client = FakeGitHub()
        client.workflow_runs = [run("in_progress")]
        runs, issues = triage.active_reviews(client)
        self.assertEqual(len(runs), 1)
        self.assertFalse(issues)


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
        item = triage.collect_pr(client, {"number": 42, "reviewDecision": "APPROVED"})
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
                item = triage.collect_pr(client, {"number": 42, "reviewDecision": decision})
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
        item = triage.collect_pr(client, {"number": 42})
        self.assertIn("GitHub review decision unavailable", item["issues"][0])

    def test_first_beta_and_author_followups_in_all_comment_channels(self):
        client = FakeGitHub()
        client.comments.append(comment())
        client.inline = [comment(identifier=3)]
        author_review = review("COMMENTED", "author", LATER, 4)
        author_review["body"] = "Ready now?"
        client.reviews.append(author_review)
        item = triage.collect_pr(client, {"number": 42, "reviewDecision": "APPROVED"})
        self.assertEqual(item["version"], "1.0.0b1")
        self.assertEqual(len(item["followups"]), 3)
        triage.classify(item, client, 9, [], [])
        self.assertIn(5, item["queues"])
        self.assertNotIn(4, item["queues"])

    def test_comments_before_approval_or_by_other_people_not_followups(self):
        client = FakeGitHub()
        client.comments += [comment(when=WHEN), comment(login="other")]
        item = triage.collect_pr(client, {"number": 42})
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
        item = triage.collect_pr(client, {"number": 42})
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
            triage.collect_pr(client, {"number": 42})

    def test_newly_closed_or_draft_pr_skipped(self):
        for changes in ({"state": "closed"}, {"draft": True}):
            client = FakeGitHub()
            client.details.update(changes)
            self.assertIsNone(triage.collect_pr(client, {"number": 42}))

    def test_truncated_files_not_treated_as_complete(self):
        client = FakeGitHub()
        client.details["changed_files"] = 3001
        with self.assertRaises(triage.CollectionError):
            triage.collect_pr(client, {"number": 42})

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
        self.assertIn("## 4. Changes after approval", report)
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
        listing = [{"number": 42, "title": PR["title"], "isDraft": False, "reviewDecision": "APPROVED"}]
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=FakeGitHub()
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main([]), 0)
            self.assertIn("Scanned 1", output.getvalue())
            self.assertIn("No PRs need action", output.getvalue())

    def test_cli_limit_marks_partial(self):
        listing = [{"number": 42, "title": PR["title"], "isDraft": False}]
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=FakeGitHub()
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main(["--limit", "1"]), 2)
            self.assertIn("reached --limit", output.getvalue())
            self.assertNotIn("No PRs need action", output.getvalue())

    def test_cli_exact_package_filter_and_drafts(self):
        listing = [
            {"number": 42, "title": PR["title"], "isDraft": False},
            {"number": 43, "title": "[AutoPR azure-mgmt-other]-generated", "isDraft": False},
            {"number": 44, "title": PR["title"], "isDraft": True},
        ]
        client = FakeGitHub()
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=client
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main(["--package", "azure-mgmt-example"]), 0)
            self.assertIn("Scanned 1", output.getvalue())

    def test_cli_unknown_version_cannot_silently_match_filter(self):
        listing = [{"number": 42, "title": PR["title"], "isDraft": False}]
        client = FakeGitHub()
        client.files[0]["patch"] = ""
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "GitHub", return_value=client
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main(["--version", "1.0.0b1"]), 2)
            self.assertIn("cannot apply --version", output.getvalue())

    def test_cli_collection_failure_reports_partial(self):
        listing = [{"number": 42, "title": PR["title"], "isDraft": False}]
        with patch.object(triage, "gh", return_value=listing), patch.object(
            triage, "collect_pr", side_effect=triage.CollectionError("HTTP 403")
        ), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(triage.main([]), 2)
            self.assertIn("collection incomplete", output.getvalue())
            self.assertNotIn("No PRs need action", output.getvalue())


if __name__ == "__main__":
    unittest.main()
