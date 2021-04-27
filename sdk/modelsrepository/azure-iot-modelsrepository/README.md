# Azure IoT Models Repository client library for Python

The Azure IoT Models Repository Library for Python provides functionality for working with the Azure IoT Models Repository

## Getting started

### Install package

Install the Azure IoT Models Repository library for Python with [pip][pip]:

```Shell
pip install azure-iot-modelsrepository
```

### Prerequisites
* A models repository following [Azure IoT conventions][repo_conventions]
    * The models repository can be hosted on the local filesystem or hosted on a webserver
    * Azure IoT hosts the global [Azure IoT Models Repository][global_azure_repo] which the client will use if no custom location is provided

### Publishing Models
Follow the [guide](https://docs.microsoft.com/azure/iot-pnp/concepts-model-repository#publish-a-model) to publish models to the global Azure IoT Models Repository.

If using a custom local or remote repository, you can simply add your model files to a directory structure in the repository location, e.g. `dtmi/com/example/thermostat-1.json`

### Authentication
Currently, no authentication mechanisms are supported. The global endpoint is not tied to an Azure subscription and does not support authentication. All models published are meant for anonymous public consumption.

## Key concepts

The Azure IoT Models Repository enables builders to manage and share digital twin models. The models are [JSON-LD][json_ld] documents defined using the Digital Twins Definition Language ([DTDL][dtdl_spec]).

The repository defines a pattern to store DTDL interfaces in a directory structure based on the Digital Twin Model Identifier (DTMI). You can locate an interface in the repository by converting the DTMI to a relative path. For example, the DTMI `dtmi:com:example:Thermostat;1` translates to `/dtmi/com/example/thermostat-1.json`.

## Examples
The following sections provide several snippets covering common Models Repository tasks:
* [Initializing the ModelsRepositoryClient](#initializing-the-modelsrepositoryclient, "Initializing the ModelsRepositoryClient")
* [Get Models](#get-models, "Get models")
* [DTMI Conventions](#dtmi-conventions, "DTMI Conventions")

### Initializing the ModelsRepositoryClient
When no repsository location is provided during instantiation, the Azure IoT Models Repository global endpoint (https://devicemodels.azure.com/) is used

```python
client = ModelsRepositoryClient()
```

Alternatively, you can provide a custom URL where your repository is located

```python
client = ModelsRepositoryClient(repository_location="https://fake.myrepository.com/")
```

The client will also work with a local filesystem path if your repository is set up locally

```python
client = ModelsRepositoryClient(repository_location="file:///home/fake/myrepository")
```

#### Additional options
The client can be configured with an optional `dependency_resolution` mode at instantiation, using one of the following values:
* `'disabled'` - The client will not resolve model dependencies
* `'enabled'` - The client will resolve any model dependencies
* `'tryFromExpanded'` - The client will attempt to resolve models using an expanded model definition (falling back on `'enabled'` mode if not possible)

```python
client = ModelsRepositoryClient(dependency_resolution="enabled")
```

If the `dependency_resolution` mode is not specified:
* Clients configured for the Azure IoT Models Repository global endpoint will default to using `'tryFromExpanded'`
* Clients configured for a custom location (remote or local) will default to using `'enabled'`

If you need to override default pipeline behavior from the [azure-core library][azure_core_docs], you can provide various [keyword arguments][azure_core_kwargs] during instantiation.

#### Client cleanup
When you are finished with your client, make sure to call `.close()` in order to free up resources

```python
client = ModelsRepositoryClient()
# Do things
client.close()
```

In order to avoid having to do this, it is recommended that you use your client from within a context manager whenever possible, which will automatically close for you
```python
with ModelsRepositoryClient() as client:
    # Do things
```

### ModelsRepositoryClient - Get Models
Note that you must first [publish models to your repository](#publishing-models, "Publishing models") before you can fetch them. The following examples assume you are using the global Azure IoT Models Repository.

Calling `.get_models()` will fetch the model at the provided DTMI and potentially its dependencies (depending on the dependency resolution mode). It will return a `dict` that maps DTMIs to model definitions.

```python
dtmi = "dtmi:com:example:TemperatureController;1"
with ModelsRepositoryClient() as client:
    models = get_models(dtmi)
print("{} resolved in {} interfaces".format(dtmi, len(models)))
```

If you provide multiple DTMIs to the method, you can retrieve multiple models (and potentially their dependencies) at once
```python
dtmis = ["dtmi:com:example:TemperatureController;1", "dtmi:com:example:azuresphere:sampledevice;1"]
with ModelsRepositoryClient() as client:
    models = get_models(dtmis)
print("{} resolved in {} interfaces".format(dtmi, len(models)))
```

By default the client will use whichever [dependency resolution mode](#additional-options, "Dependency resolution mode") it was configured with at instantiation when retreiving models. However, this behaviour can be overridden by passing any of the valid options in as an optional keyword argument to `.get_models()`

```python
dtmi = "dtmi:com:example:TemperatureController;1"
with ModelsRepositoryClient(dependency_resolution="disabled") as client:
    models = get_models(dtmi, dependency_resolution="enabled")
```

### DTMI Conventions
The package contains a module called `dtmi_conventions`, which, when imported provides a series of utility operations for working with DTMIs

```python
# Returns True - this is a valid DTMI
dtmi_conventions.is_valid_dtmi("dtmi:com:example:Thermostat;1")

# Returns False - this is NOT a valid DTMI
dtmi_conventions.is_valid_dtmi("dtmi:com:example:Thermostat")
```

```python
dtmi = "dtmi:com:example:Thermostat;1"

# Local repository example
repo_uri = "file:///path/to/repository"
print(dtmi_conventions.get_model_uri(dtmi, repo_uri))
# Prints: "file:///path/to/repository/dtmi/com/example/thermostat-1.json"
print(dtmi_conventions.get_model_uri(dtmi, repo_uri, expanded=True))
# Prints: "file:///path/to/repository/dtmi/com/example/thermostat-1.expanded.json"

# Remote repository example
repo_uri = "https://contoso.com/models/"
print(dtmi_conventions.get_model_uri(dtmi, repo_uri))
# Prints: "https://contoso/com/models/dtmi/com/example/thermostat-1.json"
print(dtmi_conventions.get_model_uri(dtmi, repo_uri, expanded=True))
# Prints: "https://contoso/com/models/dtmi/com/example/thermostat-1.expanded.json"
```


## Troubleshooting

### General
Models Repository clients raise exceptions defined in [azure-core][azure_core_exceptions].

### Logging
This library uses the standard [logging][logging_doc] library for logging. Information about HTTP sessions (URLs, headers, etc.) is logged at `DEBUG` level.

### Exceptions
Models Repository APIs may generate the following exceptions from the following packages:

#### azure.iot.modelsrepository
* `ModelError` - Indicates an error occured while trying to parse/resolve a model definition. This generally means that there is a malformed model that does not comply with the [model DTDL specification][dtdl_spec]

#### azure.core.exceptions
* `ResourceNotFoundError` - Indicates a model could not be found in the repository
* `ServiceRequestError` - Indicates there was an error in making a request to the repository for a model
* `ServiceResponseError` - Indicates that a request to the repository could not be completed
* `HttpResponseError` - Indicates that an unexpected failure response was received from the service 

### Provide Feedback
If you encounter bugs or have suggestions, please
[open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

### Samples
Additional samples are available in the [samples repository][samples_repo].

### Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.


<!-- LINKS -->
[azure_core_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core#azure-core-library-exceptions
[azure_core_kwargs]: https://aka.ms/azsdk/python/options
[dtdl_spec]: https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md
[global_azure_repo]: https://devicemodels.azure.com/
[json_ld]: https://json-ld.org/
[logging_doc]: https://docs.python.org/3.5/library/logging.html
[pip]: https://pypi.org/project/pip/
[repo_conventions]: https://github.com/Azure/iot-plugandplay-models-tools/wiki
[samples_repo]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/modelsrepository/azure-iot-modelsrepository/samples/