# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="import-untyped,return-value"
# pylint: disable=line-too-long,R,wrong-import-order,global-variable-not-assigned)
import json
import os
import re
import sys
from typing import Any, Dict
from pathlib import Path


_yaml_regex = re.compile(
    r"^\s*" + r"(?:---|\+\+\+)" + r"(.*?)" + r"(?:---|\+\+\+)" + r"\s*(.+)$",
    re.S | re.M,
)


def load_text(file_path, encoding="utf-8"):
    with open(file_path, "r", encoding=encoding) as file:
        return file.read()


def load_json(file_path, encoding="utf-8"):
    return json.loads(load_text(file_path, encoding=encoding))


def load_global_config(prompty_path: Path = Path.cwd(), configuration: str = "default") -> Dict[str, Any]:
    prompty_config_path = prompty_path.joinpath("prompty.json")
    if os.path.exists(prompty_config_path):
        c = load_json(prompty_config_path)
        if configuration in c:
            return c[configuration]
        else:
            raise ValueError(f'Item "{configuration}" not found in "{prompty_config_path}"')
    else:
        return {}


def load_prompty(file_path, encoding="utf-8") -> Dict[str, Any]:
    contents = load_text(file_path, encoding=encoding)
    return parse(contents)


def parse(contents):
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise ImportError("Please install pyyaml to use this function. Run `pip install pyyaml`.") from exc

    global _yaml_regex

    fmatter = ""
    body = ""
    result = _yaml_regex.search(contents)

    if result:
        fmatter = result.group(1)
        body = result.group(2)
    return {
        "attributes": yaml.load(fmatter, Loader=yaml.SafeLoader),
        "body": body,
        "frontmatter": fmatter,
    }


def remove_leading_empty_space(multiline_str: str) -> str:
    """
    Processes a multiline string by:
    1. Removing empty lines
    2. Finding the minimum leading spaces
    3. Indenting all lines to the minimum level

    :param multiline_str: The input multiline string.
    :type multiline_str: str
    :return: The processed multiline string.
    :rtype: str
    """
    lines = multiline_str.splitlines()
    start_index = 0
    while start_index < len(lines) and lines[start_index].strip() == "":
        start_index += 1

    # Find the minimum number of leading spaces
    min_spaces = sys.maxsize
    for line in lines[start_index:]:
        if len(line.strip()) == 0:
            continue
        spaces = len(line) - len(line.lstrip())
        spaces += line.lstrip().count("\t") * 2  # Count tabs as 2 spaces
        min_spaces = min(min_spaces, spaces)

    # Remove leading spaces and indent to the minimum level
    processed_lines = []
    for line in lines[start_index:]:
        processed_lines.append(line[min_spaces:])

    return "\n".join(processed_lines)
