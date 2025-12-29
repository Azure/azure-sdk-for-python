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


def _find_string_end(text: str, index: int) -> int:
    """
    Helper function that finds the end of a string literal.

    :param text: The input text to process.
    :type text: str
    :param index: The current index in the text, should be the position right after the opening quote.
    :type index: int
    :raises ValueError: If there is an unterminated string literal.
    :return: The index of the closing quote.
    :rtype: int
    """
    while index < len(text):
        current_char = text[index]
        if current_char == DOUBLE_QUOTE:
            # Check for escaped quote
            esc_count = 0
            j = index - 1
            while j >= 0 and text[j] == ESCAPE_CHAR:
                esc_count += 1
                j -= 1
            if esc_count % 2 == 0:
                # Found end of string
                index += 1
                return index
        index += 1
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
    index = 0
    length = len(text)
    while index < length:
        current_char = text[index]
        if current_char == DOUBLE_QUOTE:
            result.append(current_char)
            index += 1
            string_end = _find_string_end(text, index)
            result.append(text[index:string_end])
            index = string_end
        elif text[index : index + 2] == DOUBLE_FORWARD_SLASH_COMMENT:
            # Skip to end of line or end of file
            index += 2
            while index < length and text[index] != NEW_LINE:
                index += 1
            # If we found a newline, move past it
            if index < length and text[index] == NEW_LINE:
                result.append(NEW_LINE)
                index += 1
        elif text[index : index + 2] == MULTI_LINE_COMMENT:
            # Skip to end of block comment
            index += 2

            # Search for the end of the comment
            found_end = False
            while index < length - 1:
                if index + 1 < length and text[index : index + 2] == END_MULTI_LINE_COMMENT:
                    found_end = True
                    index += 2  # Skip past the end marker
                    break
                index += 1

            # If we reached the end without finding the comment closer, raise an error
            if not found_end:
                raise ValueError("Unterminated multi-line comment")
        else:
            result.append(current_char)
            index += 1
    return "".join(result)
