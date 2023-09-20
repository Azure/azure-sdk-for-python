# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta

class RemoteRenderingApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Remote Rendering API versions supported by this package"""

    #: This is the default version
    V2021_01_01 = "2021-01-01"


DEFAULT_VERSION = RemoteRenderingApiVersion.V2021_01_01

def validate_api_version(api_version):
    # type: (str) -> None
    """Raise ValueError if api_version is invalid

    :param api_version: The api version
    :type api_version: str

    """
    if not api_version:
        return

    try:
        api_version = RemoteRenderingApiVersion(api_version)
    except ValueError as exc:
        raise ValueError(
            "Unsupported API version '{}'. Please select from:\n{}".format(
                api_version, ", ".join(v.value for v in RemoteRenderingApiVersion)
            )
        ) from exc
