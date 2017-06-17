# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .compute import ComputeManagementClient
from .containerservice import ContainerServiceClient
from .version import VERSION

__version__ = VERSION
__all__ = ['ComputeManagementClient', 'ContainerServiceClient']
