# ------------------------------------------------------------------------
 # Copyright (c) Microsoft Corporation. All rights reserved.
 # Licensed under the MIT License. See License.txt in the project root for
 # license information.
 # -------------------------------------------------------------------------

from ._azureappconfigurationproviderasync import load_provider, AzureAppConfigurationProvider

__all__ = [
    "load_provider",
    "AzureAppConfigurationProvider",
]
