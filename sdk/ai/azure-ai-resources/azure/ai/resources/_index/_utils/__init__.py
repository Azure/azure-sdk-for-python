# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions."""

from collections import defaultdict

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore


def merge_dicts(dict1, dict2):
    """Merge two dictionaries recursively."""
    result = defaultdict(dict)

    for d in (dict1, dict2):
        for key, value in d.items():
            if isinstance(value, dict) and key in result:
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

    return dict(result)
