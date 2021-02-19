# Azure IoT Models Repository Library Samples

This directory contains samples showing how to use the features of the Azure IoT Models Repository Library.

The pre-configured endpoints and DTMIs within the sampmles refer to example DTDL documents that can be found on [devicemodels.azure.com](https://devicemodels.azure.com/). These values can be replaced to reflect the locations of your own DTDLs, wherever they may be.

## Resolver Samples
* [get_models_sample.py](get_models_sample.py) - Retrieve a model/models (and possibly dependencies) from a Model Repository, given a DTMI or DTMIs

* [client_configuration_sample.py](client_configuration_sample.py) - Configure the client to work with local or remote repositories, as well as custom policies and transports