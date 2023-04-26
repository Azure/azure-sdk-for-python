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


def _validate_receipt_content(receipt: Dict[str, Any]):
    """Validate the content of a write transaction receipt."""

    try:
        assert "cert" in receipt
        assert isinstance(receipt["cert"], str)

        assert "leafComponents" in receipt
        assert isinstance(receipt["leafComponents"], dict)

        assert "claimsDigest" in receipt["leafComponents"]
        assert isinstance(receipt["leafComponents"]["claimsDigest"], str)

        assert "commitEvidence" in receipt["leafComponents"]
        assert isinstance(receipt["leafComponents"]["commitEvidence"], str)

        assert "writeSetDigest" in receipt["leafComponents"]
        assert isinstance(receipt["leafComponents"]["writeSetDigest"], str)

        assert "proof" in receipt
        assert isinstance(receipt["proof"], list)

        # Validate elements in proof
        for elem in receipt["proof"]:
            assert "left" in elem or "right" in elem
            if "left" in elem:
                assert isinstance(elem["left"], str)
            if "right" in elem:
                assert isinstance(elem["right"], str)

        assert "signature" in receipt
        assert isinstance(receipt["signature"], str)

        # Validate nodeId, if present
        if "nodeId" in receipt:
            assert isinstance(receipt["nodeId"], str)

        # Validate serviceEndorsements, if present
        if "serviceEndorsements" in receipt:
            assert isinstance(receipt["serviceEndorsements"], list)

            # Validate elements in proof
            for elem in receipt["serviceEndorsements"]:
                assert isinstance(elem, str)

    except Exception as exception:
        raise ValueError("The receipt content is invalid.") from exception
