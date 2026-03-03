import argparse

from typing import Optional, List

from .sphinx import sphinx


class next_sphinx(sphinx):
    def __init__(self):
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the next-sphinx check. The next-sphinx check installs the next version of sphinx and runs sphinx against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "next-sphinx", parents=parents, help="Run the sphinx check with the next version of sphinx"
        )
        p.set_defaults(func=self.run)

        p.add_argument("--inci", dest="in_ci", action="store_true", default=False)

    def run(self, args: argparse.Namespace) -> int:
        """Run the next-sphinx check command."""
        args.next = True
        return super().run(args)
