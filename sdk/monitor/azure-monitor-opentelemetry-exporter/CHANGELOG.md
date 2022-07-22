# Release History

## 1.0.0b7 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed
- Opentelemetry span events have wrong ParentId in Azure Monitor logs
    ([#25369](https://github.com/Azure/azure-sdk-for-python/pull/25369))

### Other Changes

## 1.0.0b6 (2022-06-10)

### Features Added
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

  **Features**
  - Add `from_connection_string` method to instantiate exporters
      ([#16818](https://github.com/Azure/azure-sdk-for-python/pull/16818))

  - Remove support for Python 3.5
      ([#17747](https://github.com/Azure/azure-sdk-for-python/pull/17747))

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
