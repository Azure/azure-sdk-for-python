# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions."""

from collections import defaultdict
from typing import Any, Dict

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.

    :param dict1: The first dictionary.
    :type dict1: Dict[str, Any]
    :param dict2: The second dictionary.
    :type dict2: Dict[str, Any]
    :return: The merged dictionary.
    :rtype: Dict[str, Any]
    """
    result: defaultdict = defaultdict(dict)

    for d in (dict1, dict2):
        for key, value in d.items():
            if isinstance(value, dict) and key in result:
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

    return dict(result)
