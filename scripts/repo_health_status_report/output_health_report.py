# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import os
import csv
import typing
import json
import glob
import pathlib
import argparse
import datetime

import httpx
import markdown
from github import Github, Auth
from azure.identity import DefaultAzureCredential

from ci_tools.variables import in_ci
from ci_tools.parsing import ParsedSetup
from ci_tools.environment_exclusions import (
    is_check_enabled,
    IGNORE_FILTER,
    IGNORE_PACKAGES,
    FILTER_EXCLUSIONS,
)
IGNORE_FILTER.append("mgmt")
FILTER_EXCLUSIONS.append("azure-mgmt-core")
IGNORE_PACKAGES.extend(["azure-openai", "azure-eventhub-checkpointstoretable"])

# Github
GIT_TOKEN = os.environ["GH_TOKEN"]
auth = Auth.Token(GIT_TOKEN)
github = Github(auth=auth)
repo = github.get_repo("Azure/azure-sdk-for-python")
health_report_path = pathlib.Path(__file__).parent

# Azure DevOps
if not in_ci():
    DEVOPS_RESOURCE_UUID = "499b84ac-1321-427f-aa17-267ca6975798"
    token = DefaultAzureCredential().get_token(f"{DEVOPS_RESOURCE_UUID}/.default").token
else:
    token =os.environ["SYSTEM_ACCESSTOKEN"]
AUTH_HEADERS = {"Authorization": f"Bearer {token}"}
DEVOPS_TASK_STATUS = typing.Literal[
    "abandoned",
    "canceled",
    "failed",
    "skipped",
    "succeeded",
    "succeededWithIssues",
    "UNKNOWN",
]
DEVOPS_BUILD_STATUS = typing.Literal["succeeded", "failed", "canceled", "none", "partiallySucceeded", "UNKNOWN"]
LIST_BUILDS = "https://dev.azure.com/azure-sdk/internal/_apis/pipelines?api-version=7.0"

# Statuses for table
LIBRARY_STATUS = typing.Literal["NEEDS_ACTION", "BLOCKED", "GOOD"]
CHECK_STATUS = typing.Literal["PASS", "FAIL", "WARNING", "DISABLED", "UNKNOWN"]

NEXT_CHECKS = ("mypy", "pyright", "pylint")
RELEASE_BLOCKERS = (
    "mypy",
    "pylint",
    "pyright",
    "sphinx",
    "ci",
)  # will block release if failing
MANDATORY_CHECKS = (
    "mypy",
    "pylint",
    "sphinx",
    "ci",
)  # must be enabled to be considered GOOD

INACTIVE_CLASSIFIER = "Development Status :: 7 - Inactive"

# Script types
ServiceDirectory = str
LibraryName = str
CheckTypes = typing.Literal["mypy", "pyright", "pylint", "sphinx", "ci", "tests"]


class Status(typing.TypedDict, total=False):
    status: CHECK_STATUS
    link: str | None


class CheckStatus(typing.TypedDict, total=False):
    status: DEVOPS_TASK_STATUS
    log: str | None


class TestsWeeklyPipelineResult(typing.TypedDict, total=False):
    id: int
    link: str
    result: DEVOPS_BUILD_STATUS
    next_mypy: CheckStatus
    next_pyright: CheckStatus
    next_pylint: CheckStatus
    tests_weekly: CheckStatus


class TestsPipelineResult(typing.TypedDict, total=False):
    id: int
    link: str
    result: DEVOPS_BUILD_STATUS
    tests: CheckStatus
    samples: CheckStatus


class CIPipelineResult(typing.TypedDict, total=False):
    id: int
    link: str
    result: DEVOPS_BUILD_STATUS
    mypy: CheckStatus
    pyright: CheckStatus
    pylint: CheckStatus
    sphinx: CheckStatus
    ci: CheckStatus


class PipelineResults(typing.TypedDict, total=False):
    ci: CIPipelineResult
    tests: TestsPipelineResult
    tests_weekly: TestsWeeklyPipelineResult


class SLAStatus(typing.TypedDict, total=False):
    question: IssueDetails
    """open > 30 days"""
    bug: IssueDetails
    """open > 90 days"""


class IssueDetails(typing.TypedDict, total=False):
    num: int
    link: str


class LibraryStatus(typing.TypedDict, total=False):
    status: LIBRARY_STATUS
    path: pathlib.Path
    label: str | None
    sla: SLAStatus | None
    customer_issues: IssueDetails | None
    mypy: Status
    pyright: Status
    type_check_samples: typing.Literal["ENABLED", "DISABLED"]
    pylint: Status
    sphinx: Status
    sdk_owned: bool
    tests: Status
    samples: Status
    ci: Status


