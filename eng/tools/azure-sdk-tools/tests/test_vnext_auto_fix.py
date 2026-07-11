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


def _make_pr(
    title: str = "",
    body: str = "",
    html_url: str = "https://github.com/test/repo/pull/99",
) -> SimpleNamespace:
    return SimpleNamespace(title=title, body=body, html_url=html_url)


# ---------------------------------------------------------------------------
# Helpers for pyproject.toml-based eligibility tests
# ---------------------------------------------------------------------------


def _write_pyproject(tmp_path, vnext_copilot_fix=None):
    """Create a minimal pyproject.toml under *tmp_path*.

    When *vnext_copilot_fix* is not None the setting is written under
    ``[tool.azure-sdk-build]``.
    """
    lines = [
        '[build-system]\nrequires = ["setuptools"]\nbuild-backend = "setuptools.build_meta"\n',
        '[project]\nname = "azure-test-pkg"\nversion = "1.0.0"\ndependencies = []\n',
    ]
    if vnext_copilot_fix is not None:
        lines.append(f"[tool.azure-sdk-build]\nvnext_copilot_fix = {str(vnext_copilot_fix).lower()}\n")
    (tmp_path / "pyproject.toml").write_text("\n".join(lines))
    return str(tmp_path)


# ---------------------------------------------------------------------------
# Eligibility tests
# ---------------------------------------------------------------------------


class TestIsAutoFixEligible:
    """Tests for is_auto_fix_eligible."""

    def test_not_eligible_by_default(self, tmp_path):
        pkg = _write_pyproject(tmp_path)
        assert is_auto_fix_eligible(pkg) is False

    def test_eligible_when_true(self, tmp_path):
        pkg = _write_pyproject(tmp_path, vnext_copilot_fix=True)
        assert is_auto_fix_eligible(pkg) is True

    def test_opt_out_via_pyproject(self, tmp_path):
        pkg = _write_pyproject(tmp_path, vnext_copilot_fix=False)
        assert is_auto_fix_eligible(pkg) is False


# ---------------------------------------------------------------------------
# Duplicate PR detection tests
# ---------------------------------------------------------------------------


class TestFindExistingFixPrs:

    def test_match_by_issue_ref_in_title(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(title="Fix pylint for azure-ai-test #42"),
        ]
        result = find_existing_fix_prs(repo, 42)
        assert len(result) == 1

    def test_match_by_issue_ref_in_body(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes #42"),
        ]
        result = find_existing_fix_prs(repo, 42)
        assert len(result) == 1

    def test_match_by_repo_qualified_issue_ref(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes Azure/azure-sdk-for-python#42"),
        ]
        result = find_existing_fix_prs(repo, 42)
        assert len(result) == 1

    def test_match_by_issue_url(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes https://github.com/Azure/azure-sdk-for-python/issues/42"),
        ]
        result = find_existing_fix_prs(repo, 42)
        assert len(result) == 1

    def test_package_and_check_mention_alone_does_not_match(self):
        # Regression: an unrelated PR that merely mentions the package path and
        # the word "pylint" (e.g. in its validation command list) must NOT be
        # treated as a duplicate fix PR. See false positive on issue #43899.
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(
                title="Validate built-in transport kwargs",
                body="Validation: python eng/tox/run_pylint.py for sdk/identity/azure-ai-test",
            ),
        ]
        result = find_existing_fix_prs(repo, 99)
        assert len(result) == 0

    def test_no_match(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(title="Unrelated PR", body="Nothing here"),
        ]
        result = find_existing_fix_prs(repo, 42)
        assert len(result) == 0

    def test_issue_ref_does_not_match_longer_issue_number(self):
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(title="Fix issue #420"),
        ]
        result = find_existing_fix_prs(repo, 42)
        assert len(result) == 0

    def test_github_exception_returns_empty(self):
        repo = MagicMock()
        repo.get_pulls.side_effect = GithubException(500, "error", None)
        result = find_existing_fix_prs(repo, 42)
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
        assert assign_copilot(issue, "azure-ai-test", "pylint") is True
        issue.add_to_assignees.assert_called_once_with("copilot-swe-agent[bot]")
        issue.remove_from_assignees.assert_not_called()

    def test_already_assigned_skips(self):
        issue = _make_issue(assignees=["copilot-swe-agent"])
        assert assign_copilot(issue, "azure-ai-test", "pylint") is True
        issue.add_to_assignees.assert_not_called()

    def test_failure_returns_false(self):
        issue = _make_issue()
        issue.add_to_assignees.side_effect = Exception("assign failed")
        assert assign_copilot(issue, "azure-ai-test", "pylint") is False

    def test_force_reassign_unassigns_then_reassigns(self):
        issue = _make_issue(assignees=["copilot-swe-agent[bot]"])
        assert assign_copilot(issue, "azure-ai-test", "pylint", force_reassign=True) is True
        issue.remove_from_assignees.assert_called_once_with("copilot-swe-agent[bot]")
        issue.add_to_assignees.assert_called_once_with("copilot-swe-agent[bot]")

    def test_force_reassign_returns_false_when_unassign_fails(self):
        issue = _make_issue(assignees=["copilot-swe-agent"])
        issue.remove_from_assignees.side_effect = Exception("remove failed")
        assert assign_copilot(issue, "azure-ai-test", "pylint", force_reassign=True) is False
        issue.remove_from_assignees.assert_called_once()
        issue.add_to_assignees.assert_not_called()


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

    def test_matches_bot_suffix(self):
        issue = _make_issue(assignees=["copilot-swe-agent[bot]"])
        assert _is_copilot_already_assigned(issue) is True


