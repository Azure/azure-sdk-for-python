import argparse
import os
import tempfile
import typing
import sys
import subprocess
import json
import pathlib

from typing import Optional, List
from subprocess import CalledProcessError

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled, is_typing_ignored
from ci_tools.functions import get_pip_command
from ci_tools.logging import logger

PYRIGHT_VERSION = "1.1.287"
REPO_ROOT = discover_repo_root()


class verifytypes(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the verifytypes check. The verifytypes check installs verifytypes and runs verifytypes against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "verifytypes", parents=parents, help="Run the verifytypes check to verify type completeness of a package."
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the verifytypes check command."""
        logger.info("Running verifytypes check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            if os.getcwd() != parsed.folder:
                os.chdir(parsed.folder)
            package_dir = parsed.folder
            package_name = parsed.name
            module = parsed.namespace
            executable, staging_directory = self.get_executable(
                args.isolate,
                args.command,
                sys.executable,
                package_dir,
                python_version=getattr(args, "python_version", None),
            )
            logger.info(f"Processing {package_name} for verifytypes check")

            self.install_dev_reqs(executable, args, package_dir)

            # install pyright
            try:
                install_into_venv(executable, [f"pyright=={PYRIGHT_VERSION}"], package_dir)
            except CalledProcessError as e:
                logger.error(f"Failed to install pyright: {e}")
                return e.returncode

            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type="sdist",
                pre_download_disabled=False,
                python_executable=executable,
            )

            if in_ci():
                if not is_check_enabled(package_dir, "verifytypes") or is_typing_ignored(package_name):
                    logger.info(
                        f"{package_name} opts-out of verifytypes check. See https://aka.ms/python/typing-guide for information."
                    )
                    continue

            commands = [
                executable,
                "-m",
                "pyright",
                "--verifytypes",
                module,
                "--ignoreexternal",
                "--outputjson",
            ]

            # get type completeness score from current code
            score_from_current = self.get_type_complete_score(executable, commands, package_dir, check_pytyped=True)
            if score_from_current == -1.0:
                results.append(1)
                continue

            # show output
            try:
                response = self.run_venv_command(executable, commands[1:-1], package_dir, check=True)
                logger.info(response.stdout)
            except subprocess.CalledProcessError as e:
                logger.warning(
                    f"verifytypes reported issues: {e.stdout}"
                )  # we don't fail on verifytypes, only if type completeness score worsens from main

            if in_ci():
                # get type completeness score from main
                logger.info("Getting the type completeness score from the code in main...")
                if self.install_from_main(os.path.abspath(package_dir), executable) > 0:
                    continue

                self._log_installed_package_layout(executable, module)

                score_from_main = self.get_type_complete_score(executable, commands, package_dir)
                if score_from_main == -1.0:
                    results.append(1)
                    continue

                score_from_main_rounded = round(score_from_main * 100, 1)
                score_from_current_rounded = round(score_from_current * 100, 1)
                logger.info("\n-----Type completeness score comparison-----\n")
                logger.info(f"Score in main: {score_from_main_rounded}%")
                # Give a 5% buffer for type completeness score to decrease
                if score_from_current_rounded < score_from_main_rounded - 5:
                    logger.error(
                        f"\nERROR: The type completeness score of {package_name} has significantly decreased compared to the score in main. "
                        f"See the above output for areas to improve. See https://aka.ms/python/typing-guide for information."
                    )
                    results.append(1)
        return max(results) if results else 0

    def install_from_main(self, setup_path: str, python_executable: Optional[str] = None) -> int:
        path = pathlib.Path(setup_path)

        subdirectory = path.relative_to(REPO_ROOT)
        cwd = os.getcwd()

        def _run_git(cmd: List[str]) -> None:
            """Run a git step, capturing stderr so failures are visible in logs."""
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logger.error(
                    f"git step failed ({' '.join(cmd)}) with exit code {result.returncode}.\n"
                    f"stderr:\n{result.stderr}"
                )
                raise subprocess.CalledProcessError(result.returncode, cmd, output=None, stderr=result.stderr)

        with tempfile.TemporaryDirectory() as temp_dir_name:
            os.chdir(temp_dir_name)
            try:
                _run_git(["git", "init"])
                _run_git(
                    [
                        "git",
                        "clone",
                        "--no-checkout",
                        "https://github.com/Azure/azure-sdk-for-python.git",
                        "--depth",
                        "1",
                    ]
                )
                os.chdir("azure-sdk-for-python")
                _run_git(["git", "sparse-checkout", "init", "--cone"])
                _run_git(["git", "sparse-checkout", "set", subdirectory.as_posix()])
                _run_git(["git", "checkout", "main"])

                if not os.path.exists(os.path.join(os.getcwd(), subdirectory)):
                    # code is not checked into main yet, nothing to compare
                    logger.info(f"{subdirectory} is not checked into main, nothing to compare.")
                    return 1

                # If verifytypes was disabled on main, there's no known-good type-completeness
                # baseline to compare against — running pyright on main code that's never been
                # type-checked can fail in opaque ways (see #46426). Skip the comparison.
                main_package_dir = os.path.join(os.getcwd(), subdirectory)
                if not is_check_enabled(main_package_dir, "verifytypes"):
                    logger.info(
                        "verifytypes is disabled on main for this package; skipping "
                        "comparison with main. (The PR is enabling the check for the first time.)"
                    )
                    return 1

                os.chdir(subdirectory)

                # --no-deps: we only want the main-branch version of *this* package; dependencies
                # were already installed during the PR-version install and must remain identical
                # so that pyright sees the same dep closure for both type-completeness runs.
                command = get_pip_command(python_executable) + [
                    "install",
                    ".",
                    "--force-reinstall",
                    "--no-deps",
                ]

                # When using uv, add --no-sources to ignore [tool.uv.sources] relative paths
                # that can't resolve in a sparse checkout, and --python to target the correct venv.
                if command[0] == "uv":
                    command += ["--no-sources"]
                    if python_executable:
                        command += ["--python", python_executable]

                logger.info(f"Installing main-branch version of package: {' '.join(command)}")
                install_result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if install_result.returncode != 0:
                    # Hard-fail: callers treat a positive return from install_from_main as
                    # "nothing to compare, skip" (e.g., package not in main yet). A real install
                    # failure must surface as an exception so CI reports a check failure rather
                    # than silently skipping the comparison.
                    logger.error(
                        f"Failed to install main-branch version of {subdirectory} "
                        f"(exit code {install_result.returncode}).\n"
                        f"stdout:\n{install_result.stdout}\n"
                        f"stderr:\n{install_result.stderr}"
                    )
                    raise subprocess.CalledProcessError(
                        install_result.returncode,
                        command,
                        output=install_result.stdout,
                        stderr=install_result.stderr,
                    )
                logger.debug(f"install_from_main stdout:\n{install_result.stdout}")
                if install_result.stderr:
                    # uv/pip commonly write progress to stderr; keep at debug to avoid noise.
                    logger.debug(f"install_from_main stderr:\n{install_result.stderr}")
            finally:
                os.chdir(cwd)  # allow temp dir to be deleted
            return 0

    def _log_installed_package_layout(self, executable: str, module: str) -> None:
        """Log what was actually installed so we can diagnose empty-pyright-output cases.

        A 'successful' install that results in pyright finding zero symbols (empty
        --verifytypes output) usually means the installed package is missing
        namespace __init__.py files, missing py.typed, or was installed to an
        unexpected location. Dump enough state to diagnose that from CI logs."""
        # Distribution name derived from the module dotted path (e.g. azure.ai.transcription
        # -> azure-ai-transcription). This matches our SDK naming convention.
        dist_name = module.replace(".", "-")
        try:
            show = subprocess.run(
                [executable, "-m", "pip", "show", "-f", dist_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info(
                f"pip show -f {dist_name} (exit {show.returncode}):\n"
                f"stdout:\n{show.stdout}\n"
                f"stderr:\n{show.stderr}"
            )

            # Also list the actual files on disk for the module namespace, which is what
            # pyright will walk. Missing azure/__init__.py or azure/ai/__init__.py here
            # can make pyright --verifytypes discover zero symbols.
            probe_script = (
                "import importlib.util, os;"
                f"spec = importlib.util.find_spec({module!r});"
                "print('spec:', spec);"
                "print('origin:', getattr(spec, 'origin', None));"
                "locs = list(getattr(spec, 'submodule_search_locations', []) or []);"
                "print('submodule_search_locations:', locs);"
                "[print('  file:', os.path.join(root, f))"
                " for loc in locs"
                " for root, _, files in os.walk(loc)"
                " for f in files]"
            )
            probe = subprocess.run(
                [executable, "-c", probe_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info(
                f"Installed layout for {module} (exit {probe.returncode}):\n"
                f"stdout:\n{probe.stdout}\n"
                f"stderr:\n{probe.stderr}"
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(f"Failed to introspect installed package layout for {module}: {e}")

    def get_type_complete_score(
        self, executable, commands: typing.List[str], cwd: str, check_pytyped: bool = False
    ) -> float:
        try:
            response = self.run_venv_command(executable, commands[1:], cwd, check=True)
        except subprocess.CalledProcessError as e:
            if e.returncode != 1:
                logger.error(
                    f"Running verifytypes failed: {e.stderr}. See https://aka.ms/python/typing-guide for information."
                )
                return -1.0
            try:
                report = json.loads(e.output)
            except (json.JSONDecodeError, TypeError):
                logger.error(
                    f"pyright --verifytypes exited with code 1 but did not produce valid JSON output.\n"
                    f"stdout: {e.output}\n"
                    f"stderr: {e.stderr}\n"
                    f"Re-running without --outputjson for diagnostic output..."
                )
                non_json_commands = [c for c in commands[1:] if c != "--outputjson"] + ["--verbose"]
                diag = self.run_venv_command(executable, non_json_commands, cwd, check=False)
                logger.error(f"Diagnostic pyright stdout:\n{diag.stdout}")
                if diag.stderr:
                    logger.error(f"Diagnostic pyright stderr:\n{diag.stderr}")
                return -1.0
            if check_pytyped:
                pytyped_present = report["typeCompleteness"].get("pyTypedPath", None)
                if not pytyped_present:
                    logger.error(f"No py.typed file was found. See https://aka.ms/python/typing-guide for information.")
                    return -1.0
            return report["typeCompleteness"]["completenessScore"]

        # library scores 100%
        report = json.loads(response.stdout)
        return report["typeCompleteness"]["completenessScore"]
