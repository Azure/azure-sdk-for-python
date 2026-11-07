# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""One source of run settings; importing this module does not create SDK clients."""

import os
import uuid


RESOURCE_PREFIX = "PythonSDKTest"


def _build_run_id():
    build_id = os.getenv("BUILD_BUILDID")
    suffix = uuid.uuid4().hex[:8]
    return f"{build_id}-{suffix}" if build_id else suffix


RUN_ID = _build_run_id()


def unique_database_id(label=""):
    """Return a database name owned by this process's test run."""
    parts = [RESOURCE_PREFIX, RUN_ID]
    if label:
        parts.append(label)
    parts.append(uuid.uuid4().hex)
    return "-".join(parts)


class TestSettings:
    """Shared values inherited by the temporary legacy configuration."""

    __test__ = False
    local_host = "https://localhost:8081/"
    # Public, well-known Cosmos DB Emulator key; never a live-account credential.
    masterKey = os.getenv(
        "ACCOUNT_KEY",
        "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
    )
    host = os.getenv("ACCOUNT_HOST", local_host)
    connection_str = os.getenv("ACCOUNT_CONNECTION_STR", f"AccountEndpoint={host};AccountKey={masterKey}")
    is_emulator = host == local_host
    data_auth_mode = os.getenv("COSMOS_TEST_DATA_AUTH_MODE", "key").strip().lower()
    if data_auth_mode not in ("key", "aad"):
        raise ValueError(
            f"Unknown COSMOS_TEST_DATA_AUTH_MODE: {data_auth_mode!r}. Expected 'key' or 'aad'."
        )

    global_host = os.getenv("GLOBAL_ACCOUNT_HOST", host)
    write_location_host = os.getenv("WRITE_LOCATION_HOST", host)
    read_location_host = os.getenv("READ_LOCATION_HOST", host)
    read_location2_host = os.getenv("READ_LOCATION_HOST2", host)
    global_masterKey = os.getenv("GLOBAL_ACCOUNT_KEY", masterKey)
    write_location = os.getenv("WRITE_LOCATION", host)
    read_location = os.getenv("READ_LOCATION", host)
    read_location2 = os.getenv("READ_LOCATION2", host)
    WRITE_LOCATION = os.getenv("WRITE_LOCATION", "")
    READ_LOCATION = os.getenv("READ_LOCATION", "West US")

    THROUGHPUT_FOR_5_PARTITIONS = 30000
    THROUGHPUT_FOR_2_PARTITIONS = 12000
    THROUGHPUT_FOR_1_PARTITION = 400
    TEST_DATABASE_ID = os.getenv("COSMOS_TEST_DATABASE_ID", unique_database_id("Shared"))
    TEST_SINGLE_PARTITION_CONTAINER_ID = "SinglePartitionTestContainer-" + str(uuid.uuid4())
    TEST_MULTI_PARTITION_CONTAINER_ID = "MultiPartitionTestContainer-" + str(uuid.uuid4())
    TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID = "SinglePartitionWithPrefixPKTestContainer-" + str(uuid.uuid4())
    TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID = "MultiPartitionWithPrefixPKTestContainer-" + str(uuid.uuid4())
    TEST_CONTAINER_PARTITION_KEY = "pk"
    TEST_CONTAINER_PREFIX_PARTITION_KEY = ["pk1", "pk2"]
    TEST_CONTAINER_PREFIX_PARTITION_KEY_PATH = ["/pk1", "/pk2"]
