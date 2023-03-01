import argparse, sys, os, logging, pdb

from subprocess import run

from typing import List
from ci_tools.functions import discover_targeted_packages, str_to_bool, process_requires
from ci_tools.parsing import ParsedSetup
from ci_tools.variables import DEFAULT_BUILD_ID
from ci_tools.variables import discover_repo_root, get_artifact_directory
from ci_tools.versioning.version_shared import set_version_py, set_dev_classifier
from ci_tools.versioning.version_set_dev import get_dev_version, format_build_id
from ci_tools.logging import initialize_logger, run_logged


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
    ),

    parser.add_argument(
        "--build_id",
        default=None,
        dest="build_id",
        help="The current build id. It not provided, will default through environment variables in the following order: GITHUB_RUN_ID -> BUILD_BUILDID -> SDK_BUILD_ID -> default value.",
    )

    args = parser.parse_args()

    repo_root = discover_repo_root(args.repo)

    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(repo_root, service_dir)
    else:
        target_dir = repo_root

    targeted_packages = discover_targeted_packages(
        args.glob_string, target_dir, args.package_filter_string, filter_type="Build", compatibility_filter=True, include_inactive=args.inactive
    )
    artifact_directory = get_artifact_directory(args.distribution_directory)

    build_id = format_build_id(args.build_id or DEFAULT_BUILD_ID)

    build_packages(
        targeted_packages,
        artifact_directory,
        str_to_bool(args.is_dev_build),
        str_to_bool(args.apiview_closure),
        build_id,
    )


def build_packages(
    targeted_packages: List[str],
    distribution_directory: str = None,
    is_dev_build: bool = False,
    build_apiview_artifact: bool = False,
    build_id: str = "",
):
    logger = initialize_logger("build.py")
    logger.log(level=logging.INFO, msg=f"Generating Package Using Python {sys.version}")

    for package_root in targeted_packages:
        setup_parsed = ParsedSetup.from_path(package_root)

        package_name_in_artifacts = os.path.join(os.path.basename(package_root))
        dist_dir = os.path.join(distribution_directory, package_name_in_artifacts)

        if is_dev_build:
            process_requires(package_root)

            new_version = get_dev_version(setup_parsed.version, build_id)

            logger.log(level=logging.DEBUG, msg=f"{setup_parsed.name}: {setup_parsed.version} -> {new_version}")

            set_version_py(setup_parsed.setup_filename, new_version)
            set_dev_classifier(setup_parsed.setup_filename, new_version)

        create_package(package_root, dist_dir)


def create_package(
    setup_directory_or_file: str, dest_folder: str = None, enable_wheel: bool = True, enable_sdist: bool = True
):
    """
    Uses the invoking python executable to build a wheel and sdist file given a setup.py or setup.py directory. Outputs
    into a distribution directory and defaults to the value of get_artifact_directory().
    """

    dist = get_artifact_directory(dest_folder)

    if not os.path.isdir(setup_directory_or_file):
        setup_directory_or_file = os.path.dirname(setup_directory_or_file)

    setup_parsed = ParsedSetup.from_path(setup_directory_or_file)
    
    if len(setup_parsed.ext_modules) > 0:
        run_logged(
            [sys.executable, "-m", "cibuildwheel", "--output-dir", dist], prefix="cibuildwheel", cwd=setup_parsed.folder
        )
    else:
        if enable_wheel:
            run_logged(
                [sys.executable, "setup.py", "bdist_wheel", "-d", dist], prefix="create_wheel", cwd=setup_directory_or_file
            )
        if enable_sdist:
            run_logged(
                [sys.executable, "setup.py", "sdist", "--format", "zip", "-d", dist],
                prefix="create_sdist",
                cwd=setup_directory_or_file,
            )
