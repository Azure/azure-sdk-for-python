# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# The idea was to send a newsletter to partner as a table checklist. Each line is a service, each columnd is a requirement (mypy, samples, etc.)
# To make it easier for people to see "what is my status". We could put different colors depending on status criticality (red if you're a month away from being blocked, warning if you have work to do but you have time, etc.)
# And I would want the status email to have a red warning like "CI disabled for lack of compliance" of something like that.
# If we script the generation of that table in MD, we can copy past it straight in an email, I wouldn't want anyone to manually have to write that table
from __future__ import annotations

import os
import argparse
import typing
import requests
import base64
import json
import logging
import requests
import logging
import json
import glob
import pathlib

from ci_tools.environment_exclusions import is_check_enabled, IGNORE_FILTER, IGNORE_PACKAGES, FILTER_EXCLUSIONS

logger = logging.getLogger().setLevel(logging.INFO)

pat = os.environ["HEALTH_SCRIPT_PAT"]
USERNAME = ""
USER_PASS = USERNAME + ":" + pat
B64USERPASS = base64.b64encode(USER_PASS.encode()).decode()

LIBRARY_STATUS = typing.Literal["NEEDS_ACTION", "DISABLED", "GOOD"]
CHECK_STATUS = typing.Literal["PASS", "FAIL", "DISABLED", "UNKNOWN"]

DEVOPS_TASK_STATUS = typing.Literal["abandoned", "canceled", "failed", "skipped", "succeeded", "succeededWithIssues"]
DEVOPS_BUILD_STATUS = typing.Literal["succeeded", "failed", "canceled", "none", "partiallySucceeded"]


class CheckStatus(typing.TypedDict):
    status: DEVOPS_TASK_STATUS
    log: str | None


class TestsWeeklyPipelineResult(typing.TypedDict):
    id: str
    link: str
    multi_library: bool
    result: DEVOPS_BUILD_STATUS
    next_mypy: CheckStatus
    next_pyright: CheckStatus
    next_pylint: CheckStatus
    tests_weekly: CheckStatus


class TestsPipelineResult(typing.TypedDict):
    id: str
    link: str
    multi_library: bool
    result: DEVOPS_BUILD_STATUS
    samples: CheckStatus
    tests: CheckStatus


class CIPipelineResult(typing.TypedDict):
    id: str
    link: str
    multi_library: bool
    result: DEVOPS_BUILD_STATUS
    mypy: CheckStatus
    pyright: CheckStatus
    pylint: CheckStatus
    docs: CheckStatus
    ci: CheckStatus


class LibraryStatus(typing.TypedDict):
    status: LIBRARY_STATUS
    path: str
    mypy: CHECK_STATUS
    next_mypy: CHECK_STATUS
    pyright: CHECK_STATUS
    next_pyright: CHECK_STATUS
    type_check_samples: typing.Literal["ENABLED", "DISABLED"]
    pylint:CHECK_STATUS
    next_pylint: CHECK_STATUS
    docs: CHECK_STATUS
    tests: CHECK_STATUS
    samples: CHECK_STATUS
    ci: CHECK_STATUS
    tests_weekly: CHECK_STATUS
    links: list[str]


def skip_package(package_name: str) -> bool:
    return (not package_name.startswith("azure") and package_name != "corehttp") or package_name in IGNORE_PACKAGES or package_name not in FILTER_EXCLUSIONS and any(identifier in package_name for identifier in IGNORE_FILTER)


def get_dataplane():
    dataplane = {}
    sdk_path = pathlib.Path(__file__).parent.parent.parent / "sdk"
    service_directories = glob.glob(f"{sdk_path}/*/", recursive=True)

    for service in service_directories:
        package_paths = glob.glob(f"{service}*/", recursive=True)
        for package_path in package_paths:
            package_path = pathlib.Path(package_path)
            package_name = package_path.name
            if skip_package(package_name):
                continue
            service_directory = pathlib.Path(service).name
            dataplane.setdefault(service_directory, {})
            dataplane[service_directory][package_name] = {}
            dataplane[service_directory][package_name]["path"] = package_path
    return dataplane


def get_pipelines(dataplane):

    pipelines = requests.get(f"https://dev.azure.com/azure-sdk/internal/_apis/pipelines?api-version=7.1-preview.1", headers={"Authorization": f"Basic {B64USERPASS}"})
    pipelines_json = json.loads(pipelines.text)
    python_pipelines = [
        pipeline for pipeline in pipelines_json["value"] \
            if "python - " in pipeline["name"] \
            and "autorest" not in pipeline["name"] \
            and "update_pr" not in pipeline["name"] \
            and "azure-sdk-for-python" not in pipeline["name"] \
    ]
    pipelines = {}
    for p in python_pipelines:
        pipeline_name = p["name"]
        for service_directory, libraries in dataplane.items():
            pipelines.setdefault(service_directory, {})
            if service_directory == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update({"ci": {"id": p["id"], "multi_library": len(libraries) > 1}})
            if f"{service_directory} - tests" == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update({"tests": {"id": p["id"], "multi_library": len(libraries) > 1}})
            if f"{service_directory} - tests-weekly" == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update({"tests_weekly": {"id": p["id"], "multi_library": len(libraries) > 1}})
    return pipelines



