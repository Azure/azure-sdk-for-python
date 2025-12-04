"""Utilities for resolving dependency sets for tox-style checks.

This module contains the logic previously hosted in ``eng/tox/install_depend_packages.py``
so that both the legacy tox entry point and the azpysdk checks can share a
single implementation.
"""

import logging
import os
import re
import subprocess
import sys
from typing import Callable, List, Optional

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pypi_tools.pypi import PyPIClient

from ci_tools.functions import (
	compare_python_version,
	get_pip_command,
	handle_incompatible_minimum_dev_reqs,
)
from ci_tools.parsing import ParsedSetup, parse_require

logger = logging.getLogger(__name__)

DEV_REQ_FILE = "dev_requirements.txt"
NEW_DEV_REQ_FILE = "new_dev_requirements.txt"
PKGS_TXT_FILE = "packages.txt"

# GENERIC_OVERRIDES dictionaries pair a specific dependency with a MINIMUM or MAXIMUM inclusive bound.
# During LATEST and MINIMUM dependency checks, we sometimes need to ignore versions for various compatibility
# reasons.
MINIMUM_VERSION_GENERIC_OVERRIDES = {
	"azure-common": "1.1.10",
	"msrest": "0.6.10",
	"typing-extensions": "4.6.0",
	"opentelemetry-api": "1.3.0",
	"opentelemetry-sdk": "1.3.0",
	"azure-core": "1.11.0",
	"requests": "2.19.0",
	"six": "1.12.0",
	"cryptography": "41.0.0",
	"msal": "1.23.0",
	"azure-storage-file-datalake": "12.2.0",
}

MAXIMUM_VERSION_GENERIC_OVERRIDES = {}

# SPECIFIC OVERRIDES provide additional filtering of upper and lower bound by
# binding an override to the specific package being processed. As an example, when
# processing the latest or minimum deps for "azure-eventhub", the minimum version of "azure-core"
# will be overridden to 1.25.0.
MINIMUM_VERSION_SPECIFIC_OVERRIDES = {
	"azure-eventhub": {"azure-core": "1.25.0"},
	"azure-eventhub-checkpointstoreblob-aio": {"azure-core": "1.25.0", "azure-eventhub": "5.11.0"},
	"azure-eventhub-checkpointstoreblob": {"azure-core": "1.25.0", "azure-eventhub": "5.11.0"},
	"azure-eventhub-checkpointstoretable": {"azure-core": "1.25.0", "azure-eventhub": "5.11.0"},
	"azure-identity": {"msal": "1.23.0"},
	"azure-core-tracing-opentelemetry": {"azure-core": "1.28.0"},
	"azure-storage-file-datalake": {"azure-storage-blob": "12.22.0"},
	"azure-cosmos": {"azure-core": "1.30.0"},
	"azure-appconfiguration-provider": {"azure-appconfiguration": "1.7.2"},
	"azure-ai-evaluation": {"aiohttp": "3.8.6"},
}

MAXIMUM_VERSION_SPECIFIC_OVERRIDES = {}

# PLATFORM SPECIFIC OVERRIDES provide additional generic (EG not tied to the package whose dependencies are being processed)
# filtering on a _per platform_ basis. Primarily used to limit certain packages due to platform compatibility.
PLATFORM_SPECIFIC_MINIMUM_OVERRIDES = {
	">=3.14.0": {
		"typing-extensions": "4.15.0",
	},
	">=3.12.0": {
		"azure-core": "1.23.1",
		"aiohttp": "3.9.0",
		"six": "1.16.0",
		"requests": "2.30.0",
	},
	">=3.13.0": {
		"typing-extensions": "4.13.0",
		"aiohttp": "3.10.6",
	},
}

PLATFORM_SPECIFIC_MAXIMUM_OVERRIDES = {}

# This is used to actively _add_ requirements to the install set. These are used to actively inject
# a new requirement specifier to the set of packages being installed.
SPECIAL_CASE_OVERRIDES = {
	# this package has an override
	"azure-core": {
		# if the version being installed matches this specifier, add the listed packages to the install list
		"<1.24.0": ["msrest<0.7.0"],
	}
}

__all__ = [
	"install_dependent_packages",
	"filter_dev_requirements",
	"find_released_packages",
]


