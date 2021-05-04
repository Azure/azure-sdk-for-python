# Azure Live Video Analytics for IoT Edge client library for Python

Live Video Analytics on IoT Edge provides a platform to build intelligent video applications that span the edge and the cloud. The platform offers the capability to capture, record, and analyze live video along with publishing the results, video and video analytics, to Azure services in the cloud or the edge. It is designed to be an extensible platform, enabling you to connect different video analysis edge modules (such as Cognitive services containers, custom edge modules built by you with open-source machine learning models or custom models trained with your own data) to it and use them to analyze live video without worrying about the complexity of building and running a live video pipeline.

Use the client library for Live Video Analytics on IoT Edge to:

- Simplify interactions with the [Microsoft Azure IoT SDKs](https://github.com/azure/azure-iot-sdks) 
- Programatically construct media graph topologies and instances

[Package (PyPI)][package] | [Product documentation][doc_product] | [Direct methods][doc_direct_methods] | [Media graphs][doc_media_graph] | [Source code][source] | [Samples][samples]

## Getting started

### Install the package

Install the Live Video Analytics client library for Python with pip:

```bash
pip install azure-media-analytics-edge
```
### Prerequisites

* Python 2.7, or 3.5 or later is required to use this package.
* You need an active [Azure subscription][azure_sub], and a [IoT device connection string][iot_device_connection_string] to use this package.
* To interact with Azure IoT Hub you will need to run `pip install azure-iot-hub`
* You will need to use the version of the SDK that corresponds to the version of the LVA Edge module you are using.

    | SDK  | LVA Edge Module  |
    |---|---|
    | 1.0.0b1  | 2.0  |
### Creating a graph topology and making requests
Please visit the [Examples](#examples) for starter code
## Key concepts

### MediaGraph Topology vs MediaGraph Instance
A _graph topology_ is a blueprint or template of a graph. It defines the parameters of the graph using placeholders as values for them. A _graph instance_ references a graph topology and specifies the parameters. This way you are able to have multiple graph instances referencing the same topology but with different values for parameters. For more information please visit [Media graph topologies and instances][doc_media_graph] 

### CloudToDeviceMethod

The `CloudToDeviceMethod` is part of the [azure-iot-hub SDk][iot-hub-sdk]. This method allows you to communicate one way notifications to a device in your IoT hub. In our case, we want to communicate various graph methods such as `MediaGraphTopologySetRequest` and `MediaGraphTopologyGetRequest`. To use `CloudToDeviceMethod` you need to pass in two parameters: `method_name` and `payload`. 

The first parameter, `method_name`, is the name of the media graph request you are sending. Make sure to use each method's predefined `method_name` property. For example, `MediaGraphTopologySetRequest.method_name`. 

The second parameter, `payload`, sends the entire serialization of the media graph request. For example, `MediaGraphTopologySetRequest.serialize()`

## Examples

### Creating a graph topology
To create a graph topology you need to define parameters, sources, and sinks.
```
#Parameters
user_name_param = MediaGraphParameterDeclaration(name="rtspUserName",type="String",default="dummyusername")
password_param = MediaGraphParameterDeclaration(name="rtspPassword",type="String",default="dummypassword")
url_param = MediaGraphParameterDeclaration(name="rtspUrl",type="String",default="rtsp://rtspsim:554/media/camera-300s.mkv")

#Source and Sink
source = MediaGraphRtspSource(name="rtspSource", endpoint=MediaGraphUnsecuredEndpoint(url="${rtspUrl}",credentials=MediaGraphUsernamePasswordCredentials(username="${rtspUserName}",password="${rtspPassword}")))
node = MediaGraphNodeInput(node_name="rtspSource")
sink = MediaGraphAssetSink(name="assetsink", inputs=[node],asset_name_pattern='sampleAsset-${System.GraphTopologyName}-${System.GraphInstanceName}', segment_length="PT0H0M30S",local_media_cache_maximum_size_mi_b=2048,local_media_cache_path="/var/lib/azuremediaservices/tmp/")

graph_properties = MediaGraphTopologyProperties(parameters=[user_name_param, password_param, url_param], sources=[source], sinks=[sink], description="Continuous video recording to an Azure Media Services Asset")

graph_topology = MediaGraphTopology(name=graph_topology_name,properties=graph_properties)

```

### Creating a graph instance 
To create a graph instance, you need to have an existing graph topology.
```
url_param = MediaGraphParameterDefinition(name="rtspUrl", value=graph_url)
graph_instance_properties = MediaGraphInstanceProperties(description="Sample graph description", topology_name=graph_topology_name, parameters=[url_param])

graph_instance = MediaGraphInstance(name=graph_instance_name, properties=graph_instance_properties)

```

### Invoking a graph method request
To invoke a graph method on your device you need to first define the request using the lva sdk. Then send that method request using the iot sdk's `CloudToDeviceMethod`
```
set_method_request = MediaGraphTopologySetRequest(graph=graph_topology)
direct_method = CloudToDeviceMethod(method_name=set_method_request.method_name, payload=set_method_request.serialize())
registry_manager = IoTHubRegistryManager(connection_string)

registry_manager.invoke_device_module_method(device_id, module_d, direct_method)
```

To try different media graph topologies with the SDK, please see the official [Samples][samples].

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

If you encounter any issues, please open an issue on our [Github][github-page-issues].

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

[package]: TODO://link-to-published-package
[source]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/media
[samples]: https://github.com/Azure-Samples/live-video-analytics-iot-edge-python

[doc_direct_methods]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/direct-methods
[doc_media_graph]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/media-graph-concept#media-graph-topologies-and-instances
[doc_product]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/

[iot-device-sdk]: https://pypi.org/project/azure-iot-device/
[iot-hub-sdk]: https://pypi.org/project/azure-iot-hub/
[iot_device_connection_string]: https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/get-started-detect-motion-emit-events-quickstart

[github-page-issues]: https://github.com/Azure/azure-sdk-for-python/issues 