# ---------------------------------------------------------------------------
# Integration: _try_auto_fix tests
# ---------------------------------------------------------------------------


class TestTryAutoFix:

    def test_eligible_no_duplicate_assigns(self, tmp_path):
        pkg = _write_pyproject(tmp_path, vnext_copilot_fix=True)
        repo = MagicMock()
        repo.get_pulls.return_value = []
        issue = _make_issue(labels=["pylint"])

        _try_auto_fix(repo, issue, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", pkg)

        # Labels reconciled
        issue.add_to_labels.assert_any_call(LABEL_AUTO_FIX)
        # Instructions appended
        issue.edit.assert_called_once()
        body_arg = issue.edit.call_args[1]["body"]
        assert "Copilot instructions" in body_arg
        # Copilot assigned via REST
        issue.add_to_assignees.assert_called_once_with("copilot-swe-agent[bot]")

    def test_eligible_with_duplicate_pr_skips(self, tmp_path):
        pkg = _write_pyproject(tmp_path, vnext_copilot_fix=True)
        repo = MagicMock()
        repo.get_pulls.return_value = [
            _make_pr(body="Fixes #1"),
        ]
        issue = _make_issue(number=1, labels=["pylint"])

        _try_auto_fix(repo, issue, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", pkg)

        # Should NOT assign Copilot
        issue.add_to_assignees.assert_not_called()

    def test_opt_out_pyproject_prevents_assignment(self, tmp_path):
        pkg = _write_pyproject(tmp_path, vnext_copilot_fix=False)
        repo = MagicMock()
        issue = _make_issue(labels=["pylint"])

        _try_auto_fix(
            repo,
            issue,
            "azure-ai-test",
            "sdk/ai/azure-ai-test",
            "pylint",
            pkg,
        )

        issue.add_to_assignees.assert_not_called()

    def test_weekly_retry_reassigns_when_no_pr(self, tmp_path):
        """Simulates a weekly re-run: issue already has copilot-auto-fix label
        but no matching PR exists, so Copilot should be reassigned."""
        pkg = _write_pyproject(tmp_path, vnext_copilot_fix=True)
        repo = MagicMock()
        repo.get_pulls.return_value = []
        issue = _make_issue(labels=["pylint", LABEL_AUTO_FIX])

        _try_auto_fix(repo, issue, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", pkg)

        issue.add_to_assignees.assert_called_once_with("copilot-swe-agent[bot]")

    def test_assignment_failure_does_not_crash(self, tmp_path):
        pkg = _write_pyproject(tmp_path, vnext_copilot_fix=True)
        repo = MagicMock()
        repo.get_pulls.return_value = []
        issue = _make_issue(labels=["pylint"])
        issue.add_to_assignees.side_effect = Exception("assign failed")

        _try_auto_fix(repo, issue, "azure-ai-test", "sdk/ai/azure-ai-test", "pylint", pkg)

        issue.add_to_labels.assert_not_called()
