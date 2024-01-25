---
page_type: sample
languages:
  - python
products:
  - azure-monitor
---

# Microsoft Azure Monitor Opentelemetry Exporter Log Python Samples

These code samples show common champion scenario operations with the AzureMonitorLogExporter.

* Logs: [sample_log.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/logs/sample_log.py)
* Trace correlation: [sample_log.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/logs/sample_correlate.py)
* Custom properties: [sample_properties.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/logs/sample_properties.py)


## Installation

```sh
$ pip install azure-monitor-opentelemetry-exporter --pre
```

## Run the Applications

### Logs

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_log.py
```

### Trace correlation

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_correlate.py
```

### Custom properties

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_properties.py
```

## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)
