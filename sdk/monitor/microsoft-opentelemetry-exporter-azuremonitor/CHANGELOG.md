# Release History

## 1.0.0b1 (Unreleased)

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