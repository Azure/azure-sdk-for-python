# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable

from enum import Enum
from typing import Union
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.semconv.metrics.http_metrics import (
    HTTP_CLIENT_REQUEST_DURATION,
    HTTP_SERVER_REQUEST_DURATION,
)
from azure.core import CaseInsensitiveEnumMeta

# Environment variables

_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL = "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"
_APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED = (
    "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED"
)
_APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN = "APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN"
_APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED = "APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED"
_APPLICATIONINSIGHTS_AUTHENTICATION_STRING = "APPLICATIONINSIGHTS_AUTHENTICATION_STRING"

# RPs

_WEBSITE_SITE_NAME = "WEBSITE_SITE_NAME"
_WEBSITE_HOME_STAMPNAME = "WEBSITE_HOME_STAMPNAME"
_WEBSITE_HOSTNAME = "WEBSITE_HOSTNAME"
_FUNCTIONS_WORKER_RUNTIME = "FUNCTIONS_WORKER_RUNTIME"
_PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY = "PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY"
_AKS_ARM_NAMESPACE_ID = "AKS_ARM_NAMESPACE_ID"
_KUBERNETES_SERVICE_HOST = "KUBERNETES_SERVICE_HOST"

# Network

_INVALID_STATUS_CODES = (400,)  # Invalid Instrumentation Key/data

_REDIRECT_STATUS_CODES = (
    307,  # Temporary redirect
    308,  # Permanent redirect
)

_RETRYABLE_STATUS_CODES = (
    401,  # Unauthorized
    403,  # Forbidden
    408,  # Request Timeout
    429,  # Too Many Requests - retry after
    500,  # Internal Server Error
    502,  # BadGateway
    503,  # Service Unavailable
    504,  # Gateway timeout
)

_THROTTLE_STATUS_CODES = (
    402,  # Quota, too Many Requests over extended time
    439,  # Quota, too Many Requests over extended time (legacy)
)

_REACHED_INGESTION_STATUS_CODES = (200, 206, 402, 408, 429, 439, 500)

# Envelope constants

_METRIC_ENVELOPE_NAME = "Microsoft.ApplicationInsights.Metric"
_EXCEPTION_ENVELOPE_NAME = "Microsoft.ApplicationInsights.Exception"
_MESSAGE_ENVELOPE_NAME = "Microsoft.ApplicationInsights.Message"
_REQUEST_ENVELOPE_NAME = "Microsoft.ApplicationInsights.Request"
_REMOTE_DEPENDENCY_ENVELOPE_NAME = "Microsoft.ApplicationInsights.RemoteDependency"
_EVENT_ENVELOPE_NAME = "Microsoft.ApplicationInsights.Event"
_PAGE_VIEW_ENVELOPE_NAME = "Microsoft.ApplicationInsights.PageView"
_PERFORMANCE_COUNTER_ENVELOPE_NAME = "Microsoft.ApplicationInsights.PerformanceCounter"
_AVAILABILITY_ENVELOPE_NAME = "Microsoft.ApplicationInsights.Availability"

# Feature constants
_APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE = "APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE"
_AZURE_MONITOR_DISTRO_VERSION_ARG = "distro_version"
_MICROSOFT_CUSTOM_EVENT_NAME = "microsoft.custom_event.name"

# Statsbeat
# (OpenTelemetry metric name, Statsbeat metric name)
_ATTACH_METRIC_NAME = ("attach", "Attach")
_FEATURE_METRIC_NAME = ("feature", "Feature")
_REQ_EXCEPTION_NAME = ("statsbeat_exception_count", "Exception_Count")
_REQ_DURATION_NAME = ("statsbeat_duration", "Request_Duration")
_REQ_FAILURE_NAME = ("statsbeat_failure_count", "Request_Failure_Count")
_REQ_RETRY_NAME = ("statsbeat_retry_count", "Retry_Count")
_REQ_SUCCESS_NAME = ("statsbeat_success_count", "Request_Success_Count")
_REQ_THROTTLE_NAME = ("statsbeat_throttle_count", "Throttle_Count")

