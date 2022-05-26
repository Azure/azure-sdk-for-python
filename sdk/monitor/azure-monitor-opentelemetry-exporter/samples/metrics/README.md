---
page_type: sample
languages:
  - python
products:
  - azure-monitor
---

# Microsoft Azure Monitor Opentelemetry Exporter Metric Python Samples

These code samples show common champion scenario operations with the AzureMonitorMetricExporter.

* Metrics: [sample_metrics.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/metrics/sample_metrics.py)
* Instruments: [sample_instruments.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/metrics/sample_instruments.py)


## Installation

```sh
$ pip install azure-monitor-opentelemetry-exporter --pre
```

## Run the Applications

### Metrics

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_metrics.py
```

### Instrument usage

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_instruments.py
```

## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)
