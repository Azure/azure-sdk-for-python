# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned, separately deployed UDF for query invocation tests."""

from contextlib import contextmanager
import os
import uuid

from azure.cosmos import CosmosClient, PartitionKey, _base, http_constants


REVIEW_BAND = """function reviewBand(total) {
    if (typeof total !== "number" || !isFinite(total) || total < 0) {
        throw new Error("Order total must be a finite non-negative number.");
    }
    return total >= 500 ? "manual" : "standard";
}"""


@contextmanager
def deployed_review_band():
    database_id = "query_deployed_udf_" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
    ) as setup_client:
        database = setup_client.create_database(database_id)
        try:
            print(f"\nOwned UDF query database: {database_id}")
            container = database.create_container(
                id="orders", partition_key=PartitionKey(path="/customerId"),
            )
            connection = setup_client.client_connection
            assert connection._backend.name == "core-python"
            container_link = f"dbs/{database_id}/colls/orders"
            # Test-only deployment through the legacy signed transport. ScriptsProxy
            # is intentionally absent; neither query client deploys the UDF.
            deployed = connection.Create(
                {"id": "reviewBand", "body": REVIEW_BAND},
                _base.GetPathFromLink(container_link, http_constants.ResourceType.UserDefinedFunction),
                http_constants.ResourceType.UserDefinedFunction,
                _base.GetResourceIdOrFullNameFromLink(container_link),
                None,
            )
            assert deployed["id"] == "reviewBand"
            for item in (
                {"id": "order-42", "customerId": "customer-42", "type": "order", "total": 25},
                {"id": "order-43", "customerId": "customer-42", "type": "order", "total": 750},
                {"id": "order-44", "customerId": "customer-43", "type": "order", "total": 900},
            ):
                container.create_item(item)
            yield database_id
        finally:
            setup_client.delete_database(database_id)
            print(f"Deleted owned UDF query database: {database_id}")
