import argparse
import os
import sys

from .Check import Check

from ci_tools.functions import discover_targeted_packages

class depends(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the `whl` check.

        `subparsers` is the object returned by ArgumentParser.add_subparsers().
        `parent_parsers` is an optional list of parent ArgumentParser objects
        that contain common arguments. Avoid mutating default arguments.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("whl", parents=parents, help="Run the whl check")
        p.set_defaults(func=self.run)
        # Add any additional arguments specific to WhlCheck here (do not re-add common args)

    # todo: figure out venv abstraction mechanism via override
    def run(self, args: argparse.Namespace) -> int:
        """Run the whl check command."""
        print("Running depends check in isolated venv...")

        # this is common. we should have an abstraction layer for this somehow
        if args.target == ".":
            targeted = [os.getcwd()]
        else:
            target_dir = os.getcwd()
            targeted = discover_targeted_packages(args.target, target_dir)


        print(targeted)
