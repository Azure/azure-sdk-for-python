# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from enum import Enum


class RemoteRenderingApiVersion(str, Enum):
    """Remote Rendering API versions supported by this package"""

    #: This is the default version
    V2021_01_01 = "2021-01-01"


def validate_api_version(api_version):
    # type: (str) -> None
    """Raise ValueError if api_version is invalid """
    if not api_version:
        return

    try:
        api_version = RemoteRenderingApiVersion(api_version)
    except ValueError:
        raise ValueError(
            "Unsupported API version '{}'. Please select from:\n{}".format(
                api_version, ", ".join(v.value for v in RemoteRenderingApiVersion)
            )
        )
