# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import os
import csv
import typing
import base64
import json
import glob
import pathlib

import requests
import markdown

from ci_tools.parsing import ParsedSetup
from ci_tools.environment_exclusions import (
    is_check_enabled,
    IGNORE_FILTER,
    IGNORE_PACKAGES,
    FILTER_EXCLUSIONS,
)

# Azure DevOps
PAT = f":{os.environ["HEALTH_SCRIPT_PAT"]}"
ADO_TOKEN = base64.b64encode(PAT.encode()).decode()
AUTH_HEADERS = {"Authorization": f"Basic {ADO_TOKEN}"}
DEVOPS_TASK_STATUS = typing.Literal[
    "abandoned",
    "canceled",
    "failed",
    "skipped",
    "succeeded",
    "succeededWithIssues",
    "UNKNOWN",
]
DEVOPS_BUILD_STATUS = typing.Literal[
    "succeeded", "failed", "canceled", "none", "partiallySucceeded"
]
LIST_BUILDS = "https://dev.azure.com/azure-sdk/internal/_apis/pipelines?api-version=7.0"


def get_build_url(pipeline_id):
    return f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds?definitions={pipeline_id}&$top=1&queryOrder=finishTimeDescending&reasonFilter=schedule&api-version=7.0"


def get_build_timeline_url(build_id):
    return f"https://dev.azure.com/azure-sdk/internal/_apis/build/builds/{build_id}/Timeline?api-version=7.0"


# Statuses for table
LIBRARY_STATUS = typing.Literal["NEEDS_ACTION", "DISABLED", "GOOD"]
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

ServiceDirectory = str
LibraryName = str
CheckTypes = typing.Literal["mypy", "pyright", "pylint", "sphinx", "ci", "tests"]


class Status(typing.TypedDict):
    status: LIBRARY_STATUS
    link: str | None


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
    tests: CheckStatus


class CIPipelineResult(typing.TypedDict):
    id: str
    link: str
    multi_library: bool
    result: DEVOPS_BUILD_STATUS
    mypy: CheckStatus
    pyright: CheckStatus
    pylint: CheckStatus
    sphinx: CheckStatus
    ci: CheckStatus


class LibraryStatus(typing.TypedDict):
    status: LIBRARY_STATUS
    path: pathlib.Path
    mypy: Status
    pyright: Status
    type_check_samples: typing.Literal["ENABLED", "DISABLED"]
    pylint: Status
    sphinx: Status
    tests: Status
    ci: Status


PipelineResults = typing.Union[
    CIPipelineResult, TestsPipelineResult, TestsWeeklyPipelineResult
]


def is_package_inactive(package_path: str) -> bool:
    return INACTIVE_CLASSIFIER in ParsedSetup.from_path(package_path).classifiers


def skip_package(package_name: str) -> bool:
    return (
        (not package_name.startswith("azure") and package_name != "corehttp")
        or package_name in IGNORE_PACKAGES
        or package_name not in FILTER_EXCLUSIONS
        and any(identifier in package_name for identifier in IGNORE_FILTER)
    )


def get_dataplane() -> dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]:
    dataplane: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]] = {}
    sdk_path = pathlib.Path(__file__).parent.parent.parent / "sdk"
    service_directories = glob.glob(f"{sdk_path}/*/", recursive=True)

    for service in service_directories:
        package_paths = glob.glob(f"{service}*/", recursive=True)
        for pkg_path in package_paths:
            package_path = pathlib.Path(pkg_path)
            package_name = package_path.name
            if skip_package(package_name) or is_package_inactive(str(package_path)):
                continue
            service_directory = pathlib.Path(service).name
            dataplane.setdefault(service_directory, {})
            dataplane[service_directory][package_name] = LibraryStatus(
                path=package_path
            )
    return dataplane


