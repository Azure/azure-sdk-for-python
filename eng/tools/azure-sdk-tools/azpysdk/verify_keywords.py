import argparse

from typing import Optional, List

from ci_tools.variables import in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger

from .Check import Check

KEYWORD = "azure sdk"


class verify_keywords(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self,
        subparsers: "argparse._SubParsersAction",
        parent_parsers: Optional[List[argparse.ArgumentParser]] = None,
    ) -> None:
        """Register the `verify_keywords` check. The verify_keywords check checks the keywords of a targeted python package. If the keyword 'azure sdk' is not present, error."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "verify_keywords",
            parents=parents,
            help="Run the keyword verification check",
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the verify_keywords check command."""
        logger.info("Running verify_keywords check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_name = parsed.name

            if in_ci():
                if not is_check_enabled(args.target, "verify_keywords"):
                    logger.info(f"Package {package_name} opts-out of keyword verification check.")
                    continue

            if KEYWORD not in parsed.keywords:
                logger.error(
                    f"Keyword '{KEYWORD}' not present in keywords for {package_name}. Before attempting publishing, ensure that package {package_name} has keyword '{KEYWORD}' present in the keyword array."
                )
                results.append(1)
            else:
                logger.info(f"Package {package_name} has keyword '{KEYWORD}' present in the keyword array.")

        return max(results) if results else 0
