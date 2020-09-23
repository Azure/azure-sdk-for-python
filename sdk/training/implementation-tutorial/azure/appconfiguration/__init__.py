# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._version import VERSION
from ._client import AppConfigurationClient
from ._models import ConfigurationSetting


__all__ = [
    'AppConfigurationClient',
    'ConfigurationSetting'
]

__version__ = VERSION
