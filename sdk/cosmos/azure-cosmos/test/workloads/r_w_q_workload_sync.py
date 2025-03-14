import os
import random
import sys

from workload_configs import COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS, USE_MULTIPLE_WRITABLE_LOCATIONS

sys.path.append(r"./")

from azure.cosmos import CosmosClient, documents

import time
from datetime import datetime

import logging


def get_random_item():
    random_int = random.randint(1, 10000)
    return {"id": "Simon-" + str(random_int), "pk": "pk-" + str(random_int)}


def upsert_item(container, num_upserts):
    for _ in range(num_upserts):
        container.upsert_item(get_random_item())


def read_item(container, num_upserts):
    for _ in range(num_upserts):
        item = get_random_item()
        container.read_item(item["id"], item["pk"])


def query_items(container, num_queries):
    for _ in range(num_queries):
        perform_query(container)


def perform_query(container):
    random_item = get_random_item()
    results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                    parameters=[{"name": "@id", "value": random_item["id"]},
                                                {"name": "@pk", "value": random_item["pk"]}],
                                    partition_key=random_item["pk"])
    items = [item for item in results]


def run_workload(client_id, client_logger):
    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
    with CosmosClient(COSMOS_URI, COSMOS_KEY,
                           enable_diagnostics_logging=True, logger=client_logger,
                           user_agent=str(client_id) + "-" + datetime.now().strftime(
                               "%Y%m%d-%H%M%S"), preferred_locations=PREFERRED_LOCATIONS,
                      connection_policy=connectionPolicy) as client:
        db = client.get_database_client("SimonDB")
        cont = db.get_container_client("SimonContainer")
        time.sleep(1)

        while True:
            try:
                upsert_item(cont, 5)
                read_item(cont, 5)
                time.sleep(.2)
                query_items(cont, 2)
            except Exception as e:
                client_logger.info("Exception in application layer")
                client_logger.error(e)


if __name__ == "__main__":
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0]
    file_handler = logging.FileHandler("log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    run_workload(first_name, logger)
