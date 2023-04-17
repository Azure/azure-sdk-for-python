# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from .client_async import ProvisioningServiceClient
from .._generated import VERSION

__all__ = ["ProvisioningServiceClient"]

__version__ = VERSION
