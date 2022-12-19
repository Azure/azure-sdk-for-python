---
page_type: sample
languages:
  - python
products:
  - azure-monitor
---

# Microsoft Azure Monitor Opentelemetry Exporter Metric Python Samples

These code samples show common champion scenario operations with the AzureMonitorMetricExporter.

* Attributes: [sample_attributes.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/metrics/sample_attributes.py)
* Instruments: [sample_instruments.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/metrics/sample_instruments.py)
* Views: [sample_views.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/metrics/sample_views.py)

## Installation

```sh
$ pip install azure-monitor-opentelemetry-exporter --pre
```

## Run the Applications

### Metrics with attributes

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_attributes.py
```

### Instrument usage

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_instruments.py
```

### Configuring metrics with views

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_views.py
```

## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)