def install_dependent_packages(
	setup_py_file_path: str,
	dependency_type: str,
	temp_dir: str,
	python_executable: Optional[str] = None,
) -> None:
	"""Identify and install the dependency set for a package.

	:param setup_py_file_path: Path to the target package directory.
	:param dependency_type: Either ``"Latest"`` or ``"Minimum"``.
	:param temp_dir: Directory where temporary artifacts (e.g. filtered requirements, packages.txt) are written.
	:param python_executable: Optional interpreter whose environment should receive the installations. Defaults to
		the current ``sys.executable``.
	"""

	python_exe = python_executable or sys.executable

	released_packages = find_released_packages(setup_py_file_path, dependency_type)
	override_added_packages: List[str] = []

	for pkg_spec in released_packages:
		override_added_packages.extend(check_pkg_against_overrides(pkg_spec))

	logger.info("%s released packages: %s", dependency_type, released_packages)

	additional_filter_fn: Optional[Callable[[str, List[str], List[Requirement]], List[str]]] = None
	if dependency_type == "Minimum":
		additional_filter_fn = handle_incompatible_minimum_dev_reqs

	dev_req_file_path = filter_dev_requirements(
		setup_py_file_path, released_packages, temp_dir, additional_filter_fn
	)

	if override_added_packages:
		logger.info("Expanding the requirement set by the packages %s.", override_added_packages)

	install_set = released_packages + list(set(override_added_packages))

	if install_set or dev_req_file_path:
		install_packages(install_set, dev_req_file_path, python_exe)

	if released_packages:
		pkgs_file_path = os.path.join(temp_dir, PKGS_TXT_FILE)
		with open(pkgs_file_path, "w", encoding="utf-8") as pkgs_file:
			for package in released_packages:
				pkgs_file.write(package + "\n")
		logger.info("Created file %s to track azure packages found on PyPI", pkgs_file_path)


def check_pkg_against_overrides(pkg_specifier: str) -> List[str]:
	"""Apply ``SPECIAL_CASE_OVERRIDES`` for a resolved package specifier."""

	additional_installs: List[str] = []
	target_package, target_version = pkg_specifier.split("==")

	target_version_obj = Version(target_version)
	if target_package in SPECIAL_CASE_OVERRIDES:
		for specifier_set, extras in SPECIAL_CASE_OVERRIDES[target_package].items():
			spec = SpecifierSet(specifier_set)
			if target_version_obj in spec:
				additional_installs.extend(extras)

	return additional_installs


def find_released_packages(setup_py_path: str, dependency_type: str) -> List[str]:
	"""Resolve the appropriate released dependency versions for a package."""

	pkg_info = ParsedSetup.from_path(setup_py_path)
	requires = [r for r in pkg_info.requires if "-nspkg" not in r]
	available_packages = [
		spec for spec in map(lambda req: process_requirement(req, dependency_type, pkg_info.name), requires) if spec
	]
	return available_packages


def process_bounded_versions(originating_pkg_name: str, pkg_name: str, versions: List[str]) -> List[str]:
	"""Apply generic, platform, and package-specific bounds to the available versions list."""

	if pkg_name in MINIMUM_VERSION_GENERIC_OVERRIDES:
		versions = [
			v for v in versions if Version(v) >= Version(MINIMUM_VERSION_GENERIC_OVERRIDES[pkg_name])
		]

	for platform_bound, restrictions in PLATFORM_SPECIFIC_MINIMUM_OVERRIDES.items():
		if compare_python_version(platform_bound) and pkg_name in restrictions:
			versions = [v for v in versions if Version(v) >= Version(restrictions[pkg_name])]

	if (
		originating_pkg_name in MINIMUM_VERSION_SPECIFIC_OVERRIDES
		and pkg_name in MINIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name]
	):
		versions = [
			v
			for v in versions
			if Version(v) >= Version(MINIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name][pkg_name])
		]

	if pkg_name in MAXIMUM_VERSION_GENERIC_OVERRIDES:
		versions = [
			v for v in versions if Version(v) <= Version(MAXIMUM_VERSION_GENERIC_OVERRIDES[pkg_name])
		]

	for platform_bound, restrictions in PLATFORM_SPECIFIC_MAXIMUM_OVERRIDES.items():
		if compare_python_version(platform_bound) and pkg_name in restrictions:
			versions = [v for v in versions if Version(v) <= Version(restrictions[pkg_name])]

	if (
		originating_pkg_name in MAXIMUM_VERSION_SPECIFIC_OVERRIDES
		and pkg_name in MAXIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name]
	):
		versions = [
			v
			for v in versions
			if Version(v) <= Version(MAXIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name][pkg_name])
		]

	return versions


