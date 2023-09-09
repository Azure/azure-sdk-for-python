# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Tuple
import re
import argparse


def to_snake_case(name: str) -> str:
    def replace_upper_characters(m) -> str:
        match_str = m.group().lower()
        if m.start() > 0 and name[m.start() - 1] == "_":
            # we are good if a '_' already exists
            return match_str
        # the first letter should not have _
        prefix = "_" if m.start() > 0 else ""

        # we will add an extra _ if there are multiple upper case chars together
        next_non_upper_case_char_location = m.start() + len(match_str)
        if (
            len(match_str) > 2
            and len(name) - next_non_upper_case_char_location > 1
            and name[next_non_upper_case_char_location].isalpha()
        ):
            return (
                prefix
                + match_str[: len(match_str) - 1]
                + "_"
                + match_str[len(match_str) - 1]
            )

        return prefix + match_str

    result = re.sub("[A-Z]+", replace_upper_characters, name)
    return result.replace(" ", "_").replace("__", "_").replace("-", "")


def parse_args(
    need_cadl_file: bool = True,
) -> Tuple[argparse.Namespace, Dict[str, Any]]:
    parser = argparse.ArgumentParser(
        description="Run mypy against target folder. Add a local custom plugin to the path prior to execution. "
    )
    parser.add_argument(
        "--output-folder",
        dest="output_folder",
        help="Output folder for generated SDK",
        required=True,
    )
    parser.add_argument(
        "--cadl-file",
        dest="cadl_file",
        help="Serialized cadl file",
        required=need_cadl_file,
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        help="Debug mode",
        required=False,
        action="store_true",
    )
    args, unknown_args = parser.parse_known_args()

    def _get_value(value: Any) -> Any:
        if value == "true":
            return True
        if value == "false":
            return False
        try:
            return int(value)
        except ValueError:
            pass
        return value

    unknown_args_ret = {
        ua.strip("--").split("=", maxsplit=1)[  # pylint: disable=bad-str-strip-call
            0
        ]: _get_value(
            ua.strip("--").split("=", maxsplit=1)[  # pylint: disable=bad-str-strip-call
                1
            ]
        )
        for ua in unknown_args
    }
    return args, unknown_args_ret


def get_body_type_for_description(body_parameter: Dict[str, Any]) -> str:
    if body_parameter["type"]["type"] == "binary":
        return "binary"
    if body_parameter["type"]["type"] == "string":
        return "string"
    return "JSON"


# used if we want to get a string / binary type etc
KNOWN_TYPES: Dict[str, Dict[str, Any]] = {
    "string": {"type": "string"},
    "binary": {"type": "binary"},
    "anydict": {"type": "dict", "elementType": {"type": "any"}},
    "any-object": {"type": "any-object"},
}

JSON_REGEXP = re.compile(r"^(application|text)/(.+\+)?json$")
