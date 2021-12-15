# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._remote_rendering_client import RemoteRenderingClient
from ._version import VERSION

from ._generated.models import (AssetConversion, AssetConversionInputSettings,
                                AssetConversionOutput, AssetConversionOutputSettings,
                                AssetConversionSettings, AssetConversionStatus, RemoteRenderingError,
                                RenderingSession, RenderingSessionSize, RenderingSessionStatus)

__all__ = [
    "RemoteRenderingClient",
    "AssetConversion",
    "AssetConversionSettings",
    "AssetConversionInputSettings",
    "AssetConversionOutputSettings",
    "AssetConversionStatus",
    "AssetConversionOutput",
    "RenderingSession",
    "RenderingSessionSize",
    "RenderingSessionStatus",
    "RemoteRenderingError"
]

__version__ = VERSION
