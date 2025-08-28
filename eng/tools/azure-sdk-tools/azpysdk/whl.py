import argparse
import logging
import tempfile
import os
from typing import Optional, List, Any
import sys
from subprocess import check_call

from .Check import Check

from ci_tools.functions import discover_targeted_packages, is_error_code_5_allowed, pip_install
from ci_tools.variables import set_envvar_defaults
from ci_tools.parsing import ParsedSetup
from ci_tools.scenario.generation import create_package_and_install


class whl(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the `whl` check. The `whl` check installs the wheel version of the target package + its dev_requirements.txt,
        then invokes pytest. Failures indicate a test issue.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("whl", parents=parents, help="Run the whl check")
        p.set_defaults(func=self.run)
        # Add any additional arguments specific to WhlCheck here (do not re-add common handled by parents)

    def run(self, args: argparse.Namespace) -> int:
        """Run the whl check command."""
        print("Running whl check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            pkg = parsed.folder
            venv_location = os.path.join(parsed.folder, f".venv_{args.command}")
            # if isolation is required, the executable we get back will align with the venv
            # otherwise we'll just get sys.executable and install in current
            executable = self.handle_venv(args.isolate, args, venv_location=venv_location)

            print(f"Invoking check with {executable}")
            dev_requirements = os.path.join(pkg, "dev_requirements.txt")

            if os.path.exists(dev_requirements):
                print(f"Installing dev_requirements at {dev_requirements}")
                pip_install([f"-r", f"{dev_requirements}"], True, executable, pkg)
            else:
                print("Skipping installing dev_requirements")

            # TODO: make the staging area a folder under the venv_location
            staging_area = tempfile.mkdtemp()
            create_package_and_install(
                distribution_directory=staging_area,
                target_setup=pkg,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_area,
                force_create=False,
                package_type="wheel",
                pre_download_disabled=False,
                python_executable=executable
            )

            # todo, come up with a good pattern for passing all the additional args after -- to pytest
            logging.info(f"Invoke pytest for {pkg}")
            # + (["-m", args.mark_arg] if args.mark_arg else []) +
            exit_code = check_call(
                [executable, "-m", "pytest", "."] + [
                    "-rsfE",
                    f"--junitxml={pkg}/test-junit-{args.command}.xml",
                    "--verbose",
                    "--cov-branch",
                    "--durations=10",
                    "--ignore=azure",
                    "--ignore-glob=.venv*",
                    "--ignore=build",
                    "--ignore=.eggs",
                    "--ignore=samples"
                ]
                , cwd=pkg
            )

            if exit_code != 0:
                if exit_code == 5 and is_error_code_5_allowed(parsed.folder, parsed.name):
                    logging.info("Exit code 5 is allowed, continuing execution.")
                else:
                    logging.info(f"pytest failed with exit code {exit_code}.")
                    results.append(exit_code)

        # final result is the worst case of all the results
        return max(results)
