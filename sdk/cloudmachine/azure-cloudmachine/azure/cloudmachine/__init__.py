# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._version import VERSION
from ._client import (
    CloudMachineClient,
    CloudMachineTableData,
    DataModel,
)
from ._httpclient._storage import CloudMachineStorage, StorageFile
from ._httpclient._servicebus import CloudMachineServiceBus, Message, LockedMessage
from ._httpclient._utils import Pages, Stream
from ._httpclient._api_versions import DEFAULT_API_VERSIONS

__version__ = VERSION

__all__ = [
    "CloudMachineClient",
    "CloudMachineStorage",
    "StorageFile",
    "CloudMachineServiceBus",
    "Message",
    "LockedMessage",
    "CloudMachineTableData",
    "DataModel",
    "Pages",
    "Stream",
    "DEFAULT_API_VERSIONS"
]