_STATSBEAT_METRIC_NAME_MAPPINGS = dict(
    [
        _ATTACH_METRIC_NAME,
        _FEATURE_METRIC_NAME,
        _REQ_DURATION_NAME,
        _REQ_EXCEPTION_NAME,
        _REQ_FAILURE_NAME,
        _REQ_SUCCESS_NAME,
        _REQ_RETRY_NAME,
        _REQ_THROTTLE_NAME,
    ]
)
_APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME = "APPLICATIONINSIGHTS_STATS_CONNECTION_STRING"
_APPLICATIONINSIGHTS_STATS_SHORT_EXPORT_INTERVAL_ENV_NAME = "APPLICATIONINSIGHTS_STATS_SHORT_EXPORT_INTERVAL"
_APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL_ENV_NAME = "APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL"
# pylint: disable=line-too-long
_DEFAULT_NON_EU_STATS_CONNECTION_STRING = "InstrumentationKey=c4a29126-a7cb-47e5-b348-11414998b11e;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/"
_DEFAULT_EU_STATS_CONNECTION_STRING = "InstrumentationKey=7dc56bab-3c0c-4e9f-9ebb-d1acadee8d0f;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/"
_DEFAULT_STATS_SHORT_EXPORT_INTERVAL = 900  # 15 minutes
_DEFAULT_STATS_LONG_EXPORT_INTERVAL = 86400  # 24 hours
_EU_ENDPOINTS = [
    "westeurope",
    "northeurope",
    "francecentral",
    "francesouth",
    "germanywestcentral",
    "norwayeast",
    "norwaywest",
    "swedencentral",
    "switzerlandnorth",
    "switzerlandwest",
    "uksouth",
    "ukwest",
]

# Telemetry Types
_AVAILABILITY = "AVAILABILITY"
_CUSTOM_EVENT = "CUSTOM_EVENT"
_CUSTOM_METRIC = "CUSTOM_METRIC"
_DEPENDENCY = "DEPENDENCY"
_EXCEPTION = "EXCEPTION"
_PAGE_VIEW = "PAGE_VIEW"
_PERFORMANCE_COUNTER = "PERFORMANCE_COUNTER"
_REQUEST = "REQUEST"
_TRACE = "TRACE"
_UNKNOWN = "UNKNOWN"

# Customer Facing Statsbeat
_APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW = "APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW"

_CUSTOMER_STATSBEAT_LANGUAGE = "python"

class DropCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CLIENT_READONLY = "CLIENT_READONLY"
    CLIENT_EXCEPTION = "CLIENT_EXCEPTION"
    CLIENT_STALE_DATA = "CLIENT_STALE_DATA"
    CLIENT_PERSISTENCE_CAPACITY = "CLIENT_PERSISTENCE_CAPACITY"
    UNKNOWN = "UNKNOWN"

DropCodeType = Union[DropCode, int]

class RetryCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CLIENT_EXCEPTION = "CLIENT_EXCEPTION"
    CLIENT_TIMEOUT = "CLIENT_TIMEOUT"
    UNKNOWN = "UNKNOWN"

RetryCodeType = Union[RetryCode, int]

class CustomerStatsbeatMetricName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ITEM_SUCCESS_COUNT = "preview.item.success.count"
    ITEM_DROP_COUNT = "preview.item.dropped.count"
    ITEM_RETRY_COUNT = "preview.item.retry.count"

class CustomerStatsbeatProperties:
    language: str
    version: str
    compute_type: str
    def __init__(self, language: str, version: str, compute_type: str):
        self.language = language
        self.version = version
        self.compute_type = compute_type

## Map from Azure Monitor envelope names to TelemetryType
_TYPE_MAP = {
                _EVENT_ENVELOPE_NAME: _CUSTOM_EVENT,
                _METRIC_ENVELOPE_NAME: _CUSTOM_METRIC,
                _REMOTE_DEPENDENCY_ENVELOPE_NAME: _DEPENDENCY,
                _EXCEPTION_ENVELOPE_NAME: _EXCEPTION,
                _PAGE_VIEW_ENVELOPE_NAME: _PAGE_VIEW,
                _MESSAGE_ENVELOPE_NAME: _TRACE,
                _REQUEST_ENVELOPE_NAME: _REQUEST,
                _PERFORMANCE_COUNTER_ENVELOPE_NAME: _PERFORMANCE_COUNTER,
                _AVAILABILITY_ENVELOPE_NAME: _AVAILABILITY,
            }