PipelineResultsUnion = typing.Union[CIPipelineResult, TestsPipelineResult, TestsWeeklyPipelineResult]


# This script makes the engineering systems assumption that a pipeline exists per service directory.
# Here we have a special exception where communication creates separate pipelines for each package.
# Hardcoding pipeline IDs for now, but if this becomes a common scenario, we should
# consider updating the health report data schema to support this
communication_mapping = {
    "azure-communication-chat": {"ci": {"id": "2047", "link": ""}, "tests": {"id": "2723", "link": ""}, "tests_weekly": {"id": "3721", "link": ""}},
    "azure-communication-phonenumbers": {"ci": {"id": "2047", "link": ""}, "tests": {"id": "2722", "link": ""}, "tests_weekly": {"id": "3732", "link": ""}},
    "azure-communication-email": {"ci": {"id": "2047", "link": ""}, "tests": {"id": "5257", "link": ""}, "tests_weekly": {"id": "5258", "link": ""}},
    "azure-communication-messages": {"ci": {"id": "2047", "link": ""}},
    "azure-communication-sms": {"ci": {"id": "2047", "link": ""}, "tests": {"id": "2724", "link": ""}, "tests_weekly": {"id": "3736", "link": ""}},
    "azure-communication-callautomation": {"ci": {"id": "2047", "link": ""}},
    "azure-communication-identity": {"ci": {"id": "2047", "link": ""}, "tests": {"id": "2725", "link": ""}, "tests_weekly": {"id": "3725", "link": ""}},
    "azure-communication-rooms": {"ci": {"id": "2047", "link": ""}, "tests": {"id": "4716", "link": ""}, "tests_weekly": {"id": "5131", "link": ""}},
    "azure-communication-jobrouter": {"ci": {"id": "2047", "link": ""}},
}


SDK_TEAM_OWNED = [
    "azure-ai-documentintelligence",
    "azure-ai-formrecognizer",
    "azure-appconfiguration",
    "azure-containerregistry",
    "azure-core",
    "azure-mgmt-core",
    "azure-core-experimental",
    "azure-core-tracing-opencensus",
    "azure-core-tracing-opentelemetry",
    "azure-data-tables",
    "azure-eventgrid",
    "azure-eventhub",
    "azure-eventhub-checkpointstoreblob",
    "azure-eventhub-checkpointstoreblob-aio",
    "azure-eventhub-checkpointstoretable",
    "azure-identity",
    "azure-identity-broker",
    "azure-keyvault-administration",
    "azure-keyvault-certificates",
    "azure-keyvault-keys",
    "azure-keyvault-secrets",
    "azure-monitor-ingestion",
    "azure-monitor-query",
    "azure-schemaregistry",
    "azure-schemaregistry-avroencoder",
    "azure-search-documents",
    "azure-servicebus",
    "corehttp",
]


def get_build_url(pipeline_id: int) -> str:
    return f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds?definitions={str(pipeline_id)}&$top=1&queryOrder=finishTimeDescending&reasonFilter=schedule&api-version=7.0"


def get_build_timeline_url(build_id: str) -> str:
    return f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds/{build_id}/Timeline?api-version=7.0"


def get_github_issue_link(label: str, kind: typing.Literal["bug", "question"], created: str) -> str:
    label = label.replace(" ", "+")
    if kind == "question":
        minus = "bug"
    else:
        minus = "question"
    return f"https://github.com/Azure/azure-sdk-for-python/issues?q=is%3Aopen+is%3Aissue+label%3Acustomer-reported+label%3AClient+-label%3Aissue-addressed+-label%3A{minus}+-label%3Aneeds-author-feedback+-label%3Afeature-request+label%3A%22{label}%22+created%3A%22%3C{created}%22"


def get_github_total_issue_link(label: str) -> str:
    label = label.replace(" ", "+")
    return f"https://github.com/Azure/azure-sdk-for-python/issues?q=is%3Aopen+is%3Aissue+label%3Acustomer-reported+label%3AClient+label%3A%22{label}%22"


def is_package_inactive(package_path: str) -> bool:
    setup_py = os.path.join(package_path, "setup.py")
    return not os.path.exists(setup_py) or INACTIVE_CLASSIFIER in ParsedSetup.from_path(package_path).classifiers


def skip_package(package_name: str) -> bool:
    return (
        (not package_name.startswith("azure") and package_name != "corehttp")
        or package_name in IGNORE_PACKAGES
        or package_name not in FILTER_EXCLUSIONS
        and any(identifier in package_name for identifier in IGNORE_FILTER)
    )


