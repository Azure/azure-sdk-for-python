# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import os
import sys
import datetime
import logging
import json
import pathlib
import glob
import subprocess
import csv
import calendar
from typing import Any

import requests
from github import Github, Auth

from ci_tools.parsing import ParsedSetup
from ci_tools.environment_exclusions import (
    IGNORE_PACKAGES,
    is_check_enabled,
    FILTER_EXCLUSIONS,
    IGNORE_FILTER,
)

logging.getLogger().setLevel(logging.INFO)

INACTIVE_CLASSIFIER = "Development Status :: 7 - Inactive"

IGNORE_FILTER.append("mgmt")
FILTER_EXCLUSIONS.append("azure-mgmt-core")
IGNORE_PACKAGES.extend([
    "azure-openai",
    "azure-storage-extensions",
    "azure-schemaregistry-avroserializer",
    "azure-eventhub-checkpointstoretable",
])

SDK_TEAM_OWNED_PACKAGES = [
    "azure-ai-documentintelligence",
    "azure-appconfiguration",
    "azure-containerregistry",
    "azure-core",
    "azure-mgmt-core",
    "azure-core-experimental",
    "azure-core-tracing-opencensus",
    "azure-core-tracing-openetelemetry",
    "azure-data-tables",
    "azure-eventgrid",
    "azure-eventhub",
    "azure-identity",
    "azure-keyvault-administration",
    "azure-keyvault-certificates",
    "azure-keyvault-keys",
    "azure-keyvault-secrets",
    "azure-monitor-ingestion",
    "azure-monitor-query",
    "azure-schemaregistry",
    "azure-search-documents",
    "azure-servicebus",
    "corehttp",
]


# We install each library from the dev feed. This installs mostly alpha versions.
# These libraries have dependencies on other libraries where an alpha version is not
# considered compatible with the given version specifier. Therefore, we add a second step
# to install/score these libraries separately.

# Format: "library_to_score": [dependencies_to_uninstall]
RESOLUTION_IMPOSSIBLE_LIBRARIES = {
    "azure-mixedreality-authentication": ["azure-mixedreality-remoterendering"],
    "azure-ai-ml": ["azure-storage-blob", "azure-storage-file-share", "azure-storage-file-datalake"],
    "azure-storage-blob-changefeed": ["azure-storage-blob"],
    "azure-storage-file-datalake": ["azure-storage-blob"],
    "azure-core": ["azure-core-experimental", "azure-core-tracing-opencensus", "azure-core-tracing-opentelemetry"],
    "azure-monitor-opentelemetry": ["azure-core-tracing-opentelemetry"],
    "azure-ai-evaluation": ["azure-monitor-opentelemetry-exporter", "azure-monitor-opentelemetry"],
}


def add_entity(package: str, packages_to_score: dict[str, Any], entities: list[dict[str, Any]]) -> None:
    d = packages_to_score[package]["Date"]
    entity = {
        "Package": package,
        "Date": d,
        "LatestVersion": packages_to_score[package]["LatestVersion"],
        "Score": packages_to_score[package]["Score"],
        "PyTyped": packages_to_score[package]["PyTyped"],
        "Pyright": packages_to_score[package]["Pyright"],
        "Mypy": packages_to_score[package]["Mypy"],
        "Samples": packages_to_score[package]["Samples"],
        "Verifytypes": packages_to_score[package]["Verifytypes"],
        "SDKTeamOwned": packages_to_score[package]["SDKTeamOwned"],
        "Active": packages_to_score[package]["Active"]
    }
    entities.append(entity)


def install(packages: list[str]) -> None:
    commands = [
        sys.executable,
        "-m",
        "pip",
        "install",
    ]

    commands.extend(packages)
    subprocess.check_call(commands)


def uninstall_deps(deps: list[str]) -> None:
    commands = [
        sys.executable,
        "-m",
        "pip",
        "uninstall",
        "-y"
    ]

    commands.extend(deps)
    subprocess.check_call(commands)


