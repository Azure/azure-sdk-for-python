import abc
import argparse
from typing import Sequence, Optional, List, Any

class Check(abc.ABC):
    """
    Base class for checks.

    Subclasses must implement register() to add a subparser for the check.
    Provide:
        - name: str - command name for the check
        - specifications: Sequence[str] - requirements or local files describing spec
    """

    # Command name used in the CLI
    name: str = "unnamed"
    # Specifications that this check can use to decide applicability
    specifications: Sequence[str] = ()

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
        print(f"Running check: {self.name} ...")
        print(args)
        return 0