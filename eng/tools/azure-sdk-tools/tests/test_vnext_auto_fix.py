# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Tests for vnext issue auto-fix automation helpers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from github import GithubException

from gh_tools.vnext_issue_creator import (
    COPILOT_AUTOFIX_END,
    COPILOT_AUTOFIX_START,
    LABEL_AUTO_FIX,
    LABEL_AUTO_FIX_DISABLED,
    _is_copilot_already_assigned,
    _try_auto_fix,
    _upsert_copilot_instructions,
    assign_copilot,
    build_copilot_instructions,
    find_existing_fix_prs,
    is_auto_fix_eligible,
    reconcile_auto_fix_labels,
)


# ---------------------------------------------------------------------------
# Helpers to build lightweight fakes
# ---------------------------------------------------------------------------


def _make_label(name: str) -> SimpleNamespace:
    return SimpleNamespace(name=name)


def _make_assignee(login: str) -> SimpleNamespace:
    return SimpleNamespace(login=login)


def _make_issue(
    number: int = 1,
    body: str = "",
    labels: list | None = None,
    assignees: list | None = None,
    node_id: str = "I_abc123",
) -> MagicMock:
    issue = MagicMock()
    issue.number = number
    issue.body = body
    issue.labels = [_make_label(l) for l in (labels or [])]
    issue.assignees = [_make_assignee(a) for a in (assignees or [])]
    issue.html_url = f"https://github.com/test/repo/issues/{number}"
    issue.raw_data = {"node_id": node_id}
    return issue


def _make_github_instance() -> MagicMock:
    """Create a mock Github instance with a requester that supports graphql_named_mutation."""
    g = MagicMock()
    g._Github__requester = MagicMock()
    g._Github__requester.graphql_query.return_value = (
        {},
        {
            "data": {
                "node": {
                    "suggestedActors": {
                        "nodes": [{"login": "copilot-swe-agent", "id": "BOT_dynamic"}],
                    }
                }
            }
        },
    )
    return g


def _make_pr(
    title: str = "",
    body: str = "",
    html_url: str = "https://github.com/test/repo/pull/99",
) -> SimpleNamespace:
    return SimpleNamespace(title=title, body=body, html_url=html_url)


# ---------------------------------------------------------------------------
# Eligibility tests
# ---------------------------------------------------------------------------


class TestIsAutoFixEligible:
    """Tests for is_auto_fix_eligible."""

    def test_eligible_by_default(self):
        assert is_auto_fix_eligible([]) is True
        assert is_auto_fix_eligible(["pylint"]) is True
        assert is_auto_fix_eligible(["mypy", "some-service-label"]) is True

    def test_opt_out_label(self):
        assert is_auto_fix_eligible([LABEL_AUTO_FIX_DISABLED]) is False


# ---------------------------------------------------------------------------
# Duplicate PR detection tests
# ---------------------------------------------------------------------------


class TestFindExistingFixPrs:

    def test_match_by_issue_ref_in_title(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(title="Fix pylint for azure-ai-test #42"),
        ]
        result = find_existing_fix_prs(repo, 42, "azure-ai-test", "pylint")
        assert len(result) == 1

    def test_match_by_issue_ref_in_body(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes #42"),
        ]
        result = find_existing_fix_prs(repo, 42, "azure-ai-test", "pylint")
        assert len(result) == 1

    def test_match_by_repo_qualified_issue_ref(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes Azure/azure-sdk-for-python#42"),
        ]
        result = find_existing_fix_prs(repo, 42, "azure-ai-test", "pylint")
        assert len(result) == 1

    def test_match_by_issue_url(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes https://github.com/Azure/azure-sdk-for-python/issues/42"),
        ]
        result = find_existing_fix_prs(repo, 42, "azure-ai-test", "pylint")
        assert len(result) == 1

    def test_match_by_package_and_check(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(title="Fix azure-ai-test pylint errors"),
        ]
        result = find_existing_fix_prs(repo, 99, "azure-ai-test", "pylint")
        assert len(result) == 1

    def test_no_match(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(title="Unrelated PR", body="Nothing here"),
        ]
        result = find_existing_fix_prs(repo, 42, "azure-ai-test", "pylint")
        assert len(result) == 0

    def test_issue_ref_does_not_match_longer_issue_number(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(title="Fix issue #420"),
        ]
        result = find_existing_fix_prs(repo, 42, "azure-ai-test", "pylint")
        assert len(result) == 0

    def test_github_exception_returns_empty(self):
        repo = MagicMock()
        repo.get_pulls.side_effect = GithubException(500, "error", None)
        result = find_existing_fix_prs(repo, 42, "azure-ai-test", "pylint")
        assert result == []


