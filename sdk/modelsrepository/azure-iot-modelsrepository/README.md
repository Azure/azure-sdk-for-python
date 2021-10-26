# Azure IoT Models Repository client library for Python

The Azure IoT Models Repository enables builders to manage and share digital twin models for global consumption. The models are [JSON-LD][json_ld_reference] documents defined using the Digital Twins Definition Language ([DTDL][dtdlv2_reference]).

For more info about the Azure IoT Models Repository checkout the [docs][modelsrepository_msdocs].

## Introduction

You can explore the models repository APIs with the client library using the samples project.

The samples project demonstrates the following:

- Instantiate the client
- Get models and their dependencies from either a remote endpoint or local repository.

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
* [Initializing the ModelsRepositoryClient](#initializing-the-modelsrepositoryclient "Initializing the ModelsRepositoryClient")
* [Get Models](#modelsrepositoryclient---get-models "Get models")
* [DTMI Conventions](#dtmi-conventions "DTMI Conventions")

### Initializing the ModelsRepositoryClient

#### Repository Location
When no repository location is provided during instantiation, the Azure IoT Models Repository global endpoint (https://devicemodels.azure.com/) is used

```python
client = ModelsRepositoryClient()
```

Alternatively, you can provide a custom location for where your repository is located via the optional `repository_location` keyword. The client accepts the following location formats:
* Web URL - e.g. `"https://contoso.com/models/"`
* Local Filesystem URI - e.g. `"file:///path/to/repository/"`
* POSIX filepath - e.g. `"/path/to/repository/"`
* Drive letter filepath - e.g. `"C:/path/to/repository/"`

This form shows specifing a custom URI for the models repository client.
```python
client = ModelsRepositoryClient(repository_location="https://contoso.com/models/")
```

This form shows specifing a local filesystem URI for the models repository client.
```python
client = ModelsRepositoryClient(repository_location="c:/path/to/SampleModelsRepo/")
```

#### Repository metadata

Models repositories that implement Azure IoT conventions can **optionally** include a `metadata.json` file at the root of the repository. The `metadata.json` file provides key attributes of a repository including the features that it provides. A client can use the repository metadata to make decisions around how to optimally handle an operation.

The following snippet shows how to configure the time span in seconds in which the `ModelsRepositoryClient` considers metadata stale.  When the client metadata state is stale, the next service operation that can make use of metadata will first fetch and refresh the client metadata state. The operation will then continue as normal.
```python
client = ModelsRepositoryClient(metadata_expiration=1800)
```

#### Override options

If you need to override pipeline behavior, such as provide your own Http Pipeline policies, you can do that by specifying the corresponding kwarg.
It provides an opportunity to override default behavior including:

- Overriding [transport][azure_core_transport]
- Enabling [diagnostics][azure_core_diagnostics]
- Controlling [retry strategy](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/samples/README.md)


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
Note that you must first [publish models to your repository](#publishing-models "Publishing models") before you can fetch them. The following examples assume you are using the global Azure IoT Models Repository.

Calling `.get_models()` will fetch the model at the provided DTMI and potentially its dependencies (depending on the dependency resolution mode). It will return a `dict` that maps DTMIs to model definitions.

```python
dtmi = "dtmi:com:example:TemperatureController;1"

# Global endpoint client
with ModelsRepositoryClient() as client:
    # The output of get_models() will include at least the definition for the target dtmi.
    # If the model dependency resolution configuration is not disabled, then models in which the
    # target dtmi depends on will also be included in the returned dictionary.
    models = get_models(dtmi)

# In this case the above dtmi has 2 model dependencies.
# dtmi:com:example:Thermostat;1 and dtmi:azure:DeviceManagement:DeviceInformation;1
print("{} resolved in {} interfaces".format(dtmi, len(models)))
```

GitHub pull-request workflows are a core aspect of the IoT Models Repository service. To submit models, the user is expected to fork and clone the global [models repository project][modelsrepository_github_repo] then iterate against the local copy. Changes would then be pushed to the fork (ideally in a new branch) and a PR created against the global repository.

To support this workflow and similar use cases, the client supports initialization with a local file-system URI. You can use this for example, to test and ensure newly added models to the locally cloned models repository are in their proper locations.

```python
dtmi = "dtmi:com:example:TemperatureController;1"

# Local endpoint client
with ModelsRepositoryClient(repository_location="/samples/SampleModelsRepo/") as client:
    # The output of get_models() will include at least the definition for the target dtmi.
    # If the model dependency resolution configuration is not disabled, then models in which the
    # target dtmi depends on will also be included in the returned dictionary.
    models = get_models(dtmi)

# In this case the above dtmi has 2 model dependencies.
# dtmi:com:example:Thermostat;1 and dtmi:azure:DeviceManagement:DeviceInformation;1
print("{} resolved in {} interfaces".format(dtmi, len(models)))
```

If you provide multiple DTMIs to the method, you can retrieve multiple models (and potentially their dependencies) at once
```python
dtmis = ["dtmi:com:example:TemperatureController;1", "dtmi:com:example:azuresphere:sampledevice;1"]

# Global endpoint client
with ModelsRepositoryClient() as client:
    # When given a list of dtmis, the output of get_models() will include at
    # least the definitions of each dtmi in the list passed in.
    # If the model dependency resolution configuration is not disabled, then models in
    # which each dtmi depends on will also be included in the returned dictionary.
    models = get_models(dtmis)

# In this case the dtmi "dtmi:com:example:TemperatureController;1" has 2 model dependencies
# and the dtmi "dtmi:com:example:azuresphere:sampledevice;1" has no additional dependencies.
# The returned dictionary will include 4 models.
print("{} resolved in {} interfaces".format(dtmi, len(models)))
```

By default model dependency resolution is enabled. This can be changed by overriding the default
value for the `dependency_resolution` parameter of the `get_models` operation.

```python
dtmi = "dtmi:com:example:TemperatureController;1"

# Global endpoint client
with ModelsRepositoryClient() as client:
    # In this example model dependency resolution is disabled by passing in
    # DependencyMode.disabled.value as the value for the dependency_resolution parameter
    # for get_models(). By default the parameter has a value of DependencyMode.enabled.value.
    # When model dependency resolution is disabled, only the input dtmi(s) will be processed
    # and model dependencies (if any) will be ignored.
    models = client.get_models(dtmi, dependency_resolution=DependencyMode.disabled.value)

# In this case the above dtmi has 2 model dependencies but are not returned
# due to disabling model dependency resolution.
print("{} resolved in {} interfaces".format(dtmi, len(models)))
```

### DTMI Conventions utility functions
The package contains a module called `dtmi_conventions`, which, when imported provides a series of utility operations for working with DTMIs. These same functions are used throughout the client.

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

### Logging
This library uses the standard [logging][logging_doc] library for logging. Information about HTTP sessions (URLs, headers, etc.) is logged at `DEBUG` level.

### Exceptions
Models Repository APIs may raise exceptions defined in [azure-core][azure_core_exceptions].

Additionally, they may raise exceptions defined in the `azure-iot-modelsrepository`:
* `ModelError` - Indicates an error occurred while trying to parse/resolve a model definition. This generally means that there is a malformed model that does not comply with the [model DTDL specification][dtdl_spec]

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
[modelsrepository_github_repo]: https://github.com/Azure/iot-plugandplay-models
[modelsrepository_sample_extension]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/modelsrepository/Azure.IoT.ModelsRepository/samples/ModelsRepositoryClientSamples/ModelsRepositoryClientExtensions.cs
[modelsrepository_clientoptions]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/modelsrepository/Azure.IoT.ModelsRepository/src/ModelsRepositoryClientOptions.cs
[modelsrepository_msdocs]: https://docs.microsoft.com/azure/iot-pnp/concepts-model-repository
[modelsrepository_publish_msdocs]: https://docs.microsoft.com/azure/iot-pnp/concepts-model-repository#publish-a-model
[modelsrepository_iot_endpoint]: https://devicemodels.azure.com/
[json_ld_reference]: https://json-ld.org
[dtdlv2_reference]: https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md
[azure_core_transport]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/core/Azure.Core/samples/Pipeline.md
[azure_core_diagnostics]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/core/Azure.Core/samples/Diagnostics.md
[azure_core_configuration]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/core/Azure.Core/samples/Configuration.md
