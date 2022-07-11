import argparse, sys, os, glob
from subprocess import run

from typing import List
from ci_tools.functions import discover_targeted_packages, str_to_bool
from ci_tools.variables import discover_repo_root, get_artifact_directory


def build(args, repo_root_arg=None) -> None:
    parser = argparse.ArgumentParser(
        description="""This is the primary entrypoint for the "build" action. This command is used to build any package within the sdk-for-python repository.""",
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
        action="store_true",
        help=(
            "Set build type to dev build so package requirements will be updated if required package is not available on PyPI"
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
            "Where is the start directory that we are building against? If not provided, the current working directory will be used."
        ),
    )

    args = parser.parse_args()

    repo_root = discover_repo_root(args.repo)

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    # todo, do we want to ascend to repo root if we can?
    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(os.getcwd(), service_dir)
    else:
        target_dir = os.getcwd()

    targeted_packages = discover_targeted_packages(args.glob_string, target_dir, args.package_filter_string)

    # evaluate dev version
    build_packages(targeted_packages, args.distribution_directory, str_to_bool(args.is_dev_build))


def create_package(setup_directory_or_file: str, dest_folder: str = None):
    """
    Uses the invoking python executable to build a wheel and sdist file given a setup.py or setup.py directory. Outputs
    into a distribution directory and defaults to the value of get_artifiact_directory().
    """

    dist = get_artifact_directory(dest_folder)

    if not os.path.isdir(setup_directory_or_file):
        setup_directory_or_file = os.path.dirname(setup_directory_or_file)

    run([sys.executable, "setup.py", "bdist_wheel", "-d", dist], cwd=setup_directory_or_file)
    run([sys.executable, "setup.py", "sdist", "--format", "zip", "-d", dist], cwd=setup_directory_or_file)


# TODO: pull in build_conda_artifacts here
# TODO: pull build_alpha_version into here
# TODO: pull build_apiview_artifactzip into here
def build_packages(
    targeted_packages: List[str],
    distribution_directory: str = None,
    is_dev_build: bool = False,
    build_apiview_artifact: bool = False,
):

    pass
    # run the build and distribution
    # TODO: function updates requirements
    # for package_root in targeted_packages:
    #     service_hierarchy = os.path.join(os.path.basename(package_root))
    #     if is_dev_build:
    #         verify_update_package_requirement(package_root)
    #     print("Generating Package Using Python {}".format(sys.version))
    #     run(
    #         [
    #             sys.executable,
    #             build_packing_script_location,
    #             "--dest",
    #             os.path.join(distribution_directory, service_hierarchy),
    #             package_root,
    #         ],
    #         cwd=root_dir,
    #     )


def verify_update_package_requirement(pkg_root):
    setup_py_path = os.path.abspath(os.path.join(pkg_root, "setup.py"))
    process_requires(setup_py_path)
