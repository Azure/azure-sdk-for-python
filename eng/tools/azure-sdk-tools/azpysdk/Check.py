import abc
import os
import argparse
from typing import Sequence, Optional, List, Any
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages

class Check(abc.ABC):
    """
    Base class for checks.

    Subclasses must implement register() to add a subparser for the check.
    """

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """
        Register this check with the CLI subparsers.

        `subparsers` is the object returned by ArgumentParser.add_subparsers().
        `parent_parsers` can be a list of ArgumentParser objects to be used as parents.
        Subclasses MUST implement this method.
        """
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> int:
        """Run the check command.

        Subclasses can override this to perform the actual work.
        """
        return 0

    def get_targeted_directories(self, args: argparse.Namespace) -> List[ParsedSetup]:
        """
        Get the directories that are targeted for the check.
        """
        targeted: List[ParsedSetup] = []
        targeted_dir = os.getcwd()

        if args.target == ".":
            try:
                targeted.append(ParsedSetup.from_path(targeted_dir))
            except:
                print("Error: Current directory does not appear to be a Python package (no setup.py or setup.cfg found). Remove '.' argument to run on child directories.")
                return []
            
        else:
            targeted_packages = discover_targeted_packages(args.target, targeted_dir)
            for pkg in targeted_packages:
                try:
                    targeted.append(ParsedSetup.from_path(pkg))
                except:
                    print(f"Error: {pkg} does not appear to be a Python package (no setup.py or setup.cfg found).")
                    continue
    
        return targeted 
    