def samples_enabled(package_path: pathlib.Path) -> bool:
    tests_yaml = package_path.parent / "tests.yml"
    if not tests_yaml.exists():
        return False
    with open(tests_yaml, "r") as file:
        parameters = file.read()

    if "TestSamples=.*/true" in parameters:
        return True
    return False


def get_dataplane(
    include_sdk_owned: bool = True,
) -> dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]:
    dataplane: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]] = {}
    sdk_path = pathlib.Path(__file__).parent.parent.parent / "sdk"
    service_directories = glob.glob(f"{sdk_path}/*/", recursive=True)

    for service in service_directories:
        package_paths = glob.glob(f"{service}*/", recursive=True)
        for pkg_path in package_paths:
            package_path = pathlib.Path(pkg_path)
            package_name = package_path.name
            if (
                skip_package(package_name)
                or is_package_inactive(str(package_path))
                or (package_name in SDK_TEAM_OWNED and not include_sdk_owned)
            ):
                continue
            service_directory = pathlib.Path(service).name
            dataplane.setdefault(service_directory, {})
            dataplane[service_directory][package_name] = LibraryStatus(path=package_path)

    sorted_libs = {key: dataplane[key] for key in sorted(dataplane)}
    return sorted_libs


def get_pipelines(
    dataplane: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]
) -> dict[ServiceDirectory, PipelineResults]:

    response = httpx.get(LIST_BUILDS, headers=AUTH_HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to get pipelines - {response.status_code} {response.text}")
    pipelines_json = json.loads(response.text)
    python_pipelines = [
        pipeline
        for pipeline in pipelines_json["value"]
        if "python - " in pipeline["name"]
        and "autorest" not in pipeline["name"]
        and "update_pr" not in pipeline["name"]
        and "azure-sdk-for-python" not in pipeline["name"]
    ]
    pipelines: dict[ServiceDirectory, PipelineResults] = {}
    for p in python_pipelines:
        pipeline_name = p["name"]
        for service_directory, _ in dataplane.items():
            pipelines.setdefault(service_directory, {})
            if service_directory == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update(PipelineResults(ci=CIPipelineResult(id=p["id"], link="")))
                record_all_pipeline("ci", pipelines[service_directory], "UNKNOWN")
            if f"{service_directory} - tests" == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update(PipelineResults(tests=TestsPipelineResult(id=p["id"], link="")))
                record_all_pipeline("tests", pipelines[service_directory], "UNKNOWN")
            if f"{service_directory} - tests-weekly" == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update(
                    PipelineResults(tests_weekly=TestsWeeklyPipelineResult(id=p["id"], link=""))
                )
                record_all_pipeline("tests_weekly", pipelines[service_directory], "UNKNOWN")
    return pipelines


def record_check_result(task: dict[str, str], type: str, pipeline: PipelineResultsUnion):
    pipeline.update({type: CheckStatus(status=task["result"])})
    if task["log"]:
        pipeline[type]["log"] = task["log"].get("url")


def record_test_result(
    task: dict,
    type: typing.Literal["ci", "tests", "tests_weekly"],
    pipeline: CIPipelineResult | TestsPipelineResult | TestsWeeklyPipelineResult,
) -> None:
    unsuccessful = ["failed", "canceled", "abandoned", "skipped", "succeededWithIssues"]
    if task["result"] == "succeeded":
        if pipeline.get(type, {}).get("status") not in unsuccessful:
            pipeline.update({type: CheckStatus(status="succeeded")})
    elif task["result"] == "failed":
        pipeline.update({type: CheckStatus(status="failed")})
        if task["log"]:
            pipeline[type]["log"] = task["log"].get("url")
    elif pipeline.get(type, {}).get("status") != "failed":
        pipeline.update({type: CheckStatus(status=task["result"])})
        if task["log"]:
            pipeline[type]["log"] = task["log"].get("url")


def record_all_pipeline(
    task: typing.Literal["ci", "tests", "tests_weekly"],
    pipeline: PipelineResults,
    status: typing.Literal["succeeded", "UNKNOWN"],
) -> None:
    if task == "ci":
        pipeline.setdefault("ci", {})
        pipeline["ci"].update(
            CIPipelineResult(
                {
                    "result": status,
                    "mypy": CheckStatus(status=status),
                    "pyright": CheckStatus(status=status),
                    "pylint": CheckStatus(status=status),
                    "sphinx": CheckStatus(status=status),
                    "ci": CheckStatus(status=status),
                }
            )
        )
    elif task == "tests":
        pipeline.setdefault("tests", {})
        pipeline["tests"].update(
            TestsPipelineResult(
                {
                    "result": status,
                    "tests": CheckStatus(status=status),
                    "samples": CheckStatus(status=status),
                }
            )
        )
    elif task == "tests_weekly":
        pipeline.setdefault("tests_weekly", {})
        pipeline["tests_weekly"].update(
            TestsWeeklyPipelineResult(
                {
                    "result": status,
                    "next_mypy": CheckStatus(status=status),
                    "next_pyright": CheckStatus(status=status),
                    "next_pylint": CheckStatus(status=status),
                    "tests_weekly": CheckStatus(status=status),
                }
            )
        )


def record_all_library(details: LibraryStatus, status: CHECK_STATUS) -> None:
    details["mypy"] = Status(status=status, link=None)
    details["pyright"] = Status(status=status, link=None)
    details["type_check_samples"] = (
        "ENABLED"
        if is_check_enabled(str(details["path"]), "type_check_samples") and details["status"] != "BLOCKED"
        else "DISABLED"
    )
    details["sdk_owned"] = details["path"].name in SDK_TEAM_OWNED
    details["pylint"] = Status(status=status, link=None)
    details["sphinx"] = Status(status=status, link=None)
    details["ci"] = Status(status=status, link=None)
    details["tests"] = Status(status=status, link=None)
    details["samples"] = Status(status=status, link=None)

def get_ci_result(service: str, pipeline_id: int | None, pipelines: dict[ServiceDirectory, PipelineResults]) -> None:
    if not pipeline_id:
        print(f"No CI result for {service}")
        record_all_pipeline("ci", pipelines[service], "UNKNOWN")
        pipelines[service]["ci"]["link"] = ""
        return

    build_response = httpx.get(get_build_url(pipeline_id), headers=AUTH_HEADERS)
    build_result = json.loads(build_response.text)
    if build_response.status_code != 200 or not build_result["value"]:
        print(f"No CI result for {service}")
        record_all_pipeline("ci", pipelines[service], "UNKNOWN")
        return

    result = build_result["value"][0]
    pipelines[service]["ci"]["link"] = result["_links"]["web"]["href"]
    if result["result"] == "succeeded":
        # set all checks to pass
        record_all_pipeline("ci", pipelines[service], "succeeded")
        return

    # get timeline
    pipelines[service]["ci"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = httpx.get(get_build_timeline_url(build_id), headers=AUTH_HEADERS)
    if timeline_response.status_code != 200:
        record_all_pipeline("tests", pipelines[service], "UNKNOWN")
        return
    timeline_result = json.loads(timeline_response.text)

    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "ci", pipelines[service]["ci"])
        elif "Generate Docs" in task["name"]:
            record_check_result(task, "sphinx", pipelines[service]["ci"])
        elif "Run MyPy" in task["name"]:
            record_check_result(task, "mypy", pipelines[service]["ci"])
        elif "Run Pyright" in task["name"]:
            record_check_result(task, "pyright", pipelines[service]["ci"])
        elif "Run Pylint" in task["name"]:
            record_check_result(task, "pylint", pipelines[service]["ci"])


def get_tests_result(service: str, pipeline_id: int | None, pipelines: dict[ServiceDirectory, PipelineResults]) -> None:
    if not pipeline_id:
        print(f"No live tests result for {service}")
        record_all_pipeline("tests", pipelines[service], "UNKNOWN")
        pipelines[service]["tests"]["link"] = ""
        return

    build_response = httpx.get(get_build_url(pipeline_id), headers=AUTH_HEADERS)
    build_result = json.loads(build_response.text)
    if build_response.status_code != 200 or not build_result["value"]:
        print(f"No live tests result for {service}")
        record_all_pipeline("tests", pipelines[service], "UNKNOWN")
        return

    result = build_result["value"][0]
    pipelines[service]["tests"]["link"] = result["_links"]["web"]["href"]
    if result["result"] == "succeeded":
        # set all checks to pass
        record_all_pipeline("tests", pipelines[service], "succeeded")
        return

    # get timeline
    pipelines[service]["tests"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = httpx.get(get_build_timeline_url(build_id), headers=AUTH_HEADERS)
    if timeline_response.status_code != 200:
        record_all_pipeline("tests", pipelines[service], "UNKNOWN")
        return
    timeline_result = json.loads(timeline_response.text)

    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "tests", pipelines[service]["tests"])
        if "Test Samples" in task["name"]:
            record_test_result(task, "samples", pipelines[service]["tests"])


def get_tests_weekly_result(service: str, pipeline_id: int | None, pipelines: dict[ServiceDirectory, PipelineResults]) -> None:
    if not pipeline_id:
        print(f"No tests_weekly result for {service}")
        record_all_pipeline("tests_weekly", pipelines[service], "UNKNOWN")
        pipelines[service]["tests_weekly"]["link"] = ""
        return

    build_response = httpx.get(get_build_url(pipeline_id), headers=AUTH_HEADERS)
    build_result = json.loads(build_response.text)
    if build_response.status_code != 200 or not build_result["value"]:
        print(f"No tests_weekly result for {service}")
        record_all_pipeline("tests_weekly", pipelines[service], "UNKNOWN")
        return

    result = build_result["value"][0]
    pipelines[service]["tests_weekly"]["link"] = result["_links"]["web"]["href"]

    # get timeline
    pipelines[service]["tests_weekly"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = httpx.get(get_build_timeline_url(build_id), headers=AUTH_HEADERS)
    if timeline_response.status_code != 200:
        record_all_pipeline("tests", pipelines[service], "UNKNOWN")
        return
    timeline_result = json.loads(timeline_response.text)

    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "tests_weekly", pipelines[service]["tests_weekly"])
        elif "Run Pylint Next" in task["name"]:
            record_check_result(task, "next_pylint", pipelines[service]["tests_weekly"])
        elif "Run Pyright Next" in task["name"]:
            record_check_result(task, "next_pyright", pipelines[service]["tests_weekly"])
        elif "Run MyPy Next" in task["name"]:
            record_check_result(task, "next_mypy", pipelines[service]["tests_weekly"])


def report_overall_status(library_details: LibraryStatus) -> None:
    """Status is based on if anything is blocking release
    or could block release in the near future.
    """
    overall_status = "GOOD"
    for check, status in library_details.items():
        if check not in RELEASE_BLOCKERS:
            continue
        if status["status"] == "FAIL":
            overall_status = "BLOCKED"
            break
        if status["status"] in ["DISABLED", "WARNING", "UNKNOWN"] and check in MANDATORY_CHECKS:
            overall_status = "NEEDS_ACTION"
        if check == "pyright" and status["status"] in ["WARNING", "UNKNOWN"]:
            # special case for pyright which is not mandatory, but action is needed
            # if library has enabled it and its status is warning or unknown
            overall_status = "NEEDS_ACTION"
    library_details["status"] = overall_status


def report_test_result(
    test_type: typing.Literal["ci", "tests"],
    pipeline: PipelineResults,
    library_details: LibraryStatus,
) -> None:
    test_status = pipeline[test_type][test_type]["status"]
    if test_status in ["succeeded", "partiallySucceeded"]:
        library_details[test_type] = Status(status="PASS", link=pipeline[test_type]["link"])
    elif test_status == "failed":
        library_details[test_type] = Status(status="FAIL", link=pipeline[test_type]["link"])
    else:
        library_details[test_type] = Status(status="UNKNOWN", link=pipeline[test_type].get("link"))


def report_samples_result(
    check: typing.Literal["samples"],
    pipeline: PipelineResults,
    library_details: LibraryStatus, 
) -> None:
    enabled = samples_enabled(library_details["path"])
    if not enabled:
        library_details[check] = Status(status="DISABLED", link=None)
        return

    ci_check = pipeline["tests"][check]["status"]
    if ci_check == "succeeded":
        library_details[check] = Status(status="PASS", link=pipeline["tests"]["link"])
    elif ci_check == "failed":
        library_details[check] = Status(status="FAIL", link=pipeline["tests"]["link"])
    else:
        library_details[check] = Status(status="UNKNOWN", link=pipeline["tests"].get("link"))


def report_check_result(
    check: CheckTypes,
    pipeline: PipelineResults,
    library_details: LibraryStatus,
) -> None:
    enabled = is_check_enabled(str(library_details["path"]), check)
    if not enabled:
        library_details[check] = Status(status="DISABLED", link=None)
        return

    if check in NEXT_CHECKS:
        ci_check = pipeline["ci"][check]["status"]
        next_check = pipeline["tests_weekly"][f"next_{check}"]["status"]
        if ci_check == "succeeded" and next_check == "succeeded":
            library_details[check] = Status(status="PASS", link=pipeline["ci"]["link"])
        elif ci_check == "succeeded" and next_check in [
            "succeededWithIssues",
            "UNKNOWN",
        ]:
            library_details[check] = Status(status="WARNING", link=pipeline["tests_weekly"].get("link"))

        elif ci_check == "failed":
            library_details[check] = Status(status="FAIL", link=pipeline["ci"]["link"])
        else:
            library_details[check] = Status(status="UNKNOWN", link=pipeline["ci"].get("link"))
    else:
        ci_check = pipeline["ci"][check]["status"]
        if ci_check == "succeeded":
            library_details[check] = Status(status="PASS", link=pipeline["ci"]["link"])
        elif ci_check == "failed":
            library_details[check] = Status(status="FAIL", link=pipeline["ci"]["link"])
        else:
            library_details[check] = Status(status="UNKNOWN", link=pipeline["ci"].get("link"))


def report_status(
    dataplane: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]],
    pipelines: dict[ServiceDirectory, PipelineResults],
) -> None:
    for service_directory, libraries in dataplane.items():
        for _, details in libraries.items():
            if not is_check_enabled(str(details["path"]), "ci_enabled"):
                details["status"] = "BLOCKED"
                record_all_library(details, "DISABLED")
                continue
            report_check_result("mypy", pipelines[service_directory], details)
            report_check_result("pylint", pipelines[service_directory], details)
            report_check_result("pyright", pipelines[service_directory], details)
            report_check_result("sphinx", pipelines[service_directory], details)
            details["type_check_samples"] = (
                "ENABLED" if is_check_enabled(str(details["path"]), "type_check_samples") else "DISABLED"
            )
            report_samples_result("samples", pipelines[service_directory], details)
            details["sdk_owned"] = details["path"].name in SDK_TEAM_OWNED
            report_test_result("tests", pipelines[service_directory], details)
            report_test_result("ci", pipelines[service_directory], details)
            report_overall_status(details)


