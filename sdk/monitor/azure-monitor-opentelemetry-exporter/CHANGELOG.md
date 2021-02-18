# Release History

## 1.0.0b4 (Unreleased)

  **Features**
  - Add `from_connection_string` method to instantiate exporters
      ([#16818](https://github.com/Azure/azure-sdk-for-python/pull/16818))

## 1.0.0b3 (2021-02-11)

  **Breaking Changes**
  - The package has been renamed to `azure-monitor-opentelemetry-exporter`
      ([#16621](https://github.com/Azure/azure-sdk-for-python/pull/16621))
  - Remove `ExporterOptions`
      ([#16669](https://github.com/Azure/azure-sdk-for-python/pull/16669))

  **Features**
  - Add azure servicebus samples and docstrings to samples
      ([#16580](https://github.com/Azure/azure-sdk-for-python/pull/16580))
  - Support configuration of `api_version` in exporter
      ([#16669](https://github.com/Azure/azure-sdk-for-python/pull/16669))

## 1.0.0b2 (2021-01-13)

  **Breaking Changes**
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

  **Breaking Changes**
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
