import sys
import os
import subprocess
import logging
import datetime
from github import Github, Auth
logging.getLogger().setLevel(logging.INFO)


def get_mypy_version_running():
    # TODO need to pin the mypy and pyright next checks
    commands = [
        sys.executable,
        "-m",
        "mypy",
        "--version"
    ]
    mypy_version = subprocess.run(
        commands,
        check=True,
        capture_output=True,
    )
    version = mypy_version.stdout.rstrip().decode("utf-8")
    return str(version).split(" ")[1]


def get_build_link():
    run_mypy_next_id = "59f5c573-b3ce-57f7-6a79-55fe2db3a175"
    build_id = os.getenv('BUILD_BUILDID')
    job_id = os.getenv('SYSTEM_JOBID')
    url = f"https://dev.azure.com/azure-sdk/internal/_build/results?buildId={build_id}&view=logs&j={job_id}&t={run_mypy_next_id}"
    return url


def get_date_for_version_bump(today):
    first = datetime.datetime(year=today.year, month=1, day=31)
    second = datetime.datetime(year=today.year, month=4, day=30)
    third = datetime.datetime(year=today.year, month=7, day=31)
    fourth = datetime.datetime(year=today.year, month=10, day=31)
    dates = [first, second, third, fourth]
    try:
        merge_date = min(date for date in dates if date > today)
    except ValueError:
        # today's date is after Oct 31, rollover to next year
        merge_date = datetime.datetime(year=first.year+1, month=first.month, day=first.day)
    return merge_date.strftime('%Y-%m-%d')

def create_vnext_issue(package_name):

    auth = Auth.Token("")
    g = Github(auth=auth)

    today = datetime.datetime.today()
    repo = g.get_repo("kristapratico/python-sdk-typescoring-function")
    issues = repo.get_issues(state="open", labels=["bug"], creator="kristapratico")
    issues_list = [issue for issue in issues if issue.body.find(package_name) != -1]
    mypy_version = get_mypy_version_running()
    build_link = get_build_link()
    merge_date = get_date_for_version_bump(today)

    title = f"{package_name} needs typing updates for mypy version {mypy_version}"
    template = (
        f"**ACTION NEEDED:** This version of mypy will be merged on **{merge_date}**. The build will begin to fail for this library if errors are not fixed."
        f"\n\n**Library name:** {package_name}"
        f"\n**Mypy version:** {mypy_version}"
        f"\n**Mypy errors:** [Link to build ({today.strftime('%Y-%m-%d')})]({build_link})"
        f"\n**How to fix:** Run the `next-mypy` tox command at the library package-level and resolve the typing errors.\n"
        f"1) `../{package_name}>pip install tox<5`\n"
        f"2) `../{package_name}>tox run -e next-mypy -c ../../../eng/tox/tox.ini --root .`\n\n"
        "See the [Typing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md#run-mypy) for more information."
    )

    # create a mypy issue for the library failing the nvext check
    if not issues_list:
        repo.create_issue(
            title=title,
            body=template,
            labels=["bug"]
        )
        return

    # a mypy issue exists, let's update it so it reflects the latest typing errors
    issues_list[0].edit(
        title=title,
        body=template,
    )


create_vnext_issue("azure-ai-formrecognizer")