# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from ._async_load import load
from ._azureappconfigurationproviderasync import AzureAppConfigurationProvider

__all__ = [
    "load",
    "AzureAppConfigurationProvider",
]
