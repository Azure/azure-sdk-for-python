import fnmatch
import subprocess
import shutil
import zipfile
import tarfile
import stat
from ast import Not
from packaging.specifiers import SpecifierSet
from packaging.version import Version, parse, InvalidVersion
from pkg_resources import Requirement
import io

from ci_tools.variables import discover_repo_root, DEV_BUILD_IDENTIFIER, str_to_bool
from ci_tools.parsing import ParsedSetup, get_config_setting, get_pyproject
from pypi_tools.pypi import PyPIClient

import os, sys, platform, glob, re, logging
from typing import List, Any, Optional

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

NO_TESTS_ALLOWED = []


META_PACKAGES = ["azure", "azure-mgmt", "azure-keyvault"]

REGRESSION_EXCLUDED_PACKAGES = [
    "azure-common",
]

MANAGEMENT_PACKAGES_FILTER_EXCLUSIONS = [
    "azure-mgmt-core",
]

TEST_COMPATIBILITY_MAP = {
    "azure-ai-ml": ">=3.7",
    "azure-ai-evaluation": ">=3.9, !=3.13.*"
}
TEST_PYTHON_DISTRO_INCOMPATIBILITY_MAP = {
    "azure-storage-blob": "pypy",
    "azure-storage-queue": "pypy",
    "azure-storage-file-datalake": "pypy",
    "azure-storage-file-share": "pypy",
    "azure-eventhub": "pypy",
    "azure-servicebus": "pypy",
    "azure-ai-projects": "pypy",
    "azure-ai-agents": "pypy",
}

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


def unzip_file_to_directory(path_to_zip_file: str, extract_location: str) -> str:
    if path_to_zip_file.endswith(".zip"):
        with zipfile.ZipFile(path_to_zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_location)
            extracted_dir = os.path.basename(os.path.splitext(path_to_zip_file)[0])
            return os.path.join(extract_location, extracted_dir)
    else:
        with tarfile.open(path_to_zip_file) as tar_ref:
            tar_ref.extractall(extract_location)
            extracted_dir = os.path.basename(path_to_zip_file).replace(".tar.gz", "")
            return os.path.join(extract_location, extracted_dir)


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

        distro_compat = True
        distro_incompat = TEST_PYTHON_DISTRO_INCOMPATIBILITY_MAP.get(os.path.basename(pkg), None)
        if distro_incompat and distro_incompat in platform.python_implementation().lower():
            distro_compat = False

        if running_major_version in spec_set and distro_compat:
            collected_packages.append(pkg)

    logging.debug("Target packages after applying compatibility filter: {}".format(collected_packages))
    logging.debug(
        "Package(s) omitted by compatibility filter: {}".format(generate_difference(package_set, collected_packages))
    )

    return collected_packages


def compare_python_version(version_spec: str) -> bool:
    """
    Compares the current running platform version of python against a version spec. Sanitizes
    the running platform version to just the major version.
    """
    platform_version = platform.python_version()
    parsed_version = re.match(r"[0-9\.]+", platform_version, re.IGNORECASE)

    # we want to be loud if we can't parse out a major version from the version string, not silently
    # fail and skip running samples on a platform we really should be
    if parsed_version is None:
        raise InvalidVersion(f'Unable to parse the platform version. Unparsed value was "{platform_version}".')
    else:
        current_sys_version = parse(parsed_version[0])
        spec_set = SpecifierSet(version_spec)

    return current_sys_version in spec_set


def generate_difference(original_packages: List[str], filtered_packages: List[str]):
    return list(set(original_packages) - set(filtered_packages))


