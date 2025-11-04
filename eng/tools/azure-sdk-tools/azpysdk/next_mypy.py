import argparse

from typing import Optional, List

from .mypy import mypy


class next_mypy(mypy):
    def __init__(self):
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the next-mypy check. The next-mypy check installs the next version of mypy and runs mypy against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser("next-mypy", parents=parents, help="Run the mypy check with the next version of mypy")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the next-mypy check command."""
        args.next = True
        return super().run(args)