def get_pipelines(
    dataplane: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]
) -> dict[ServiceDirectory, PipelineResults]:

    pipelines = requests.get(LIST_BUILDS, headers=AUTH_HEADERS)
    pipelines_json = json.loads(pipelines.text)
    python_pipelines = [
        pipeline
        for pipeline in pipelines_json["value"]
        if "python - " in pipeline["name"]
        and "autorest" not in pipeline["name"]
        and "update_pr" not in pipeline["name"]
        and "azure-sdk-for-python" not in pipeline["name"]
    ]
    pipelines = {}
    for p in python_pipelines:
        pipeline_name = p["name"]
        for service_directory, libraries in dataplane.items():
            pipelines.setdefault(service_directory, {})
            if service_directory == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update(
                    CIPipelineResult(
                        ci={
                            "id": p["id"],
                            "multi_library": len(libraries) > 1,
                            "link": "",
                            "result": "UNKNOWN",
                            "ci": CheckStatus(status="UNKNOWN"),
                            "mypy": CheckStatus(status="UNKNOWN"),
                            "pyright": CheckStatus(status="UNKNOWN"),
                            "pylint": CheckStatus(status="UNKNOWN"),
                            "sphinx": CheckStatus(status="UNKNOWN"),
                        }
                    )
                )
            if f"{service_directory} - tests" == pipeline_name.split("python - ")[1]:
                pipelines[service_directory].update(
                    TestsPipelineResult(
                        tests={
                            "id": p["id"],
                            "multi_library": len(libraries) > 1,
                            "link": "",
                            "result": "UNKNOWN",
                            "tests": CheckStatus(status="UNKNOWN"),
                        }
                    )
                )
            if (
                f"{service_directory} - tests-weekly"
                == pipeline_name.split("python - ")[1]
            ):
                pipelines[service_directory].update(
                    TestsWeeklyPipelineResult(
                        tests_weekly={
                            "id": p["id"],
                            "multi_library": len(libraries) > 1,
                            "link": "",
                            "result": "UNKNOWN",
                            "next_mypy": CheckStatus(status="UNKNOWN"),
                            "next_pyright": CheckStatus(status="UNKNOWN"),
                            "next_pylint": CheckStatus(status="UNKNOWN"),
                            "tests_weekly": CheckStatus(status="UNKNOWN"),
                        }
                    )
                )
    return pipelines


def record_check_result(task: dict, type: CheckTypes, pipeline: PipelineResults):
    pipeline.update({type: CheckStatus(status=task["result"])})
    if pipeline["multi_library"]:
        pipeline[type]["log"] = task["log"]["url"]


def record_test_result(
    task: dict,
    type: typing.Literal["ci", "tests"],
    pipeline: CIPipelineResult | TestsPipelineResult,
) -> None:
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


def record_all(
    task: typing.Literal["ci", "tests", "tests_weekly"],
    pipeline: CIPipelineResult | TestsPipelineResult | TestsWeeklyPipelineResult,
    status: typing.Literal["succeeded", "UNKNOWN"],
) -> None:
    if task == "ci":
        pipeline.setdefault("ci", {})
        pipeline["ci"].update(
            {
                "result": status,
                "mypy": CheckStatus(status=status),
                "pyright": CheckStatus(status=status),
                "pylint": CheckStatus(status=status),
                "sphinx": CheckStatus(status=status),
                "ci": CheckStatus(status=status),
            }
        )
    elif task == "tests":
        pipeline.setdefault("tests", {})
        pipeline["tests"].update(
            {
                "result": status,
                "tests": CheckStatus(status=status),
            }
        )
    elif task == "tests_weekly":
        pipeline.setdefault("tests_weekly", {})
        pipeline["tests_weekly"].update(
            {
                "result": status,
                "next_mypy": CheckStatus(status=status),
                "next_pyright": CheckStatus(status=status),
                "next_pylint": CheckStatus(status=status),
                "tests_weekly": CheckStatus(status=status),
            }
        )