def score_package(package: str, packages_to_score: dict[str, Any], entities: list[dict[str, Any]]) -> None:
    try:
        logging.info(f"Running verifytypes on {package}")
        commands = [sys.executable, "-m", "pyright", "--verifytypes", packages_to_score[package]["Module"], "--ignoreexternal", "--outputjson"]
        response = subprocess.run(
            commands,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            logging.info(
                f"Running verifytypes for {package} failed: {e.stderr}"
            )
        else:
            report = json.loads(e.output)
    else:
        report = json.loads(response.stdout)  # package scores 100%
    pytyped_present = False if report["typeCompleteness"].get("pyTypedPath", None) is None else True
    packages_to_score[package].update({"PyTyped": pytyped_present})
    packages_to_score[package].update({"Score": round(report["typeCompleteness"]["completenessScore"] * 100, 1)})
    add_entity(package, packages_to_score, entities)


def get_alpha_installs(packages_to_score: dict[str, Any]) -> tuple[list[str], dict[str, list[str]]]:
    feed_id = "3572dbf9-b5ef-433b-9137-fc4d7768e7cc"
    feed_resp = requests.get(f"https://feeds.dev.azure.com/azure-sdk/public/_apis/packaging/feeds/{feed_id}/Packages?api-version=7.0")
    packages = json.loads(feed_resp.text)
    versions_to_install = {}

    # Dev feed doesn't default to latest version, so we have to check publish dates for most recent
    for package in packages["value"]:
        if package["name"] in packages_to_score:
            url = f"{package['url']}/Versions"
            versions = requests.get(url)
            version_list = json.loads(versions.text)["value"]
            latest_version = max(version_list, key=lambda v: datetime.datetime.strptime(v["publishDate"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))
            versions_to_install[package["name"]] = latest_version["version"]

    extra_index_url = ("--extra-index-url", "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple", "--pre")
    first_round = []
    second_round = {}

    for package_name, version in versions_to_install.items():
        packages_to_score[package_name].update({'LatestVersion': version})
        package_info = [f"{package_name}=={version}", *extra_index_url]
        
        if package_name in RESOLUTION_IMPOSSIBLE_LIBRARIES:
            second_round[package_name] = package_info
        else:
            first_round.extend(package_info)

    return first_round, second_round


def is_package_inactive(package_path: str) -> bool:
    return INACTIVE_CLASSIFIER in ParsedSetup.from_path(package_path).classifiers


def skip_package(package_name: str) -> bool:
    return (
        (not package_name.startswith("azure") and package_name != "corehttp")
        or package_name in IGNORE_PACKAGES
        or package_name not in FILTER_EXCLUSIONS
        and any(identifier in package_name for identifier in IGNORE_FILTER)
    )


def get_packages_to_score() -> dict[str, dict[str, Any]]:
    dataplane = {}
    sdk_path = pathlib.Path(__file__).parent.parent.parent / "sdk"
    service_directories = glob.glob(f"{sdk_path}/*/", recursive=True)
    today = datetime.datetime.today()
    for service in service_directories:
        package_paths = glob.glob(f"{service}*/", recursive=True)
        for pkg_path in package_paths:
            package_path = pathlib.Path(pkg_path)
            package_name = package_path.name
            if skip_package(package_name) or not (package_path / "setup.py").exists():
                continue
            package_path = str(package_path)
            package_info = ParsedSetup.from_path(package_path)
            dataplane[package_name] = {"LatestVersion": package_info.version}
            dataplane[package_name].update({"Path": package_path})
            dataplane[package_name].update({"Module": package_info.namespace})
            dataplane[package_name].update({"Pyright": is_check_enabled(package_path, "pyright")})
            dataplane[package_name].update({"Mypy": is_check_enabled(package_path, "mypy")})
            dataplane[package_name].update({"Samples": is_check_enabled(package_path, "type_check_samples")})
            dataplane[package_name].update({"Verifytypes": is_check_enabled(package_path, "verifytypes")})
            dataplane[package_name].update({"Date": today})
            dataplane[package_name].update({"SDKTeamOwned": package_name in SDK_TEAM_OWNED_PACKAGES})
            dataplane[package_name].update({"Active": not is_package_inactive(package_path)})

    sorted_libs = {key: dataplane[key] for key in sorted(dataplane)}
    return sorted_libs


def append_results_to_csv(entities: list[dict[str, Any]]) -> None:
    typescore_path = pathlib.Path(__file__).parent

    github = Github(auth=Auth.Token(os.environ["GH_TOKEN"]))
    repo = github.get_repo("Azure/azure-sdk-for-python")

    path = "scripts/repo_type_completeness/typescores.csv"
    content = repo.get_contents(path, ref="python-sdk-type-completeness")
    decoded_content = content.decoded_content.decode("utf-8")

    with open(typescore_path / "typescores.csv", mode="a", newline='', encoding="utf-8") as file:
        file.write(decoded_content)
        writer = csv.writer(file)

        for data in entities:
            row = [
                data["Package"],
                data["Date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                data["LatestVersion"],
                data["Score"],
                data["PyTyped"],
                data["Pyright"],
                data["Mypy"],
                data["Samples"],
                data["Verifytypes"],
                data["SDKTeamOwned"],
                data["Active"],
            ]
            writer.writerow(row)

    repo.update_file(
        path=path,
        message="Update typing dashboard",
        content=open(path, "rb").read(),
        branch="python-sdk-type-completeness",
        sha=content.sha
    )


def should_run() -> bool:
    """We only update the typing dashboard once a month on the Monday after release week.
    """
    pst = datetime.datetime.now(datetime.timezone(offset=datetime.timedelta(hours=-8)))
    today = pst.date()
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    month_dates = c.monthdatescalendar(today.year, today.month)

    monday_after_release_week = None
    for week in month_dates:
        for day in week:
            if day.weekday() == calendar.FRIDAY and day.month == today.month:
                monday_after_release_week = day + datetime.timedelta(days=10)
                return today == monday_after_release_week

    return False


def update_main_typescores() -> None:
    if not should_run():
        logging.info(f"Skipping type scoring update - only runs once a month on the Monday after release week.")
        return

    packages_to_score = get_packages_to_score()

    first_round, second_round = get_alpha_installs(packages_to_score)

    install(first_round)

    entities = []
    for package, _ in packages_to_score.items():
        if package in RESOLUTION_IMPOSSIBLE_LIBRARIES:
            continue
        score_package(package, packages_to_score, entities)

    for package, deps in RESOLUTION_IMPOSSIBLE_LIBRARIES.items():
        uninstall_deps(deps)
        install(second_round[package])
        score_package(package, packages_to_score, entities)

    append_results_to_csv(entities)


if __name__ == "__main__":
    update_main_typescores()
