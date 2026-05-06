# Azure Core - Environment Variables Reference

This document lists all environment variables recognized by `azure-core`.

## SDK Configuration

### `AZURE_LOG_LEVEL`

Controls the logging level for all Azure SDK clients.

| | |
|---|---|
| **Used by** | `azure.core.settings.Settings.log_level` |
| **Default** | `INFO` |
| **Accepted values** | `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `VERBOSE` (case-insensitive). `VERBOSE` is treated as `DEBUG`. |

If the value is not one of the accepted values, a warning is logged and `INFO` is used.

**Example:**

```bash
export AZURE_LOG_LEVEL=DEBUG
```

### `AZURE_TRACING_ENABLED`

Enables or disables distributed tracing across Azure SDK clients.

| | |
|---|---|
| **Used by** | `azure.core.settings.Settings.tracing_enabled` |
| **Default** | Auto-detected based on whether `AZURE_SDK_TRACING_IMPLEMENTATION` is set |
| **Accepted values** | `true`, `yes`, `1`, `on` to enable; `false`, `no`, `0`, `off` to disable (case-insensitive) |

If enabled and `settings.tracing_implementation` is not set (i.e. `AZURE_SDK_TRACING_IMPLEMENTATION` is unset), native OpenTelemetry tracing is used, provided that `opentelemetry-api` is installed. However, if a tracing implementation is configured, then that configured plugin is used instead.

If disabled, distributed tracing is disabled entirely, regardless of the other configuration.

If not set, tracing is automatically enabled if a tracing implementation is configured (via `AZURE_SDK_TRACING_IMPLEMENTATION`), and disabled otherwise.

If the value is not one of the accepted values, a warning is logged and the default behavior is used.

**Example:**

```bash
export AZURE_TRACING_ENABLED=true
```

### `AZURE_SDK_TRACING_IMPLEMENTATION`

Specifies which distributed tracing implementation the SDK should use.

| | |
|---|---|
| **Used by** | `azure.core.settings.Settings.tracing_implementation` |
| **Default** | None |
| **Accepted values** | `opentelemetry` |

The corresponding tracing plugin package must be installed:

- `opentelemetry` — requires `azure-core-tracing-opentelemetry`

If the value is not one of the accepted values, a warning is logged and the default (None) is used.

**Example:**

```bash
export AZURE_SDK_TRACING_IMPLEMENTATION=opentelemetry
```

### `AZURE_SDK_CLOUD_CONF`

Sets the Azure cloud environment used by SDK clients.

| | |
|---|---|
| **Used by** | `azure.core.settings.Settings.azure_cloud` |
| **Default** | `AZURE_PUBLIC_CLOUD` |
| **Accepted values** | `AZURE_PUBLIC_CLOUD`, `AZURE_CHINA_CLOUD`, `AZURE_US_GOVERNMENT` (case-sensitive)|

**Example:**

```bash
export AZURE_SDK_CLOUD_CONF=AZURE_CHINA_CLOUD
```

## HTTP Pipeline

### `AZURE_HTTP_USER_AGENT`

Appends a custom string to the `User-Agent` header sent with every HTTP request.

| | |
|---|---|
| **Used by** | `azure.core.pipeline.policies.UserAgentPolicy` |
| **Default** | None |
| **Accepted values** | Any string |

The value is appended to the end of the SDK-generated User-Agent string. This variable is only read when `user_agent_use_env=True` (the default).

**Example:**

```bash
export AZURE_HTTP_USER_AGENT="my-app/1.0"
```

### `AZURE_SDK_LOGGING_MULTIRECORD`

Controls the HTTP logging format used by `HttpLoggingPolicy`.

| | |
|---|---|
| **Used by** | `azure.core.pipeline.policies.HttpLoggingPolicy` |
| **Default** | Disabled (single-record format) |
| **Accepted values** | Any non-empty value to enable |

When set, HTTP request and response details are logged as separate log records instead of a single combined record. This can make log output easier to parse in structured logging systems.

**Example:**

```bash
export AZURE_SDK_LOGGING_MULTIRECORD=1
```

## Network & Proxy

These standard proxy environment variables are honored by the underlying HTTP transport libraries (`requests` and `aiohttp`) when the transport is created with `use_env_settings=True` (the default).

### `HTTP_PROXY`

HTTP proxy URL for requests made over HTTP.

| | |
|---|---|
| **Used by** | `RequestsTransport`, `AioHttpTransport` (via `session.trust_env`) |
| **Default** | None |
| **Accepted values** | `http://[user:password@]host:port` |

### `HTTPS_PROXY`

HTTP proxy URL for requests made over HTTPS.

| | |
|---|---|
| **Used by** | `RequestsTransport`, `AioHttpTransport` (via `session.trust_env`) |
| **Default** | None |
| **Accepted values** | `http://[user:password@]host:port` |

### `NO_PROXY`

Comma-separated list of hostnames or IP addresses that should bypass the proxy.

| | |
|---|---|
| **Used by** | `RequestsTransport`, `AioHttpTransport` (via `session.trust_env`) |
| **Default** | None |
| **Accepted values** | Comma-separated hostnames, e.g. `localhost,127.0.0.1,.example.com` |

**Example:**

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1,.internal.corp
```

To disable reading proxy settings from the environment, create the transport with `use_env_settings=False`:

```python
from azure.core.pipeline.transport import RequestsTransport

transport = RequestsTransport(use_env_settings=False)
```

## Settings Priority

Environment variables are just one source of configuration. The `azure.core.settings` module resolves values in the following priority order (highest to lowest):

1. **Immediate values** — passed directly when retrieving the setting
2. **User-set values** — assigned programmatically via `settings.<name> = value`
3. **Environment variables** — read from `os.environ`
4. **System settings** — obtained from OS-level registries or hooks
5. **Implicit defaults** — defined by the setting itself