# ---------------------------------------------------------------------------
# Copilot instruction builder tests
# ---------------------------------------------------------------------------


class TestBuildCopilotInstructions:

    @pytest.mark.parametrize("check_type", ["pylint", "mypy", "sphinx", "pyright"])
    def test_contains_required_elements(self, check_type):
        result = build_copilot_instructions("sdk/ai/azure-ai-test", check_type)

        assert f"fix-{check_type}" in result
        assert "sdk/ai/azure-ai-test" in result
        assert "Automated Fix" in result
        assert "Do not make unrelated" in result


class TestUpsertCopilotInstructions:

    def test_appends_when_no_existing_block(self):
        instructions = build_copilot_instructions("sdk/ai/azure-ai-test", "pylint")
        body = "Existing issue body"

        result = _upsert_copilot_instructions(body, instructions)

        assert result == body + instructions

    def test_replaces_existing_block_and_preserves_tail(self):
        instructions = build_copilot_instructions("sdk/ai/azure-ai-test", "pyright")
        body = (
            "Existing issue body\n\n"
            f"{COPILOT_AUTOFIX_START}\n"
            "old instructions\n"
            f"{COPILOT_AUTOFIX_END}\n\n"
            "Human-authored follow-up"
        )

        result = _upsert_copilot_instructions(body, instructions)

        assert "old instructions" not in result
        assert result.startswith("Existing issue body")
        assert instructions in result
        assert result.endswith("\n\nHuman-authored follow-up")

    def test_appends_when_existing_markers_are_malformed(self):
        instructions = build_copilot_instructions("sdk/ai/azure-ai-test", "mypy")
        body = f"Existing issue body\n\n{COPILOT_AUTOFIX_END}\nold instructions\n{COPILOT_AUTOFIX_START}"

        result = _upsert_copilot_instructions(body, instructions)

        assert result == body + instructions


# ---------------------------------------------------------------------------
# Label reconciliation tests
# ---------------------------------------------------------------------------


class TestReconcileAutoFixLabels:

    def test_adds_auto_fix_label(self):
        issue = _make_issue(labels=["pylint"])
        reconcile_auto_fix_labels(issue, eligible=True)
        issue.add_to_labels.assert_called_once_with(LABEL_AUTO_FIX)

    def test_skips_if_already_labeled(self):
        issue = _make_issue(labels=["pylint", LABEL_AUTO_FIX])
        reconcile_auto_fix_labels(issue, eligible=True)
        issue.add_to_labels.assert_not_called()

    def test_not_eligible_no_op(self):
        issue = _make_issue(labels=["pylint"])
        reconcile_auto_fix_labels(issue, eligible=False)
        issue.add_to_labels.assert_not_called()
        issue.remove_from_labels.assert_not_called()


# ---------------------------------------------------------------------------
# Copilot assignment tests
# ---------------------------------------------------------------------------


class TestAssignCopilot:

    def test_success(self):
        issue = _make_issue()
        g = _make_github_instance()
        assert assign_copilot(issue, g, "BOT_dynamic", "azure-ai-test", "pylint") is True
        g._Github__requester.graphql_named_mutation.assert_called_once()
        call_args = g._Github__requester.graphql_named_mutation.call_args
        assert call_args[0][0] == "addAssigneesToAssignable"
        assert call_args[0][1]["assigneeIds"] == ["BOT_dynamic"]

    def test_already_assigned_skips(self):
        issue = _make_issue(assignees=["copilot-swe-agent"])
        g = _make_github_instance()
        assert assign_copilot(issue, g, "BOT_dynamic", "azure-ai-test", "pylint") is True
        g._Github__requester.graphql_named_mutation.assert_not_called()

    def test_failure_returns_false(self):
        issue = _make_issue()
        g = _make_github_instance()
        g._Github__requester.graphql_named_mutation.side_effect = Exception("mutation failed")
        assert assign_copilot(issue, g, "BOT_dynamic", "azure-ai-test", "pylint") is False

    def test_force_reassign_returns_false_when_unassign_fails(self):
        issue = _make_issue(assignees=["copilot-swe-agent"])
        g = _make_github_instance()
        g._Github__requester.graphql_named_mutation.side_effect = Exception("remove failed")
        assert assign_copilot(issue, g, "BOT_dynamic", "azure-ai-test", "pylint", force_reassign=True) is False
        g._Github__requester.graphql_named_mutation.assert_called_once()


