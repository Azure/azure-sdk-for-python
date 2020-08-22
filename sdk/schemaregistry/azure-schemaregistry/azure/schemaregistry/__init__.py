# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from ._version import VERSION
__version__ = VERSION

from ._schema_registry_client import SchemaRegistryClient
from ._common._constants import SerializationType

__all__ = [
    "SchemaRegistryClient",
    "SerializationType"
]
