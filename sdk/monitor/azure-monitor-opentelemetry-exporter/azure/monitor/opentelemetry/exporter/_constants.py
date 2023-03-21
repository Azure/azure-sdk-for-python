# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable

# Network

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

# Statsbeat

# (OpenTelemetry metric name, Statsbeat metric name)
_ATTACH_METRIC_NAME = ("attach", "Attach")
_FEATURE_METRIC_NAME = ("feature", "Feature")
_REQ_EXCEPTION_NAME = ("statsbeat_exception_count", "Exception Count")
_REQ_DURATION_NAME = ("statsbeat_duration", "Request Duration")
_REQ_FAILURE_NAME = ("statsbeat_failure_count", "Request Failure Count")
_REQ_RETRY_NAME = ("statsbeat_retry_count", "Retry Count")
_REQ_SUCCESS_NAME = ("statsbeat_success_count", "Request Success Count")
_REQ_THROTTLE_NAME = ("statsbeat_throttle_count", "Throttle Count")

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
]

_INSTRUMENTATIONS_BIT_MAP = {_INSTRUMENTATIONS_LIST[i]: _BASE**i for i in range(len(_INSTRUMENTATIONS_LIST))}

# Standard metrics

# List of metric instrument names that are autocollected from instrumentations
# TODO: switch to semconv constants
_AUTOCOLLECTED_INSTRUMENT_NAMES = (
    "http.server.duration",
    "http.server.request.size",
    "http.server.response.size",
    "http.server.active_requests",
    "http.client.duration",
    "http.client.request.size",
    "http.client.response.size",
)

# Temporary solution for checking which instrumentations support metric collection
_INSTRUMENTATION_SUPPORTING_METRICS_LIST = (
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

# cSpell:disable