# ---------------------------------------------------------------------------
# _is_copilot_already_assigned tests
# ---------------------------------------------------------------------------


class TestIsCopilotAlreadyAssigned:

    def test_assigned(self):
        issue = _make_issue(assignees=["copilot-swe-agent"])
        assert _is_copilot_already_assigned(issue) is True

    def test_not_assigned(self):
        issue = _make_issue(assignees=["human-user"])
        assert _is_copilot_already_assigned(issue) is False

    def test_case_insensitive(self):
        issue = _make_issue(assignees=["Copilot-SWE-Agent"])
        assert _is_copilot_already_assigned(issue) is True


# ---------------------------------------------------------------------------
# Integration: _try_auto_fix tests
# ---------------------------------------------------------------------------


class TestTryAutoFix:

    def test_eligible_no_duplicate_assigns(self):
        repo = MagicMock()
        repo.get_pulls.return_value = []
        issue = _make_issue(labels=["pylint"])
        g = _make_github_instance()

        _try_auto_fix(repo, issue, g, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", ["pylint"])

        # Labels reconciled
        issue.add_to_labels.assert_any_call(LABEL_AUTO_FIX)
        # Instructions appended
        issue.edit.assert_called_once()
        body_arg = issue.edit.call_args[1]["body"]
        assert "Copilot instructions" in body_arg
        # Copilot assigned via GraphQL
        g._Github__requester.graphql_named_mutation.assert_called_once()
        g._Github__requester.graphql_query.assert_called_once()

    def test_eligible_with_duplicate_pr_skips(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes #1"),
        ]
        issue = _make_issue(number=1, labels=["pylint"])
        g = _make_github_instance()

        _try_auto_fix(repo, issue, g, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", ["pylint"])

        # Should NOT assign Copilot
        g._Github__requester.graphql_named_mutation.assert_not_called()

    def test_opt_out_label_prevents_assignment(self):
        repo = MagicMock()
        issue = _make_issue(labels=["pylint", LABEL_AUTO_FIX_DISABLED])
        g = _make_github_instance()

        _try_auto_fix(
            repo,
            issue,
            g,
            "azure-ai-test",
            "sdk/ai/azure-ai-test",
            "pylint",
            ["pylint", LABEL_AUTO_FIX_DISABLED],
        )

        g._Github__requester.graphql_named_mutation.assert_not_called()

    def test_weekly_retry_reassigns_when_no_pr(self):
        """Simulates a weekly re-run: issue already has copilot-auto-fix label
        but no matching PR exists, so Copilot should be reassigned."""
        repo = MagicMock()
        repo.get_pulls.return_value = []
        issue = _make_issue(labels=["pylint", LABEL_AUTO_FIX])
        g = _make_github_instance()

        _try_auto_fix(repo, issue, g, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", ["pylint", LABEL_AUTO_FIX])

        g._Github__requester.graphql_named_mutation.assert_called_once()

    def test_assignment_failure_does_not_crash(self):
        repo = MagicMock()
        repo.get_pulls.return_value = []
        issue = _make_issue(labels=["pylint"])
        g = _make_github_instance()
        g._Github__requester.graphql_named_mutation.side_effect = Exception("mutation failed")

        _try_auto_fix(repo, issue, g, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", ["pylint"])

        issue.add_to_labels.assert_not_called()

    def test_missing_copilot_node_id_skips_assignment(self):
        repo = MagicMock()
        repo.get_pulls.return_value = []
        issue = _make_issue(labels=["pylint"])
        g = _make_github_instance()
        g._Github__requester.graphql_query.return_value = (
            {},
            {"data": {"node": {"suggestedActors": {"nodes": []}}}},
        )

        _try_auto_fix(repo, issue, g, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", ["pylint"])

        g._Github__requester.graphql_query.assert_called_once()
        g._Github__requester.graphql_named_mutation.assert_not_called()
        issue.add_to_labels.assert_not_called()
