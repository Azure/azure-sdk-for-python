# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Azure PostgreSQL Auth client library for Python.

This library provides Microsoft Entra ID authentication for Python database drivers
connecting to Azure Database for PostgreSQL. It supports psycopg2, psycopg3,
and SQLAlchemy with automatic token management.

Available submodules (with optional dependencies):
    - psycopg2: Support for psycopg2 driver (pip install azure-postgresql-auth[psycopg2])
    - psycopg3: Support for psycopg (v3) driver (pip install azure-postgresql-auth[psycopg3])
    - sqlalchemy: Support for SQLAlchemy ORM (pip install azure-postgresql-auth[sqlalchemy])
"""

from azure_postgresql_auth._version import VERSION

__version__ = VERSION
