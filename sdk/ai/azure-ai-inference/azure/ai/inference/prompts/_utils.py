# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="import-untyped,return-value"
# pylint: disable=line-too-long,R,wrong-import-order,global-variable-not-assigned)
import re
import yaml
import json
from typing import Any, Dict, Union
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


def _find_global_config(prompty_path: Path = Path.cwd()) -> Union[Path, None]:
    prompty_config = list(Path.cwd().glob("**/prompty.json"))

    if len(prompty_config) > 0:
        return sorted(
            [c for c in prompty_config if len(c.parent.parts) <= len(prompty_path.parts)],
            key=lambda p: len(p.parts),
        )[-1]
    else:
        return None


def load_global_config(prompty_path: Path = Path.cwd(), configuration: str = "default") -> Dict[str, Any]:
    # prompty.config laying around?
    config = _find_global_config(prompty_path)

    # if there is one load it
    if config is not None:
        c = load_json(config)
        if configuration in c:
            return c[configuration]
        else:
            raise ValueError(f'Item "{configuration}" not found in "{config}"')

    return {}


def load_prompty(file_path, encoding="utf-8") -> Dict[str, Any]:
    contents = load_text(file_path, encoding=encoding)
    return parse(contents)


def parse(contents):
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
