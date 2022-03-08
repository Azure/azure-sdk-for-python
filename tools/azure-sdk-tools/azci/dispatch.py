import argparse
import pdb
import os
import sys

from .run_configuration import RunConfiguration
from .variables import ENV_NAME_REPO_ROOT
from .build import build_action

class EntryArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def main() -> None:
    """
    Primary entry point for the 'azci' command. Processes a "command" and passes it on to the appropriate function.
    """
    options_mapping = {
        "ask": ask,
        "build": build,  # equivalent to python build_packages.py
        "version": version,  # equivalent to eng/versioning scripts
        "test": test,  # equivalent to setup_execute_tests
    }

    parser = EntryArgParser(
        description="""
            This is the primary entry point for azure sdk automation during CI and local testing.  
            While this help text only documents accepting a single positional parameter. Unused args will be passed on to deeper invocations. For instance
            "pytest"-specific params like "--pdb" will be passed on to subseqeuent abstracted pytest invocations.""",
        add_help=False,
    )
    parser.add_argument("-h", "--help", dest="show_help", action="store_true", default=False, help="Show Help")
    parser.add_argument(dest="command", help=("The operation being invoked."), choices=["ask", "build", "version", "test"])
    parser.add_argument(
        "--python_repo_root",
        dest="root",
        help=(
            "The root of the azure-sdk-for-python repo. Overridden by environment variable "
            + "{}. In absence of both, repo root will be evaluated based on folder traversal and guess/check.".format(
                ENV_NAME_REPO_ROOT
            )
        ),
        required=False,
    )
    args, unused_args = parser.parse_known_args()
    
    if args.show_help:
        if args.command:
            # we will have parsed the help already, so lets add it back to the list for the argparse deeper in to process
            unused_args.append("--help")

    run_function = options_mapping.get(args.command)

    if run_function is not None:
        run_function(unused_args, args.root)
    else:
        print("azci cannot process command: {}.".format(args.command))
        parser.print_help()
        exit(1)


def determine_target_packages(glob_str: str) -> list[str]:
    pass


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
        help=(
            "Name of service directory (under sdk/) to build."
            "Example: --service applicationinsights"
        ),
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
    calculated_args, unmatched_args = parser.parse_known_args(args)
    run_config = RunConfiguration(repo_root_arg, args)
    print(run_config)
    build_action(run_config, calculated_args)


def test(args, repo_root_arg=None):
    run_config = RunConfiguration(args)
    print(run_config)

    pdb.set_trace()
    pass


def version(args, repo_root_arg=None):
    run_config = RunConfiguration(args)
    print(run_config)

    pdb.set_trace()
    pass


def ask(args, repo_root_arg=None):
    run_config = RunConfiguration(args)
    print(run_config)

    pdb.set_trace()
    pass
