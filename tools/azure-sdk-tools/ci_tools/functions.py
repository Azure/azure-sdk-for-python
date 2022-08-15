from ast import Not
from packaging.specifiers import SpecifierSet
from packaging.version import Version, parse
from pkg_resources import Requirement

from ci_tools.variables import discover_repo_root, get_artifact_directory, DEV_BUILD_IDENTIFIER
import os, sys, platform, glob, re

from ci_tools.parsing import ParsedSetup
from pypi_tools.pypi import PyPIClient


from typing import List
import logging


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
omit_function_dict = {
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


def compare_python_version(version_spec: str):
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


def discover_targeted_packages(
    glob_string: str,
    target_root_dir: str,
    additional_contains_filter: str = "",
    filter_type: str = "Build",
) -> List[str]:
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

    # deduplicate, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
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
    pkg_set_ci_filtered = list(filter(omit_function_dict.get(filter_type, omit_build), pkg_set_ci_filtered))
    logging.info("Target packages after filtering by CI Type: {}".format(pkg_set_ci_filtered))
    logging.info(
        "Package(s) omitted by CI filter: {}".format(list(set(collected_directories) - set(pkg_set_ci_filtered)))
    )
    return sorted(pkg_set_ci_filtered)


def remove_omitted_packages(collected_directories):
    packages = [
        package_dir for package_dir in collected_directories if os.path.basename(package_dir) not in OMITTED_CI_PACKAGES
    ]

    return packages


def update_requires(setup_py_path, requires_dict):
    # This method changes package requirement by overriding the specifier
    contents = []
    with open(setup_py_path, "r") as setup_file:
        contents = setup_file.readlines()

    # find and replace all existing package requirement with new requirement
    for i in range(0, len(contents) - 1):
        keys = [k for k in requires_dict.keys() if k in contents[i]]
        for key in keys:
            contents[i] = contents[i].replace(key, requires_dict[key])

    with open(setup_py_path, "w") as setup_file:
        setup_file.writelines(contents)


def is_required_version_on_pypi(package_name, spec):
    client = PyPIClient()
    try:
        pypi_results = client.get_ordered_versions(package_name)
    except:
        pypi_results = []

    versions = [str(v) for v in pypi_results if str(v) in spec]
    return versions


def get_version_from_repo(pkg_name: str, repo_root: str = None):
    root_dir = discover_repo_root(repo_root)

    # find version for the package from source. This logic should be revisited to find version from devops feed
    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)
    if paths:
        setup_py_path = paths[0]
        parsed_setup = ParsedSetup.from_path(setup_py_path)

        # Remove dev build part if version for this package is already updated to dev build
        # When building package with dev build version, version for packages in same service is updated to dev build
        # and other packages will not have dev build number
        # strip dev build number so we can check if package exists in PyPI and replace

        version_obj = Version(parsed_setup.version)
        if version_obj.pre:
            if version_obj.pre[0] == DEV_BUILD_IDENTIFIER:
                version = version_obj.base_version

        return version
    else:
        logging.error("setup.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)


def get_base_version(pkg_name):
    root_dir = discover_repo_root()
    # find version for the package from source. This logic should be revisited to find version from devops feed
    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)
    if paths:
        setup_py_path = paths[0]
        parsed_setup = ParsedSetup.from_path(setup_py_path)
        version_obj = Version(parsed_setup.version)
        return version_obj.base_version
    else:
        logging.error("setup.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)


def process_requires(setup_py_path: str):
    """
    This method processes a setup.py's package requirements to verify if all required packages are available on PyPI.
    If any azure sdk package is not available on PyPI then requirement will be updated to refer to the sdk "dev_identifier".

    Examples:
    azure-storage-blob >= 1.0.1b1
    <there is no azure-storage-blob with any 1.0.1 patch version>
    update to require 1.0.1a1 to allow previously published dev versions to be allowed.
    """

    pkg_details = ParsedSetup.from_path(setup_py_path)
    azure_requirements = [Requirement.parse(r) for r in pkg_details.requires if r.startswith("azure")]

    # Find package requirements that are not available on PyPI
    requirement_to_update = {}
    for req in azure_requirements:
        pkg_name = req.key
        spec = SpecifierSet(str(req).replace(pkg_name, ""))

        if not is_required_version_on_pypi(pkg_name, spec):
            old_req = str(req)
            version = get_version_from_repo(pkg_name)
            base_version = get_base_version(pkg_name)
            logging.info("Updating version {0} in requirement {1} to dev build version".format(version, old_req))
            #       {} =             <must have a base version>
            #       (                <optionally, we have a prerelease version>
            #        (               <we must have 0 or 1 prerelease versions>
            #            (a|b|rc)    <we must have a prelease identifier>
            #            \d+         <followed by a number of digits N>
            #        )?
            #        (               <optionally, we have a postrelease version>
            #            \.post      <which is ".post">
            #            \d+         <followed by number of digits N>
            #        )?
            #       )?
            rx = r'{}(((a|b|rc)\d+)?(\.post\d+)?)?'.format(base_version)
            new_req = re.sub(rx, "{}{}1".format(base_version, DEV_BUILD_IDENTIFIER), str(req), flags=re.IGNORECASE)
            logging.info("New requirement for package {0}: {1}".format(pkg_name, new_req))
            requirement_to_update[old_req] = new_req

    if not requirement_to_update:
        logging.info("All required packages are available on PyPI")
    else:
        logging.info("Packages not available on PyPI:{}".format(requirement_to_update))
        update_requires(setup_py_path, requirement_to_update)
        logging.info("Package requirement is updated in setup.py")
