# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._version import VERSION
from ._client import (
    CloudMachineClient,
    CloudMachineStorage,
    CloudMachineMessaging,
    CloudMachineTableData,
    load_dev_environment
)

__version__ = VERSION

__all__ = [
    "CloudMachineClient",
    "CloudMachineStorage",
    "CloudMachineMessaging",
    "CloudMachineTableData",
    "load_dev_environment"
]
