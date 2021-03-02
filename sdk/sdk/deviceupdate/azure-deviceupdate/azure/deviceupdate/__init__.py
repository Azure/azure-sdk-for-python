# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#
# --------------------------------------------------------------------------

from ._configuration import DeviceUpdateClientConfiguration
from ._device_update_client import DeviceUpdateClient
__all__ = ['DeviceUpdateClient', 'DeviceUpdateClientConfiguration']

from .version import VERSION

__version__ = VERSION