def map_codeowners_to_label(
    dataplane: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]
) -> dict[str, ServiceDirectory]:
    codeowners_url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/.github/CODEOWNERS"
    codeowners_response = httpx.get(codeowners_url)
    if codeowners_response.status_code != 200:
        raise Exception("Failed to get CODEOWNERS file")
    codeowners = codeowners_response.text.splitlines()

    tracked_labels = {}
    label = ""
    for line in codeowners:
        if line.startswith("# PRLabel:"):
            label = line.split("# PRLabel: %")[1].strip()
        if label and line.startswith("/sdk/"):
            parts = line.split("@")[0].split("/")[2:-1]
            if len(parts) > 3:
                # we don't distinguish past package level for SLA
                continue
            try:
                service_directory = parts[0]
            except IndexError:
                # it was a single file
                continue
            tracked_labels[label] = service_directory
            try:
                library = parts[1]
            except IndexError:
                library = None

            if library:
                try:
                    service = dataplane[service_directory]
                except KeyError:
                    continue
                try:
                    service[library]["label"] = label
                except KeyError:
                    continue
                continue
            try:
                service = dataplane[service_directory]
                for _, details in service.items():
                    if details.get("label") is None:
                        details["label"] = label
            except KeyError:
                continue
    return tracked_labels


def record_total_customer_reported_issues(
    libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]],
    tracked_labels: dict[str, ServiceDirectory],
    issues: list[object],
) -> None:
    for issue in issues:
        for lbl in issue.labels:
            if lbl.name in tracked_labels:
                service_directory = tracked_labels[lbl.name]
                applicable = libraries.get(service_directory, None)
                if not applicable:
                    continue
                for _, details in applicable.items():
                    if lbl.name == details["label"]:
                        details.setdefault("customer_issues", {})
                        details["customer_issues"].setdefault("num", 0)
                        details["customer_issues"]["num"] += 1
                        details["customer_issues"]["link"] = get_github_total_issue_link(lbl.name)


