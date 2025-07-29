# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import random
from datetime import datetime
from logging.handlers import RotatingFileHandler

from azure.monitor.opentelemetry import configure_azure_monitor
from workload_configs import *

_NOISY_ERRORS = set([404, 409, 412])
_NOISY_SUB_STATUS_CODES = set([0, None])
_REQUIRED_ATTRIBUTES = ["resource_type", "verb", "operation_type", "status_code", "sub_status_code", "duration"]

def get_user_agent(client_id):
    prefix = USER_AGENT_PREFIX + "-" if USER_AGENT_PREFIX else ""
    return prefix + str(client_id) + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")

def get_random_item():
    random_int = random.randint(0, NUMBER_OF_LOGICAL_PARTITIONS)
    return {"id": "test-" + str(random_int), "pk": "pk-" + str(random_int)}

def upsert_item(container, excluded_locations, num_upserts):
    for _ in range(num_upserts):
        if excluded_locations:
            container.upsert_item(get_random_item(), etag=None, match_condition=None,
                                  excluded_locations=excluded_locations)
        else:
            container.upsert_item(get_random_item(), etag=None, match_condition=None)


def read_item(container, excluded_locations, num_reads):
    for _ in range(num_reads):
        item = get_random_item()
        if excluded_locations:
            container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None,
                                excluded_locations=excluded_locations)
        else:
            container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None)

def query_items(container, excluded_locations, num_queries):
    for _ in range(num_queries):
        perform_query(container, excluded_locations)


def perform_query(container, excluded_locations):
    random_item = get_random_item()
    if excluded_locations:
        results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                        parameters=[{"name": "@id", "value": random_item["id"]},
                                                    {"name": "@pk", "value": random_item["pk"]}],
                                        partition_key=random_item[PARTITION_KEY],
                                        excluded_locations=excluded_locations)
    else:
        results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                        parameters=[{"name": "@id", "value": random_item["id"]},
                                                    {"name": "@pk", "value": random_item["pk"]}],
                                        partition_key=random_item[PARTITION_KEY])
    items = [item for item in results]

async def upsert_item_concurrently(container, excluded_locations, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        if excluded_locations:
            tasks.append(container.upsert_item(get_random_item(), etag=None, match_condition=None,
                                               excluded_locations=excluded_locations))
        else:
            tasks.append(container.upsert_item(get_random_item(), etag=None, match_condition=None))
    await asyncio.gather(*tasks)


async def read_item_concurrently(container, excluded_locations, num_reads):
    tasks = []
    for _ in range(num_reads):
        item = get_random_item()
        if excluded_locations:
            tasks.append(container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None,
                                             excluded_locations=excluded_locations))
        else:
            tasks.append(container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None))
    await asyncio.gather(*tasks)


async def query_items_concurrently(container, excluded_locations, num_queries):
    tasks = []
    for _ in range(num_queries):
        tasks.append(perform_query_concurrently(container, excluded_locations))
    await asyncio.gather(*tasks)


async def perform_query_concurrently(container, excluded_locations):
    random_item = get_random_item()
    if excluded_locations:
        results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                        parameters=[{"name": "@id", "value": random_item["id"]},
                                                    {"name": "@pk", "value": random_item["pk"]}],
                                        partition_key=random_item[PARTITION_KEY],
                                        excluded_locations=excluded_locations)
    else:
        results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                        parameters=[{"name": "@id", "value": random_item["id"]},
                                                    {"name": "@pk", "value": random_item["pk"]}],
                                        partition_key=random_item[PARTITION_KEY])
    items = [item async for item in results]

def create_logger(file_name):
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = str(CIRCUIT_BREAKER_ENABLED)
    logger = logging.getLogger()
    if APP_INSIGHTS_CONNECTION_STRING:
        configure_azure_monitor(
            logger_name="azure.cosmos",
            connection_string=APP_INSIGHTS_CONNECTION_STRING,
        )
    prefix = os.path.splitext(file_name)[0] + "-" + str(os.getpid())
    # Create a rotating file handler
    handler = RotatingFileHandler(
        "log-" + get_user_agent(prefix) + '.log',
        maxBytes=1024 * 1024 * 10,  # 10 mb
        backupCount=2
    )
    logger.setLevel(LOG_LEVEL)
    # create filters for the logger handler to reduce the noise
    workload_logger_filter = WorkloadLoggerFilter()
    handler.addFilter(workload_logger_filter)
    logger.addHandler(handler)
    return prefix, logger


class WorkloadLoggerFilter(logging.Filter):
    def filter(self, record):
        # Check if the required attributes exist in the log record
        if all(hasattr(record, attr) for attr in _REQUIRED_ATTRIBUTES):
            # Check the conditions
            # Check database account reads
            if record.resource_type == "databaseaccount" and record.verb == "GET" and record.operation_type == "Read":
                return True
            # Check if there is an error and omit noisy errors
            if record.status_code >= 400 and not (
                    record.status_code in _NOISY_ERRORS and record.sub_status_code in _NOISY_SUB_STATUS_CODES):
                return True
            # Check if the latency (duration) was above 1000 ms
            if record.duration >= 1000:
                return True
        return False
