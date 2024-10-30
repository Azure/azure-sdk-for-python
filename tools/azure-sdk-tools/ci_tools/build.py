import argparse, sys, os, logging, glob, shutil

from subprocess import run

from typing import List, Optional
from ci_tools.functions import discover_targeted_packages, process_requires, get_pip_list_output
from ci_tools.parsing import ParsedSetup, parse_require
from ci_tools.variables import DEFAULT_BUILD_ID, str_to_bool, discover_repo_root, get_artifact_directory
from ci_tools.versioning.version_shared import set_version_py, set_dev_classifier
from ci_tools.versioning.version_set_dev import get_dev_version, format_build_id


def build() -> None:
    parser = argparse.ArgumentParser(
        description="""This is the primary entrypoint for the "build" action. This command is used to build any package within the azure-sdk-for-python repository.""",
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        default="azure*",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages. "
            'Examples: All == "azure-*", Single = "azure-keyvault"'
        ),
    )

    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition."
        + "If that is not provided, will default to env variable SDK_ARTIFACT_DIRECTORY -> <calculated_repo_root>/.artifacts.",
    )

    parser.add_argument(
        "--service",
        help=("Name of service directory (under sdk/) to build." "Example: --service applicationinsights"),
    )

    parser.add_argument(
        "--pkgfilter",
        default="",
        dest="package_filter_string",
        help=(
            "An additional string used to filter the set of artifacts by a simple CONTAINS clause. This filters packages AFTER the set is built with compatibility and omission lists accounted."
        ),
    )

    parser.add_argument(
        "--devbuild",
        default=False,
        dest="is_dev_build",
        help=(
            "Set build type to dev build so package requirements will be updated if required package is not available on PyPI"
        ),
    )

    parser.add_argument(
        "--inactive",
        default=False,
        dest="inactive",
        action="store_true",
        help=(
            "Include inactive packages when assembling artifacts. CI builds will include inactive packages as a way to ensure that the yml"
            + " controlled artifacts can be associated with a wheel/sdist."
        ),
    )

    parser.add_argument(
        "--produce_apiview_artifact",
        default=False,
        dest="apiview_closure",
        action="store_true",
        help=(
            "Should an additional build artifact that contains the targeted package + its direct dependencies be produced?"
        ),
    )

    parser.add_argument(
        "--repo",
        default=None,
        dest="repo",
        help=(
            "Where is the start directory that we are building against? If not provided, the current working directory will be used. Please ensure you are within the azure-sdk-for-python repository."
        ),
    )

    parser.add_argument(
        "--build_id",
        default=None,
        dest="build_id",
        help="The current build id. It not provided, will default through environment variables in the following order: GITHUB_RUN_ID -> BUILD_BUILDID -> SDK_BUILD_ID -> default value.",
    )

    args = parser.parse_args()

    repo_root = discover_repo_root(args.repo)

    if args.service and args.service != "auto":
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(repo_root, service_dir)
    else:
        target_dir = repo_root

    logging.debug(
        f"Searching for packages starting from {target_dir} with glob string {args.glob_string} and package filter {args.package_filter_string}"
    )

    targeted_packages = discover_targeted_packages(
        args.glob_string,
        target_dir,
        args.package_filter_string,
        filter_type="Build",
        compatibility_filter=True,
        include_inactive=args.inactive,
    )

    artifact_directory = get_artifact_directory(args.distribution_directory)

    build_id = format_build_id(args.build_id or DEFAULT_BUILD_ID)

    build_packages(
        targeted_packages,
        artifact_directory,
        str_to_bool(args.is_dev_build),
        build_id,
    )


def cleanup_build_artifacts(build_folder):
    # clean up egginfo
    results = glob.glob(os.path.join(build_folder, "*.egg-info"))

    if results:
        shutil.rmtree(results[0])

    # clean up build results
    build_path = os.path.join(build_folder, "build")
    if os.path.exists(build_path):
        shutil.rmtree(build_path)


def build_packages(
    targeted_packages: List[str],
    distribution_directory: Optional[str] = None,
    is_dev_build: bool = False,
    build_id: str = "",
):
    logging.log(level=logging.INFO, msg=f"Generating {targeted_packages} using python{sys.version}")

    for package_root in targeted_packages:
        setup_parsed = ParsedSetup.from_path(package_root)
        package_name_in_artifacts = os.path.join(os.path.basename(package_root))

        if distribution_directory:
            dist_dir = os.path.join(distribution_directory, package_name_in_artifacts)
        else:
            dist_dir = package_name_in_artifacts

        if is_dev_build:
            process_requires(package_root, True)

            new_version = get_dev_version(setup_parsed.version, build_id)

            logging.log(level=logging.DEBUG, msg=f"{setup_parsed.name}: {setup_parsed.version} -> {new_version}")

            set_version_py(setup_parsed.setup_filename, new_version)
            set_dev_classifier(setup_parsed.setup_filename, new_version)

        create_package(package_root, dist_dir)


def create_package(
    setup_directory_or_file: str, dest_folder: str, enable_wheel: bool = True, enable_sdist: bool = True
):
    """
    Uses the invoking python executable to build a wheel and sdist file given a setup.py or setup.py directory. Outputs
    into a distribution directory and defaults to the value of get_artifact_directory().
    """

    dist = get_artifact_directory(dest_folder)
    setup_parsed = ParsedSetup.from_path(setup_directory_or_file)

    if setup_parsed.is_pyproject:
        # when building with pyproject, we will use `python -m build` to build the package
        # -n argument will not use an isolated environment, which means the current environment must have all the dependencies of the package installed, to successfully
        # pull in the dynamic `__version__` attribute. This is because setuptools is actually walking the __init__.py to get that attribute, which will fail
        # if the imports within the setup.py don't work. Perhaps an isolated environment is better, pulling all the "dependencies" into the [build-system].requires list

        # given the additional requirements of the package, we should install them in the current environment before attempting to build the package
        # we assume the presence of `wheel`, `build`, `setuptools>=61.0.0`
        pip_output = get_pip_list_output(sys.executable)
        necessary_install_requirements = [req for req in setup_parsed.requires if parse_require(req).key not in pip_output.keys()]
        run([sys.executable, "-m", "pip", "install", *necessary_install_requirements], cwd=setup_parsed.folder)
        run([sys.executable, "-m", "build", f"-n{'s' if enable_sdist else ''}{'w' if enable_wheel else ''}", "-o", dist], cwd=setup_parsed.folder)
    else:
        if enable_wheel:
            if setup_parsed.ext_modules:
                run([sys.executable, "-m", "cibuildwheel", "--output-dir", dist], cwd=setup_parsed.folder, check=True)
            else:
                run([sys.executable, "setup.py", "bdist_wheel", "-d", dist], cwd=setup_parsed.folder, check=True)

        if enable_sdist:
            run([sys.executable, "setup.py", "sdist", "-d", dist], cwd=setup_parsed.folder, check=True)