def record_sla_status(
    libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]],
    issue: object,
    tracked_labels: dict[str, ServiceDirectory],
    kind: typing.Literal["question", "bug"],
    time_period: datetime.datetime,
) -> None:
    for lbl in issue.labels:
        if lbl.name in tracked_labels:
            service_directory = tracked_labels[lbl.name]
            applicable = libraries.get(service_directory, None)
            if not applicable:
                return
            for _, details in applicable.items():
                if lbl.name == details["label"]:
                    details.setdefault("sla", {})
                    details["sla"].setdefault(
                        kind,
                        {"num": 0, "link": get_github_issue_link(lbl.name, kind, str(time_period.date()))},
                    )
                    details["sla"][kind]["num"] += 1


def report_sla_and_total_issues(
    libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]],
) -> None:

    tracked_labels = map_codeowners_to_label(libraries)
    today = datetime.datetime.now(datetime.UTC)
    filter_labels = ["issue-addressed", "needs-author-feedback", "feature-request"]
    issues = list(repo.get_issues(state="open", labels=["customer-reported", "Client"]))
    record_total_customer_reported_issues(libraries, tracked_labels, issues)
    filtered = [issue for issue in issues if not any(label for label in issue.labels if label.name in filter_labels)]

    thirty_days_ago = today - datetime.timedelta(days=30)
    ninety_days_ago = today - datetime.timedelta(days=90)
    for issue in filtered:
        if "question" in (label.name for label in issue.labels) and issue.created_at < thirty_days_ago:
            record_sla_status(libraries, issue, tracked_labels, "question", thirty_days_ago)
        if "bug" in (label.name for label in issue.labels) and issue.created_at < ninety_days_ago:
            record_sla_status(libraries, issue, tracked_labels, "bug", ninety_days_ago)


