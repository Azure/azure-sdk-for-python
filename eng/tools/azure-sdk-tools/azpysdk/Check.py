import abc
import os
import argparse
import traceback
import sys

from typing import Sequence, Optional, List, Any, Tuple
from subprocess import check_call

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages, get_venv_call
from ci_tools.variables import discover_repo_root
from ci_tools.scenario import install_into_venv, get_venv_python

# right now, we are assuming you HAVE to be in the azure-sdk-tools repo
# we assume this because we don't know how a dev has installed this package, and might be
# being called from within a site-packages folder. Due to that, we can't trust the location of __file__
REPO_ROOT = discover_repo_root()

class Check(abc.ABC):
    """
    Base class for checks.

    Subclasses must implement register() to add a subparser for the check.
    """

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """
        Register this check with the CLI subparsers.

        `subparsers` is the object returned by ArgumentParser.add_subparsers().
        `parent_parsers` can be a list of ArgumentParser objects to be used as parents.
        Subclasses MUST implement this method.
        """
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> int:
        """Run the check command.

        Subclasses can override this to perform the actual work.
        """
        return 0

    def create_venv(self, isolate: bool,venv_location: Optional[str]) -> str:
        """Abstraction for creating a virtual environment."""
        if (isolate):

            venv_cmd = get_venv_call()
            if not venv_location:
                venv_location = os.path.join(REPO_ROOT, f".venv_{args.command}")

            # todo, make this a consistent directory based on the command
            # I'm seriously thinking we should move handle_venv within each check's main(),
            # which will mean that we will _know_ what folder we're in.
            # however, that comes at the cost of not having every check be able to handle one or multiple packages
            # I don't want to get into an isolation loop where every time we need a new venv, we create it, call it,
            # and now as we foreach across the targeted packages we've lost our spot.
            check_call(venv_cmd + [venv_location])

            # TODO: we should reuse part of build_whl_for_req to integrate with PREBUILT_WHL_DIR so that we don't have to fresh build for each
            # venv
            install_into_venv(venv_location, os.path.join(REPO_ROOT, "eng/tools/azure-sdk-tools"), False, "build")
            venv_python_exe = get_venv_python(venv_location)

            # here is a newly prepped virtual environment (which includes azure-sdk-tools)
            return venv_python_exe
            # command_args = [venv_python_exe, "-m", "azpysdk.main"] + sys.argv[1:]
            # check_call(command_args)

        # if we don't need to isolate, just return the python executable that we're invoking
        return sys.executable

    def get_executable(self, isolate: bool, check_name: str, executable: str, package_folder: str) -> Tuple[str, str]:
        """Get the Python executable that should be used for this check."""
        venv_location = os.path.join(package_folder, f".venv_{check_name}")

        # if isolation is required, the executable we get back will align with the venv
        # otherwise we'll just get sys.executable and install in current
        executable = self.create_venv(isolate, venv_location)
        staging_directory = os.path.join(venv_location, ".staging")
        os.makedirs(staging_directory, exist_ok=True)
        return executable, staging_directory


    def get_targeted_directories(self, args: argparse.Namespace) -> List[ParsedSetup]:
        """
        Get the directories that are targeted for the check.
        """
        targeted: List[ParsedSetup] = []
        targeted_dir = os.getcwd()

        if args.target == ".":
            try:
                targeted.append(ParsedSetup.from_path(targeted_dir))
            except Exception as e:
                print("Error: Current directory does not appear to be a Python package (no setup.py or setup.cfg found). Remove '.' argument to run on child directories.")
                print(f"Exception: {e}")
                return []
        else:
            targeted_packages = discover_targeted_packages(args.target, targeted_dir)
            for pkg in targeted_packages:
                try:
                    targeted.append(ParsedSetup.from_path(pkg))
                except Exception as e:
                    print(f"Unable to parse {pkg} as a Python package. Dumping exception detail and skipping.")
                    print(f"Exception: {e}")
                    print(traceback.format_exc())

        return targeted
