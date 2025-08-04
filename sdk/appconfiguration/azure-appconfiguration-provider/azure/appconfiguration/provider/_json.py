# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

ESCAPE_CHAR = "\\"
DOUBLE_FORWARD_SLASH_COMMENT = "//"
MULTI_LINE_COMMENT = "/*"
END_MULTI_LINE_COMMENT = "*/"
DOUBLE_QUOTE = '"'
NEW_LINE = "\n"


def _strip_ignore_string(text: str, i: int, result: list[str]) -> tuple[list[str], int]:
    """
    Helper function to strip comments within a string literal.
    Handles both single and double quotes, and escaped quotes.
    Returns the updated index and the result list.

    :param text: The input text to process.
    :type text: str
    :param i: The current index in the text.
    :type i: int
    :param result: The list to accumulate the processed characters.
    :type result: list[str]
    :raises ValueError: If there is an unterminated string literal.
    :return: A tuple containing the updated result list and the next index.
    :rtype: tuple[list[str], int]
    """
    while i < len(text):
        current_char = text[i]
        result.append(current_char)
        if current_char == DOUBLE_QUOTE:
            # Check for escaped quote
            esc_count = 0
            j = i - 1
            while j >= 0 and text[j] == ESCAPE_CHAR:
                esc_count += 1
                j -= 1
            if esc_count % 2 == 0:
                return result, i + 1
        i += 1
    raise ValueError("Unterminated string literal")


def remove_json_comments(text: str) -> str:
    """
    Removes comments from a JSON file. Supports //, and /* ... */ comments.
    Returns as string.

    :param text: The input JSON string with comments.
    :type text: str
    :raises ValueError: If there is an unterminated string literal.
    :return: A string with comments removed.
    :rtype: str
    """
    result = []
    i = 0
    length = len(text)
    while i < length:
        current_char = text[i]
        if current_char == DOUBLE_QUOTE:
            result.append(current_char)
            i += 1
            result, i = _strip_ignore_string(text, i, result)
        elif text[i : i + 2] == DOUBLE_FORWARD_SLASH_COMMENT:
            # Skip to end of line or end of file
            i += 2
            while i < length and text[i] != NEW_LINE:
                i += 1
            # If we found a newline, move past it
            if i < length and text[i] == NEW_LINE:
                i += 1
        elif text[i : i + 2] == MULTI_LINE_COMMENT:
            # Skip to end of block comment
            i += 2

            # Search for the end of the comment
            found_end = False
            while i < length - 1:
                if i + 1 < length and text[i : i + 2] == END_MULTI_LINE_COMMENT:
                    found_end = True
                    i += 2  # Skip past the end marker
                    break
                i += 1

            # If we reached the end without finding the comment closer, raise an error
            if not found_end:
                raise ValueError("Unterminated multi-line comment")
        else:
            result.append(current_char)
            i += 1
    return "".join(result)
