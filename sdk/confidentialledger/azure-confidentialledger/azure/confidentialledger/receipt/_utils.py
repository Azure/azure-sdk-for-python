# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Utils file for receipt verification."""

from typing import Dict, Any


def _to_camel_case(string: str) -> str:
    """Convert a string to camel case."""

    # Split the string by underscore
    components = string.split("_")

    # Capitalize the first letter of each component except the first one
    # with the 'title' method and join them together
    return components[0] + "".join(elem.title() for elem in components[1:])


def _convert_dict_to_camel_case(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """Convert dictionary keys to camel case recursively."""

    new_dictionary = {}

    # Iterate through all the keys in the dictionary
    for key, value in dictionary.items():
        # Convert the key to camel case
        camel_case_key = _to_camel_case(key)

        # If the value is a dictionary, apply algorithm recursively
        if isinstance(value, dict):
            new_dictionary[camel_case_key] = _convert_dict_to_camel_case(value)

        # If the value is a list, apply algorithm recursively to each element
        elif isinstance(value, list):
            new_dictionary[camel_case_key] = [
                _convert_dict_to_camel_case(elem) if isinstance(elem, dict) else elem
                for elem in value
            ]

        # Otherwise, add the key and value to the new dictionary
        else:
            new_dictionary[camel_case_key] = value

    return new_dictionary