def write_to_csv(libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]) -> None:
    with open(health_report_path / "health_report.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        column_names = [
            "Library",
            "Status",
            "Mypy",
            "Pyright",
            "Type Checked Samples",
            "Pylint",
            "Sphinx",
            "Tests - CI",
            "Tests - Live",
            "Tests - Samples",
            "SLA - Questions",
            "SLA - Bugs",
            "Total customer-reported issues",
            "Mypy_link",
            "Pyright_link",
            "Pylint_link",
            "Sphinx_link",
            "Tests - CI_link",
            "Tests - Live_link",
            "Tests - Samples_link",
            "SLA - Questions_link",
            "SLA - Bugs_link",
            "Total customer-reported issues_link",
            "Last Refresh",
            "SDK Owned",
        ]
        writer.writerow(column_names)

        rows = []
        for _, libs in libraries.items():
            for library, details in libs.items():
                rows.append(
                    [
                        library,
                        details["status"],
                        details["mypy"]["status"],
                        details["pyright"]["status"],
                        details["type_check_samples"],
                        details["pylint"]["status"],
                        details["sphinx"]["status"],
                        details["ci"]["status"],
                        details["tests"]["status"],
                        details["samples"]["status"],
                        details.get("sla", {}).get("question", {}).get("num", 0),
                        details.get("sla", {}).get("bug", {}).get("num", 0),
                        details.get("customer_issues", {}).get("num", 0),
                        details["mypy"].get("link", ""),
                        details["pyright"].get("link", ""),
                        details["pylint"].get("link", ""),
                        details["sphinx"].get("link", ""),
                        details["ci"].get("link", ""),
                        details["tests"].get("link", ""),
                        details["samples"].get("link", ""),
                        details.get("sla", {}).get("question", {}).get("link", ""),
                        details.get("sla", {}).get("bug", {}).get("link", ""),
                        details.get("customer_issues", {}).get("link", ""),
                        datetime.datetime.today().strftime("%m-%d-%Y %H:%M:%S"),
                        details["sdk_owned"],
                    ]
                )
        sorted_rows = sorted(rows)
        writer.writerows(sorted_rows)


