# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys


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