def glob_packages(glob_string: str, target_root_dir: str) -> List[str]:
    if glob_string:
        individual_globs = [glob_string.strip() for glob_string in glob_string.split(",")]
    else:
        individual_globs = "azure-*"
    collected_top_level_directories = []

    for glob_string in individual_globs:
        globbed = glob.glob(os.path.join(target_root_dir, glob_string, "setup.py")) + glob.glob(
            os.path.join(target_root_dir, "sdk/*/", glob_string, "setup.py")
        )
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # handle pyproject.toml separately, as we need to filter them by the presence of a `[project]` section
    for glob_string in individual_globs:
        globbed = glob.glob(os.path.join(target_root_dir, glob_string, "pyproject.toml")) + glob.glob(
            os.path.join(target_root_dir, "sdk/*/", glob_string, "pyproject.toml")
        )
        for p in globbed:
            if get_pyproject(os.path.dirname(p)):
                collected_top_level_directories.append(os.path.dirname(p))

    # deduplicate, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    return list(set(collected_top_level_directories))


def apply_business_filter(collected_packages: List[str], filter_type: str) -> List[str]:
    pkg_set_ci_filtered = list(filter(omit_function_dict.get(filter_type, omit_build), collected_packages))

    logging.debug("Target packages after applying business filter: {}".format(pkg_set_ci_filtered))
    logging.debug(
        "Package(s) omitted by business filter: {}".format(generate_difference(collected_packages, pkg_set_ci_filtered))
    )

    return pkg_set_ci_filtered


def discover_targeted_packages(
    glob_string: str,
    target_root_dir: str,
    additional_contains_filter: str = "",
    filter_type: str = "Build",
    compatibility_filter: bool = True,
    include_inactive: bool = False,
) -> List[str]:
    """
    During build and test, the set of targeted packages may expand or contract depending on the needs of the invocation.
    This function centralizes business and material requirements and outputs the set of packages that should be targeted.

    :param str glob_string: The basic glob used to query packages within the repo. Defaults to "azure-*"
    :param str target_root_dir: The root directory in which globbing will begin.
    :param str additional_contains_filter: Additional filter option.
        Used when needing to provide one-off filtration that doesn't merit an additional filter_type. Defaults to empty string.
    :param str filter_type: One a string representing a filter function as a set of options.
        Options [ "Build", "Docs", "Regression", "Omit_management" ] Defaults to "Build".
    :param bool compatibility_filter: Enables or disables compatibility filtering of found packages.
        If the invoking python executable does not match a found package's specifiers, the package will be omitted.
        Defaults to True.
    """

    # glob the starting package set
    collected_packages = glob_packages(glob_string, target_root_dir)
    logging.info(
        f'Results for glob_string "{glob_string}" and root directory "{target_root_dir}" are: {collected_packages}'
    )

    # apply the additional contains filter
    collected_packages = [pkg for pkg in collected_packages if additional_contains_filter in pkg]
    logging.info(f'Results after additional contains filter: "{additional_contains_filter}" {collected_packages}')

    # filter for compatibility, this means excluding a package that doesn't support py36 when we are running a py36 executable
    if compatibility_filter:
        collected_packages = apply_compatibility_filter(collected_packages)
        logging.info(f"Results after compatibility filter: {collected_packages}")

    if not include_inactive:
        collected_packages = apply_inactive_filter(collected_packages)

    # Apply filter based on filter type. for e.g. Docs, Regression, Management
    collected_packages = apply_business_filter(collected_packages, filter_type)
    logging.info(f"Results after business filter: {collected_packages}")

    return sorted(collected_packages)


def is_package_active(package_path: str):
    disabled = INACTIVE_CLASSIFIER in ParsedSetup.from_path(package_path).classifiers

    override_value = os.getenv(f"ENABLE_{os.path.basename(package_path).upper().replace('-', '_')}", None)

    if override_value:
        return str_to_bool(override_value)
    else:
        return not disabled


def apply_inactive_filter(collected_packages: List[str]) -> List[str]:
    packages = [pkg for pkg in collected_packages if is_package_active(pkg)]

    logging.debug("Target packages after applying inactive filter: {}".format(collected_packages))
    logging.debug("Package(s) omitted by inactive filter: {}".format(generate_difference(collected_packages, packages)))

    return packages


