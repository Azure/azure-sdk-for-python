# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import mock

import pytest

from gh_tools import vnext_issue_creator


class _FakeParsedSetup:
    def __init__(self, name, classifiers):
        self.name = name
        self.classifiers = classifiers


class _FakeIssue:
    def __init__(self, number, title, login):
        self.number = number
        self.title = title
        self.user = mock.MagicMock()
        self.user.login = login
        self.edit = mock.MagicMock()
        self.add_to_assignees = mock.MagicMock()


@pytest.mark.parametrize(
    "classifiers, expected_deprecated",
    [
        (["Development Status :: 5 - Production/Stable"], False),
        (["Development Status :: 4 - Beta"], False),
        (["Development Status :: 7 - Inactive"], True),
        (["Development Status :: 5 - Production/Stable", "Development Status :: 7 - Inactive"], True),
    ],
)
def test_is_package_deprecated(classifiers, expected_deprecated):
    parsed = _FakeParsedSetup("azure-mgmt-fake", classifiers)
    with mock.patch.object(vnext_issue_creator.ParsedSetup, "from_path", return_value=parsed):
        assert vnext_issue_creator.is_package_deprecated("some/path") is expected_deprecated


def test_is_package_deprecated_parse_failure_returns_false():
    with mock.patch.object(vnext_issue_creator.ParsedSetup, "from_path", side_effect=RuntimeError("boom")):
        assert vnext_issue_creator.is_package_deprecated("some/path") is False


def test_create_vnext_issue_skips_and_closes_for_deprecated_package():
    with mock.patch.object(
        vnext_issue_creator, "is_package_deprecated", return_value=True
    ) as mock_deprecated, mock.patch.object(vnext_issue_creator, "close_vnext_issue") as mock_close, mock.patch.object(
        vnext_issue_creator, "Github"
    ) as mock_github:
        vnext_issue_creator.create_vnext_issue("sdk/mixedreality/azure-mgmt-mixedreality", "mypy")

    mock_deprecated.assert_called_once()
    mock_close.assert_called_once_with("azure-mgmt-mixedreality", "mypy")
    # No GitHub client should be constructed when short-circuiting on a deprecated package.
    mock_github.assert_not_called()


def test_create_vnext_issue_proceeds_for_active_package():
    with mock.patch.object(vnext_issue_creator, "is_package_deprecated", return_value=False), mock.patch.object(
        vnext_issue_creator, "close_vnext_issue"
    ) as mock_close, mock.patch.dict("os.environ", {"GH_TOKEN": "fake-token"}), mock.patch.object(
        vnext_issue_creator, "Github"
    ) as mock_github:
        repo = mock.MagicMock()
        repo.get_issues.return_value = []
        mock_github.return_value.get_repo.return_value = repo
        with mock.patch.object(vnext_issue_creator, "get_labels", return_value=([], [])), mock.patch.object(
            vnext_issue_creator, "get_build_link", return_value="http://build"
        ), mock.patch.object(vnext_issue_creator, "get_date_for_version_bump", return_value="2026-04-13"):
            vnext_issue_creator.create_vnext_issue("sdk/fake/azure-mgmt-fake", "mypy", check_version="1.0.0")

    # Active package: we do not close an issue, we create one.
    mock_close.assert_not_called()
    repo.create_issue.assert_called_once()


def test_find_vnext_issues_matches_all_automation_creators_and_ignores_others():
    repo = mock.MagicMock()
    repo.get_issues.return_value = [
        _FakeIssue(100, "azure-ai-textanalytics needs typing updates for mypy version 1.19.1", "azure-sdk"),
        _FakeIssue(
            200, "azure-ai-textanalytics needs typing updates for mypy version 1.19.1", "azure-sdk-automation[bot]"
        ),
        # Same title but opened by a human -> must be ignored.
        _FakeIssue(300, "azure-ai-textanalytics needs typing updates for mypy version 1.19.1", "some-human"),
        # Different package -> must be ignored.
        _FakeIssue(400, "azure-core needs typing updates for mypy version 1.19.1", "azure-sdk"),
    ]

    result = vnext_issue_creator.find_vnext_issues(repo, "mypy", "azure-ai-textanalytics")

    assert [issue.number for issue in result] == [100, 200]


def test_close_vnext_issue_closes_all_duplicates():
    dup_a = _FakeIssue(100, "azure-ai-textanalytics needs typing updates for mypy version 1.19.1", "azure-sdk")
    dup_b = _FakeIssue(
        200, "azure-ai-textanalytics needs typing updates for mypy version 1.19.1", "azure-sdk-automation[bot]"
    )
    repo = mock.MagicMock()
    with mock.patch.dict("os.environ", {"GH_TOKEN": "fake-token"}), mock.patch.object(
        vnext_issue_creator, "Github"
    ) as mock_github, mock.patch.object(vnext_issue_creator, "find_vnext_issues", return_value=[dup_a, dup_b]):
        mock_github.return_value.get_repo.return_value = repo
        vnext_issue_creator.close_vnext_issue("azure-ai-textanalytics", "mypy")

    dup_a.edit.assert_called_once_with(state="closed")
    dup_b.edit.assert_called_once_with(state="closed")


def test_create_vnext_issue_updates_newest_and_closes_older_duplicates():
    dup_a = _FakeIssue(100, "azure-ai-textanalytics needs typing updates for mypy version 1.19.1", "azure-sdk")
    dup_b = _FakeIssue(
        200, "azure-ai-textanalytics needs typing updates for mypy version 1.19.1", "azure-sdk-automation[bot]"
    )
    repo = mock.MagicMock()
    with mock.patch.object(vnext_issue_creator, "is_package_deprecated", return_value=False), mock.patch.dict(
        "os.environ", {"GH_TOKEN": "fake-token"}
    ), mock.patch.object(vnext_issue_creator, "Github") as mock_github, mock.patch.object(
        vnext_issue_creator, "find_vnext_issues", return_value=[dup_a, dup_b]
    ), mock.patch.object(
        vnext_issue_creator, "get_labels", return_value=([], [])
    ), mock.patch.object(
        vnext_issue_creator, "get_build_link", return_value="http://build"
    ), mock.patch.object(
        vnext_issue_creator, "get_date_for_version_bump", return_value="2026-04-13"
    ):
        mock_github.return_value.get_repo.return_value = repo
        vnext_issue_creator.create_vnext_issue(
            "sdk/textanalytics/azure-ai-textanalytics", "mypy", check_version="1.19.1"
        )

    # No new issue created when duplicates already exist.
    repo.create_issue.assert_not_called()
    # Older duplicate is closed; newest is updated (edited but not closed).
    dup_a.edit.assert_called_once_with(state="closed")
    dup_b.edit.assert_called_once()
    assert dup_b.edit.call_args.kwargs.get("state") != "closed"
