# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable

from opentelemetry.semconv.metrics import MetricInstruments

# Environment variables

_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL = "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"
_APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED = \
    "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED"
_APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN = "APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN"
_WEBSITE_SITE_NAME = "WEBSITE_SITE_NAME"
_WEBSITE_HOME_STAMPNAME = "WEBSITE_HOME_STAMPNAME"
_WEBSITE_HOSTNAME = "WEBSITE_HOSTNAME"
_FUNCTIONS_WORKER_RUNTIME = "FUNCTIONS_WORKER_RUNTIME"
_AKS_ARM_NAMESPACE_ID = "AKS_ARM_NAMESPACE_ID"

# Network

_INVALID_STATUS_CODES = (
    400, # Invalid Instrumentation Key/data
)

_REDIRECT_STATUS_CODES = (
    307,  # Temporary redirect
    308,  # Permanent redirect
)

_RETRYABLE_STATUS_CODES = (
    206,  # Partial success
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

# Feature constants
_APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE = "APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE"
_AZURE_MONITOR_DISTRO_VERSION_ARG = "distro_version"

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

# Instrumentations

# Special constant for azure-sdk opentelemetry instrumentation
_AZURE_SDK_OPENTELEMETRY_NAME = "azure-sdk-opentelemetry"
_AZURE_SDK_NAMESPACE_NAME = "az.namespace"

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
    "aiohttp-client",
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
    "kafka-python",
    "pika",
    "pymemcache",
    "redis",
    "remoulade",
    "sklearn",
    "sqlite3",
    "starlette",
    "system-metrics",
    "tornado",
    "urllib",
    "urllib3",
    _AZURE_SDK_OPENTELEMETRY_NAME,
    # Instrumentations below this line have not been added to statsbeat report yet
    "cassandra",
    "tortoiseorm",
    "aiohttp-server",
    "asyncio",
    "mysqlclient",
    "psycopg",
    "threading",
    "wsgi",
]

_INSTRUMENTATIONS_BIT_MAP = {_INSTRUMENTATIONS_LIST[i]: _BASE**i for i in range(len(_INSTRUMENTATIONS_LIST))}

# Standard metrics

# List of metric instrument names that are autocollected from instrumentations
_AUTOCOLLECTED_INSTRUMENT_NAMES = (
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

_APPLICATION_INSIGHTS_RESOURCE_SCOPE = "https://monitor.azure.com//.default"

# cSpell:disable
