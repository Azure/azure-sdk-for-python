# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Psycopg3 support for Microsoft Entra ID authentication with Azure Database for PostgreSQL.

This module provides connection classes that extend psycopg's Connection and AsyncConnection
to automatically handle Microsoft Entra ID token acquisition and authentication.

Requirements:
    Install with: pip install azure-postgresql-auth[psycopg3]

    This will install:
    - psycopg[binary]>=3.1.0

Classes:
    EntraConnection: Synchronous connection class with Entra ID authentication
    AsyncEntraConnection: Asynchronous connection class with Entra ID authentication
"""

from .async_entra_connection import AsyncEntraConnection
from .entra_connection import EntraConnection

__all__ = ["EntraConnection", "AsyncEntraConnection"]