def update_requires(setup_path, requires_dict):
    # This method changes package requirement by overriding the specifier
    contents = []
    with open(setup_path, "r") as setup_file:
        contents = setup_file.readlines()

    # find and replace all existing package requirement with new requirement
    for i in range(0, len(contents) - 1):
        keys = [k for k in requires_dict.keys() if k in contents[i]]
        for key in keys:
            contents[i] = contents[i].replace(key, requires_dict[key])

    with open(setup_path, "w") as setup_file:
        setup_file.writelines(contents)


def is_required_version_on_pypi(package_name, spec):
    client = PyPIClient()
    try:
        pypi_results = client.get_ordered_versions(package_name)
    except:
        pypi_results = []

    versions = [str(v) for v in pypi_results if str(v) in spec]
    return versions


def get_package_from_repo(pkg_name: str, repo_root: Optional[str] = None) -> Optional[ParsedSetup]:
    root_dir = discover_repo_root(repo_root)

    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)

    if paths:
        setup_py_path = paths[0]
        parsed_setup = ParsedSetup.from_path(setup_py_path)
        return parsed_setup

    return None


def get_package_from_repo_or_folder(req: str, prebuilt_wheel_dir: Optional[str] = None) -> Optional[str]:
    """Takes a package name and a possible prebuilt wheel directory. Attempts to resolve a wheel that matches the package name, and if it can't,
    attempts to find the package within the repo to install directly from path on disk.

    During a CI build, it is preferred that the package is installed from a prebuilt wheel directory, as multiple CI environments attempting to install the relative
    req can cause inconsistent installation issues during parallel tox environment execution.
    """

    local_package = get_package_from_repo(req)

    if prebuilt_wheel_dir and os.path.exists(prebuilt_wheel_dir) and local_package:
        prebuilt_package = discover_prebuilt_package(prebuilt_wheel_dir, local_package.setup_filename, "wheel")
        if prebuilt_package:
            # return the first package found, there should only be a single one matching given that our prebuilt wheel directory
            # is populated by the replacement of dev_reqs.txt with the prebuilt wheels
            # ref tox_harness replace_dev_reqs() calls
            return os.path.join(prebuilt_wheel_dir, prebuilt_package[0])

    if local_package:
        return local_package.folder
    else:
        return None


def get_version_from_repo(pkg_name: str, repo_root: Optional[str] = None) -> str:
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


def process_requires(setup_py_path: str, is_dev_build: bool = False):
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

        if not is_required_version_on_pypi(pkg_name, spec) or is_dev_build:
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
            new_req_format = f"{base_version}{DEV_BUILD_IDENTIFIER}1,<{base_version}b0"
            new_req = re.sub(rx, new_req_format, str(req), flags=re.IGNORECASE)
            logging.info("New requirement for package {0}: {1}".format(pkg_name, new_req))
            requirement_to_update[old_req] = new_req

    if not requirement_to_update:
        logging.info("All required packages are available on PyPI")
    else:
        logging.info("Packages not available on PyPI:{}".format(requirement_to_update))
        update_requires(setup_py_path, requirement_to_update)
        logging.info("Package requirement is updated in setup.py")


def find_sdist(dist_dir: str, pkg_name: str, pkg_version: str) -> Optional[str]:
    """This function attempts to look within a directory (and all subdirs therein) and find a source distribution for the targeted package and version."""
    # This function will find a sdist for given package name
    if not os.path.exists(dist_dir):
        logging.error("dist_dir is incorrect")
        return

    if pkg_name is None:
        logging.error("Package name cannot be empty to find sdist")
        return
    else:
        # ensure package name matches cananonicalized package name
        pkg_name = pkg_name.replace("-", "[-_]")

    pkg_format = f"{pkg_name}-{pkg_version}.tar.gz"

    packages = []
    for root, dirnames, filenames in os.walk(dist_dir):
        for filename in fnmatch.filter(filenames, pkg_format):
            packages.append(os.path.join(root, filename))

    packages = [os.path.relpath(w, dist_dir) for w in packages]

    if not packages:
        logging.error(f"No sdist is found in directory {dist_dir} with package name format {pkg_format}.")
        return
    return packages[0]


