# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._azureappconfigurationprovider import load, AzureAppConfigurationProvider
from ._models import (
    AzureAppConfigurationKeyVaultOptions,
    SettingSelector,
    WatchKey,
)

from ._version import VERSION

__version__ = VERSION
__all__ = [
    "load",
    "AzureAppConfigurationProvider",
    "AzureAppConfigurationKeyVaultOptions",
    "SettingSelector",
    "WatchKey",
]
