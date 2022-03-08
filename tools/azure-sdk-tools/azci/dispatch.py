import argparse
import pdb
import os

from .run_configuration import RunConfiguration
from .variables import ENV_NAME_REPO_ROOT


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

    parser = argparse.ArgumentParser(
        description="""
            This is the primary entry point for azure sdk automation during CI and local testing.  
            While this help text only documents accepting a single positional parameter. Unmatched args will be passed on to deeper invocations. For instance
            "pytest"-specific params like "--pdb" will be passed on to subseqeuent abstracted pytest invocations."""
    )
    parser.add_argument(
        dest="command", help=("The operation being invoked."), choices=["ask", "build", "version", "test"]
    )
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
    args, unmatched = parser.parse_known_args()
    options_mapping.get(args.command)(unmatched, args.root)


def determine_target_packages(glob_str: str) -> list[str]:
    pass


def build(args, repo_root_arg=None):
    run_config = RunConfiguration(repo_root_arg, args)
    print(run_config)

    pdb.set_trace()
    pass


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
