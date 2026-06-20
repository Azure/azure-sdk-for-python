import argparse

from typing import Optional, List

from .pylint import pylint


class next_pylint(pylint):
    def __init__(self):
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the next-pylint check. The next-pylint check installs the next version of pylint and runs pylint against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "next-pylint", parents=parents, help="Run the pylint check with the next version of pylint"
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the next-pylint check command."""
        args.next = True
        return super().run(args)
