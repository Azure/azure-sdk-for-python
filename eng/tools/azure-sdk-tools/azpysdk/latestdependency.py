import argparse
from typing import List, Optional

from .dependency_check import DependencyCheck


class latestdependency(DependencyCheck):
    def __init__(self) -> None:
        super().__init__(
            dependency_type="Latest",
            proxy_url="http://localhost:5012",
            display_name="latestdependency",
        )

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `latestdependency` check."""

        parents = parent_parsers or []
        parser = subparsers.add_parser("latestdependency", parents=parents, help="Run the latestdependency check")
        parser.set_defaults(func=self.run)
        parser.add_argument(
            "--pytest-args",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to pytest.",
        )
