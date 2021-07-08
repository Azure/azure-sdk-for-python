# Azure IoT Models Repository Library Samples

This directory contains samples showing how to use the features of the Azure IoT Models Repository Library.

The pre-configured endpoints and DTMIs within the samples refer to example models that can be found on [devicemodels.azure.com](https://devicemodels.azure.com/). These values can be replaced to reflect the locations of your own models, wherever they may be.

## ModelsRepositoryClient Samples
* [get_models_sample.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/modelsrepository/azure-iot-modelsrepository/samples/get_models_sample.py) - Retrieve a model/models (and possibly dependencies) from a Model Repository, given a DTMI or DTMIs

* [client_configuration_sample.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/modelsrepository/azure-iot-modelsrepository/samples/client_configuration_sample.py)- Configure the client to work with local or remote repositories, as well as custom policies and transports

* [dtmi_conventions_sample.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/modelsrepository/azure-iot-modelsrepository/samples/dtmi_conventions_sample.py) - Use the `dtmi_conventions` module to manipulate and check DTMIs
