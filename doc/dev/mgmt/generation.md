# Generation of SDK

Assuming your Swagger are associated with correct Readmes (otherwise see previous chapter [Swagger conf](./swagger_conf.md)), this page explains how to generate your packages.

IMPORTANT NOTE: All the commands in this page assumes you have loaded the [dev_setup](../dev_setup.md) in your currently loaded virtual environment.

## Building the code

### Autorest versioning

A few notes on [Autorest for Python versionning](https://github.com/Azure/autorest.python/blob/master/ChangeLog.md):
- Autorest for Python v2.x is deprecated, and should not be used anymore for any generation under any circumstances.
- Autorest for Python v3.x is the most currently used one. Should not be used, but still ok if service team are still in v3.x and they want to avoid breaking changes for a given version (rare).
- Autorest for Python v4.x is the current recommendation. This generator can generates async code, but this should be disabled with --no-async. No package should be shipped with async based on v4
- Autorest for Python v5.x is the work in progress based on new runtime called `azure-core` (no `msrest` anymore). To be released in November 2019 (current plan). This version will bring the official async support.

#### How to recognize what version of autorest was used?

Autorest doesn't write the version number in the generated code, but a few indicator will tell you what generation is used, just looking at the "models" folder

- Autorest v2: One model file per model class
- Autorest v3: Two model files per model class, the second one being suffixed by "_py3" (e.g. `vm.py` and `vm_py3.py`)
- Autorest v4: Two gigantic model files, one called `_models.py` and the second one `_models_py3.py`
- Autorest v5: `paged` file will import base classes from `azure.core` and not `msrest`

### Basics of generation

A basic autorest command line will looks like this:

```shell
autorest readme.md --python --use="@microsoft.azure/autorest.python@~4.0.71" --python-mode=update --python-sdks-folder=<root of sdk clone>/sdks/ --no-async --multiapi
```

Which means "Generate the Python code for the Swagger mentioned in this readme, using autorest for Pyton v4.0.71 or above (but not v5), do not generate async files, generate multiapi if supported (if not ignore), and assume the package was already generated and it's an update"

In pratical terms, this is not necessary since the Python SDK has the necessary tooling to simplify to just specify the readme.md:

- Checkout the branch
- Checkout the RestAPI specs repo
- Call the tool: `python -m packaging_tools.generate_sdk -v -m restapi_path/readme.md` changing the last path to the readme you want to generate.

The common configuration to pass to all generation are located in the [swagger_to_sdk.json file](https://github.com/Azure/azure-sdk-for-python/blob/master/swagger_to_sdk_config.json)

### Automation bot

If the automation is doing its job correctly, you should not have to build the SDK, but look for an integration PR for the service in question. This link will give you for instance [the list of all integration PRs](https://github.com/Azure/azure-sdk-for-python/labels/ServicePR).

