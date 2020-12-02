# Azure Live Video Analytics for IoT Edge client library for Python

Live Video Analytics on IoT Edge provides a platform to build intelligent video applications that span the edge and the cloud. The platform offers the capability to capture, record, and analyze live video along with publishing the results, video and video analytics, to Azure services in the cloud or the edge. It is designed to be an extensible platform, enabling you to connect different video analysis edge modules (such as Cognitive services containers, custom edge modules built by you with open-source machine learning models or custom models trained with your own data) to it and use them to analyze live video without worrying about the complexity of building and running a live video pipeline.

Use the client library for Live Video Analytics on IoT Edge to:

- simplify interactions with the [Microsoft Azure IoT SDKs](https://github.com/azure/azure-iot-sdks) 
- programatically construct media graph topologies and instances

[Package (PyPi)][package] | [Product documentation][doc_product] | [Direct methods][doc_direct_methods] | [Media graphs][doc_media_graph] | [Source code][source] | [Samples][samples]

## Getting started

### Install the package

Install the Live Video Analytics client library for Python with pip:

```bash
pip install azure-lva-edge
```
### Prerequisites

* Python 2.7, or 3.5 or later is required to use this package.
* You need an [Azure subscription][azure_sub], and a [IOT device connection string][iot_device_connection_string] to use this package.


## Key concepts

### Graph Topology vs Graph Instance
A graph topology is essentially the blueprint or template of a graph. It defines the parameters of the graph using placeholders as values for them. A graph instance references a graph topology and specifies the parameters. This way you are able to have multiple graph instances referencing the same topology but with different values for parameters. For more information please visit [Media graph topologies and instances][doc_media_graph] 

### CloudToDeviceMethod

The `CloudToDeviceMethod` is part of the azure-iot-hub sdk. This method allows you to communicate one way notifications to a device in your iot hub. In our case we want to communicate various graph methods such as `MediaGraphTopologySetRequest` and `MediaGraphTopologyGetRequest`. To use `CloudToDeviceMethod` you need to pass in two parameters: `method_name` and `payload`. `method_name` should be the name of the media graph request you are sending. Each media graph request has a property called `method_name`. For example, `MediaGraphTopologySetRequest.method_name`. For the second parameter `payload` send the entire serialization of the media graph request. For example, `MediaGraphTopologySetRequest.serialize()`

## Examples

[Samples][samples]

## Troubleshooting

- When sending a method request using the IoT Hub's `CloudToDeviceMethod` remember to not type in the method request name directly. Instead use `[MethodRequestName.method_name]`
- Make sure to serialize the entire method request before passing it to `CloudToDeviceMethod`

## Next steps

- [Samples][samples]
- [Azure IoT Device SDK][iot-device-sdk]
- [Azure IoTHub Service SDK][iot-hub-sdk]

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com

[package]: placeholder
[source]: TODO://link-to-path-in-the-SDK-repo
[samples]: https://github.com/Azure-Samples/live-video-analytics-iot-edge-python

[doc_direct_methods]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/direct-methods
[doc_media_graph]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/media-graph-concept#media-graph-topologies-and-instances
[doc_product]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/

[iot-device-sdk]: https://pypi.org/project/azure-iot-device/
[iot-hub-sdk]: https://pypi.org/project/azure-iot-hub/
[iot_device_connection_string]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/get-started-detect-motion-emit-events-quickstart