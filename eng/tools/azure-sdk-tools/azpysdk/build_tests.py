import argparse
from typing import List, Optional

from .install_and_test import InstallAndTest
from ci_tools.logging import logger


class build_tests(InstallAndTest):
    """Build and install a package's test environment without running pytest.

    This check installs packaging tools, test tools (from eng/test_tools.txt),
    dev requirements, and builds/installs the package as a wheel — but does NOT
    invoke pytest or coverage. Useful for pre-validating the test environment in
    isolation (e.g. to surface dependency or build errors before running tests).
    """

    def __init__(self) -> None:
        super().__init__(
            package_type="wheel",
            proxy_url=None,
            display_name="build-tests",
            coverage_enabled=False,
        )

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the ``build-tests`` subcommand.

        The ``build-tests`` check installs packaging tools, test tools, dev
        requirements, and builds/installs the target package as a wheel without
        running pytest or coverage.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "build-tests",
            parents=parents,
            help=(
                "Build the test environment for a package (installs deps, builds wheel) "
                "without running pytest. Useful for pre-validating the test environment."
            ),
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Install requirements and build/install the package; skip pytest and coverage."""
        import os
        import sys

        logger.info("Running build-tests check...")

        targeted = self.get_targeted_directories(args)
        if not targeted:
            logger.warning("No target packages discovered for build-tests check.")
            return 0

        results: List[int] = []

        for parsed in targeted:
            if os.getcwd() != parsed.folder:
                os.chdir(parsed.folder)
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} using interpreter {executable}")

            install_result = self.install_all_requirements(
                executable, staging_directory, package_name, package_dir, args
            )
            if install_result != 0:
                logger.error(f"build-tests FAILED for {package_name} (exit code {install_result}).")
                results.append(install_result)
            else:
                logger.info(f"build-tests SUCCEEDED for {package_name}.")

        return max(results) if results else 0
