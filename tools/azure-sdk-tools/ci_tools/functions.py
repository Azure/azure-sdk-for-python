from ast import Not
from packaging.specifiers import SpecifierSet
from packaging.version import Version, parse
from pkg_resources import Requirement

from ci_tools.variables import discover_repo_root, get_artifact_directory, DEV_BUILD_IDENTIFIER
import os, sys, platform, glob, re

from ci_tools.parsing import ParsedSetup, get_build_config
from pypi_tools.pypi import PyPIClient


from typing import List, Any
import logging

INACTIVE_CLASSIFIER = "Development Status :: 7 - Inactive"

MANAGEMENT_PACKAGE_IDENTIFIERS = [
    "mgmt",
    "nspkg",
    "azure-cognitiveservices",
    "azure-servicefabric",
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

TEST_COMPATIBILITY_MAP = {}

omit_regression = (
    lambda x: "nspkg" not in x
    and "mgmt" not in x
    and os.path.basename(x) not in MANAGEMENT_PACKAGE_IDENTIFIERS
    and os.path.basename(x) not in META_PACKAGES
    and str_to_bool(get_config_setting(x, "regression", True))
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


def apply_compatibility_filter(package_set: List[str]) -> List[str]:
    """
    This function takes in a set of paths to python packages. It returns the set filtered by compatibility with the currently running python executable.
    If a package is unsupported by the executable, it will be omitted from the returned list.

    A manual override list of these compatibilities is also supported, but requires code change to enable. Check TEST_COMPATIBILITY_MAP in this same file.

    :param List[str] package_set: a list of paths to python packages. Each item can either be a package folder or a direct path to setup.py.
    """
    collected_packages = []
    v = sys.version_info
    running_major_version = Version(".".join([str(v[0]), str(v[1]), str(v[2])]))

    for pkg in package_set:
        try:
            spec_set = SpecifierSet(ParsedSetup.from_path(pkg).python_requires)    
        except RuntimeError as e:
            logging.error(f"Unable to parse metadata for package {pkg}, omitting from build.")
            continue

        pkg_specs_override = TEST_COMPATIBILITY_MAP.get(os.path.basename(pkg), None)

        if pkg_specs_override:
            spec_set = SpecifierSet(pkg_specs_override)

        if running_major_version in spec_set:
            collected_packages.append(pkg)

    logging.debug("Target packages after applying compatibility filter: {}".format(collected_packages))
    logging.debug("Package(s) omitted by compatibility filter: {}".format(generate_difference(package_set, collected_packages)))

    return collected_packages


def compare_python_version(version_spec: str):
    current_sys_version = parse(platform.python_version())
    spec_set = SpecifierSet(version_spec)

    return current_sys_version in spec_set


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

def generate_difference(original_packages: List[str], filtered_packages: List[str]):
    return list(set(original_packages) - set(filtered_packages))

def glob_packages(glob_string: str, target_root_dir: str) -> List[str]:
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
    return list(set(collected_top_level_directories))


def apply_business_filter(collected_packages: List[str], filter_type: str) -> List[str]:
    pkg_set_ci_filtered = list(filter(omit_function_dict.get(filter_type, omit_build), collected_packages))

    logging.debug("Target packages after applying business filter: {}".format(pkg_set_ci_filtered))
    logging.debug("Package(s) omitted by business filter: {}".format(generate_difference(collected_packages, pkg_set_ci_filtered)))
    
    return pkg_set_ci_filtered


def discover_targeted_packages(
    glob_string: str,
    target_root_dir: str,
    additional_contains_filter: str = "",
    filter_type: str = "Build",
    compatibility_filter: bool = True,
    include_inactive: bool = False
) -> List[str]:
    """
    During build and test, the set of targeted packages may expand or contract depending on the needs of the invocation.
    This function centralizes business and material requirements and outputs the set of packages that should be targeted.

    :param str glob_string: The basic glob used to query packages within the repo. Defaults to "azure-*"
    :param str target_root_dir: The root directory in which globbing will begin.
    :param str additional_contains_filter: Additional filter option. Used when needing to provide one-off filtration that doesn't merit an additional filter_type. Defaults to empty string.
    :param str filter_type: One a string representing a filter function as a set of options. Options [ "Build", "Docs", "Regression", "Omit_management" ] Defaults to "Build".
    :param bool compatibility_filter: Enables or disables compatibility filtering of found packages. If the invoking python executable does not match a found package's specifiers, the package will be omitted. Defaults to True.
    """

    # glob the starting package set
    collected_packages = glob_packages(glob_string, target_root_dir)

    # apply the additional contains filter
    collected_packages = [pkg for pkg in collected_packages if additional_contains_filter in pkg]

    # filter for compatibility, this means excluding a package that doesn't support py36 when we are running a py36 executable
    if compatibility_filter:
        collected_packages = apply_compatibility_filter(collected_packages)

    # apply package-specific exclusions only if we have gotten more than one
    if len(collected_packages) > 1:
        if not include_inactive:
            collected_packages = apply_inactive_filter(collected_packages)

    # Apply filter based on filter type. for e.g. Docs, Regression, Management
    collected_packages = apply_business_filter(collected_packages, filter_type)

    return sorted(collected_packages)


def get_config_setting(package_path: str, setting: str, default: Any = True) -> Any:
    # we should always take the override if one is present
    override_value = os.getenv(f"{os.path.basename(package_path).upper()}_{setting.upper()}", None)
    if override_value:
        return override_value
    
    # if no override, check for the config setting in the pyproject.toml
    config = get_build_config(package_path)

    if config:
        if setting.lower() in config:
            return config[setting.lower()]

    return default


def is_package_active(package_path: str):
    disabled = INACTIVE_CLASSIFIER in ParsedSetup.from_path(package_path).classifiers

    override_value = os.getenv(f"ENABLE_{os.path.basename(package_path).upper()}", None)

    if override_value:
        return str_to_bool(override_value)
    else:
        return not disabled


def apply_inactive_filter(collected_packages: List[str]) -> List[str]:
    packages = [pkg for pkg in collected_packages if is_package_active(pkg)]

    logging.debug("Target packages after applying inactive filter: {}".format(collected_packages))
    logging.debug("Package(s) omitted by inactive filter: {}".format(generate_difference(collected_packages, packages)))

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


def get_package_from_repo(pkg_name: str, repo_root: str = None) -> ParsedSetup:
    root_dir = discover_repo_root(repo_root)

    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)

    if paths:
        setup_py_path = paths[0]
        parsed_setup = ParsedSetup.from_path(setup_py_path)
        return parsed_setup

    return None


def get_version_from_repo(pkg_name: str, repo_root: str = None) -> str:
    pkg_info = get_package_from_repo(pkg_name, repo_root)
    if pkg_info:
        # Remove dev build part if version for this package is already updated to dev build
        # When building package with dev build version, version for packages in same service is updated to dev build
        # and other packages will not have dev build number
        # strip dev build number so we can check if package exists in PyPI and replace
        version_obj = Version(pkg_info.version)
        if version_obj.pre:
            if version_obj.pre[0] == DEV_BUILD_IDENTIFIER:
                return version_obj.base_version

        return str(version_obj)
    else:
        logging.error("setup.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)


def get_base_version(pkg_name: str) -> str:
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
            rx = r"{}(((a|b|rc)\d+)?(\.post\d+)?)?".format(base_version)
            new_req = re.sub(rx, "{}{}1".format(base_version, DEV_BUILD_IDENTIFIER), str(req), flags=re.IGNORECASE)
            logging.info("New requirement for package {0}: {1}".format(pkg_name, new_req))
            requirement_to_update[old_req] = new_req

    if not requirement_to_update:
        logging.info("All required packages are available on PyPI")
    else:
        logging.info("Packages not available on PyPI:{}".format(requirement_to_update))
        update_requires(setup_py_path, requirement_to_update)
        logging.info("Package requirement is updated in setup.py")
