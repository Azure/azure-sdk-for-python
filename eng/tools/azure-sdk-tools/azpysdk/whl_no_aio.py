import argparse
from typing import List, Optional

from .install_and_test import InstallAndTest
from ci_tools.logging import logger


class whl_no_aio(InstallAndTest):
    def __init__(self) -> None:
        super().__init__(
            package_type="wheel",
            proxy_url="http://localhost:5004",
            display_name="whl_no_aio",
        )

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `whl_no_aio` check. Matches the wheel check but ensures aiohttp is absent before pytest."""

        parents = parent_parsers or []
        parser = subparsers.add_parser("whl_no_aio", parents=parents, help="Run the whl_no_aio check")
        parser.set_defaults(func=self.run)
        parser.add_argument(
            "--pytest-args",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to pytest.",
        )

    def before_pytest(
        self, executable: str, package_dir: str, staging_directory: str, args: argparse.Namespace
    ) -> None:
        uninstall_cmd = ["-m", "pip", "uninstall", "aiohttp", "--yes"]
        result = self.run_venv_command(executable, uninstall_cmd, cwd=package_dir)
        if result.returncode != 0:
            logger.warning(
                "Failed to uninstall aiohttp prior to pytest for %s. Exit code %s.",
                package_dir,
                result.returncode,
            )
            if result.stdout:
                logger.warning(result.stdout)
            if result.stderr:
                logger.warning(result.stderr)