def get_ci_result(
    service: str, pipeline_id: int, pipelines: dict[ServiceDirectory, PipelineResults]
) -> None:
    if not pipeline_id:
        print(f"No CI result for {service}")
        record_all("ci", pipelines[service], "UNKNOWN")
        return

    build_response = requests.get(get_build_url(pipeline_id), headers=AUTH_HEADERS)
    build_result = json.loads(build_response.text)
    if build_response.status_code != 200 or not build_result["value"]:
        print(f"No CI result for {service}")
        record_all("ci", pipelines[service], "UNKNOWN")
        return

    result = build_result["value"][0]
    pipelines[service]["ci"]["link"] = result["_links"]["web"]["href"]
    if result["result"] == "succeeded":
        # set all checks to pass
        record_all("ci", pipelines[service], "succeeded")
        return

    # get timeline
    pipelines[service]["ci"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = requests.get(
        get_build_timeline_url(build_id), headers=AUTH_HEADERS
    )
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


def get_tests_result(
    service: str, pipeline_id: int, pipelines: dict[ServiceDirectory, PipelineResults]
) -> None:
    if not pipeline_id:
        print(f"No live tests result for {service}")
        record_all("tests", pipelines[service], "UNKNOWN")
        return

    build_response = requests.get(get_build_url(pipeline_id), headers=AUTH_HEADERS)
    build_result = json.loads(build_response.text)
    if build_response.status_code != 200 or not build_result["value"]:
        print(f"No live tests result for {service}")
        record_all("tests", pipelines[service], "UNKNOWN")
        return

    result = build_result["value"][0]
    pipelines[service]["tests"]["link"] = result["_links"]["web"]["href"]
    if result["result"] == "succeeded":
        # set all checks to pass
        record_all("tests", pipelines[service], "succeeded")
        return

    # get timeline
    pipelines[service]["tests"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = requests.get(
        get_build_timeline_url(build_id), headers=AUTH_HEADERS
    )
    timeline_result = json.loads(timeline_response.text)

    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "tests", pipelines[service]["tests"])
        elif "Test Samples" in task["name"]:
            record_check_result(task, "samples", pipelines[service]["tests"])


def get_tests_weekly_result(
    service: str, pipeline_id: int, pipelines: dict[ServiceDirectory, PipelineResults]
) -> None:
    if not pipeline_id:
        print(f"No tests_weekly result for {service}")
        record_all("tests_weekly", pipelines[service], "UNKNOWN")
        return

    build_response = requests.get(get_build_url(pipeline_id), headers=AUTH_HEADERS)
    build_result = json.loads(build_response.text)
    if build_response.status_code != 200 or not build_result["value"]:
        print(f"No tests_weekly result for {service}")
        record_all("tests_weekly", pipelines[service], "UNKNOWN")
        return

    result = build_result["value"][0]
    pipelines[service]["tests_weekly"]["link"] = result["_links"]["web"]["href"]

    # get timeline
    pipelines[service]["tests_weekly"].update({"result": result["result"]})
    build_id = result["id"]
    timeline_response = requests.get(
        get_build_timeline_url(build_id), headers=AUTH_HEADERS
    )
    timeline_result = json.loads(timeline_response.text)

    for task in timeline_result["records"]:
        if "Run Tests" in task["name"]:
            record_test_result(task, "tests_weekly", pipelines[service]["tests_weekly"])
        elif "Run Pylint Next" in task["name"]:
            record_check_result(task, "next_pylint", pipelines[service]["tests_weekly"])
        elif "Run Pyright Next" in task["name"]:
            record_check_result(
                task, "next_pyright", pipelines[service]["tests_weekly"]
            )
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
            overall_status = "NEEDS_ACTION"
            break
        if status["status"] == "DISABLED" and check in MANDATORY_CHECKS:
            overall_status = "NEEDS_ACTION"
            break
    library_details["status"] = overall_status


def report_test_result(
    test_type: typing.Literal["ci", "tests"],
    pipeline: CIPipelineResult | TestsPipelineResult,
    library_details: LibraryStatus,
) -> None:
    test_status = pipeline[test_type][test_type]["status"]
    if test_status in ["succeeded", "partiallySucceeded"]:
        library_details[test_type] = Status(
            status="PASS", link=pipeline[test_type]["link"]
        )
    elif test_status == "failed":
        library_details[test_type] = Status(
            status="FAIL", link=pipeline[test_type]["link"]
        )
    else:
        library_details[test_type] = Status(
            status="UNKNOWN", link=pipeline[test_type].get("link")
        )


def report_check_result(
    check: CheckTypes,
    pipeline: CIPipelineResult | TestsWeeklyPipelineResult,
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
            library_details[check] = Status(
                status="WARNING", link=pipeline["tests_weekly"].get("link")
            )

        elif ci_check == "failed":
            library_details[check] = Status(status="FAIL", link=pipeline["ci"]["link"])
        else:
            library_details[check] = Status(
                status="UNKNOWN", link=pipeline["ci"].get("link")
            )
    else:
        ci_check = pipeline["ci"][check]["status"]
        if ci_check == "succeeded":
            library_details[check] = Status(status="PASS", link=pipeline["ci"]["link"])
        elif ci_check == "failed":
            library_details[check] = Status(status="FAIL", link=pipeline["ci"]["link"])
        else:
            library_details[check] = Status(
                status="UNKNOWN", link=pipeline["ci"].get("link")
            )


def report_status(
    dataplane: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]],
    pipelines: dict[ServiceDirectory, PipelineResults],
) -> None:
    for service_directory, libraries in dataplane.items():
        for _, details in libraries.items():
            if not is_check_enabled(str(details["path"]), "ci_enabled"):
                details["status"] = "DISABLED"
                continue
            report_check_result("mypy", pipelines[service_directory], details)
            report_check_result("pylint", pipelines[service_directory], details)
            report_check_result("pyright", pipelines[service_directory], details)
            report_check_result("sphinx", pipelines[service_directory], details)
            details["type_check_samples"] = Status(
                status=(
                    "ENABLED"
                    if is_check_enabled(str(details["path"]), "type_check_samples")
                    else "DISABLED"
                )
            )
            report_test_result("tests", pipelines[service_directory], details)
            report_test_result("ci", pipelines[service_directory], details)
            report_overall_status(details)


