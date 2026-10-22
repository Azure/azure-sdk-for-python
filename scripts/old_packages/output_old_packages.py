# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import typing
import csv
import argparse
import pathlib
import glob
import datetime

import requests

from ci_tools.parsing import get_config_setting
from pypi_tools.pypi import PyPIClient

INACTIVE_CLASSIFIER = "Development Status :: 7 - Inactive"


def get_newer(current: datetime.date, contender: datetime.date) -> datetime.date:
    if current > contender:
        return current
    return contender


def write_csv(packages: typing.Mapping[str, str]) -> None:
    if not packages:
        print("No packages found.")
        return

    with open("./old_packages.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        column_names = [
            "Package",
            "Last released version",
            "Last released date",
            "Status",
            "Downloads (last 90 days)"
        ]
        writer.writerow(column_names)

        for package, info in packages.items():
            writer.writerow([package, info["version"], info["date"], info["status"], info["downloads_90d"]])


def get_latest_release(
    project: typing.Mapping[str, typing.Any]
) -> typing.Mapping[str, str]:
    current = datetime.datetime(1970, 1, 1).date()

    for version, release in project["releases"].items():
        if not release:
            # somehow we release without whl/sdist?
            continue

        release_date = datetime.datetime.strptime(
            release[0]["upload_time"], "%Y-%m-%dT%H:%M:%S"
        ).date()
        if get_newer(current, release_date) == release_date:
            latest = {
                "version": version,
                "date": release_date,
                "status": project["info"]["classifiers"][0],
            }
            current = release_date
    return latest


def apply_filters(pkg_path: str, release: typing.Mapping[str, str]) -> bool:
    """Filter out packages that are marked as Inactive or have a verify_status_by date in the future. 
    If the package has no verify_status_by date, it is considered active.
    """
    if release["status"] == INACTIVE_CLASSIFIER:
        return False

    verify_status_by = get_config_setting(pkg_path, "verify_status_by", default=None)
    if verify_status_by is None:
        return True

    today = datetime.datetime.today().date()
    if get_newer(today, verify_status_by) == verify_status_by:
        return False

    return True


class PepyClient:
    """Client to interact with the Pepy API to fetch package download data."""

    def __init__(self, api_key: str):
        """Initialize the client with your API key - https://www.pepy.tech/pepy-api (register first)"""
        self.api_key = api_key

    def get_downloads_90d(self, package: str) -> int:
        """Get the total downloads in the last 90 days for a given package."""
        url = f"https://api.pepy.tech/api/v2/projects/{package}"
        headers = {"x-api-key": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            downloads_90d = response.json().get("downloads", {})
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return -1

        total_downloads_90d = sum(
            downloads
            for versions in downloads_90d.values()
            for downloads in versions.values()
        )

        return total_downloads_90d


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Output old packages in the repo.")

    parser.add_argument(
        "-y",
        "--years",
        dest="years",
        help="How many years since last release. Defaults to 2.",
        type=int,
        default=2,
    )

    parser.add_argument(
        "-f",
        "--disable-filter",
        dest="filter",
        help="Disable the filter which removes Inactive packages and ones with verify_status_by dates in the future.",
        action="store_false",
    )

    args = parser.parse_args()
    sdk_path = pathlib.Path(__file__).parent.parent.parent / "sdk"
    service_directories = glob.glob(f"{sdk_path}/*/", recursive=True)
    pypi_client = PyPIClient()
    pepy_client = PepyClient(os.environ["PEPY_API_KEY"])
    old_packages = {}

    years = args.years
    timepoint = datetime.datetime.today().date() - datetime.timedelta(days=365 * years)

    for service in service_directories:
        package_paths = glob.glob(f"{service}*/", recursive=True)
        for package_path in package_paths:
            package_name = pathlib.Path(package_path).name
            if not package_name.startswith("azure"):
                continue

            pypi_project = pypi_client.project(package_name)
            if pypi_project.get("releases") is None:
                # not yet released
                continue

            latest_release = get_latest_release(pypi_project)

            if (
                get_newer(latest_release["date"], timepoint) == timepoint
            ):
                add_package = not args.filter or apply_filters(package_path, latest_release)
                if add_package:
                    old_packages[package_name] = latest_release
                    old_packages[package_name]["downloads_90d"] = (
                        pepy_client.get_downloads_90d(package_name)
                    )

    write_csv(old_packages)
