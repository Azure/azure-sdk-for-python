# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class MapsSearchApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Azure Map Search API versions supported by this package"""

    #: This is the default version
    V1_0 = "0.1.0"


def validate_api_version(api_version: str) -> None:
    """Raise ValueError if api_version is invalid """
    if not api_version:
        return

    try:
        api_version =  MapsSearchApiVersion(api_version)
    except ValueError:
        raise ValueError(
            "Unsupported API version '{}'. Please select from:\n{}".format(
                api_version, ", ".join(v.value for v in  MapsSearchApiVersion)
            )
        )
