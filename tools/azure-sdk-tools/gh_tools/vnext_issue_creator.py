# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to create issues for client libraries failing the vnext of mypy, pyright, and pylint. 

import sys
import os
import subprocess
import logging
import datetime
import re
import calendar
import typing
from typing_extensions import Literal
from github import Github, Auth

logging.getLogger().setLevel(logging.INFO)


def get_version_running(check_type: Literal["mypy", "pylint", "pyright"]) -> str:
    commands = [
        sys.executable,
        "-m",
        check_type,
        "--version"
    ]
    version = subprocess.run(
        commands,
        check=True,
        capture_output=True,
    )
    version = version.stdout.rstrip().decode("utf-8")
    version_running = re.findall(r'(\d+.\d+.\d+)', version)[0]
    logging.info(f"Running {check_type} version {version_running}")
    return version_running


def get_build_link(check_type: Literal["mypy", "pylint", "pyright"]) -> str:
    build_id = os.getenv('BUILD_BUILDID')
    job_id = os.getenv('SYSTEM_JOBID')

    next_id: str
    if check_type == "mypy":
        next_id = "59f5c573-b3ce-57f7-6a79-55fe2db3a175"
    if check_type == "pyright":
        next_id = "c0edaab3-85d6-5e4b-81a8-d1190a6ee92b"
    if check_type == "pylint":
        next_id = "e1fa7d9e-8471-5a74-cd7d-e1c9a992e07e"

    return f"https://dev.azure.com/azure-sdk/internal/_build/results?buildId={build_id}&view=logs&j={job_id}&t={next_id}"    


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
        code_complete = [day for week in month for day in week if \
                        day.weekday() == calendar.FRIDAY and day.month in [1, 4, 7, 10]][0]
        monday_after_release_week = code_complete + datetime.timedelta(days=10)
        merge_dates.append(monday_after_release_week)
    return merge_dates


def get_date_for_version_bump(today: datetime.datetime) -> str:
    merge_dates = get_merge_dates(today.year)
    try:
        merge_date = min(date for date in merge_dates if date >= today)
    except ValueError:
        # today's date is after October merge date, so rollover to next year
        merge_dates = get_merge_dates(today.year+1)
        merge_date = min(date for date in merge_dates if date >= today)
    return merge_date.strftime('%Y-%m-%d')


def create_vnext_issue(package_name: str, check_type: Literal["mypy", "pylint", "pyright"]) -> None:
    """This is called when a client library fails a vnext check.
    An issue is created with the details or an existing issue is updated with the latest information."""

    auth = Auth.Token(os.environ["GH_TOKEN"])
    g = Github(auth=auth)

    today = datetime.date.today()
    repo = g.get_repo("Azure/azure-sdk-for-python")

    issues = repo.get_issues(state="open", labels=[check_type], creator="azure-sdk")
    vnext_issue = [issue for issue in issues if issue.title.split("needs")[0].strip() == package_name]

    version = get_version_running(check_type)
    build_link = get_build_link(check_type)
    merge_date = get_date_for_version_bump(today)
    error_type = "linting" if check_type == "pylint" else "typing"
    guide_link = "[Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)" \
        if check_type == "pylint" else "[Typing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md#run-mypy)"

    title = f"{package_name} needs {error_type} updates for {check_type} version {version}"
    template = (
        f"**ACTION NEEDED:** This version of {check_type} will be merged on **{merge_date}**. "
        f"The build will begin to fail for this library if errors are not fixed."
        f"\n\n**Library name:** {package_name}"
        f"\n**{check_type.capitalize()} version:** {version}"
        f"\n**{check_type.capitalize()} errors:** [Link to build ({today.strftime('%Y-%m-%d')})]({build_link})"
        f"\n**How to fix:** Run the `next-{check_type}` tox command at the library package-level and resolve "
        f"the {error_type} errors.\n"
        f"1) `../{package_name}>pip install \"tox<5\"`\n"
        f"2) `../{package_name}>tox run -e next-{check_type} -c ../../../eng/tox/tox.ini --root .`\n\n"
        f"See the {guide_link} for more information."
    )

    # create an issue for the library failing the vnext check
    if not vnext_issue:
        logging.info(f"Issue does not exist for {package_name} with {check_type} version {version}. Creating...")
        repo.create_issue(
            title=title,
            body=template,
            labels=[check_type]
        )
        return

    # an issue exists, let's update it so it reflects the latest typing/linting errors
    logging.info(f"Issue exists for {package_name} with {check_type} version {version}. Updating...")
    vnext_issue[0].edit(
        title=title,
        body=template,
    )
