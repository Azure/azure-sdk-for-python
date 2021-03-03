# Azure Device Update for IoT Hub client library for Python

The library provides access to the Device Update for IoT Hub service that enables customers to publish updates for their IoT devices to the cloud, and then deploy these updates to their devices (approve updates to groups of devices managed and provisioned in IoT Hub).

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/deviceupdate/azure-iot-deviceupdate) | [Package (PyPI)](https://aka.ms/azsdk/python/deviceupdate-pypi) | [Product documentation](https://docs.microsoft.com/azure/iot-hub-device-update/understand-device-update)

## Getting started

### Prerequisites

- Microsoft Azure Subscription: To call Microsoft Azure services, you need to create an [Azure subscription](https://azure.microsoft.com/free/)
- Device Update for IoT Hub instance
- Azure IoT Hub instance
- Python 2.7, or 3.6 or later is required to use this package.

### Install the package

Install the Device Update for IoT Hub client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-iot-deviceupdate --pre
```

## Key concepts

Device Update for IoT Hub is a managed service that enables you to deploy over-the-air updates for your IoT devices. The client library has one main component named **AzureDeviceUpdateServiceDataPlane**. The component allows you to access all three main client services:

- **UpdatesOperations**: update management (import, enumerate, delete, etc.)
- **DevicesOperations**: device management (enumerate devices and retrieve device properties)
- **DeploymentsOperations**: deployment management (start and monitor update deployments to a set of devices)

You can learn more about Device Update for IoT Hub by visiting [Device Update for IoT Hub](https://github.com/azure/iot-hub-device-update).

## Examples

You can familiarize yourself with different APIs using [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/deviceupdate/azure-iot-deviceupdate/samples).

## Troubleshooting

The Device Update for IoT Hub client will raise exceptions defined in [Azure Core][https://github.com/azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/readme.md].

## Next steps

Get started with our [Device Update for IoT Hub samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/deviceupdate/azure-iot-deviceupdate/samples)

## Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

<!-- LINKS -->
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