def record_check_result(task, type, pipeline):
    pipeline.update({type: CheckStatus(status=task["result"])})
    if pipeline["multi_library"]:
        pipeline[type]["log"] = task["log"]["url"]


def record_test_result(task, type, pipeline):
    if task["result"] == "succeeded":
        if pipeline.get(type, {}).get("status") is None:
            pipeline.update({type: CheckStatus(status="succeeded")})
    elif task["result"] == "failed":
        pipeline.update({type: CheckStatus(status="failed")})
        if pipeline["multi_library"]:
            pipeline[type]["log"] = task["log"]["url"]
    elif pipeline.get(type, {}).get("status") != "failed":
        pipeline.update({type: CheckStatus(status=task["result"])})
        if pipeline["multi_library"]:
            pipeline[type]["log"] = task["log"]["url"]


def get_ci_result(service, pipeline_id, pipelines):
    build_response = requests.get(f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds?definitions={pipeline_id}&$top=1&queryOrder=finishTimeDescending&reasonFilter=schedule?api-version=7.1-preview.7", headers={"Authorization": f"Basic {B64USERPASS}"})
    build_result = json.loads(build_response.text)
    result = build_result["value"][0]
    pipelines[service]["ci"]["link"] = result["_links"]["web"]["href"]
    if result["result"] == "succeeded":
        # set all checks to pass
        pipelines[service]["ci"].update(
            {
                "result": "succeeded",
                "mypy": CheckStatus(status="succeeded"),
                "pyright": CheckStatus(status="succeeded"),
                "pylint": CheckStatus(status="succeeded"),
                "docs": CheckStatus(status="succeeded"),
                "ci": CheckStatus(status="succeeded"),
            }
        )
        return

    # get timeline
    pipelines[service]["ci"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = requests.get(f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds/{build_id}/Timeline", headers={"Authorization": f"Basic {B64USERPASS}"})
    timeline_result = json.loads(timeline_response.text)

    # TODO if task status anything other than succeeded or failed then set to unknown?
    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "ci", pipelines[service]["ci"])
        elif "Generate Docs" in task["name"]:
            record_check_result(task, "docs", pipelines[service]["ci"])
        elif "Run MyPy" in task["name"]:
            record_check_result(task, "mypy", pipelines[service]["ci"])
        elif "Run Pyright" in task["name"]:
            record_check_result(task, "pyright", pipelines[service]["ci"])
        elif "Run Pylint" in task["name"]:
            record_check_result(task, "pylint", pipelines[service]["ci"])

    print()


def get_tests_result(service, pipeline_id, pipelines):
    build_response = requests.get(f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds?definitions={pipeline_id}&$top=1&queryOrder=finishTimeDescending&reasonFilter=schedule?api-version=7.1-preview.7", headers={"Authorization": f"Basic {B64USERPASS}"})
    build_result = json.loads(build_response.text)
    result = build_result["value"][0]
    pipelines[service]["tests"]["link"] = result["_links"]["web"]["href"]
    if result["result"] == "succeeded":
        # set all checks to pass
        pipelines[service]["tests"].update(
            {
                "result": "succeeded",
                "tests": CheckStatus(status="succeeded"),
            }
        )
        return

    # get timeline
    pipelines[service]["tests"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = requests.get(f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds/{build_id}/Timeline", headers={"Authorization": f"Basic {B64USERPASS}"})
    timeline_result = json.loads(timeline_response.text)

    # TODO if task status anything other than succeeded or failed then set to unknown?
    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "tests", pipelines[service]["tests"])
        elif "Test Samples" in task["name"]:
            record_check_result(task, "samples", pipelines[service]["tests"])


def get_tests_weekly_result(service, pipeline_id, pipelines):
    build_response = requests.get(f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds?definitions={pipeline_id}&$top=1&queryOrder=finishTimeDescending&reasonFilter=schedule?api-version=7.1-preview.7", headers={"Authorization": f"Basic {B64USERPASS}"})
    build_result = json.loads(build_response.text)
    result = build_result["value"][0]
    pipelines[service]["tests_weekly"]["link"] = result["_links"]["web"]["href"]

    # get timeline
    pipelines[service]["tests_weekly"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = requests.get(f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds/{build_id}/Timeline", headers={"Authorization": f"Basic {B64USERPASS}"})
    timeline_result = json.loads(timeline_response.text)

    # TODO if task status anything other than succeeded or failed then set to unknown?
    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "tests_weekly", pipelines[service]["tests_weekly"])
        elif "Run Pylint Next" in task["name"]:
            record_check_result(task, "next_pylint", pipelines[service]["tests_weekly"])
        elif "Run Pyright Next" in task["name"]:
            record_check_result(task, "next_pyright", pipelines[service]["tests_weekly"])
        elif "Run MyPy Next" in task["name"]:
            record_check_result(task, "next_mypy", pipelines[service]["tests_weekly"])


libraries = get_dataplane()
pipelines = get_pipelines(libraries)
for service, pipeline_ids in pipelines.items():
    # TODO need to account for ci_enabled
    get_ci_result(service, pipeline_ids["ci"]["id"], pipelines)
    # get_tests_result(service, pipeline_ids["tests"]["id"], pipelines)
    # get_tests_weekly_result(service, pipeline_ids["tests_weekly"]["id"], pipelines)


# TODO some services will need special parsing for live tests like storage