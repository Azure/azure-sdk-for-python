import argparse
import re
from pathlib import Path

from typing import Optional, List, Dict

from ci_tools.variables import set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.variables import in_ci
from ci_tools.logging import logger

from .Check import Check

target_snippet_sources = ["samples/*.py", "samples/**/*.py"]
target_md_files = ["README.md"]


def get_snippets_from_directory(package_dir: str) -> Dict[str, str]:
    """Extract all code snippets from sample files in the given package directory.

    Looks for ``# [START name]`` / ``# [END name]`` markers in Python files
    matching *target_snippet_sources* under *package_dir*.

    Returns a mapping of ``<file_stem>.<snippet_name>`` to the dedented snippet body.
    """
    snippets: Dict[str, str] = {}
    pkg_path = Path(package_dir)

    for source in target_snippet_sources:
        for py_file in pkg_path.rglob(source):
            try:
                content = py_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            pattern = "# \\[START(?P<name>[A-Z a-z0-9_]+)\\](?P<body>[\\s\\S]+?)# \\[END[A-Z a-z0-9_]+\\]"
            matches = re.findall(pattern, content)

            for match in matches:
                name = match[0].strip()
                snippet = match[1]
                # Remove extra spaces
                # A sample code snippet could be like:
                # \n
                #         # [START trio]
                #         from azure.core.pipeline.transport import TrioRequestsTransport

                #         async with AsyncPipeline(TrioRequestsTransport(), policies=policies) as pipeline:
                #             return await pipeline.run(request)
                #         # [END trio]
                # \n
                # On one hand, the spaces in the beginning of the line may vary. e.g. If the snippet
                # is in a class, it may have more spaces than if it is not in a class.
                # On the other hand, we cannot remove all spaces because indents are part of Python syntax.
                # Here is our algorithm:
                # We firstly count the spaces of the # [START snippet] line.
                # And for every line, we remove this amount of spaces in the beginning of the line.
                # To only remove the spaces in the beginning and to make sure we only remove it once per line,
                # We use replace('\n' + spaces, '\n').
                spaces = ""
                for char in snippet[1:]:
                    if char == " ":
                        spaces += char
                    else:
                        break
                snippet = snippet.replace("\n" + spaces, "\n")
                # Remove leading newline and trailing whitespace
                snippet = snippet[1:].rstrip()
                if snippet and snippet[-1] == "\n":
                    snippet = snippet[:-1]

                file_name = py_file.stem
                identifier = f"{file_name}.{name}"
                if identifier in snippets:
                    logger.warning(f'Found duplicated snippet name "{identifier}" in {py_file}.')
                logger.debug(f"Found snippet: {identifier}")
                snippets[identifier] = snippet

    return snippets


def update_snippets_in_file(file: str, snippets: Dict[str, str]) -> bool:
    """Replace snippet placeholders in a Markdown file with the extracted code.

    Returns ``True`` if any snippet was out of date (and therefore updated).
    """
    file_obj = Path(file)
    content = file_obj.read_text(encoding="utf-8")
    not_up_to_date = False

    pattern = r"(?P<content>(?P<header><!-- SNIPPET:(?P<name>[A-Z a-z0-9_.]+)-->)[\n]+```python\n[\s\S]*?\n<!-- END SNIPPET -->)"
    matches = re.findall(pattern, content, flags=re.MULTILINE)

    for match in matches:
        body = match[0].strip()
        header = match[1].strip()
        name = match[2].strip()
        logger.debug(f"Found snippet reference: {name}")
        if name not in snippets:
            logger.error(f'In {file}, failed to find snippet name "{name}".')
            return True  # signal failure
        target_code = "".join([header, "\n\n```python\n", snippets[name], "\n```\n\n", "<!-- END SNIPPET -->"])
        if body != target_code:
            logger.warning(f'Snippet "{name}" is not up to date in {file}.')
            not_up_to_date = True
            content = content.replace(body, target_code)

    file_obj.write_text(content, encoding="utf-8")
    return not_up_to_date


class update_snippet(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self,
        subparsers: "argparse._SubParsersAction",
        parent_parsers: Optional[List[argparse.ArgumentParser]] = None,
    ) -> None:
        """Register the ``update_snippet`` command.

        ``update_snippet`` extracts code snippets from sample files and
        synchronises them into README.md files for the targeted packages.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "update_snippet",
            parents=parents,
            help="Update README code snippets from sample files",
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the update_snippet check."""
        logger.info("Running update_snippet check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            pkg_dir = parsed.folder
            pkg_name = parsed.name

            logger.info(f"Processing snippets for {pkg_name} ({pkg_dir})")

            snippets = get_snippets_from_directory(pkg_dir)
            if not snippets:
                logger.info(f"No snippets found for {pkg_name}, skipping.")
                continue

            logger.info(f"Found {len(snippets)} snippet(s) for {pkg_name}.")

            # Update README.md files
            any_out_of_date = False
            for target in target_md_files:
                for md_file in Path(pkg_dir).rglob(target):
                    try:
                        out_of_date = update_snippets_in_file(str(md_file), snippets)
                        if out_of_date:
                            any_out_of_date = True
                    except UnicodeDecodeError:
                        logger.warning(f"Unable to read {md_file} due to encoding error, skipping.")

            if any_out_of_date:
                if in_ci():
                    logger.error(
                        f"Snippets for {pkg_name} are out of sync. Run 'azpysdk update_snippet .' from the package directory to fix."
                    )
                else:
                    logger.error(f"Snippets for {pkg_name} were out of sync and updated.")

                results.append(1)
            else:
                logger.info(f"Snippets for {pkg_name} are up to date.")
                results.append(0)

        return max(results) if results else 0
