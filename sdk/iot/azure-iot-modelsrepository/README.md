# Azure IoT Models Repository client library for Python

The Azure IoT Models Repository Library for Python provides functionality for working with the Azure IoT Models Repository

## Getting started

### Install package

Install the Azure IoT Models Repository library for Python with [pip][pip]:

```Shell
pip install azure-iot-modelsrepository
```

### Prerequisites
* A models repository following [repo_conventions][Azure IoT conventions]
    * The models repository can be hosted on the local filesystem or hosted on a webserver
    * Azure IoT hosts the global [global_azure_repo][Azure IoT Models Repository] which the client will use if no custom location is provided

### Authentication
Currently, no authentication mechanisms are supported. The global endpoint is not tied to an Azure subscription and does not support authentication. All models published are meant for anonymous public consumption.

## Key concepts

The Azure IoT Models Repository enables builders to manage and share digital twin models. The models are [json_ld][JSON-LD] documents defined using the Digital Twins Definition Language ([dtdl_spec][DTDL]).

The repository defines a pattern to store DTDL interfaces in a directory structure based on the Digital Twin Model Identifier (DTMI). You can locate an interface in the repository by converting the DTMI to a relative path. For example, the DTMI `dtmi:com:example:Thermostat;1` translates to `/dtmi/com/example/thermostat-1.json`.

## Examples

## Troubleshooting

### General
Models Repository clients raise exceptions defined in [azure_core_exceptions][azure-core].

### Logging
This library uses the standard [logging_doc][logging] library for logging. Information about HTTP sessions (URLs, headers, etc.) is logged at `DEBUG` level.

## Next steps

Several samples are available in the Azure SDK for Python GitHub repository. These provide example code for Models Repository Client scenarios:

* [client_configuration_sample][client_configuration_sample] - Configure a ModelsRepositoryClient for a local or remote repository
* [get_models_sample][get_models_sample] - Retrieve models from a repository
* [dtmi_conventions_sample][dtmi_conventions_sample] - Use utility functions to generate and validate DTMIs

<!-- LINKS -->
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core#azure-core-library-exceptions
[client_configuration_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/iot/azure-iot-modelsrepository/samples/client_configuration_sample.py
[dtdl_spec]: https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md
[dtmi_conventions_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/iot/azure-iot-modelsrepository/samples/dtmi_conventions_sample.py
[get_models_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/iot/azure-iot-modelsrepository/samples/get_models_sample.py
[global_azure_repo]: https://devicemodels.azure.com/
[json_ld]: https://json-ld.org/
[logging_doc]: https://docs.python.org/3.5/library/logging.html
[pip]: https://pypi.org/project/pip/
[repo_conventions]: https://github.com/Azure/iot-plugandplay-models-tools/wiki

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
