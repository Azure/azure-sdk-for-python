# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import locale
from os import environ
from os.path import isdir
import platform
import threading
import time
import warnings
from typing import Any, Callable, Dict, Optional

from opentelemetry.semconv.attributes.service_attributes import SERVICE_NAME
from opentelemetry.semconv.trace import DbSystemValues, SpanAttributes
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.util.types import Attributes

from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys, TelemetryItem
from azure.monitor.opentelemetry.exporter._version import VERSION as ext_version
from azure.monitor.opentelemetry.exporter._constants import (
    _AKS_ARM_NAMESPACE_ID,
    _APPLICATION_INSIGHTS_RESOURCE_SCOPE,
    _PYTHON_ENABLE_OPENTELEMETRY,
    _INSTRUMENTATIONS_BIT_MAP,
    _FUNCTIONS_WORKER_RUNTIME,
    _WEBSITE_SITE_NAME,
)

# pylint:disable=too-many-return-statements
def _get_default_port_db(db_system: str) -> int:
    if db_system == DbSystemValues.POSTGRESQL.value:
        return 5432
    if db_system == DbSystemValues.CASSANDRA.value:
        return 9042
    if db_system in (DbSystemValues.MARIADB.value, DbSystemValues.MYSQL.value):
        return 3306
    if db_system == DbSystemValues.MSSQL.value:
        return 1433
    # TODO: Add in memcached
    if db_system == "memcached":
        return 11211
    if db_system == DbSystemValues.DB2.value:
        return 50000
    if db_system == DbSystemValues.ORACLE.value:
        return 1521
    if db_system == DbSystemValues.H2.value:
        return 8082
    if db_system == DbSystemValues.DERBY.value:
        return 1527
    if db_system == DbSystemValues.REDIS.value:
        return 6379
    return 0


def _get_default_port_http(scheme: str) -> int:
    if scheme == "http":
        return 80
    if scheme == "https":
        return 443
    return 0


def _is_sql_db(db_system: str) -> bool:
    return db_system in (
        DbSystemValues.DB2.value,
        DbSystemValues.DERBY.value,
        DbSystemValues.MARIADB.value,
        DbSystemValues.MSSQL.value,
        DbSystemValues.ORACLE.value,
        DbSystemValues.SQLITE.value,
        DbSystemValues.OTHER_SQL.value,
        # spell-checker:ignore HSQLDB
        DbSystemValues.HSQLDB.value,
        DbSystemValues.H2.value,
      )


def _get_azure_sdk_target_source(attributes: Attributes) -> Optional[str]:
    # Currently logic only works for ServiceBus and EventHub
    if attributes:
        peer_address = attributes.get("peer.address")
        destination = attributes.get("message_bus.destination")
        if peer_address and destination:
            return str(peer_address) + "/" + str(destination)
    return None
