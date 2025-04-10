import asyncio
import logging
import os
import random
from datetime import datetime
from logging.handlers import RotatingFileHandler


def get_random_item():
    random_int = random.randint(1, 10000)
    return {"id": "test-" + str(random_int), "pk": "pk-" + str(random_int)}

async def upsert_item_concurrently(container, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        tasks.append(container.upsert_item(get_random_item(), etag=None, match_condition=None))
    await asyncio.gather(*tasks)


async def read_item_concurrently(container, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        item = get_random_item()
        tasks.append(container.read_item(item["id"], item["id"], etag=None, match_condition=None))
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
                                    partition_key=random_item["id"])
    items = [item async for item in results]

def create_logger():
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0] + str(os.getpid())
    # Create a rotating file handler
    handler = RotatingFileHandler(
        "log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log',
        maxBytes=1024 * 1024 * 10, # 10 mb
        backupCount=3
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return first_name, logger