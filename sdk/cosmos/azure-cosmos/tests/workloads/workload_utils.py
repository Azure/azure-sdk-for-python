# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import logging
import os
import random
from datetime import datetime
from logging.handlers import RotatingFileHandler
from workload_configs import NUMBER_OF_LOGICAL_PARTITIONS, PARTITION_KEY


def get_random_item():
    random_int = random.randint(0, NUMBER_OF_LOGICAL_PARTITIONS)
    return {"id": "test-" + str(random_int), "pk": "pk-" + str(random_int)}

async def upsert_item_concurrently(container, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        tasks.append(container.upsert_item(get_random_item(), etag=None, match_condition=None))
    await asyncio.gather(*tasks)


async def read_item_concurrently(container, num_reads):
    tasks = []
    for _ in range(num_reads):
        item = get_random_item()
        tasks.append(container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None))
    await asyncio.gather(*tasks)


async def query_items_concurrently(container, num_queries):
    tasks = []
    for _ in range(num_queries):
        tasks.append(perform_query(container))
    await asyncio.gather(*tasks)


async def perform_query(container):
    random_item = get_random_item()
    results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                    parameters=[{"name": "@id", "value": random_item["id"]},
                                                {"name": "@pk", "value": random_item["pk"]}],
                                    partition_key=random_item[PARTITION_KEY])
    items = [item async for item in results]

def create_logger(file_name):
    logger = logging.getLogger('azure.cosmos')
    prefix = os.path.splitext(file_name)[0] + "-" + str(os.getpid())
    # Create a rotating file handler
    handler = RotatingFileHandler(
        "log-" + prefix + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log',
        maxBytes=1024 * 1024 * 10, # 10 mb
        backupCount=3
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return prefix, logger