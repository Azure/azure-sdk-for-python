# Azure Video Analyzer Edge client library for Python

Deprecated. We’re retiring the Azure Video Analyzer preview service, you're advised to transition your applications off of Video Analyzer by 01 December 2022. This SDK is not longer maintained.

Azure Video Analyzer is an [Azure Applied AI Service][applied-ai-service] that provides a platform for you to build intelligent video applications that can span both edge and cloud infrastructures. The platform offers the capability to capture, record, and analyze live video along with publishing the results, video and video analytics, to Azure services at the edge or in the cloud. It is designed to be an extensible platform, enabling you to connect different video inferencing edge modules such as Cognitive services modules, or custom inferencing modules that have been trained with your own data using either open-source machine learning or [Azure Machine Learning][machine-learning].

Use the client library for Video Analyzer Edge to:

- Simplify interactions with the [Microsoft Azure IoT SDKs](https://github.com/azure/azure-iot-sdks)
- Programmatically construct pipeline topologies and live pipelines

[Package (PyPI)][package] | [Product documentation][doc_product] | [Direct methods][doc_direct_methods] | [Pipelines][doc_pipelines] | [Source code][source] | [Samples][samples]

## Getting started

### Install the package

Install the Video Analyzer Edge client library for Python with pip:

```bash
pip install azure-media-videoanalyzer-edge
```

### Prerequisites

- 3.6 or later is required to use this package.
- You need an active [Azure subscription][azure_sub], and a IoT device connection string to use this package.
- To interact with Azure IoT Hub you will need to run `pip install azure-iot-hub`
- You will need to use the version of the SDK that corresponds to the version of the Video Analyzer Edge module you are using.

    | SDK  | Video Analyzer edge module  |
    |---|---|
    | 1.0.0b3  | 1.1  |
    | 1.0.0b2  | 1.0  |
    | 1.0.0b1  | 1.0  |

### Creating a pipeline topology and making requests

Please visit the [Examples](#examples) for starter code.

## Key concepts

### Pipeline topology vs live pipeline

A _pipeline topology_ is a blueprint or template for creating live pipelines. It defines the parameters of the pipeline using placeholders as values for them. A _live pipeline_ references a pipeline topology and specifies the parameters. This way you are able to have multiple live pipelines referencing the same topology but with different values for parameters. For more information please visit [pipeline topologies and live pipelines][doc_pipelines].

### CloudToDeviceMethod

The `CloudToDeviceMethod` is part of the [azure-iot-hub SDk][iot-hub-sdk]. This method allows you to communicate one way notifications to a device in your IoT hub. In our case, we want to communicate various direct methods such as `PipelineTopologySetRequest` and `PipelineTopologyGetRequest`. To use `CloudToDeviceMethod` you need to pass in two parameters: `method_name` and `payload`.

The first parameter, `method_name`, is the name of the direct method request you are sending. Make sure to use each method's predefined `method_name` property. For example, `PipelineTopologySetRequest.method_name`.

The second parameter, `payload`, sends the entire serialization of the pipeline topology request. For example, `PipelineTopologySetRequest.serialize()`

## Examples

### Creating a pipeline topology

To create a pipeline topology you need to define sources and sinks.

```python
#Parameters
user_name_param = ParameterDeclaration(name="rtspUserName",type="String",default="testusername")
password_param = ParameterDeclaration(name="rtspPassword",type="SecretString",default="testpassword")
url_param = ParameterDeclaration(name="rtspUrl",type="String",default="rtsp://www.sample.com")

#Source and Sink
source = RtspSource(name="rtspSource", endpoint=UnsecuredEndpoint(url="${rtspUrl}",credentials=UsernamePasswordCredentials(username="${rtspUserName}",password="${rtspPassword}")))
node = NodeInput(node_name="rtspSource")
sink = VideoSink(name="videoSink", inputs=[node], video_name="video", local_media_cache_path="/var/lib/videoanalyzer/tmp/", local_media_cache_maximum_size_mi_b="1024");
    
pipeline_topology_properties = PipelineTopologyProperties()
pipeline_topology_properties.parameters = [user_name_param, password_param, url_param]
pipeline_topology_properties.sources = [source]
pipeline_topology_properties.sinks = [sink]
pipeline_topology = PipelineTopology(name=pipeline_topology_name,properties=pipeline_topology_properties)

```

### Creating a live pipeline

To create a live pipeline, you need to have an existing pipeline topology.

```python
url_param = ParameterDefinition(name="rtspUrl", value=pipeline_url)
pass_param = ParameterDefinition(name="rtspPassword", value="secret_password")
live_pipeline_properties = LivePipelineProperties(description="Sample pipeline description", topology_name=pipeline_topology_name, parameters=[url_param])

live_pipeline = LivePipeline(name=live_pipeline_name, properties=live_pipeline_properties)

```

### Invoking a direct method

To invoke a direct method on your device you need to first define the request using the Video Analyzer Edge SDK, then send that method request using the IoT SDK's `CloudToDeviceMethod`.

```python
set_method_request = PipelineTopologySetRequest(pipeline_topology=pipeline_topology)
direct_method = CloudToDeviceMethod(method_name=set_method_request.method_name, payload=set_method_request.serialize())
registry_manager = IoTHubRegistryManager(connection_string)

registry_manager.invoke_device_module_method(device_id, module_d, direct_method)
```

To try different pipeline topologies with the SDK, please see the official [Samples][samples].

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
[doc_pipelines]: https://go.microsoft.com/fwlink/?linkid=2162396
[package]: https://aka.ms/ava/sdk/client/python
[source]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/videoanalyzer
[samples]: https://go.microsoft.com/fwlink/?linkid=2162278
[doc_product]: https://go.microsoft.com/fwlink/?linkid=2162396
[doc_direct_methods]: https://go.microsoft.com/fwlink/?linkid=2162396
[iot-device-sdk]: https://pypi.org/project/azure-iot-device/
[iot-hub-sdk]: https://pypi.org/project/azure-iot-hub/
[github-page-issues]: https://github.com/Azure/azure-sdk-for-python/issues
[applied-ai-service]: https://azure.microsoft.com/product-categories/applied-ai-services/#services
[machine-learning]: https://azure.microsoft.com/services/machine-learning