def pip_install(
    requirements: List[str], include_dependencies: bool = True, python_executable: Optional[str] = None
) -> bool:
    """
    Attempts to invoke an install operation using the invoking python's pip. Empty requirements are auto-success.
    """

    exe = python_executable or sys.executable

    command = [exe, "-m", "pip", "install"]

    if requirements:
        command.extend([req.strip() for req in requirements])
    else:
        return True

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as f:
        return False

    return True


def pip_uninstall(requirements: List[str], python_executable: str) -> bool:
    """
    Attempts to invoke an install operation using the invoking python's pip. Empty requirements are auto-success.
    """
    exe = python_executable or sys.executable
    command = [exe, "-m", "pip", "uninstall", "-y"]

    if requirements:
        command.extend([req.strip() for req in requirements])
    else:
        return True

    try:
        result = subprocess.check_call(command)
        return True
    except subprocess.CalledProcessError as f:
        return False


def pip_install_requirements_file(requirements_file: str, python_executable: Optional[str] = None) -> bool:
    return pip_install(["-r", requirements_file], True, python_executable)


def get_pip_list_output(python_executable: Optional[str] = None):
    """Uses the invoking python executable to get the output from pip list."""
    exe = python_executable or sys.executable

    out = subprocess.Popen(
        [exe, "-m", "pip", "list", "--disable-pip-version-check", "--format", "freeze"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    stdout, stderr = out.communicate()

    collected_output = {}

    if stdout and (stderr is None):
        # this should be compatible with py27 https://docs.python.org/2.7/library/stdtypes.html#str.decode
        for line in stdout.decode("utf-8").split(os.linesep)[2:]:
            if line:
                package, version = re.split("==", line)
                collected_output[package] = version
    else:
        raise Exception(stderr)

    return collected_output


def pytest(args: list, cwd: Optional[str] = None, python_executable: Optional[str] = None) -> bool:
    """
    Invokes a set of tests, returns true if successful, false otherwise.
    """

    exe = python_executable or sys.executable

    commands = [
        exe,
        "-m",
        "pytest",
    ]

    commands.extend(args)

    logging.info(commands)
    if cwd:
        result = subprocess.run(commands, cwd=cwd)
    else:
        result = subprocess.run(commands)

    return result.returncode == 0


def get_interpreter_compatible_tags() -> List[str]:
    """
    This function invokes pip from the invoking interpreter and discovers which tags the interpreter is compatible with.
    """

    commands = [sys.executable, "-m", "pip", "debug", "--verbose"]

    output = subprocess.run(
        commands,
        check=True,
        capture_output=True,
    ).stdout.decode(encoding="utf-8")

    tag_strings = output.split(os.linesep)

    index = 0
    for index, value in enumerate(tag_strings):
        if "Compatible tags" in value:
            break

    tags = tag_strings[index + 1 :]

    return [tag.strip() for tag in tags if tag]


def check_whl_against_tags(whl_name: str, tags: List[str]) -> bool:
    for tag in tags:
        if tag in whl_name:
            return True
    return False


def find_whl(whl_dir: str, pkg_name: str, pkg_version: str) -> Optional[str]:
    """This function attempts to look within a directory (and all subdirs therein) and find a wheel that matches our targeted name and version AND
    whose compilation is compatible with the invoking interpreter."""
    if not os.path.exists(whl_dir):
        logging.error("whl_dir is incorrect")
        return

    if pkg_name is None:
        logging.error("Package name cannot be empty to find whl")
        return

    pkg_name_format = f"{pkg_name.replace('-', '_')}-{pkg_version}*.whl"
    whls = []

    # todo: replace with glob, we aren't using py2 anymore!
    for root, dirnames, filenames in os.walk(whl_dir):
        for filename in fnmatch.filter(filenames, pkg_name_format):
            whls.append(os.path.join(root, filename))

    whls = [os.path.relpath(w, whl_dir) for w in whls]

    if not whls:
        logging.info(f"No whl is found in directory {whl_dir} with package name format {pkg_name_format}")
        logging.info(f"List of whls in directory: {glob.glob(os.path.join(whl_dir, '*.whl'))}")
        return

    compatible_tags = get_interpreter_compatible_tags()

    logging.debug("Dumping visible tags and whls")
    logging.debug(compatible_tags)
    logging.debug(whls)

    if whls:
        # grab the first whl that matches a tag from our compatible_tags list
        for whl in whls:
            if check_whl_against_tags(whl, compatible_tags):
                logging.info(f"Found whl {whl}")
                return whl

        # if whl is platform independent then there should only be one whl in filtered list
        if len(whls) > 1:
            # if we have reached here, that means we have whl specific to platform as well.
            # for now we are failing the test if platform specific wheels are found. Todo: enhance to find platform specific whl
            logging.error(f"We were unable to locate a compatible wheel for {pkg_name}")
            sys.exit(1)

    return None


def error_handler_git_access(func, path, exc):
    """
    This function exists because the git idx file is written with strange permissions that prevent it from being
    deleted. Due to this, we need to register an error handler that attempts to fix the file permissions before
    re-attempting the delete operations.
    """

    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def cleanup_directory(target_directory: str) -> None:
    """Invokes a directory delete. Specifically handles the case where bad permissions on a git .idx file
    prevent cleanup of the directory with a generic error.
    """
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory, ignore_errors=False, onerror=error_handler_git_access)


def discover_prebuilt_package(dist_directory: str, setup_path: str, package_type: str) -> List[str]:
    """Discovers a prebuild wheel or sdist for a given setup path."""
    packages = []
    pkg = ParsedSetup.from_path(setup_path)
    if package_type == "wheel":
        prebuilt_package = find_whl(dist_directory, pkg.name, pkg.version)
    else:
        prebuilt_package = find_sdist(dist_directory, pkg.name, pkg.version)

    if prebuilt_package is not None:
        packages.append(prebuilt_package)
    return packages


def is_package_compatible(
    package_name: str,
    package_requirements: List[Requirement],
    immutable_requirements: List[Requirement],
    should_log: bool = True,
) -> bool:
    """
    This function accepts a set of requirements for a package, and ensures that the package is compatible with the
    immutable_requirements.

    It is factored this way because we retrieve requirements differently according to the source of the package.
        If published, we can get requires() from PyPI
        If locally built wheel, we can get requires() from the metadata of the package
        If local relative requirement, we can get requires() from a ParsedSetup of the setup.py for the package

    :param List[Requirement] package_requirements: The dependencies of a dev_requirement file. This is the set of
        requirements that we are checking compatibility for.
    :param List[Requirement] immutable_requirements: A list of requirements that the other packages must be compatible
        with.
    """

    for immutable_requirement in immutable_requirements:
        for package_requirement in package_requirements:
            if package_requirement.key == immutable_requirement.key:
                # if the dev_req line has a requirement that conflicts with the immutable requirement,
                # we need to resolve it. We KNOW that the immutable requirement will be of form package==version,
                # so we can reliably pull out the version and check it against the specifier of the dev_req line.
                try:
                    immutable_version = next(iter(immutable_requirement.specifier)).version
                # we have no specifier set, so we don't even need to check this
                except StopIteration:
                    continue

                if not package_requirement.specifier.contains(immutable_version):
                    if should_log:
                        logging.info(
                            f"Dev req dependency {package_name}'s requirement specifier of {package_requirement}"
                            f"is not compatible with immutable requirement {immutable_requirement}."
                        )
                    return False

    return True


def get_total_coverage(coverage_file: str, coverage_config_file: str, package_name: str, repo_root: Optional[str] = None) -> Optional[float]:
    try:
        import coverage
        from coverage.exceptions import NoDataError
    except ImportError:
        logging.error("Coverage is not installed.")
        return None

    cov = coverage.Coverage(data_file=coverage_file, config_file=coverage_config_file)
    cov.load()
    original = os.getcwd()
    output = io.StringIO()

    old_stdout = sys.stdout
    sys.stdout = output

    report = 0.0
    try:
        if repo_root:
            os.chdir(repo_root)
        logging.info(f"Running coverage report against \"{coverage_file}\" with \"{coverage_config_file}\" from \"{os.getcwd()}\".")
        report = cov.report()
    except NoDataError as e:
        logging.info(f"Package {package_name} did not generate any coverage output: {e}")
    except Exception as e:
        logging.error(f"An error occurred while generating the coverage report for {package_name}: {e}")
    finally:
        if repo_root:
            os.chdir(original)
        sys.stdout = old_stdout
        logging.info(f"Total coverage {report} for package {package_name}")
        return report


def resolve_compatible_package(package_name: str, immutable_requirements: List[Requirement]) -> Optional[str]:
    """
    This function attempts to resolve a compatible package version for whatever set of immutable_requirements that
    the package must be compatible with.

    It should only be utilized when a package is found to be incompatible with the immutable_requirements.
    It will attempt to resolve the incompatibility by walking backwards through different versions of <package_name>
    until a compatible version is found that works with the immutable_requirements.
    """

    pypi = PyPIClient()
    immovable_pkgs = {req.key: req for req in immutable_requirements}

    # Let's use a real use-case to walk through this function. We're going to use the azure-ai-language-conversations
    # package as an example.

    # immovable_pkgs = the selected mindependency for azure-ai-language-conversations
    #   -> "azure-core==1.28.0",
    #   -> "isodate==0.6.1",
    #   -> "typing-extensions==4.0.1",
    # we have the following dev_reqs for azure-ai-language-conversations
    #   -> ../azure-sdk-tools
    #   ->  ../azure-identity
    #   -> ../azure-core

    # as we walk each of the dev reqs, we check for compatibility with the immovable_packages.
    # (this happens in is_package_compatible) if the dev req is incompatible, we need to resolve it.
    # THIS function is what resolves it!

    # since we already know that package_name is incompatible with the immovable_pkgs, we need to walk backwards
    # through the versions of package_name checking to ensure that each version is compatible with the immovable_pkgs.
    # if we find one that is, we will return a new requirement string for that package which will replace this dev_req line.
    for pkg in immovable_pkgs:
        required_package = immovable_pkgs[pkg].name
        try:
            required_pkg_version = next(iter(immovable_pkgs[pkg].specifier)).version
        except StopIteration:
            required_pkg_version = None

        versions = pypi.get_ordered_versions(package_name, True)
        versions.reverse()

        # only allow prerelease versions if the dev_req we're targeting is also prerelease
        if required_pkg_version:
            if not Version(required_pkg_version).is_prerelease:
                versions = [v for v in versions if not v.is_prerelease]

        for version in versions:
            version_release = pypi.project_release(package_name, version).get("info", {}).get("requires_dist", [])

            if version_release:
                requirements_for_dev_req = [Requirement(r) for r in version_release]

                compatible = is_package_compatible(
                    required_package, requirements_for_dev_req, immutable_requirements, should_log=False
                )
                if compatible:
                    # we have found a compatible version. We can return this as the new requirement line for the dev_req file.
                    return f"{package_name}=={version}"

    # no changes necessary
    return None


def handle_incompatible_minimum_dev_reqs(
    setup_path: str, filtered_requirement_list: List[str], packages_for_install: List[Requirement]
) -> List[str]:
    """
    This function is used to handle the case where a dev requirement is incompatible with the current set of packages
    being installed. This is used to update or remove dev_requirements that are incompatible with a targeted set of
        packages.

    :param str setup_path: The path to the setup.py file whose dev_requirements are being filtered.

    :param List[str] filtered_requirement_list: A filtered copy of the dev_requirements.txt for the targeted package.
        This list will be
    modified in place to remove any requirements incompatible with the packages_for_install.

    :param List[Requirement] packages_for_install: A list of packages that dev_requirements MUST be compatible with.
    """

    cleansed_reqs = []

    for dev_requirement_line in filtered_requirement_list:
        cleansed_dev_requirement_line = dev_requirement_line.strip().replace("-e ", "").split("#")[0].split(";")[0]

        if cleansed_dev_requirement_line:
            dev_req_package = None
            dev_req_version = None
            requirements_for_dev_req = []

            # this is a locally built wheel file, ise pkginfo to get the metadata
            if os.path.exists(cleansed_dev_requirement_line) and os.path.isfile(cleansed_dev_requirement_line):
                logging.info(
                    f"We are processing a replaced relative requirement built into a wheel: {cleansed_dev_requirement_line}"
                )
                import pkginfo

                try:
                    local_package_metadata = pkginfo.get_metadata(cleansed_dev_requirement_line)
                    if local_package_metadata:
                        dev_req_package = local_package_metadata.name
                        dev_req_version = local_package_metadata.version
                        requirements_for_dev_req = [Requirement(r) for r in local_package_metadata.requires_dist]
                    else:
                        logging.error(
                            f"Error while processing locally built requirement {cleansed_dev_requirement_line}. Unable to resolve metadata."
                        )
                        cleansed_reqs.append(cleansed_dev_requirement_line)
                except Exception as e:
                    logging.error(
                        f"Unable to determine metadata for locally built requirement {cleansed_dev_requirement_line}: {e}"
                    )
                    cleansed_reqs.append(cleansed_dev_requirement_line)
                    continue

            # this is a relative requirement to a package path in the repo, use our ParsedSetup class to get data from setup.py or pyproject.toml
            elif cleansed_dev_requirement_line.startswith("."):
                logging.info(f"We are processing a relative requirement: {cleansed_dev_requirement_line}")
                try:
                    local_package = ParsedSetup.from_path(os.path.join(setup_path, cleansed_dev_requirement_line))

                    if local_package:
                        dev_req_package = local_package.name
                        dev_req_version = local_package.version
                        requirements_for_dev_req = [Requirement(r) for r in local_package.requires]
                    else:
                        logging.error(
                            f"Error while processing relative requirement {cleansed_dev_requirement_line}. Unable to resolve metadata."
                        )
                        cleansed_reqs.append(cleansed_dev_requirement_line)

                except Exception as e:
                    logging.error(
                        f'Unable to determine metadata for relative requirement "{cleansed_dev_requirement_line}", not modifying: {e}'
                    )
                    cleansed_reqs.append(cleansed_dev_requirement_line)
                    continue
            # If we got here, this has to be a standard requirement, attempt to parse it as a specifier and if unable to do so,
            # simply add it to the list as a last fallback. we will log so that we can implement a fix for the edge case later.
            else:
                logging.info(f"We are processing a standard requirement: {cleansed_dev_requirement_line}")
                cleansed_reqs.append(dev_requirement_line)

            # we understand how to parse it, so we should handle it
            if dev_req_package:
                if not is_package_compatible(dev_req_package, requirements_for_dev_req, packages_for_install):
                    new_req = resolve_compatible_package(dev_req_package, packages_for_install)

                    if new_req:
                        cleansed_reqs.append(new_req)
                    else:
                        logging.error(
                            f'Found incompatible dev requirement {dev_req_package}, but unable to locate a compatible version. Not modifying the line: "{dev_requirement_line}".'
                        )
                        cleansed_reqs.append(cleansed_dev_requirement_line)
                else:
                    cleansed_reqs.append(cleansed_dev_requirement_line)

    return cleansed_reqs
