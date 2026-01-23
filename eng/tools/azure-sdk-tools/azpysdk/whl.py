import argparse
from typing import List, Optional

from .install_and_test import InstallAndTest
from .proxy_ports import get_proxy_url_for_check


class whl(InstallAndTest):
    def __init__(self) -> None:
        super().__init__(
            package_type="wheel",
            proxy_url=get_proxy_url_for_check("whl"),
            display_name="whl",
        )

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `whl` check. The `whl` check installs the wheel version of the target package + its
        dev requirements, then invokes pytest. Failures indicate a test issue."""

        parents = parent_parsers or []
        parser = subparsers.add_parser("whl", parents=parents, help="Run the whl check")
        parser.set_defaults(func=self.run)
        parser.add_argument(
            "--pytest-args",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to pytest.",
        )
