# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to create issues for client libraries failing the vnext of mypy, pyright, and pylint.
from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import sys
import os
import subprocess
import logging
import datetime
import re
import calendar
import typing
import pathlib
from typing_extensions import Literal
from github import Github, Auth, GithubException

from ci_tools.variables import discover_repo_root
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import is_package_active

if TYPE_CHECKING:
    from github.Repository import Repository

logging.getLogger().setLevel(logging.INFO)

CHECK_TYPE = Literal["mypy", "pylint", "pyright", "sphinx"]

# The automation that files vnext issues has run under different identities over time
# (the `azure-sdk` user account and the `azure-sdk-automation[bot]` GitHub App). We match
# issues from any known automation creator so existing issues are correctly found and
# de-duplicated regardless of which identity created them. Filtering by creator (rather
# than title alone) avoids ever editing/closing an issue a human happened to open.
VNEXT_ISSUE_CREATORS = ["azure-sdk", "azure-sdk-automation[bot]"]


def find_vnext_issues(repo: "Repository", check_type: CHECK_TYPE, package_name: str) -> list:
    """Return all open vnext issues for the given package and check_type, across every
    known automation creator identity, sorted oldest-first (by issue number)."""
    matches = [
        issue
        for issue in repo.get_issues(state="open", labels=[check_type])
        if issue.title.split("needs")[0].strip() == package_name and issue.user.login in VNEXT_ISSUE_CREATORS
    ]
    return sorted(matches, key=lambda issue: issue.number)


def is_package_deprecated(package_dir: str) -> bool:
    """Returns True if the package is deprecated/inactive (e.g. carries the
    'Development Status :: 7 - Inactive' classifier). Deprecated packages should
    not have vnext issues created against them."""
    try:
        parsed = ParsedSetup.from_path(package_dir)
    except Exception as e:  # pragma: no cover - defensive
        logging.warning(f"Unable to parse metadata for {package_dir} to determine deprecation status: {e}")
        return False
    return not is_package_active(parsed)


def get_version_running(check_type: CHECK_TYPE) -> str:
    commands = [sys.executable, "-m", check_type, "--version"]
    version = subprocess.run(
        commands,
        check=True,
        capture_output=True,
    )
    version = version.stdout.rstrip().decode("utf-8")
    version_running = re.findall(r"(\d+.\d+.\d+)", version)[0]
    logging.info(f"Running {check_type} version {version_running}")
    return version_running


def get_build_link(check_type: CHECK_TYPE) -> str:
    build_id = os.getenv("BUILD_BUILDID")
    job_id = os.getenv("SYSTEM_JOBID")

    next_id: str
    if check_type == "mypy":
        next_id = "c4b2a078-69a7-55a2-d776-67715c71590f"
    if check_type == "pyright":
        next_id = "d243185e-b901-5eef-29fe-f7943e030451"
    if check_type == "pylint":
        next_id = "b33d1587-3539-5735-af43-e3e62f02ca4b"
    if check_type == "sphinx":
        next_id = "82919efa-82d6-5dc4-2e9a-f82117bff292"

    return (
        f"https://dev.azure.com/azure-sdk/internal/_build/results?buildId={build_id}&view=logs&j={job_id}&t={next_id}"
    )


def get_merge_dates(year: str) -> typing.List[datetime.datetime]:
    """We'll merge the latest version of the type checker/linter quarterly
    on the Monday after release week. This function returns those 4 Mondays
    for the given year.
    """
    c = calendar.Calendar(firstweekday=calendar.FRIDAY)
    first = c.monthdatescalendar(year, 1)
    second = c.monthdatescalendar(year, 4)
    third = c.monthdatescalendar(year, 7)
    fourth = c.monthdatescalendar(year, 10)

    merge_months = [first, second, third, fourth]

    merge_dates = []
    for month in merge_months:
        code_complete = [
            day for week in month for day in week if day.weekday() == calendar.FRIDAY and day.month in [1, 4, 7, 10]
        ][0]
        monday_after_release_week = code_complete + datetime.timedelta(days=10)
        merge_dates.append(monday_after_release_week)
    return merge_dates


def get_date_for_version_bump(today: datetime.datetime) -> str:
    merge_dates = get_merge_dates(today.year)
    try:
        merge_date = min(date for date in merge_dates if date >= today)
    except ValueError:
        # today's date is after October merge date, so rollover to next year
        merge_dates = get_merge_dates(today.year + 1)
        merge_date = min(date for date in merge_dates if date >= today)
    return merge_date.strftime("%Y-%m-%d")


def get_labels(package_name: str, service: str) -> tuple[list[str], list[str]]:
    repo_root = discover_repo_root()
    codeowners_path = pathlib.Path(repo_root) / ".github" / "CODEOWNERS"
    with open(codeowners_path, "r") as codeowners_file:
        codeowners = codeowners_file.readlines()

    label = ""
    service_label = ""
    service_owners = []
    labels = []
    assignees = []
    if "mgmt" in package_name:
        labels.append("Mgmt")
    for line in codeowners:
        if line.startswith("# PRLabel:"):
            label = line.split("# PRLabel: %")[1].strip()
        if label and line.startswith("/sdk/"):
            parts = [part for part in line.split("@")[0].split("/") if part.strip()][1:]
            if len(parts) > 2:
                continue
            try:
                service_directory = parts[0]
            except IndexError:
                # it was a single file
                continue
            try:
                library = parts[1]
                if package_name == library:
                    labels.append(label)
                    # Extract codeowners from the line
                    tokens = line.split()
                    owners = [token.lstrip("@") for token in tokens if token.startswith("@")]
                    # Filter out teams (containing '/')
                    assignees = [owner for owner in owners if "/" not in owner]
                    return labels, assignees
            except IndexError:
                if service_directory == service:
                    service_label = label
                    # Extract service-level codeowners
                    tokens = line.split()
                    owners = [token.lstrip("@") for token in tokens if token.startswith("@")]
                    service_owners = [owner for owner in owners if "/" not in owner]

    if service_label:
        labels.append(service_label)
        assignees = service_owners
    return labels, assignees


