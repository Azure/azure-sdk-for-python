import argparse

from typing import Optional, List

from .pyright import pyright


class next_pyright(pyright):
    def __init__(self):
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the next-pyright check. The next-pyright check installs the next version of pyright and runs pyright against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "next-pyright", parents=parents, help="Run the pyright check with the next version of pyright"
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the next-pyright check command."""
        args.next = True
        return super().run(args)
