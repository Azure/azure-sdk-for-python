import sys
import logging
from pathlib import Path
import argparse
import re
from typing import Dict

_LOGGER = logging.getLogger(__name__)

snippets = {}
not_up_to_date = False

target_snippet_sources = ["samples/*.py", "samples/*/*.py"]
target_md_files = ["README.md"]

def check_snippets() -> Dict:
    return snippets

def check_not_up_to_date() -> bool:
    return not_up_to_date

def get_snippet(file: str) -> None:
    file_obj = Path(file)
    with open(file_obj, 'r', encoding='utf8') as f:
        content = f.read()
    pattern = "# \\[START(?P<name>[A-Z a-z0-9_]+)\\](?P<body>[\\s\\S]+?)# \\[END[A-Z a-z0-9_]+\\]"
    matches = re.findall(pattern, content)
    for match in matches:
        s = match
        name = s[0].strip()
        snippet = s[1]
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
        # Remove first newline
        snippet = snippet[1:].rstrip()
        if snippet[-1] == "\n":
            snippet = snippet[:-1]

        file_name = str(file_obj.name)[:-3]
        identifier = ".".join([file_name, name])
        if identifier in snippets.keys():
            _LOGGER.warning(f'Found duplicated snippet name "{identifier}".')
            _LOGGER.warning(file)
        _LOGGER.debug(f"Found: {file_obj.name}.{name}")
        snippets[identifier] = snippet


def update_snippet(file: str) -> None:
    file_obj = Path(file)
    with open(file_obj, 'r', encoding='utf8') as f:
        content = f.read()
    pattern = "(?P<content>(?P<header><!-- SNIPPET:(?P<name>[A-Z a-z0-9_.]+)-->)\\n```python\\n[\\s\\S]*?\\n<!-- END SNIPPET -->)"
    matches = re.findall(pattern, content)
    for match in matches:
        s = match
        body = s[0].strip()
        header = s[1].strip()
        name = s[2].strip()
        _LOGGER.debug(f"Found name: {name}")
        if name not in snippets.keys():
            _LOGGER.error(f'In {file}, failed to find snippet name "{name}".')
            exit(1)
        target_code = "".join([header, "\n```python\n", snippets[name], "\n```\n", "<!-- END SNIPPET -->"])
        if body != target_code:
            _LOGGER.warning(f'Snippet "{name}" is not up to date.')
            global not_up_to_date
            not_up_to_date = True
            content = content.replace(body, target_code)
    with open(file_obj, 'w', encoding='utf8') as f:
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        help=(
            "The targeted path for update."
        ),
    )
    args = parser.parse_args()
    path = sys.argv[1]
    _LOGGER.info(f"Path: {path}")
    for source in target_snippet_sources:
        for py_file in Path(path).rglob(source):
            try:
                get_snippet(py_file)
            except UnicodeDecodeError:
                pass
    for key in snippets.keys():
        _LOGGER.debug(f"Found snippet: {key}")
    for target in target_md_files:
        for md_file in Path(path).rglob(target):
            try:
                update_snippet(md_file)
            except UnicodeDecodeError:
                pass
    if not_up_to_date:
        _LOGGER.error(f'Error: code snippets are out of sync. Please run Python python_snippet_updater.py "{path}" to fix it.')
        exit(1)
    _LOGGER.info(f"README.md under {path} is up to date.")
