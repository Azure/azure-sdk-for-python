import abc
import os
import argparse
import traceback
import sys
import shutil
import tempfile
import pathlib

from typing import Sequence, Optional, List, Any, Tuple
import subprocess

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import (
    discover_targeted_packages,
    get_venv_call,
    install_into_venv,
    get_venv_python,
    get_pip_command,
    find_whl,
)
from ci_tools.variables import discover_repo_root, in_ci
from ci_tools.logging import logger

# right now, we are assuming you HAVE to be in the azure-sdk-tools repo
# we assume this because we don't know how a dev has installed this package, and might be
# being called from within a site-packages folder. Due to that, we can't trust the location of __file__
REPO_ROOT = discover_repo_root()

PACKAGING_REQUIREMENTS = [
    "wheel==0.45.1",
    "packaging==24.2",
    "urllib3==2.2.3",
    "tomli==2.2.1",
    "build==1.2.2.post1",
    "pkginfo==1.12.1.2",
]

TEST_TOOLS_REQUIREMENTS = os.path.join(REPO_ROOT, "eng/test_tools.txt")
DEPENDENCY_TOOLS_REQUIREMENTS = os.path.join(REPO_ROOT, "eng/dependency_tools.txt")


class Check(abc.ABC):
    """
    Base class for checks.

    Subclasses must implement register() to add a subparser for the check.
    """

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
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

    def create_venv(self, isolate: bool, venv_location: str) -> str:
        """Abstraction for creating a virtual environment."""
        if isolate:
            venv_cmd = get_venv_call(sys.executable)
            venv_python = get_venv_python(venv_location)
            if os.path.exists(venv_python):
                logger.info(f"Reusing existing venv at {venv_python}")
                return venv_python
            else:
                shutil.rmtree(venv_location, ignore_errors=True)

            subprocess.check_call(venv_cmd + [venv_location])

            if in_ci():
                # first attempt to retrieve azure-sdk-tools from the prebuilt wheel directory
                # if present, install from there instead of constantly rebuilding azure-sdk-tools in a possible
                # parallel situation
                wheel_dir = os.getenv("PREBUILT_WHEEL_DIR", None) or os.path.join(REPO_ROOT, ".wheels")
                prebuilt_whl = find_whl(wheel_dir, "azure-sdk-tools", "0.0.0")

                if prebuilt_whl:
                    install_location = os.path.join(wheel_dir, prebuilt_whl)
                    install_into_venv(venv_location, [f"{install_location}[build]"], REPO_ROOT)
                else:
                    logger.error(
                        "Falling back to manual build and install of azure-sdk-tools into isolated env,"
                        f" unable to locate prebuilt azure-sdk-tools within {wheel_dir}"
                    )
            else:
                install_into_venv(venv_location, [os.path.join(REPO_ROOT, "eng/tools/azure-sdk-tools")], REPO_ROOT)

            venv_python_exe = get_venv_python(venv_location)

            return venv_python_exe

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

    def run_venv_command(
        self,
        executable: str,
        command: Sequence[str],
        cwd: str,
        check: bool = False,
        append_executable: bool = True,
        immediately_dump: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """Run a command in the given virtual environment.
        - Prepends the virtual environment's bin directory to the PATH environment variable (if one exists)
        - Uses the provided Python executable to run the command.
        - Collects the output.
        - If check is True, raise CalledProcessError on failure."""

        if command[0].endswith("python") or command[0].endswith("python.exe"):
            raise ValueError(
                "The command array should not include the python executable, it is provided by the 'executable' argument"
            )

        env = os.environ.copy()

        python_exec = pathlib.Path(executable)
        if python_exec.exists():
            venv_bin = str(python_exec.parent)
            venv_root = str(python_exec.parent.parent)
            env["VIRTUAL_ENV"] = venv_root
            env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
            env.pop("PYTHONPATH", None)
            env.pop("PYTHONHOME", None)
        else:
            raise RuntimeError(f"Unable to find parent venv for executable {executable}")

        # When not appending executable, resolve the command using the modified PATH
        if not append_executable:
            resolved = shutil.which(command[0], path=env["PATH"])
            if not resolved:
                raise RuntimeError(f"Command '{command[0]}' not found in PATH: {env['PATH']}")
            cmd_to_run = [resolved] + list(command[1:])
        else:
            cmd_to_run = [executable] + list(command)

        logger.debug(f"Running command: {cmd_to_run}.")
        logger.debug(f"VIRTUAL_ENV: {env['VIRTUAL_ENV']}.")
        logger.debug(f"PATH : {env['PATH']}.")

        s_out = None if immediately_dump else subprocess.PIPE
        s_err = None if immediately_dump else subprocess.PIPE
        result = subprocess.run(cmd_to_run, cwd=cwd, stdout=s_out, stderr=s_err, text=True, check=check, env=env)

        return result

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
                logger.error(
                    "Error: Current directory does not appear to be a Python package (no setup.py or setup.cfg found). Remove '.' argument to run on child directories."
                )
                logger.error(f"Exception: {e}")
                return []
        else:
            targeted_packages = discover_targeted_packages(args.target, targeted_dir)
            for pkg in targeted_packages:
                try:
                    targeted.append(ParsedSetup.from_path(pkg))
                except Exception as e:
                    logger.error(f"Unable to parse {pkg} as a Python package. Dumping exception detail and skipping.")
                    logger.error(f"Exception: {e}")
                    logger.error(traceback.format_exc())

        return targeted

    def install_dev_reqs(self, executable: str, args: argparse.Namespace, package_dir: str) -> None:
        """Install dev requirements for the given package."""
        dev_requirements = os.path.join(package_dir, "dev_requirements.txt")

        requirements = []
        if os.path.exists(dev_requirements):
            requirements += ["-r", dev_requirements]
        else:
            logger.warning(
                f"No dev_requirements.txt found for {package_dir}, skipping installation of dev requirements."
            )
            return

        temp_req_file = None
        if not getattr(args, "isolate", False):
            # don't install azure-sdk-tools when not isolated
            with open(dev_requirements, "r") as f:
                filtered_req_lines = [line.strip() for line in f if "eng/tools/azure-sdk-tools" not in line]
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_req_file:
                temp_req_file.write("\n".join(filtered_req_lines))
            if temp_req_file.name:
                requirements = ["-r", temp_req_file.name]
        try:
            logger.info(f"Installing dev requirements for {package_dir}")
            install_into_venv(executable, requirements, package_dir)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to install dev requirements:", e)
            raise e
        finally:
            if temp_req_file and temp_req_file.name:
                try:
                    os.remove(temp_req_file.name)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to remove temporary requirements file: {cleanup_error}")

    def pip_freeze(self, executable: str) -> None:
        """Run pip freeze in the given virtual environment and log the output. This function handles both isolated and non-isolated
        environments, as well as calling the proper `uv` executable with additional --python argument if needed.

        :param executable: Path to the python executable that should invoke this check.
        :returns None:
        """
        try:
            # to uv pip install or freeze to a target environment, we have to add `--python <path to python exe>`
            # to tell uv which environment to target
            command = get_pip_command(executable)

            if command[0] == "uv":
                command += ["freeze", "--python", executable]
            else:
                command += ["freeze"]

            result = subprocess.run(command, cwd=os.getcwd(), check=True, capture_output=True, text=True)
            logger.info("Installed packages:")
            logger.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run pip freeze: {e}")
            logger.error(e.stdout)
            logger.error(e.stderr)

    def _build_pytest_args(self, package_dir: str, args: argparse.Namespace) -> List[str]:
        """
        Builds the pytest arguments used for the given package directory.

        :param package_dir: The package directory to build pytest args for.
        :param args: The argparse.Namespace object containing command-line arguments.
        :return: A list of pytest arguments.
        """
        log_level = os.getenv("PYTEST_LOG_LEVEL", "51")
        junit_path = os.path.join(package_dir, f"test-junit-{args.command}.xml")

        default_args = [
            "-rsfE",
            f"--junitxml={junit_path}",
            "--verbose",
            "--cov-branch",
            "--durations=10",
            "--ignore=azure",
            "--ignore=.tox",
            "--ignore-glob=.venv*",
            "--ignore=build",
            "--ignore=.eggs",
            "--ignore=samples",
            f"--log-cli-level={log_level}",
        ]

        additional = args.pytest_args if args.pytest_args else []

        return [*default_args, *additional, package_dir]
