# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_psycopg2_connection.py

DESCRIPTION:
    This sample demonstrates how to connect to Azure PostgreSQL using psycopg2
    with synchronous Entra ID authentication.

USAGE:
    python sample_psycopg2_connection.py
"""

import os
from functools import partial

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from psycopg2 import pool

from azure_postgresql_auth.psycopg2 import EntraConnection

# Load environment variables from .env file
load_dotenv()
SERVER = os.getenv("POSTGRES_SERVER")
DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")


def main() -> None:
    # We use the EntraConnection class to enable synchronous Entra-based authentication for database access.
    # This class is applied whenever the connection pool creates a new connection, ensuring that Entra
    # authentication tokens are properly managed and refreshed so that each connection uses a valid token.
    #
    # For more details, see: https://www.psycopg.org/docs/advanced.html#subclassing-connection

    # Create a connection factory with the credential bound using functools.partial
    credential = DefaultAzureCredential()
    connection_factory = partial(EntraConnection, credential=credential)

    connection_pool = pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=5,
        host=SERVER,
        database=DATABASE,
        connection_factory=connection_factory,
    )

    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT now()")
            result = cur.fetchone()
            print(f"Database time: {result[0]}")
    finally:
        connection_pool.putconn(conn)
        connection_pool.closeall()


if __name__ == "__main__":
    main()
