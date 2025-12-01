# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import random
import sys
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler
from aiohttp import ClientSession
from azure.monitor.opentelemetry import configure_azure_monitor

from custom_tcp_connector import ProxiedTCPConnector
from workload_configs import *

_NOISY_ERRORS = set([404, 409, 412])
_NOISY_SUB_STATUS_CODES = set([0, None])
_REQUIRED_ATTRIBUTES = ["resource_type", "verb", "operation_type", "status_code", "sub_status_code", "duration"]

def get_user_agent(client_id):
    prefix = USER_AGENT_PREFIX + "-" if USER_AGENT_PREFIX else ""
    return prefix + str(client_id) + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")

def get_existing_random_item():
    random_int = random.randint(0, NUMBER_OF_LOGICAL_PARTITIONS)
    item = create_random_item()
    item["id"] = "test-" + str(random_int)
    item["pk"] = "pk-" + str(random_int)
    return item

def create_random_item():
    paragraph1 = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        f"Random ID: {uuid.uuid4()}"
    )
    paragraph2 = (
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. "
        f" Timestamp: {datetime.utcnow().isoformat()}"
    )
    return {
        "id": "test-" + str(uuid.uuid4()),
        "pk": "pk-" + str(uuid.uuid4()),
        "value": random.randint(1, 1000000000),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "flag": random.choice([True, False]),
        "description": paragraph1 + "\n\n" + paragraph2
    }

# Added per request: generate a random embedding vector of floating point values.
# create_random_embedding uses snake_case; createRandomEmbedding provided as a thin wrapper
# to mirror the Go-style signature the user specified.
def create_random_embedding(length: int = 10) -> list[float]:
    """Return a list of 'length' random float values in range [0.0, 1.0)."""
    return [random.random() for _ in range(length)]

def _get_upsert_item():
    # 10 percent of the time, create a new item instead of updating an existing one
    return create_random_item() if random.random() < 0.1 else get_existing_random_item()

def upsert_item(container, excluded_locations, num_upserts):
    item = _get_upsert_item()
    for _ in range(num_upserts):
        if excluded_locations:
            container.upsert_item(item, etag=None, match_condition=None,
                                  excluded_locations=excluded_locations)
        else:
            container.upsert_item(item, etag=None, match_condition=None)


def read_item(container, excluded_locations, num_reads):
    for _ in range(num_reads):
        item = get_existing_random_item()
        if excluded_locations:
            container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None,
                                excluded_locations=excluded_locations)
        else:
            container.read_item(item["id"], item[PARTITION_KEY], etag=None, match_condition=None)

def query_items(container, excluded_locations, num_queries):
    for _ in range(num_queries):
        perform_query(container, excluded_locations)


def perform_query(container, excluded_locations):
    random_item = get_existing_random_item()
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
        item = _get_upsert_item()
        if excluded_locations:
            tasks.append(container.upsert_item(item, etag=None, match_condition=None,
                                               excluded_locations=excluded_locations))
        else:
            tasks.append(container.upsert_item(item, etag=None, match_condition=None))
    await asyncio.gather(*tasks)


async def read_item_concurrently(container, excluded_locations, num_reads):
    tasks = []
    for _ in range(num_reads):
        item = get_existing_random_item()
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


async def vs_query_items_concurrently(container, excluded_locations, num_queries):
    tasks = []
    for _ in range(num_queries):
        tasks.append(vs_perform_query_concurrently(container, excluded_locations))
    await asyncio.gather(*tasks)

def create_custom_session():
    proxied_connector = ProxiedTCPConnector(proxy_host=COSMOS_PROXY_URI,
                         proxy_port=5100,
                         limit=100,             # Max total open connections
                         limit_per_host=10,     # Max per Cosmos DB host
                         keepalive_timeout=30,  # Keep-alive duration for idle connections
                         enable_cleanup_closed=True)  # Helpful for TLS/FIN issues

    session = ClientSession(connector=proxied_connector)
    return session

async def perform_query_concurrently(container, excluded_locations):
    random_item = get_existing_random_item()
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


async def vs_perform_query_concurrently(container, excluded_locations):
    random_item = get_existing_random_item()
    embedding = create_random_embedding(10)
    if excluded_locations:
        results = container.query_items(query="SELECT TOP 10 c.id FROM c ORDER BY VectorDistance(c.embedding, @embedding)",
                                        parameters=[{"name": "@embedding", "value": embedding}],
                                        partition_key=random_item[PARTITION_KEY],
                                        excluded_locations=excluded_locations)
    else:
        results = container.query_items(query="SELECT TOP 10 c.id FROM c ORDER BY VectorDistance(c.embedding, @embedding)",
                                        parameters=[{"name": "@embedding", "value": embedding}],
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
        backupCount=5
    )
    logger.setLevel(LOG_LEVEL)
    # create filters for the logger handler to reduce the noise
    workload_logger_filter = WorkloadLoggerFilter()
    # handler.addFilter(workload_logger_filter)
    logger.addHandler(handler)
    return prefix, logger

def create_inner_logger(file_name="internal_logger_tues"):
    logger = logging.getLogger("internal_requests")
    prefix = os.path.splitext(file_name)[0] + "-" + str(os.getpid())
    # Create a rotating file handler
    handler = RotatingFileHandler(
        "log-" + file_name + '.log',
        maxBytes=1024 * 1024 * 10,  # 10 mb
        backupCount=5
    )
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)


class WorkloadLoggerFilter(logging.Filter):
    def filter(self, record):
        if record.msg:
            if isinstance(record.msg, str):
                request_url_index = record.msg.find("Request URL:")
                response_status_index = record.msg.find("Response status:")
                if request_url_index == -1 and response_status_index == -1:
                    return True
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