def write_to_markdown(libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]) -> None:

    rows = []
    column_names = [
        "Library",
        "Status",
        "Mypy",
        "Pyright",
        "Type Checked Samples",
        "Pylint",
        "Sphinx",
        "Tests - CI",
        "Tests - Live",
        "Tests - Samples",
        "SLA - Questions / Bugs",
        "Total customer-reported issues",
    ]
    for _, libs in libraries.items():
        for library, details in libs.items():
            if details["status"] == "BLOCKED":
                status_colored = f'<span style="color: red;">{details["status"]}</span>'
            elif details["status"] == "NEEDS_ACTION":
                status_colored = f'<span style="color: orange;">{details["status"]}</span>'
            elif details["status"] == "GOOD":
                status_colored = f'<span style="color: green;">{details["status"]}</span>'

            sla = details.get("sla")
            if sla:
                question_link = (
                    f"([link]({sla.get('question', {}).get('link', None)}))"
                    if sla.get("question", {}).get("link", None) is not None
                    else ""
                )
                bug_link = (
                    f"([link]({sla.get('bug', {}).get('link', None)}))"
                    if sla.get("bug", {}).get("link", None) is not None
                    else ""
                )
                sla_str = f"{sla.get('question', {}).get('num', 0)} {question_link} / {sla.get('bug', {}).get('num', 0)} {bug_link}"
            else:
                sla_str = "0 / 0"

            row = [
                library,
                status_colored,
                details["mypy"]["status"]
                + (f" ([link]({details['mypy']['link']}))" if details["mypy"]["link"] is not None else ""),
                details["pyright"]["status"]
                + (f" ([link]({details['pyright']['link']}))" if details["pyright"]["link"] is not None else ""),
                details["type_check_samples"],
                details["pylint"]["status"]
                + (f" ([link]({details['pylint']['link']}))" if details["pylint"]["link"] is not None else ""),
                details["sphinx"]["status"]
                + (f" ([link]({details['sphinx']['link']}))" if details["sphinx"]["link"] is not None else ""),
                details["ci"]["status"]
                + (f" ([link]({details['ci']['link']}))" if details["ci"]["link"] is not None else ""),
                details["tests"]["status"]
                + (f" ([link]({details['tests']['link']}))" if details["tests"]["link"] is not None else ""),
                details["samples"]["status"]
                + (f" ([link]({details['samples']['link']}))" if details["samples"]["link"] is not None else ""),
                sla_str,
                str(details.get("customer_issues", {}).get("num", 0))
                + (
                    f" ([link]({details.get('customer_issues', {}).get('link', '')}))"
                    if details.get('customer_issues', {}).get('link', None) is not None
                    else ""
                ),
            ]
            rows.append(row)

    with open(health_report_path / "health_report.md", mode="w", newline="", encoding="utf-8") as file:

        file.write("|" + "|".join(column_names) + "|\n")
        file.write("|" + "---|" * len(column_names) + "\n")

        for row in sorted(rows):
            row_str = [str(item).strip() for item in row]
            file.write("|" + "|".join(row_str) + "|\n")