def process_requirement(req: str, dependency_type: str, orig_pkg_name: str) -> str:
	"""Determine the matching version for a requirement based on dependency type."""

	requirement = parse_require(req)
	pkg_name = requirement.name
	spec = requirement.specifier if len(requirement.specifier) else None

	if not (requirement.marker is None or requirement.marker.evaluate()):
		logger.info(
			"Skipping requirement %r. Environment marker %r does not apply to current environment.",
			req,
			str(requirement.marker),
		)
		return ""

	client = PyPIClient()
	versions = [str(v) for v in client.get_ordered_versions(pkg_name, True)]
	logger.info("Versions available on PyPI for %s: %s", pkg_name, versions)

	versions = process_bounded_versions(orig_pkg_name, pkg_name, versions)

	if dependency_type == "Latest":
		versions.reverse()

	for version in versions:
		if spec is None or version in spec:
			logger.info(
				"Found %s version %s that matches specifier %s",
				dependency_type,
				version,
				spec,
			)
			return pkg_name + "==" + version

	logger.error("No version is found on PyPI for package %s that matches specifier %s", pkg_name, spec)
	return ""


def check_req_against_exclusion(req: str, req_to_exclude: str) -> bool:
	"""Return ``True`` if the dev requirement matches the package slated for exclusion."""

	req_id = ""
	for char in req:
		if re.match(r"[A-Za-z0-9_-]", char):
			req_id += char
		else:
			break

	return req_id == req_to_exclude


def filter_dev_requirements(
	package_directory: str,
	released_packages: List[str],
	temp_dir: str,
	additional_filter_fn: Optional[Callable[[str, List[str], List[Requirement]], List[str]]] = None,
) -> str:
	"""Filter dev requirements to avoid reinstalling packages we just resolved."""

	dev_req_path = os.path.join(package_directory, DEV_REQ_FILE)
	with open(dev_req_path, "r", encoding="utf-8") as dev_req_file:
		requirements = dev_req_file.readlines()

	released_packages_parsed = [parse_require(p) for p in released_packages]
	released_package_names = [p.name for p in released_packages_parsed]

	prebuilt_dev_reqs = [os.path.basename(req.replace("\n", "")) for req in requirements if os.path.sep in req]
	req_to_exclude = [
		req for req in prebuilt_dev_reqs if req.split("-")[0].replace("_", "-") in released_package_names
	]
	req_to_exclude.extend(released_package_names)

	filtered_req = [
		req
		for req in requirements
		if os.path.basename(req.replace("\n", "")) not in req_to_exclude
		and not any(check_req_against_exclusion(req, item) for item in req_to_exclude)
	]

	if additional_filter_fn:
		filtered_req = additional_filter_fn(package_directory, filtered_req, released_packages_parsed)

	logger.info("Filtered dev requirements: %s", filtered_req)

	new_dev_req_path = ""
	if filtered_req:
		new_dev_req_path = os.path.join(temp_dir, NEW_DEV_REQ_FILE)
		with open(new_dev_req_path, "w", encoding="utf-8") as dev_req_file:
			dev_req_file.writelines(line if line.endswith("\n") else line + "\n" for line in filtered_req)

	return new_dev_req_path


def install_packages(packages: List[str], req_file: str, python_executable: str) -> None:
	"""Install resolved packages (and optionally a requirements file) into the target environment."""

	python_exe = python_executable or sys.executable
	commands = get_pip_command(python_exe)
	commands.append("install")

	if commands[0] == "uv":
		commands.extend(["--python", python_exe])

	if packages:
		commands.extend(packages)

	if req_file:
		commands.extend(["-r", req_file])

	logger.info("Installing packages. Command: %s", commands)
	subprocess.check_call(commands)
