# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from ._client import AppConfigurationClient

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

__all__ = [
    'AppConfigurationClient',
    'ConfigurationSetting'
]
