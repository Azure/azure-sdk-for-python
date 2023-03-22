# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import warnings
from importlib.abc import MetaPathFinder
from importlib.util import find_spec
import sys

from ._version import VERSION
from ._retry_utility import ConnectionRetryPolicy
from ._container import ContainerProxy
from ._cosmos_client import CosmosClient
from ._database import DatabaseProxy
from ._user import UserProxy
from ._scripts import ScriptsProxy
from ._offer import Offer, ThroughputProperties
from ._documents import (
    ConsistencyLevel,
    DataType,
    IndexKind,
    IndexingMode,
    PermissionMode,
    ProxyConfiguration,
    SSLConfiguration,
    TriggerOperation,
    TriggerType,
    DatabaseAccount,
)
from ._partition_key import PartitionKey
from ._permission import Permission

__all__ = (
    "CosmosClient",
    "DatabaseProxy",
    "ContainerProxy",
    "PartitionKey",
    "Permission",
    "ScriptsProxy",
    "UserProxy",
    "Offer",
    "DatabaseAccount",
    "ConsistencyLevel",
    "DataType",
    "IndexKind",
    "IndexingMode",
    "PermissionMode",
    "ProxyConfiguration",
    "SSLConfiguration",
    "TriggerOperation",
    "TriggerType",
    "ConnectionRetryPolicy",
    "ThroughputProperties"
)
__version__ = VERSION


class _DeprecatedModuleBackCompat(MetaPathFinder):
    deprecated_modules = [
        'auth',
        'container',
        'cosmos_client',
        'database',
        'diagnostics',
        'documents',
        'errors',
        'http_constants',
        'offer',
        'partition_key',
        'permission',
        'scripts',
        'user'
    ]

    def find_spec(fullname, path, target=None):
        separated_name = fullname.split('.')
        name = separated_name[-1]
        if name in _DeprecatedModuleBackCompat.deprecated_modules:
            warnings.warn(
                f"The path 'azure.cosmos.{name} is deprecated and should not be used. "
                "Please import from 'azure.cosmos' instead.",
                DeprecationWarning
            )
            internal_name = ".".join(separated_name[:-1]) + f"._{name}"
            return find_spec(internal_name)
        return None

sys.meta_path.append(_DeprecatedModuleBackCompat)