# Map RP names
class _RP_Names(Enum):
    APP_SERVICE = "appsvc"
    FUNCTIONS = "functions"
    AKS = "aks"
    VM = "vm"
    UNKNOWN = "unknown"

# Instrumentations

# Special constant for azure-sdk opentelemetry instrumentation
_AZURE_SDK_OPENTELEMETRY_NAME = "azure-sdk-opentelemetry"
_AZURE_SDK_NAMESPACE_NAME = "az.namespace"
_AZURE_AI_SDK_NAME = "azure-ai-opentelemetry"

_BASE = 2

_INSTRUMENTATIONS_LIST = [
    "django",
    "flask",
    "google_cloud",
    "http_lib",
    "logging",
    "mysql",
    "psycopg2",
    "pymongo",
    "pymysql",
    "pyramid",
    "requests",
    "sqlalchemy",
    "aio-pika",
    "aiohttp_client",
    "aiopg",
    "asgi",
    "asyncpg",
    "celery",
    "confluent-kafka",
    "dbapi",
    "elasticsearch",
    "falcon",
    "fastapi",
    "grpc",
    "httpx",
    "jinja2",
    "kafka",
    "pika",
    "pymemcache",
    "redis",
    "remoulade",
    "sklearn",
    "sqlite3",
    "starlette",
    "system_metrics",
    "tornado",
    "urllib",
    "urllib3",
    _AZURE_SDK_OPENTELEMETRY_NAME,
    "cassandra",
    "tortoiseorm",
    "aiohttp_server",
    "asyncio",
    "mysqlclient",
    "psycopg",
    "threading",
    "wsgi",
    "aiokafka",
    "asyncclick",
    "click",
    "pymssql",
    "google_genai",
    "openai_v2",
    "vertexai",
    # Instrumentations below this line have not been added to statsbeat report yet
    _AZURE_AI_SDK_NAME
]

_INSTRUMENTATIONS_BIT_MAP = {_INSTRUMENTATIONS_LIST[i]: _BASE**i for i in range(len(_INSTRUMENTATIONS_LIST))}

# Standard metrics

# List of metric instrument names that are autocollected from instrumentations
_AUTOCOLLECTED_INSTRUMENT_NAMES = (
    HTTP_CLIENT_REQUEST_DURATION,
    HTTP_SERVER_REQUEST_DURATION,
    MetricInstruments.HTTP_SERVER_DURATION,
    MetricInstruments.HTTP_SERVER_REQUEST_SIZE,
    MetricInstruments.HTTP_SERVER_RESPONSE_SIZE,
    MetricInstruments.HTTP_SERVER_ACTIVE_REQUESTS,
    MetricInstruments.HTTP_CLIENT_DURATION,
    MetricInstruments.HTTP_CLIENT_REQUEST_SIZE,
    MetricInstruments.HTTP_CLIENT_RESPONSE_SIZE,
)

# Temporary solution for checking which instrumentations support metric collection
_INSTRUMENTATION_SUPPORTING_METRICS_LIST = (
    "opentelemetry.instrumentation.asgi",
    "opentelemetry.instrumentation.django",
    "opentelemetry.instrumentation.falcon",
    "opentelemetry.instrumentation.fastapi",
    "opentelemetry.instrumentation.flask",
    "opentelemetry.instrumentation.pyramid",
    "opentelemetry.instrumentation.requests",
    "opentelemetry-instrumentation-sqlalchemy",
    "opentelemetry.instrumentation.starlette",
    "opentelemetry-instrumentation-tornado",
    "opentelemetry-instrumentation-urllib",
    "opentelemetry.instrumentation.urllib3",
    "opentelemetry.instrumentation.wsgi",
)

# sampleRate

_SAMPLE_RATE_KEY = "_MS.sampleRate"

# AAD Auth

_DEFAULT_AAD_SCOPE = "https://monitor.azure.com//.default"

# cSpell:disable
