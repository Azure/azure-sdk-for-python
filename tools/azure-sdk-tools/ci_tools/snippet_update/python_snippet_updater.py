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
    with open(file_obj, 'r') as f:
        content = f.read()
    pattern = "# \\[START(?P<name>[A-Z a-z0-9_]+)\\](?P<body>[\\s\\S]+?)# \\[END[A-Z a-z0-9_]+\\]"
    matches = re.findall(pattern, content)
    for match in matches:
        s = match
        name = s[0].strip()
        snippet = s[1]
        # Remove extra spaces
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
    with open(file_obj, 'r') as f:
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
            _LOGGER.error(f'In {file}, failed to found snippet name "{name}".')
            exit(1)
        target_code = "".join([header, "\n```python\n", snippets[name], "\n```\n", "<!-- END SNIPPET -->"])
        if body != target_code:
            _LOGGER.warning(f'Snippet "{name}" is not up to date.')
            global not_up_to_date
            not_up_to_date = True
            content = content.replace(body, target_code)
    with open(file_obj, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="The path to your service folder")
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
        _LOGGER.error(f'Error: code snippets are out of sync. Please run Python PythonSnippetUpdater.py "{path}" to fix it.')
        exit(1)
    _LOGGER.info(f"README.md under {path} is up to date.")
