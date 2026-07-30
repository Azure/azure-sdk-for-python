import argparse
import configparser
import os
import re
import sys
from pathlib import Path

from typing import Optional, List
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger, run_logged

REPO_ROOT = discover_repo_root()
PYLINT_VERSION = "4.0.4"
PYLINT_GUIDELINES_CHECKER_VERSION = "0.5.7"
NEXT_PYLINT_VERSION = "4.0.6"
NEXT_PYLINT_GUIDELINES_CHECKER_VERSION = "0.5.9"
SNIPPET_SAMPLE_IMPORT_DISABLES = (
    "reimported",
    "wrong-import-position",
    "wrong-import-order",
    "ungrouped-imports",
)


def get_snippet_aware_sample_pylint_commands(executable: str, rcfile: str, samples_dir: str) -> List[List[str]]:
    """Build the normal sample command plus an exception for README snippet files."""
    # When files are passed explicitly to pylint, ignore-patterns from the rcfile are NOT applied
    # (they only apply during directory-based discovery). Parse and apply the patterns ourselves
    # to preserve the same exclusion behaviour (e.g. conftest/setup files in samples/).
    ignore_patterns: List[re.Pattern] = []
    _config = configparser.ConfigParser()
    _config.read(rcfile)
    _raw = _config.get("MASTER", "ignore-patterns", fallback="")
    if _raw:
        ignore_patterns = [
            re.compile(p.strip())
            for p in _raw.replace("\n", ",").split(",")
            if p.strip()
        ]

    regular_samples: List[str] = []
    snippet_samples: List[str] = []

    for sample_file in sorted(Path(samples_dir).rglob("*.py")):
        if any(pat.match(sample_file.name) for pat in ignore_patterns):
            continue
        targets = snippet_samples if b"# [START" in sample_file.read_bytes() else regular_samples
        targets.append(str(sample_file))

    base_command = [
        executable,
        "-m",
        "pylint",
        f"--rcfile={rcfile}",
        "--output-format=parseable",
    ]
    commands = []
    if regular_samples:
        commands.append(base_command + regular_samples)
    if snippet_samples:
        commands.append(base_command + [f"--disable={','.join(SNIPPET_SAMPLE_IMPORT_DISABLES)}"] + snippet_samples)
    return commands


class pylint(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the pylint check. The pylint check installs pylint and runs pylint against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser("pylint", parents=parents, help="Run the pylint check")
        p.set_defaults(func=self.run)

        p.add_argument(
            "--next",
            default=False,
            help="Next version of pylint is being tested.",
            required=False,
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the pylint check command."""
        logger.info("Running pylint check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            if os.getcwd() != parsed.folder:
                os.chdir(parsed.folder)
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(
                args.isolate,
                args.command,
                sys.executable,
                package_dir,
                python_version=getattr(args, "python_version", None),
            )
            logger.info(f"Processing {package_name} for pylint check")
            package_failed = False

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)
            try:
                if args.next:
                    # use latest version of azure-pylint-guidelines-checker for next pylint checks
                    cmds = [
                        f"azure-pylint-guidelines-checker=={NEXT_PYLINT_GUIDELINES_CHECKER_VERSION}",
                    ]
                else:
                    cmds = [
                        f"azure-pylint-guidelines-checker=={PYLINT_GUIDELINES_CHECKER_VERSION}",
                    ]
                cmds.append(
                    "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"
                )

                install_into_venv(
                    executable,
                    cmds,
                    package_dir,
                )
            except CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e}")
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

            # install pylint
            try:
                if args.next:
                    # use latest version of pylint
                    install_into_venv(executable, [f"pylint=={NEXT_PYLINT_VERSION}"], package_dir)
                else:
                    install_into_venv(executable, [f"pylint=={PYLINT_VERSION}"], package_dir)
            except CalledProcessError as e:
                logger.error(f"Failed to install pylint: {e}")
                return e.returncode

            self.pip_freeze(executable)

            top_level_module = parsed.namespace.split(".")[0]

            if in_ci():
                if not is_check_enabled(package_dir, "pylint"):
                    logger.info(f"Package {package_name} opts-out of pylint check.")
                    continue

            rcFileLocation = (
                os.path.join(REPO_ROOT, "eng/pylintrc") if args.next else os.path.join(REPO_ROOT, "pylintrc")
            )

            # Run pylint on main package
            try:
                main_pylint_targets = [os.path.join(package_dir, top_level_module)]

                logger.info(
                    [
                        executable,
                        "-m",
                        "pylint",
                        "--rcfile={}".format(rcFileLocation),
                        "--output-format=parseable",
                    ]
                    + main_pylint_targets
                )

                results.append(
                    check_call(
                        [
                            executable,
                            "-m",
                            "pylint",
                            "--rcfile={}".format(rcFileLocation),
                            "--output-format=parseable",
                        ]
                        + main_pylint_targets
                    )
                )
            except CalledProcessError as e:
                logger.error(
                    "{} main package exited with linting error {}. Please see this link for more information https://aka.ms/azsdk/python/pylint-guide".format(
                        package_name, e.returncode
                    )
                )
                results.append(e.returncode)
                package_failed = True

            # Run pylint on tests and samples with appropriate pylintrc if they exist and next pylint is being used
            if args.next:
                tests_dir = os.path.join(package_dir, "tests")
                samples_dir = os.path.join(package_dir, "samples")

                # Run tests with test_pylintrc
                if os.path.exists(tests_dir):
                    try:
                        test_rcfile = os.path.join(REPO_ROOT, "eng/test_pylintrc")
                        logger.info(
                            [
                                executable,
                                "-m",
                                "pylint",
                                "--rcfile={}".format(test_rcfile),
                                "--output-format=parseable",
                                tests_dir,
                            ]
                        )
                        results.append(
                            check_call(
                                [
                                    executable,
                                    "-m",
                                    "pylint",
                                    "--rcfile={}".format(test_rcfile),
                                    "--output-format=parseable",
                                    tests_dir,
                                ]
                            )
                        )
                    except CalledProcessError as e:
                        logger.error(
                            "{} tests exited with linting error {}. Please see this link for more information https://aka.ms/azsdk/python/pylint-guide".format(
                                package_name, e.returncode
                            )
                        )
                        results.append(e.returncode)
                        package_failed = True

                # Run samples with samples_pylintrc
                if os.path.exists(samples_dir):
                    samples_rcfile = os.path.join(REPO_ROOT, "eng/samples_pylintrc")
                    for command in get_snippet_aware_sample_pylint_commands(executable, samples_rcfile, samples_dir):
                        try:
                            logger.info(command)
                            results.append(check_call(command))
                        except CalledProcessError as e:
                            logger.error(
                                "{} samples exited with linting error {}. Please see this link for more information https://aka.ms/azsdk/python/pylint-guide".format(
                                    package_name, e.returncode
                                )
                            )
                            results.append(e.returncode)
                            package_failed = True

            if args.next and in_ci():
                if package_failed:
                    from gh_tools.vnext_issue_creator import create_vnext_issue

                    check_version = self.get_check_version(executable, "pylint")
                    create_vnext_issue(package_dir, "pylint", check_version)
                else:
                    from gh_tools.vnext_issue_creator import close_vnext_issue

                    close_vnext_issue(package_name, "pylint")

        return max(results) if results else 0
