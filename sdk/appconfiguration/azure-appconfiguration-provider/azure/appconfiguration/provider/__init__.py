# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._azureappconfigurationprovider import loadProvider
from ._azureappconfigurationkeyvaultoptions import AzureAppConfigurationKeyVaultOptions
from ._settingselector import SettingSelector

from ._version import VERSION

__version__ = VERSION
__all__ = ["loadProvider", "AzureAppConfigurationKeyVaultOptions", "SettingSelector"]