def create_vnext_issue(package_dir: str, check_type: CHECK_TYPE, check_version: Optional[str] = None) -> None:
    """This is called when a client library fails a vnext check.
    An issue is created with the details or an existing issue is updated with the latest information."""

    package_path = pathlib.Path(package_dir)
    package_name = package_path.name
    service_directory = package_path.parent.name

    # Deprecated/inactive packages should never have vnext issues created against them.
    if is_package_deprecated(package_dir):
        logging.info(f"Package {package_name} is deprecated/inactive. Skipping vnext issue creation for {check_type}.")
        close_vnext_issue(package_name, check_type)
        return

    auth = Auth.Token(os.environ["GH_TOKEN"])
    g = Github(auth=auth)

    today = datetime.date.today()
    repo = g.get_repo("Azure/azure-sdk-for-python")

    vnext_issue = find_vnext_issues(repo, check_type, package_name)

    version = check_version or get_version_running(check_type)
    build_link = get_build_link(check_type)
    merge_date = get_date_for_version_bump(today)
    error_type = "linting" if check_type == "pylint" else "docstring" if check_type == "sphinx" else "typing"
    guide_link = (
        "[Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)"
        if check_type == "pylint"
        else (
            "[Sphinx and docstring checker](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#sphinx-and-docstring-checker)"
            if check_type == "sphinx"
            else "[Typing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md#run-mypy)"
        )
    )

    repo_root = discover_repo_root()
    title = f"{package_name} needs {error_type} updates for {check_type} version {version}"
    template = (
        f"**ACTION NEEDED:** This version of {check_type} will be merged on **{merge_date}**. "
        f"The build will begin to fail for this library if errors are not fixed."
        f"\n\n**Library name:** {package_name}"
        f"\n**{check_type.capitalize()} version:** {version}"
        f"\n**{check_type.capitalize()} Build:** [Link to build ({today.strftime('%Y-%m-%d')})]({build_link})"
        f"\n**How to fix:** Run the `next-{check_type}` azpysdk command at the library package-level and resolve "
        f"the {error_type} errors.\n"
        f"1) `{repo_root}>pip install -e ./eng/tools/azure-sdk-tools`\n"
        f"2) `../{package_name}>azpysdk next-{check_type} --isolate .`\n\n"
        f"See the {guide_link} for more information."
    )

    # create an issue for the library failing the vnext check
    if not vnext_issue:
        try:
            labels, assignees = get_labels(package_name, service_directory)
        except Exception as e:
            logging.warning(f"Failed to get labels and assignees from CODEOWNERS for {package_name}: {e}")
            labels = []
            assignees = []
            if "mgmt" in package_name:
                labels.append("Mgmt")

        labels.extend([check_type])
        logging.info(f"Issue does not exist for {package_name} with {check_type} version {version}. Creating...")
        issue = repo.create_issue(title=title, body=template, labels=labels)

        # Assign codeowners individually with error handling
        for assignee in assignees:
            try:
                issue.add_to_assignees(assignee)
                logging.info(f"Assigned {assignee} to issue for {package_name}")
            except GithubException as e:
                logging.warning(f"Failed to assign {assignee} to issue for {package_name}: {e}")
        return

    # an issue exists, let's update it so it reflects the latest typing/linting errors
    logging.info(f"Issue exists for {package_name} with {check_type} version {version}. Updating...")
    try:
        labels, assignees = get_labels(package_name, service_directory)
    except Exception as e:
        logging.warning(f"Failed to get labels and assignees from CODEOWNERS for {package_name}: {e}")
        labels = []
        assignees = []

    # Update the most recent issue and close any older duplicates so we converge on a single issue.
    primary_issue = vnext_issue[-1]
    for duplicate in vnext_issue[:-1]:
        logging.info(f"Closing duplicate vnext issue #{duplicate.number} for {package_name} ({check_type}).")
        duplicate.edit(state="closed")

    primary_issue.edit(
        title=title,
        body=template,
    )

    # Assign codeowners individually with error handling
    for assignee in assignees:
        try:
            primary_issue.add_to_assignees(assignee)
            logging.info(f"Assigned {assignee} to issue for {package_name}")
        except GithubException as e:
            logging.warning(f"Failed to assign {assignee} to issue for {package_name}: {e}")


def close_vnext_issue(package_name: str, check_type: CHECK_TYPE) -> None:
    """This is called when a client library passes a vnext check. If an issue exists for the library, it is closed."""

    auth = Auth.Token(os.environ["GH_TOKEN"])
    g = Github(auth=auth)

    repo = g.get_repo("Azure/azure-sdk-for-python")

    vnext_issues = find_vnext_issues(repo, check_type, package_name)
    for issue in vnext_issues:
        logging.info(f"{package_name} passes {check_type}. Closing existing GH issue #{issue.number}...")
        issue.edit(state="closed")
