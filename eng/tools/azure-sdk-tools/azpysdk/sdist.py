import argparse
from typing import List, Optional

from .install_and_test import InstallAndTest


class sdist(InstallAndTest):
    def __init__(self) -> None:
        super().__init__(
            package_type="sdist",
            proxy_url="http://localhost:5005",
            display_name="sdist",
        )

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `sdist` check. This builds and installs the source distribution before running pytest."""

        parents = parent_parsers or []
        parser = subparsers.add_parser("sdist", parents=parents, help="Run the sdist check")
        parser.set_defaults(func=self.run)
        parser.add_argument(
            "--pytest-args",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to pytest.",
        )
