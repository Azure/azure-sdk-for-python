import argparse
from typing import List, Optional

from .dependency_check import DependencyCheck
from .proxy_ports import get_proxy_url_for_check


class mindependency(DependencyCheck):
    def __init__(self) -> None:
        super().__init__(
            dependency_type="Minimum",
            proxy_url=get_proxy_url_for_check("mindependency"),
            display_name="mindependency",
            additional_packages=[
                "azure-mgmt-keyvault<7.0.0",
                "azure-mgmt-resource<15.0.0",
                "azure-mgmt-storage<15.0.0",
            ],
        )

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `mindependency` check."""

        parents = parent_parsers or []
        parser = subparsers.add_parser("mindependency", parents=parents, help="Run the mindependency check")
        parser.set_defaults(func=self.run)
        parser.add_argument(
            "--pytest-args",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to pytest.",
        )
