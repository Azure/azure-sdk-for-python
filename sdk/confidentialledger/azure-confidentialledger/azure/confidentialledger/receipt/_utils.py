# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Utils file for receipt verification."""

from typing import Dict, Any


def _to_camel_case(string: str) -> str:
    """Convert a string to camel case.

    :param str string: The string to convert to camel case.
    :return: The string converted to camel case.
    :rtype: str
    """

    # Split the string by underscore
    components = string.split("_")

    # Capitalize the first letter of each component except the first one
    # with the 'title' method and join them together
    return components[0] + "".join(elem.title() for elem in components[1:])


def _convert_dict_to_camel_case(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """Convert dictionary keys to camel case recursively.

    :param dict[str, any] dictionary: The dictionary to convert to camel case.
    :return: The dictionary with keys converted to camel case.
    :rtype: dict[str, any]
    :raises ValueError: If two keys of a dictionary are converted to the same camel case key.
    """

    new_dictionary: Dict[str, Any] = {}

    # Iterate through all the keys in the dictionary
    for key, value in dictionary.items():
        # Convert the key to camel case
        camel_case_key = _to_camel_case(key)

        # Reject a key that converts to the same name as a previous key
        if camel_case_key in new_dictionary:
            raise ValueError(f"Duplicate key after normalization: {camel_case_key}")

        # Convert nested dictionaries, including dictionaries inside lists at any depth
        new_dictionary[camel_case_key] = _convert_value_to_camel_case(value)

    return new_dictionary


def _convert_value_to_camel_case(value: Any) -> Any:
    """Convert dictionary keys to camel case in a value, recursing into lists.

    :param any value: The value to convert.
    :return: The value with the keys of all nested dictionaries converted to camel case.
    :rtype: any
    :raises ValueError: If two keys of a dictionary are converted to the same camel case key.
    """

    if isinstance(value, dict):
        return _convert_dict_to_camel_case(value)
    if isinstance(value, list):
        return [_convert_value_to_camel_case(elem) for elem in value]
    return value
