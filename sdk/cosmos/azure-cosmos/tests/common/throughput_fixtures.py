# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Own test databases and clean them up even when setup or the test body fails."""

from contextlib import asynccontextmanager, contextmanager

from azure.cosmos import exceptions
from config.provisioning import create_owned_database


@contextmanager
def owned_database(client, database_id, **kwargs):
    """Clean up a unique ID even when creation loses its response, but not on conflict."""
    owned = True
    try:
        try:
            database = create_owned_database(client, id=database_id, **kwargs)
        except exceptions.CosmosResourceExistsError:
            owned = False
            raise
        yield database
    finally:
        if owned:
            try:
                client.delete_database(database_id)
            except exceptions.CosmosResourceNotFoundError:
                pass


@asynccontextmanager
async def owned_database_async(client, database_id, **kwargs):
    """Async ownership also covers setup failure and cancellation."""
    owned = True
    try:
        try:
            database = await client.create_database(id=database_id, **kwargs)
        except exceptions.CosmosResourceExistsError:
            owned = False
            raise
        yield database
    finally:
        if owned:
            try:
                await client.delete_database(database_id)
            except exceptions.CosmosResourceNotFoundError:
                pass

