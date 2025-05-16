# cSpell:disable

# Release History

## 1.0.0b37 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

- Extend version range for `psutil` to include 7.x
  ([#40459](https://github.com/Azure/azure-sdk-for-python/pull/40459))

## 1.0.0b36 (2025-04-07)

### Features Added

- Support `syntheticSource` from `user_agent.synthetic.type` semantic convention
  ([#40004](https://github.com/Azure/azure-sdk-for-python/pull/40004))
- Support `server.address` attributes when converting Azure SDK messaging spans to envelopes
  ([#40059](https://github.com/Azure/azure-sdk-for-python/pull/40059))
- Update AKS check to use KUBERNETES_SERVICE_HOST
  ([#39941](https://github.com/Azure/azure-sdk-for-python/pull/39941))
- Enabled Entra ID Credential configuration via env var
  ([#40237](https://github.com/Azure/azure-sdk-for-python/pull/40237))

## 1.0.0b35 (2025-03-04)

### Features Added

- Support sending `customEvent` telemetry through special `microsoft` marker
  ([#39886](https://github.com/Azure/azure-sdk-for-python/pull/39886))
- Populate `client_Ip` on `customEvent` telemetry
  ([#39923](https://github.com/Azure/azure-sdk-for-python/pull/39923))

### Bugs Fixed

- Implement `from_log_record` for `Trace` data types in live metrics
  ([#39922](https://github.com/Azure/azure-sdk-for-python/pull/39922))

## 1.0.0b34 (2025-02-26)

### Features Added

- Support AAD for sovereign clouds
  ([#39379](https://github.com/Azure/azure-sdk-for-python/pull/39379))
- Support stable http semantic conventions for breeze exporter - REQUESTS
  ([#39208](https://github.com/Azure/azure-sdk-for-python/pull/39208))
- Support stable http semantic conventions for breeze exporter - DEPENDENCIES
  ([#39441](https://github.com/Azure/azure-sdk-for-python/pull/39441))
  - Support stable http semantic conventions for standard metrics + synthetic type for server standard metrics
  ([#39799](https://github.com/Azure/azure-sdk-for-python/pull/39799))

## 1.0.0b33 (2025-01-14)

### Features Added

- Implement live metrics filtering for metrics
  ([#37998](https://github.com/Azure/azure-sdk-for-python/pull/37998))
- Add applying filter/validating filter logic to live metrics filtering
  ([#38451](https://github.com/Azure/azure-sdk-for-python/pull/38451))
- Implement live metrics filtering for docs
  ([#38925](https://github.com/Azure/azure-sdk-for-python/pull/38925))
- Implement live metrics + filtering for span event exceptions
  ([#39168](https://github.com/Azure/azure-sdk-for-python/pull/39168))

### Bugs Fixed

- Detect live metrics usage during runtime in addition to on startup
  ([#37694](https://github.com/Azure/azure-sdk-for-python/pull/37694))
- Remove status code `206` from retry code + only count batch level for statsbeat
  ([#38647](https://github.com/Azure/azure-sdk-for-python/pull/38647))

### Other Changes

- Refactored live metrics filtering modules
  ([#38837](https://github.com/Azure/azure-sdk-for-python/pull/38837))

## 1.0.0b32 (2024-11-04)

### Breaking Changes

- Serialize complex objects provided as log or event bodies to JSON and
  fall back to string representation if they are not serializable.
  ([#37694](https://github.com/Azure/azure-sdk-for-python/pull/37694))

### Other Changes

- Refactor trace mapping logic for target and data into trace utils
    ([#37897](https://github.com/Azure/azure-sdk-for-python/pull/37897))

## 1.0.0b31 (2024-10-08)

### Features Added

- Allow tracking of whether in a Azure Functions attach scenario
    ([#37717](https://github.com/Azure/azure-sdk-for-python/pull/37717))

## 1.0.0b30 (2024-09-20)

### Bugs Fixed

- Fix setting custom `TracerProvider` bug
    ([#37469](https://github.com/Azure/azure-sdk-for-python/pull/37469))

## 1.0.0b29 (2024-09-10)

### Features Added

- Allow passing in of custom `TracerProvider` for `AzureMonitorTraceExporter`
    ([#36363](https://github.com/Azure/azure-sdk-for-python/pull/36363))
- Support AAD Auth for live metrics
    ([#37258](https://github.com/Azure/azure-sdk-for-python/pull/37258))

### Other Changes

- Update instrumentation constants info
    ([#36696](https://github.com/Azure/azure-sdk-for-python/pull/36696))
- Refactor statsbeat utils functions
    ([#36824](https://github.com/Azure/azure-sdk-for-python/pull/36824))

## 1.0.0b28 (2024-07-29)

### Other Changes

- Support for Python 3.12
    ([#36481](https://github.com/Azure/azure-sdk-for-python/pull/36481))

## 1.0.0b27 (2024-06-21)

### Features Added

- Implement redirect for live metrics
    ([#35910](https://github.com/Azure/azure-sdk-for-python/pull/35910))

### Bugs Fixed

- Default missing/invalid status codes to "0" for standard metrics/trace payloads, change
    success criteria to `False` for those invalid cases, change success criteria to status_code < 400 for
    both client and server standard metrics
    ([#36079](https://github.com/Azure/azure-sdk-for-python/pull/36079))

## 1.0.0b26 (2024-05-29)

### Bugs Fixed

- Handle invalid status codes in std metric payload
    ([#35762](https://github.com/Azure/azure-sdk-for-python/pull/35762))
- Disable distributed tracing for live metrics client calls
    ([#35822](https://github.com/Azure/azure-sdk-for-python/pull/35822))

### Other Changes

- Update live metrics to use typespec generated swagger
    ([#34840](https://github.com/Azure/azure-sdk-for-python/pull/34840))
- Send old and new process level live metrics
    ([#35753](https://github.com/Azure/azure-sdk-for-python/pull/35753))

## 1.0.0b25 (2024-04-19)

### Features Added

- Enable sampling for attach
    ([#35218](https://github.com/Azure/azure-sdk-for-python/pull/35218))

## 1.0.0b24 (2024-04-05)

### Features Added

- Add live metrics collection of requests/dependencies/exceptions
    ([#34673](https://github.com/Azure/azure-sdk-for-python/pull/34673))
- Add live metrics collection of cpu time/process memory
    ([#34735](https://github.com/Azure/azure-sdk-for-python/pull/34735))
- Add live metrics collection feature detection to statsbeat
    ([#34752](https://github.com/Azure/azure-sdk-for-python/pull/34752))

### Breaking Changes

- Rename Statbeat environments variables to use `APPLICATIONINSIGHTS_*`
    ([#34742](https://github.com/Azure/azure-sdk-for-python/pull/34742))

### Bugs Fixed

- Reduce vm metadata service timeout to 200ms
    ([#35039](https://github.com/Azure/azure-sdk-for-python/pull/35039))

### Other Changes

- Updated FastAPI sample
    ([#34738](https://github.com/Azure/azure-sdk-for-python/pull/34738))
- Set up branching logic for attach function
    ([#35066](https://github.com/Azure/azure-sdk-for-python/pull/35066))

## 1.0.0b23 (2024-02-28)

### Features Added

- Add device.* to part A fields
    ([#34229](https://github.com/Azure/azure-sdk-for-python/pull/34229))
- Add live metrics exporting functionality
    ([#34141](https://github.com/Azure/azure-sdk-for-python/pull/34141))
- Add application.ver to part A fields
    ([#34401](https://github.com/Azure/azure-sdk-for-python/pull/34401))
- Add `APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN`
    ([#34463](https://github.com/Azure/azure-sdk-for-python/pull/34463))

### Other Changes

- Add attachType character to sdkVersion prefix
    ([#34226](https://github.com/Azure/azure-sdk-for-python/pull/34226))
- Add AKS scenarios to statsbeat metric and sdkVersion prefix
    ([#34427](https://github.com/Azure/azure-sdk-for-python/pull/34427))

## 1.0.0b22 (2024-02-01)

### Features Added

- Add live metrics skeleton + swagger definitions
    ([#33983](https://github.com/Azure/azure-sdk-for-python/pull/33983))
- Only create temporary folder if local storage is enabled without storage directory.
    ([#34061](https://github.com/Azure/azure-sdk-for-python/pull/34061))

### Bugs Fixed

- Update exception details messsage based on `LogRecord` body
    ([#34020](https://github.com/Azure/azure-sdk-for-python/pull/34020))

### Other Changes

- Drop support for Python 3.7
    ([#34105](https://github.com/Azure/azure-sdk-for-python/pull/34105))

## 1.0.0b21 (2024-01-16)

### Other Changes

- Update to OTel SKD/API 1.21
    ([#33864](https://github.com/Azure/azure-sdk-for-python/pull/33864))
- Update Django sample
    ([#33834](https://github.com/Azure/azure-sdk-for-python/pull/33834))

## 1.0.0b20 (2024-01-04)

### Other Changes

- Store global instance of `StatsbeatMetric`
    ([#33432](https://github.com/Azure/azure-sdk-for-python/pull/33432))
- Shutdown statsbeat on customer getting 400 error code
    ([#33489](https://github.com/Azure/azure-sdk-for-python/pull/33489))
- Track custom events extension in feature statsbeat
    ([#33667](https://github.com/Azure/azure-sdk-for-python/pull/33667))
- Readme examples are updated with correct imports
    ([#33691](https://github.com/Azure/azure-sdk-for-python/pull/33691))
- Implement distro detection for statsbeat feature
    ([#33761](https://github.com/Azure/azure-sdk-for-python/pull/33761))
- Use empty resource for statsbeat `MeterProvider`
    ([#33768](https://github.com/Azure/azure-sdk-for-python/pull/33768))

## 1.0.0b19 (2023-11-20)

### Bugs Fixed

- Fix deserialization of `TelemetryItem` from local storage
    ([#33163](https://github.com/Azure/azure-sdk-for-python/pull/33163))

## 1.0.0b18 (2023-11-06)

### Bugs Fixed

- Default exception type for blank exceptions
    ([#32327](https://github.com/Azure/azure-sdk-for-python/pull/32327))
- Updated django samples with clearly artificial secret key
    ([#32698](https://github.com/Azure/azure-sdk-for-python/pull/32698))
- Remove metric namespace
    ([#32897](https://github.com/Azure/azure-sdk-for-python/pull/32897))

## 1.0.0b17 (2023-09-12)

### Bugs Fixed

- Handle missing or empty message data
    ([#31944](https://github.com/Azure/azure-sdk-for-python/pull/31944))

## 1.0.0b16 (2023-08-30)

### Features Added

- Export OTel Resource
    ([#31355](https://github.com/Azure/azure-sdk-for-python/pull/31355))
- Use observed timestamp for log record if timetamp is None
    ([#31660](https://github.com/Azure/azure-sdk-for-python/pull/31660))
- Support custom events
    ([#31883](https://github.com/Azure/azure-sdk-for-python/pull/31883))

### Other Changes

- Unpin Opentelemetry SDK/API.
    ([#31253](https://github.com/Azure/azure-sdk-for-python/pull/31253))

## 1.0.0b15 (2023-07-17)

### Features Added

- Upgrading to OpenTelemetry SDK/API 1.19.
    ([#31170](https://github.com/Azure/azure-sdk-for-python/pull/31170))

## 1.0.0b14 (2023-06-09)

### Features Added

- Upgrading to OpenTelemetry SDK/API 1.18.
    ([#30611](https://github.com/Azure/azure-sdk-for-python/pull/30611))

## 1.0.0b13 (2023-04-11)

### Features Added

- Enable AAD Credentials
    ([#28888](https://github.com/Azure/azure-sdk-for-python/pull/28888))
- Upgrading to OpenTelemetry SDK/API 1.17
    ([#29656](https://github.com/Azure/azure-sdk-for-python/pull/29656))
- Updating sdkVersion prefix according to new spec. Using agents folder for marker.
    ([#29730](https://github.com/Azure/azure-sdk-for-python/pull/29730))

## 1.0.0b12 (2023-02-06)

### Features Added

- Add sdkVersion prefix during App Service attach
    ([#28637](https://github.com/Azure/azure-sdk-for-python/pull/28637))
- Correcting sdkVersion prefix
    ([#29227](https://github.com/Azure/azure-sdk-for-python/pull/29227))

### Bugs Fixed

- Update success criteria for requests
    ([#28486](https://github.com/Azure/azure-sdk-for-python/pull/28486))

### Other Changes

- Loosen instrumentation key validation strictness
    ([#28316](https://github.com/Azure/azure-sdk-for-python/pull/28316))
- Disable storage for statsbeat if storage is disabled for exporter
    ([#28322](https://github.com/Azure/azure-sdk-for-python/pull/28322))
- Add UK to eu statsbeats
    ([#28379](https://github.com/Azure/azure-sdk-for-python/pull/28379))
- Update to opentelemetry api/sdk v1.15
    ([#28499](https://github.com/Azure/azure-sdk-for-python/pull/28499))
- Update logging samples import paths to opentelemetry api/sdk v1.15
    ([#28646](https://github.com/Azure/azure-sdk-for-python/pull/28646))

## 1.0.0b11 (2022-12-15)

### Features Added

- Add pre-aggregated standard metrics - requests/duration, dependencies/duration
    ([#26753](https://github.com/Azure/azure-sdk-for-python/pull/26753))
- Add azure-sdk usage to instrumentations statsbeat
    ([#27756](https://github.com/Azure/azure-sdk-for-python/pull/27756))

### Bugs Fixed

- Pinning OpenTelemetry SDK and API to between 1.12 and 1.14 to avoid bug from change in module path. Reverting [#27913]
    ([#27958](https://github.com/Azure/azure-sdk-for-python/pull/27958))
- Pass along sampleRate in SpanEvents from Span
    ([#27629](https://github.com/Azure/azure-sdk-for-python/pull/27629))

## 1.0.0b10 (2022-11-10)

### Bugs Fixed

- Fix missing local storage attribute
    ([#27405](https://github.com/Azure/azure-sdk-for-python/pull/27405))
- Fix offline storage rename
    ([#27414](https://github.com/Azure/azure-sdk-for-python/pull/27414))

## 1.0.0b9 (2022-11-08)

### Features Added

- Add Sampler factory and entry point
    ([#27236](https://github.com/Azure/azure-sdk-for-python/pull/27236))
- Add validation logic to ApplicationInsightsSampler
    ([#26546](https://github.com/Azure/azure-sdk-for-python/pull/26546))
- Change default temporality of metrics to follow OTLP
    ([#26924](https://github.com/Azure/azure-sdk-for-python/pull/26924))

### Breaking Changes

- Rename local storage configuration, change default path
    ([#26891](https://github.com/Azure/azure-sdk-for-python/pull/26891))
- Change default storage retention period to 48 hours
    ([#26960](https://github.com/Azure/azure-sdk-for-python/pull/26960))

### Bugs Fixed

- Fixed sampleRate field in ApplicationInsightsSampler, changed attribute to `_MS.sampleRate`
    ([#26771](https://github.com/Azure/azure-sdk-for-python/pull/26771))

### Other Changes

- Update `README.md`
    ([#26520](https://github.com/Azure/azure-sdk-for-python/pull/26520))

## 1.0.0b8 (2022-09-26)

### Features Added

- Implement success count network statsbeat
    ([#25752](https://github.com/Azure/azure-sdk-for-python/pull/25752))
- Implement all network statsbeat
    ([#25845](https://github.com/Azure/azure-sdk-for-python/pull/25845))
- Implement attach statsbeat
    ([#25956](https://github.com/Azure/azure-sdk-for-python/pull/25956))
- Implement feature statsbeat
    ([#26009](https://github.com/Azure/azure-sdk-for-python/pull/26009))
- Implement instrumentation statsbeat
    ([#26023](https://github.com/Azure/azure-sdk-for-python/pull/26023))
- Implement statsbeat shutdown
    ([#26077](https://github.com/Azure/azure-sdk-for-python/pull/26077))
- Add ApplicationInsightsSampler
    ([#26224](https://github.com/Azure/azure-sdk-for-python/pull/26224))
- Implement truncation logic for telemetry payload
    ([#26257](https://github.com/Azure/azure-sdk-for-python/pull/26257))
- Populate metric namespace with meter instrumentation scope name
    ([#26257](https://github.com/Azure/azure-sdk-for-python/pull/26257))

## 1.0.0b7 (2022-08-12)

### Features Added

- Moved OpenTelemetry `entry_points` to setup.py
    ([#25674](https://github.com/Azure/azure-sdk-for-python/pull/25674))
- Added storage configuration options
    ([#25633](https://github.com/Azure/azure-sdk-for-python/pull/25633))

### Breaking Changes

- Update to OpenTelemetry api/sdk v1.12.0
    ([#25659](https://github.com/Azure/azure-sdk-for-python/pull/25659))

### Bugs Fixed

- Opentelemetry span events have wrong ParentId in Azure Monitor logs
    ([#25369](https://github.com/Azure/azure-sdk-for-python/pull/25369))

## 1.0.0b6 (2022-06-10)

### Features Added

- Added OpenTelemetry entry points for auto-instrumentation of Azure Monitor exporters
    ([#25368](https://github.com/Azure/azure-sdk-for-python/pull/25368))
- Implement log exporter using experimental OT logging sdk
    ([#23486](https://github.com/Azure/azure-sdk-for-python/pull/23486))
- Implement sending of exception telemetry via log exporter
    ([#23633](https://github.com/Azure/azure-sdk-for-python/pull/23633))
- Implement exporting span events as message/exception telemetry
    ([#23708](https://github.com/Azure/azure-sdk-for-python/pull/23708))
- Implement metrics exporter using experimental OT metrics sdk
    ([#23960](https://github.com/Azure/azure-sdk-for-python/pull/23960))

### Breaking Changes

- Update to OpenTelemetry api/sdk 1.12.0rc1
    ([#24619](https://github.com/Azure/azure-sdk-for-python/pull/24619))

## 1.0.0b5 (2021-10-05)

### Features Added

- Support stamp specific redirect in exporters
    ([#20489](https://github.com/Azure/azure-sdk-for-python/pull/20489))

### Breaking Changes

- Change exporter OT to AI mapping fields following common schema
    ([#20445](https://github.com/Azure/azure-sdk-for-python/pull/20445))

## 1.0.0b4 (2021-04-06)

### Features Added

- Add `from_connection_string` method to instantiate exporters
    ([#16818](https://github.com/Azure/azure-sdk-for-python/pull/16818))

- Remove support for Python 3.5
    ([#17747](https://github.com/Azure/azure-sdk-for-python/pull/17747))

## 1.0.0b3 (2021-02-11)

### Breaking Changes

- The package has been renamed to `azure-monitor-opentelemetry-exporter`
    ([#16621](https://github.com/Azure/azure-sdk-for-python/pull/16621))
- Remove `ExporterOptions`
    ([#16669](https://github.com/Azure/azure-sdk-for-python/pull/16669))

### Features Added

- Add azure servicebus samples and docstrings to samples
    ([#16580](https://github.com/Azure/azure-sdk-for-python/pull/16580))
- Support configuration of `api_version` in exporter
    ([#16669](https://github.com/Azure/azure-sdk-for-python/pull/16669))

## 1.0.0b2 (2021-01-13)

### Breaking Changes

- Rename Azure Trace exporter class, only allow connection string configuration
  ([#15349](https://github.com/Azure/azure-sdk-for-python/pull/15349))

- OpenTelemetry Exporter use Resources API to retrieve cloud role props
  ([#15816](https://github.com/Azure/azure-sdk-for-python/pull/15816))

- Change span to envelope conversion to adhere to common schema and other languages
  ([#15344](https://github.com/Azure/azure-sdk-for-python/pull/15344))

- This library is renamed to `azure-opentelemetry-exporter-azuremonitor`.
  ([#16030](https://github.com/Azure/azure-sdk-for-python/pull/16030))

- Fix to only retry upon request error
  ([#16087](https://github.com/Azure/azure-sdk-for-python/pull/16087))

## 1.0.0b1 (2020-11-13)

### Breaking Changes

- This library is renamed to `microsoft-opentelemetry-exporter-azuremonitor`.

## 0.5b.0 (2020-09-24)

- Change epoch for live metrics
  ([#115](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/115))
- Dropping support for Python 3.4
  ([#117](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/117))

## 0.4b.0 (2020-06-29)

- Added live metrics
  ([#96](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/96))
- Remove dependency metrics from auto-collection
  ([#92](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/92))
- Change default local storage directory
  ([#100](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/100))
- Implement proxies in exporter configuration
  ([#101](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/101))
- Remove request failed per second metrics from auto-collection
  ([#102](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/102))

## 0.3b.1 (2020-05-21)

- Fix metrics exporter serialization bug
  ([#92](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/92))

## 0.3b.0 (2020-05-19)

- Implement max size logic for local storage
  ([#74](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/74))
- Remove label sets + add is_remote to spancontext
  ([#75](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/75))
- Adding live metrics manager
  ([#78](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/78))
- Handle status 439 - Too Many Requests over extended time
  ([#80](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/80))
- Fix breaking changes from OT release 0.7b.0
  ([#86](https://github.com/microsoft/opentelemetry-azure-monitor-python/pull/86))

## 0.2b.0 (2020-03-31)

- Initial beta release

## 0.1a.0 (2019-11-06)

- Initial alpha release

# cSpell:enable
