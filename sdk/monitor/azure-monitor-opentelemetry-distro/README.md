# Azure Monitor Opentelemetry Distro

[![Gitter chat](https://img.shields.io/gitter/room/Microsoft/azure-monitor-python)](https://gitter.im/Azure/azure-sdk-for-python)

Azure Monitor Distro of [Opentelemetry Python][opentelemetry-python] provides multiple installable components available for an Opentelemetry Azure Monitor monitoring solution. It allows you to instrument your Python applications to capture and report telemetry to Azure Monitor via the Azure monitor exporters.

This distro automatically installs the following libraries:

* [Azure Monitor OpenTelemetry exporters][azure_monitor_opentelemetry_exporters]

## Install the package

Install the Azure Monitor Opentelemetry Distro with [pip][pip]:

```Bash
pip install azure-monitor-opentelemetry-distro --pre
```

### Additional documentation

[Azure Portal][azure_portal]

<!-- LINKS -->
[azure_monitor_opentelemetry_exporters]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter#microsoft-opentelemetry-exporter-for-azure-monitor
[azure_portal]: https://portal.azure.com
[pip]: https://pypi.org/project/pip/
[opentelemetry-python]: https://github.com/open-telemetry/opentelemetry-python