def write_to_html(libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]) -> None:
    write_to_markdown(libraries)
    with open(health_report_path / "health_report.md", "r", encoding="utf-8") as f:
        markd = f.read()

    html = markdown.markdown(markd, extensions=["tables"])

    css_styles = """
    <style>
    table {
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid black;
        padding: 8px;
    }
    </style>
    """

    html_with_css = css_styles + html

    with open(health_report_path / "health_report.html", "w", encoding="utf-8") as file:
        file.write(html_with_css)


def handle_special_case(service_directory: str, special_case_mapping: dict[str, typing.Any]) -> None:
    """This script makes the engineering systems assumption that a pipeline exists per service directory.
    For special exceptions where a pipeline was created per library, we need to handle things separately for now.
    """
    for library, pipeline_map in special_case_mapping.items():
        record_all_pipeline("ci", pipelines[service_directory], "UNKNOWN")
        record_all_pipeline("tests", pipelines[service_directory], "UNKNOWN")
        record_all_pipeline("tests_weekly", pipelines[service_directory], "UNKNOWN")
        get_ci_result(service_directory, pipeline_map.get("ci", {}).get("id"), pipelines)
        get_tests_result(service_directory, pipeline_map.get("tests", {}).get("id"), pipelines)
        get_tests_weekly_result(service_directory, pipeline_map.get("tests_weekly", {}).get("id"), pipelines)

        details = libraries[service_directory][library]
        if not is_check_enabled(str(details["path"]), "ci_enabled"):
            details["status"] = "BLOCKED"
            record_all_library(details, "DISABLED")
            continue
        report_check_result("mypy", pipelines[service_directory], details)
        report_check_result("pylint", pipelines[service_directory], details)
        report_check_result("pyright", pipelines[service_directory], details)
        report_check_result("sphinx", pipelines[service_directory], details)
        details["type_check_samples"] = (
            "ENABLED" if is_check_enabled(str(details["path"]), "type_check_samples") else "DISABLED"
        )
        report_samples_result("samples", pipelines[service_directory], details)
        details["sdk_owned"] = details["path"].name in SDK_TEAM_OWNED
        report_test_result("tests", pipelines[service_directory], details)
        report_test_result("ci", pipelines[service_directory], details)
        report_overall_status(details)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Report the health status for the Python SDK repo.")

    parser.add_argument(
        "-s",
        "--include-sdk-owned",
        dest="include_sdk_owned",
        help="Include SDK team owned libraries in the report. Defaults to True.",
        action="store_false",
    )

    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        help="Which format to output the result. Possible values: csv, md, html. Defaults to csv.",
        type=str,
        default="csv",
    )

    args = parser.parse_args()

    libraries = get_dataplane(include_sdk_owned=args.include_sdk_owned)
    pipelines = get_pipelines(libraries)
    for service, pipeline_ids in pipelines.items():
        get_ci_result(service, pipeline_ids.get("ci", {}).get("id"), pipelines)
        get_tests_result(service, pipeline_ids.get("tests", {}).get("id"), pipelines)
        get_tests_weekly_result(service, pipeline_ids.get("tests_weekly", {}).get("id"), pipelines)

    report_status(libraries, pipelines)
    handle_special_case(service_directory="communication", special_case_mapping=communication_mapping)
    report_sla_and_total_issues(libraries)

    if args.format == "csv":
        write_to_csv(libraries)
    elif args.format == "md":
        write_to_markdown(libraries)
    elif args.format == "html":
        write_to_html(libraries)

    if in_ci():
        path = "scripts/repo_health_status_report/health_report.csv"
        content = repo.get_contents(path, ref="python-sdk-health-report")
        repo.update_file(
            path=path,
            message="Update health report",
            content=open(path, "rb").read(),
            branch="python-sdk-health-report",
            sha=content.sha
        )
