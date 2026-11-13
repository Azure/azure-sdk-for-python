# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Provision and clean up test resources using the client supplied by the caller."""

import asyncio
import random
import time

from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.http_constants import HttpHeaders, StatusCodes

from config.settings import TestSettings
from config.provisioning import (
    create_owned_container as create_owned_container,
    create_owned_database as create_owned_database,
)


CONTROL_PLANE_MAX_ATTEMPTS = 20
CONTROL_PLANE_MAX_BACKOFF_SECONDS = 15
CONTROL_PLANE_RETRY_STATUS_CODES = frozenset({408, 429, 449, 500, 503})


def _control_plane_backoff(attempt, error):
    headers = getattr(error, "headers", None) or {}
    for header in (HttpHeaders.RetryAfterInMilliseconds, HttpHeaders.RetryAfter):
        raw = headers.get(header)
        if raw is None:
            continue
        try:
            hinted = float(raw) / 1000 if header == HttpHeaders.RetryAfterInMilliseconds else float(raw)
        except (TypeError, ValueError):
            continue
        return min(max(hinted, 0.1), CONTROL_PLANE_MAX_BACKOFF_SECONDS)
    backoff = min(0.5 * (2 ** attempt), CONTROL_PLANE_MAX_BACKOFF_SECONDS)
    return backoff * (0.5 + random.random() / 2)


def _should_retry_control_plane(error, attempt):
    return (
        error.status_code in CONTROL_PLANE_RETRY_STATUS_CODES
        and attempt < CONTROL_PLANE_MAX_ATTEMPTS - 1
    )


def retry_control_plane(operation, *args, **kwargs):
    """Retry transient setup failures, never customer-operation assertions."""
    for attempt in range(CONTROL_PLANE_MAX_ATTEMPTS):
        try:
            return operation(*args, **kwargs)
        except exceptions.CosmosHttpResponseError as error:
            if not _should_retry_control_plane(error, attempt):
                raise
            time.sleep(_control_plane_backoff(attempt, error))
    raise AssertionError("unreachable")  # pragma: no cover


async def retry_control_plane_async(operation, *args, **kwargs):
    """Async equivalent of retry_control_plane."""
    for attempt in range(CONTROL_PLANE_MAX_ATTEMPTS):
        try:
            return await operation(*args, **kwargs)
        except exceptions.CosmosHttpResponseError as error:
            if not _should_retry_control_plane(error, attempt):
                raise
            await asyncio.sleep(_control_plane_backoff(attempt, error))
    raise AssertionError("unreachable")  # pragma: no cover


def create_database_if_not_exist(client, *, settings=TestSettings):
    return retry_control_plane(
        client.create_database_if_not_exists,
        settings.TEST_DATABASE_ID,
        offer_throughput=settings.THROUGHPUT_FOR_1_PARTITION,
    )


def _create_container(client, identifier, partition_key, throughput, settings):
    database = create_database_if_not_exist(client, settings=settings)
    return retry_control_plane(
        database.create_container_if_not_exists,
        id=identifier,
        partition_key=partition_key,
        offer_throughput=throughput,
    )


def create_single_partition_container_if_not_exist(client, *, settings=TestSettings):
    return _create_container(
        client, settings.TEST_SINGLE_PARTITION_CONTAINER_ID,
        PartitionKey(path="/" + settings.TEST_CONTAINER_PARTITION_KEY, kind="Hash"),
        settings.THROUGHPUT_FOR_1_PARTITION, settings,
    )


def create_multi_partition_container_if_not_exist(client, *, settings=TestSettings):
    return _create_container(
        client, settings.TEST_MULTI_PARTITION_CONTAINER_ID,
        PartitionKey(path="/" + settings.TEST_CONTAINER_PARTITION_KEY, kind="Hash"),
        settings.THROUGHPUT_FOR_5_PARTITIONS, settings,
    )


def create_single_partition_prefix_pk_container_if_not_exist(client, *, settings=TestSettings):
    return _create_container(
        client, settings.TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID,
        PartitionKey(path=settings.TEST_CONTAINER_PREFIX_PARTITION_KEY_PATH, kind="MultiHash"),
        settings.THROUGHPUT_FOR_1_PARTITION, settings,
    )


def create_multi_partition_prefix_pk_container_if_not_exist(client, *, settings=TestSettings):
    return _create_container(
        client, settings.TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID,
        PartitionKey(path=settings.TEST_CONTAINER_PREFIX_PARTITION_KEY_PATH, kind="MultiHash"),
        settings.THROUGHPUT_FOR_5_PARTITIONS, settings,
    )


def try_delete_database(client, *, settings=TestSettings):
    try_delete_database_with_id(client, settings.TEST_DATABASE_ID)


def try_delete_database_with_id(client, database_id):
    """Delete the caller's owned database; only an already-deleted resource is ignored."""
    try:
        retry_control_plane(client.delete_database, database_id)
    except exceptions.CosmosHttpResponseError as error:
        if error.status_code != StatusCodes.NOT_FOUND:
            raise
