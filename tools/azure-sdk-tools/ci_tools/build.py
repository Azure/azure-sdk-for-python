import argparse, sys, os, glob
from subprocess import check_call

from ci_tools.functions import discover_targeted_packages, str_to_bool

DEFAULT_DEST_FOLDER = "./dist"


def build(args, repo_root_arg=None) -> None:
    parser = argparse.ArgumentParser(
        description="""This is the primary entrypoint for the "build" action. This command is used to build any package within the sdk-for-python repository.""",
    )
    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition.",
        required=True,
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages. "
            'Examples: All == "azure-*", Single = "azure-keyvault"'
        ),
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
        "--repodir",
        default=None,
        dest="repo",
        help=(
            "Where is the start directory that we are building against? If not provided, the current working directory will be used."
        ),
    )

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


def create_package(name, dest_folder=DEFAULT_DEST_FOLDER):
    # a package will exist in either one, or the other folder. this is why we can resolve both at the same time.
    absdirs = [
        os.path.dirname(package)
        for package in (glob.glob("{}/setup.py".format(name)) + glob.glob("sdk/*/{}/setup.py".format(name)))
    ]

    absdirpath = os.path.abspath(absdirs[0])
    check_call([sys.executable, "setup.py", "bdist_wheel", "-d", dest_folder], cwd=absdirpath)
    check_call([sys.executable, "setup.py", "sdist", "--format", "zip", "-d", dest_folder], cwd=absdirpath)


def build_packages(targeted_packages, distribution_directory, is_dev_build=False):
    # run the build and distribution
    for package_root in targeted_packages:
        service_hierarchy = os.path.join(os.path.basename(package_root))
        if is_dev_build:
            verify_update_package_requirement(package_root)
        print("Generating Package Using Python {}".format(sys.version))
        run_check_call(
            [
                sys.executable,
                build_packing_script_location,
                "--dest",
                os.path.join(distribution_directory, service_hierarchy),
                package_root,
            ],
            root_dir,
        )


def verify_update_package_requirement(pkg_root):
    setup_py_path = os.path.abspath(os.path.join(pkg_root, "setup.py"))
    process_requires(setup_py_path)
