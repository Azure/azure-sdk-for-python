# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import sys

from workload_utils import create_logger, get_random_item
from workload_configs import (COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS, USE_MULTIPLE_WRITABLE_LOCATIONS,
                                              CONCURRENT_REQUESTS, COSMOS_DATABASE, COSMOS_CONTAINER, CONCURRENT_QUERIES,
                                              PARTITION_KEY)

sys.path.append(r"/")

from azure.cosmos import CosmosClient, documents

import time
from datetime import datetime

def upsert_item(container, num_upserts):
    for _ in range(num_upserts):
        container.upsert_item(get_random_item(), etag=None, match_condition=None)


def read_item(container, num_reads):
    for _ in range(num_reads):
        item = get_random_item()
        container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None)


def query_items(container, num_queries):
    for _ in range(num_queries):
        perform_query(container)


def perform_query(container):
    random_item = get_random_item()
    results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                    parameters=[{"name": "@id", "value": random_item["id"]},
                                                {"name": "@pk", "value": random_item["pk"]}],
                                    partition_key=random_item[PARTITION_KEY])
    items = [item for item in results]


def run_workload(client_id, client_logger):
    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
    with CosmosClient(COSMOS_URI, COSMOS_KEY,
                           enable_diagnostics_logging=True, logger=client_logger,
                           user_agent=str(client_id) + "-" + datetime.now().strftime(
                               "%Y%m%d-%H%M%S"), preferred_locations=PREFERRED_LOCATIONS,
                      connection_policy=connectionPolicy) as client:
        db = client.get_database_client(COSMOS_DATABASE)
        cont = db.get_container_client(COSMOS_CONTAINER)
        time.sleep(1)

        while True:
            try:
                upsert_item(cont, CONCURRENT_REQUESTS)
                read_item(cont, CONCURRENT_REQUESTS)
                query_items(cont, CONCURRENT_QUERIES)
            except Exception as e:
                client_logger.info("Exception in application layer")
                client_logger.error(e)


if __name__ == "__main__":
    file_name = os.path.basename(__file__)
    prefix, logger = create_logger(file_name)
    run_workload(prefix, logger)
