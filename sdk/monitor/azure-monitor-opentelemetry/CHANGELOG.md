# Release History

## 1.0.0b16 (2023-08-28)

### Features Added

- Unpin OTel SDK/API version
    ([#310](https://github.com/microsoft/ApplicationInsights-Python/pull/310))
- Replace explicit log processor exporter interval env var with OT SDK env var
    ([#31740](https://github.com/Azure/azure-sdk-for-python/pull/31740))
- Un-vendoring instrumentations
    ([#31744](https://github.com/Azure/azure-sdk-for-python/pull/31740))
- Add preview warning for Autoinstrumentation entry points
    ([#31767](https://github.com/Azure/azure-sdk-for-python/pull/31767))

## 1.0.0b15 (2023-07-17)

### Features Added

- Upgrade to exporter 1.0.0b15 and OTel 1.19
    ([#308](https://github.com/microsoft/ApplicationInsights-Python/pull/308))

## 1.0.0b14 (2023-07-12)

### Features Added

- Upgrade to exporter 1.0.0b14 and OTel 1.18
    ([#295](https://github.com/microsoft/ApplicationInsights-Python/pull/295))
- Enable Azure Core Tracing OpenTelemetry plugin
    ([#269](https://github.com/microsoft/ApplicationInsights-Python/pull/269))
- Fix connection string environment variable bug for manual instrumentation
    ([#302](https://github.com/microsoft/ApplicationInsights-Python/pull/302))
- Update Azure Core Tracing OpenTelemetry plugin
    ([#306](https://github.com/microsoft/ApplicationInsights-Python/pull/306))

## 1.0.0b13 (2023-06-14)

### Features Added

- Vendor Instrumentations
    ([#280](https://github.com/microsoft/ApplicationInsights-Python/pull/280))
- Support OTEL_PYTHON_DISABLED_INSTRUMENTATIONS
    ([#294](https://github.com/microsoft/ApplicationInsights-Python/pull/294))

### Other Changes

- Update samples
    ([#281](https://github.com/microsoft/ApplicationInsights-Python/pull/281))
- Fixed spelling
    ([#291](https://github.com/microsoft/ApplicationInsights-Python/pull/291))
- Fixing formatting issues for azure sdk
    ([#292](https://github.com/microsoft/ApplicationInsights-Python/pull/292))

## 1.0.0b12 (2023-05-05)

### Features Added

- Remove most configuration for Public Preview
    ([#277](https://github.com/microsoft/ApplicationInsights-Python/pull/277))
- Infer telemetry category disablement from exporter environment variables
    ([#278](https://github.com/microsoft/ApplicationInsights-Python/pull/278))

## 1.0.0b11 (2023-04-12)

### Features Added

- Reverse default behavior of instrumentations and implement configuration for exclusion
    ([#253](https://github.com/microsoft/ApplicationInsights-Python/pull/253))
- Use entrypoints instead of importlib to load instrumentations
    ([#254](https://github.com/microsoft/ApplicationInsights-Python/pull/254))
- Add support for FastAPI instrumentation
    ([#255](https://github.com/microsoft/ApplicationInsights-Python/pull/255))
- Add support for Urllib3/Urllib instrumentation
    ([#256](https://github.com/microsoft/ApplicationInsights-Python/pull/256))
- Change instrumentation config to use TypedDict InstrumentationConfig
    ([#259](https://github.com/microsoft/ApplicationInsights-Python/pull/259))
- Change interval params to use `_ms` as suffix
    ([#260](https://github.com/microsoft/ApplicationInsights-Python/pull/260))
- Update exporter version to 1.0.0b13 and OTel sdk/api to 1.17
    ([#270](https://github.com/microsoft/ApplicationInsights-Python/pull/270))

## 1.0.0b10 (2023-02-23)

### Features Added

- Fix source and wheel distribution, include MANIFEST.in and use `pkgutils` style `__init__.py`
    ([#250](https://github.com/microsoft/ApplicationInsights-Python/pull/250))

## 1.0.0b9 (2023-02-22)

### Features Added

- Made build.sh script executable from publish workflow
    ([#213](https://github.com/microsoft/ApplicationInsights-Python/pull/213))
- Updated main and distro READMEs
    ([#205](https://github.com/microsoft/ApplicationInsights-Python/pull/205))
- Update CONTRIBUTING.md, support Py3.11
    ([#210](https://github.com/microsoft/ApplicationInsights-Python/pull/210))
- Added Diagnostic Logging for App Service
    ([#212](https://github.com/microsoft/ApplicationInsights-Python/pull/212))
- Updated setup.py, directory structure
    ([#214](https://github.com/microsoft/ApplicationInsights-Python/pull/214))
- Introduce Distro API
    ([#215](https://github.com/microsoft/ApplicationInsights-Python/pull/215))
- Rename to `configure_azure_monitor`, add sampler to config
    ([#216](https://github.com/microsoft/ApplicationInsights-Python/pull/216))
- Added Status Logger
    ([#217](https://github.com/microsoft/ApplicationInsights-Python/pull/217))
- Add Logging configuration to Distro API
    ([#218](https://github.com/microsoft/ApplicationInsights-Python/pull/218))
- Add instrumentation selection config
    ([#228](https://github.com/microsoft/ApplicationInsights-Python/pull/228))
- Removing diagnostic logging from its module's logger.
    ([#225](https://github.com/microsoft/ApplicationInsights-Python/pull/225))
- Add ability to specify logger for logging configuration
    ([#227](https://github.com/microsoft/ApplicationInsights-Python/pull/227))
- Add metric configuration to distro api
    ([#232](https://github.com/microsoft/ApplicationInsights-Python/pull/232))
- Add ability to pass custom configuration into instrumentations
    ([#235](https://github.com/microsoft/ApplicationInsights-Python/pull/235))
- Fix export interval bug
    ([#237](https://github.com/microsoft/ApplicationInsights-Python/pull/237))
- Add ability to specify custom metric readers
    ([#241](https://github.com/microsoft/ApplicationInsights-Python/pull/241))
- Defaulting logging env var for auto-instrumentation. Added logging samples.
    ([#240](https://github.com/microsoft/ApplicationInsights-Python/pull/240))
- Removed old log_diagnostic_error calls from configurator
    ([#242](https://github.com/microsoft/ApplicationInsights-Python/pull/242))
- Update to azure-monitor-opentelemetry-exporter 1.0.0b12
    ([#243](https://github.com/microsoft/ApplicationInsights-Python/pull/243))
- Move symbols to protected, add docstring for api, pin opentelemetry-api/sdk versions
    ([#244](https://github.com/microsoft/ApplicationInsights-Python/pull/244))
- Replace service.X configurations with Resource
    ([#246](https://github.com/microsoft/ApplicationInsights-Python/pull/246))
- Change namespace to `azure.monitor.opentelemetry`
    ([#247](https://github.com/microsoft/ApplicationInsights-Python/pull/247))
- Updating documents for new namespace
    ([#249](https://github.com/microsoft/ApplicationInsights-Python/pull/249))
- Configuration via env vars and argument validation.
    ([#262](https://github.com/microsoft/ApplicationInsights-Python/pull/262))

## 1.0.0b8 (2022-09-26)

### Features Added

- Changing instrumentation dependencies to ~=0.33b0
    ([#203](https://github.com/microsoft/ApplicationInsights-Python/pull/203))

## 1.0.0b7 (2022-09-26)

### Features Added

- Moved and updated README
    ([#201](https://github.com/microsoft/ApplicationInsights-Python/pull/201))
- Adding requests, flask, and psycopg2 instrumentations
    ([#199](https://github.com/microsoft/ApplicationInsights-Python/pull/199))
- Added publishing action
    ([#193](https://github.com/microsoft/ApplicationInsights-Python/pull/193))

## 1.0.0b6 (2022-08-30)

### Features Added

- Drop support for Python 3.6
    ([#190](https://github.com/microsoft/ApplicationInsights-Python/pull/190))
- Changed repository structure to use submodules
    ([#190](https://github.com/microsoft/ApplicationInsights-Python/pull/190))
- Added OpenTelemetry Distro and Configurator
    ([#187](https://github.com/microsoft/ApplicationInsights-Python/pull/187))
- Initial commit
