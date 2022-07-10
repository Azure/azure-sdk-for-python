from ast import Not
from click import BadArgumentUsage
from packaging.specifiers import SpecifierSet
from packaging.version import Version, parse

import os, sys, platform, glob

from ci_tools.parsing import ParsedSetup
from typing import List


OMITTED_CI_PACKAGES = [
    "azure-mgmt-documentdb",
    "azure-servicemanagement-legacy",
    "azure-mgmt-scheduler",
    "azure",
    "azure-mgmt",
    "azure-storage",
    "azure-monitor",
    "azure-mgmt-regionmove",
]
MANAGEMENT_PACKAGE_IDENTIFIERS = [
    "mgmt",
    "azure-cognitiveservices",
    "azure-servicefabric",
    "nspkg",
    "azure-keyvault",
    "azure-synapse",
    "azure-ai-anomalydetector",
]
META_PACKAGES = ["azure", "azure-mgmt", "azure-keyvault"]
REGRESSION_EXCLUDED_PACKAGES = [
    "azure-common",
]

MANAGEMENT_PACKAGES_FILTER_EXCLUSIONS = [
    "azure-mgmt-core",
]

TEST_COMPATIBILITY_MAP = {"azure-core-tracing-opentelemetry": "<3.10"}

omit_regression = (
    lambda x: "nspkg" not in x
    and "mgmt" not in x
    and os.path.basename(x) not in MANAGEMENT_PACKAGE_IDENTIFIERS
    and os.path.basename(x) not in META_PACKAGES
    and os.path.basename(x) not in REGRESSION_EXCLUDED_PACKAGES
)
omit_docs = lambda x: "nspkg" not in x and os.path.basename(x) not in META_PACKAGES
omit_build = lambda x: x  # Dummy lambda to match omit type
lambda_filter_azure_pkg = lambda x: x.startswith("azure") and "-nspkg" not in x
omit_mgmt = lambda x: "mgmt" not in x or os.path.basename(x) in MANAGEMENT_PACKAGES_FILTER_EXCLUSIONS


# dict of filter type and filter function
omit_funct_dict = {
    "Build": omit_build,
    "Docs": omit_docs,
    "Regression": omit_regression,
    "Omit_management": omit_mgmt,
}


def filter_for_compatibility(package_set):
    collected_packages = []
    v = sys.version_info
    running_major_version = Version(".".join([str(v[0]), str(v[1]), str(v[2])]))

    for pkg in package_set:
        spec_set = SpecifierSet(ParsedSetup.from_path(pkg).python_requires)

        if running_major_version in spec_set:
            collected_packages.append(pkg)

    return collected_packages


def compare_python_version(version_spec):
    current_sys_version = parse(platform.python_version())
    spec_set = SpecifierSet(version_spec)

    return current_sys_version in spec_set


def filter_packages_by_compatibility_override(package_set: List[str], resolve_basename: bool = True) -> List[str]:
    return [
        p
        for p in package_set
        if compare_python_version(TEST_COMPATIBILITY_MAP.get(os.path.basename(p) if resolve_basename else p, ">=2.7"))
    ]


def str_to_bool(input_string: str) -> bool:
    """
    Takes a boolean string representation and returns a bool type value.
    """
    if isinstance(input_string, bool):
        return input_string
    elif input_string.lower() in ("true", "t", "1"):
        return True
    elif input_string.lower() in ("false", "f", "0"):
        return False
    else:
        return False


def discover_repo_root():
    """
    Resolves the root of the repository given a current working directory. This function should be used if a target repo argument is not provided.
    """

    current_dir: str = os.getcwd()

    while current_dir is not None and not (os.path.dirname(current_dir) == current_dir):
        if os.path.exists(os.path.join(current_dir, ".git")):
            return current_dir
        else:
            current_dir = os.path.dirname(current_dir)

    raise BadArgumentUsage(
        "Commands invoked against azure-sdk-tooling should either be run from within the repo directory or provide --repo_root argument that directs at one."
    )


def discover_targeted_packages(
    glob_string,
    target_root_dir,
    additional_contains_filter="",
    filter_type="Build",
) -> list[str]:
    """
    During build and test, the set of targeted packages may expand or contract depending on the needs of the invocation.
    This function centralizes business and material requirements and outputs the set of packages that should be targeted.
    """
    if glob_string:
        individual_globs = glob_string.split(",")
    else:
        individual_globs = "azure-*"
    collected_top_level_directories = []

    for glob_string in individual_globs:
        globbed = glob.glob(os.path.join(target_root_dir, glob_string, "setup.py")) + glob.glob(
            os.path.join(target_root_dir, "sdk/*/", glob_string, "setup.py")
        )
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # dedup, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    collected_directories = list(set([p for p in collected_top_level_directories if additional_contains_filter in p]))

    # if we have individually queued this specific package, it's obvious that we want to build it specifically
    # in this case, do not honor the omission list
    if len(collected_directories) == 1:
        pkg_set_ci_filtered = filter_for_compatibility(collected_directories)
    # however, if there are multiple packages being built, we should honor the omission list and NOT build the omitted
    # packages
    else:
        allowed_package_set = remove_omitted_packages(collected_directories)
        pkg_set_ci_filtered = filter_for_compatibility(allowed_package_set)

    # Apply filter based on filter type. for e.g. Docs, Regression, Management
    pkg_set_ci_filtered = list(filter(omit_funct_dict.get(filter_type, omit_build), pkg_set_ci_filtered))
    # logging.info("Target packages after filtering by CI: {}".format(pkg_set_ci_filtered))
    # logging.info(
    #     "Package(s) omitted by CI filter: {}".format(list(set(collected_directories) - set(pkg_set_ci_filtered)))
    # )
    return sorted(pkg_set_ci_filtered)


def remove_omitted_packages(collected_directories):
    packages = [
        package_dir for package_dir in collected_directories if os.path.basename(package_dir) not in OMITTED_CI_PACKAGES
    ]

    return packages