def write_to_csv(
    libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]
) -> None:
    with open("./health_report.csv", mode="w", newline="", encoding="utf-8") as file:
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
        ]
        writer.writerow(column_names)

        for _, libs in libraries.items():
            for library, details in libs.items():
                if details["status"] == "DISABLED":
                    writer.writerow([library, details["status"]])
                else:
                    writer.writerow(
                        [
                            library,
                            details["status"],
                            details["mypy"]["status"],
                            details["pyright"]["status"],
                            details["type_check_samples"]["status"],
                            details["pylint"]["status"],
                            details["sphinx"]["status"],
                            details["ci"]["status"],
                            details["tests"]["status"],
                        ]
                    )


def write_to_markdown(
    libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]
) -> None:
    with open("./health_report.md", mode="w", newline="", encoding="utf-8") as file:
        # Write the column names
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
        ]
        file.write("|" + "|".join(column_names) + "|\n")

        # Write the header separator
        file.write("|" + "---|" * len(column_names) + "\n")

        for _, libs in libraries.items():
            for library, details in libs.items():
                if details["status"] == "DISABLED":
                    status_colored = (
                        f'<span style="color: red;">{details["status"]}</span>'
                    )
                elif details["status"] == "NEEDS_ACTION":
                    status_colored = (
                        f'<span style="color: orange;">{details["status"]}</span>'
                    )
                elif details["status"] == "GOOD":
                    status_colored = (
                        f'<span style="color: green;">{details["status"]}</span>'
                    )

                if details["status"] == "DISABLED":
                    row = [library, status_colored] + [""] * (len(column_names) - 2)
                else:
                    row = [
                        library,
                        status_colored,
                        details["mypy"]["status"]
                        + (
                            f" ([link]({details["mypy"]["link"]}))"
                            if details["mypy"]["link"] is not None
                            else ""
                        ),
                        details["pyright"]["status"]
                        + (
                            f" ([link]({details["pyright"]["link"]}))"
                            if details["pyright"]["link"] is not None
                            else ""
                        ),
                        details["type_check_samples"]["status"],
                        details["pylint"]["status"]
                        + (
                            f" ([link]({details["pylint"]["link"]}))"
                            if details["pylint"]["link"] is not None
                            else ""
                        ),
                        details["sphinx"]["status"]
                        + (
                            f" ([link]({details["sphinx"]["link"]}))"
                            if details["sphinx"]["link"] is not None
                            else ""
                        ),
                        details["ci"]["status"]
                        + (
                            f" ([link]({details["ci"]["link"]}))"
                            if details["ci"]["link"] is not None
                            else ""
                        ),
                        details["tests"]["status"]
                        + (
                            f" ([link]({details["tests"]["link"]}))"
                            if details["tests"]["link"] is not None
                            else ""
                        ),
                    ]

                row_str = [str(item).strip() for item in row]
                file.write("|" + "|".join(row_str) + "|\n")


def write_to_html(
    libraries: dict[ServiceDirectory, dict[LibraryName, LibraryStatus]]
) -> None:
    write_to_markdown(libraries)
    with open("./health_report.md", "r") as f:
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

    with open("./health_report.html", "w", encoding="utf-8") as file:
        file.write(html_with_css)


libraries = get_dataplane()
pipelines = get_pipelines(libraries)
for service, pipeline_ids in pipelines.items():
    get_ci_result(service, pipeline_ids.get("ci", {}).get("id", ""), pipelines)
    get_tests_result(service, pipeline_ids.get("tests", {}).get("id", ""), pipelines)
    get_tests_weekly_result(
        service, pipeline_ids.get("tests_weekly", {}).get("id", ""), pipelines
    )


report_status(libraries, pipelines)
# write_to_markdown(libraries)
# write_to_csv(libraries)
write_to_html(libraries)
