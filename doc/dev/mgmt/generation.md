# Generation of SDK

IMPORTANT NOTE: All the commands prefixed by `python` in this page assumes you have loaded the [dev_setup](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/dev_setup.md) in your currently loaded virtual environment.

## Generating from TypeSpec

### Prerequisites

#### Setting Up Your Basic Environment
- Python 3.10 or newer is required
  - [Download for Windows](https://www.python.org/downloads/windows/)
  - For Linux:
    - Install Python 3 with `sudo apt install python3`
    - Install Python 3 Pip with `sudo apt install python3-pip`
    - If needed, install Python 3.{?}-venv with `sudo apt install python3.{?}-venv`

- [Node.js 20.x LTS](https://nodejs.org/en/download/) or newer is required

#### Preparing Your Repos

- Fork and clone the [azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python) repo (the "SDK repo")
- Fork and clone the [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repo (the "Rest repo")

#### Identifying `tspconfig.yaml`

Find the `tspconfig.yaml` file for your package in the Rest repo. Ensure there's a configuration for the Python SDK similar to the one shown below and in [this example](https://github.com/Azure/azure-rest-api-specs/blob/85ed8fc06e19c902c95b531cbd8a643428d5f28d/specification/contosowidgetmanager/Contoso.Management/tspconfig.yaml#L18-L23):

```yaml
parameters:
  "service-dir":
    default: "sdk/SERVICE_DIRECTORY_NAME"
options:
  "@azure-tools/typespec-python":
    emitter-output-dir: "{output-dir}/{service-dir}/azure-mgmt-NAMESPACE"
    namespace: "azure.mgmt.NAMESPACE"
    generate-test: true
    generate-sample: true
    flavor: "azure"
```

Replace `SERVICE_DIRECTORY_NAME` and `NAMESPACE` with the actual values for your service.

#### Installing Necessary Dependencies

1. Install `typespec-client-generator-cli` globally:
```
npm install -g @azure-tools/typespec-client-generator-cli
```

2. Create a Python virtual environment and activate it:
```
PS C:\dev\azure-sdk-for-python> python -m venv .venv
PS C:\dev\azure-sdk-for-python> .\.venv\Scripts\Activate.ps1  # Windows
   /C/dev/azure-sdk-for-python> source .venv/bin/activate     # Linux
```

3. Install Python dependencies:
```
(.venv) PS C:\dev\azure-sdk-for-python> python .\scripts\dev_setup.py -p azure-core
(.venv) PS C:\dev\azure-sdk-for-python> pip install setuptools
```

### Generate the SDK

1. Create a local JSON file named `generatedInput.json` outside the SDK repo with content like:

```json
{
  "specFolder": "LOCAL_AZURE-REST-API-SPECS_REPO_ROOT",
  "headSha": "SHA_OF_AZURE-REST-API-SPECS_REPO",
  "repoHttpsUrl": "https://github.com/Azure/azure-rest-api-specs",
  "relatedTypeSpecProjectFolder": [
    "specification/SERVICE_DIRECTORY_NAME/PACKAGE_DIRECTORY_NAME/"
  ]
}
```

Use `git rev-parse HEAD` on the local Rest repo root to get the `headSha` value.

2. Run the generation command:
```
(.venv) PS C:\dev\azure-sdk-for-python> python -m packaging_tools.sdk_generator ..\generatedInput.json ..\generatedOutput.json
```

3. View information about the generated SDK in `generatedOutput.json`.

### Key Concepts: Service Name and Namespace

The `service_name` is the short name for the Azure service. It should match across all SDK language repos and should be the name of the directory in the `specification` folder of the Rest repo that contains the REST API definition file. An example is Service Bus, whose API definitions are in `specification/servicebus`, using the service_name `servicebus`.

In Python, a project's `package name` is the name used to publish to [PyPI](https://pypi.org/). By default, the package name is derived from the `namespace`, swapping `.`s for `-`s. For management plane libraries, the package_name is typically `azure-mgmt-{service_name}` (e.g., `azure-mgmt-servicebus`).

### Project Folder Structure

The standard folder structure in the SDK repo is:

- `sdk/{service_name}/{package_name}/` — the project root
  - `tests/` — manual test files
  - `generated_tests/` — auto-generated test files
  - `samples/` — manual sample files
  - `generated_samples/` — auto-generated sample files

More details on the structure is available in the [Azure SDK common repo](https://github.com/Azure/azure-sdk/blob/main/docs/policies/repostructure.md#sdk-directory-layout).

### Additional TypeSpec Resources

- [Getting Started with TypeSpec Generation (using Copilot)](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/ai/typespec_generation.md)
- [TypeSpec Documentation](https://typespec.io/docs)

## Post-Generation Steps

See the [Post-Generation Steps](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/dataplane_generation.md#post-generation-steps) for the steps to follow after generating your SDK code (writing README, tests, samples, ci.yml, CODEOWNERS, and release preparation).

---

## Legacy: Generating from Swagger (AutoRest)

> **Deprecated:** Swagger-based generation with AutoRest is deprecated. All new SDKs should be generated from [TypeSpec](#generating-from-typespec). The instructions below are preserved for maintaining existing legacy packages only.

### Swagger Configuration

Assuming your Swagger are associated with correct Readmes (otherwise see [Swagger conf](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/swagger_conf.md)), you can use AutoRest to generate packages.

### Building the Code

#### Autorest Versioning

> **Historical Note:** The version details below are preserved for reference. AutoRest-based generation is no longer the recommended approach.

A few notes on [Autorest for Python versioning](https://github.com/Azure/autorest.python/blob/main/ChangeLog.md):
- Autorest for Python v2.x is deprecated, and should not be used anymore for any generation under any circumstances.
- Autorest for Python v3.x is the most currently used one. Should not be used, but still ok if service team are still in v3.x and they want to avoid breaking changes for a given version (rare).
- Autorest for Python v4.x is the current recommendation. This generator can generates async code, but this should be disabled with --no-async. No package should be shipped with async based on v4
- Autorest for Python v5.x is based on the `azure-core` runtime (no `msrest` anymore). This version brings the official async support.

##### How to recognize what version of autorest was used?

Autorest doesn't write the version number in the generated code, but a few indicator will tell you what generation is used, just looking at the "models" folder

- Autorest v2: One model file per model class
- Autorest v3: Two model files per model class, the second one being suffixed by "_py3" (e.g. `vm.py` and `vm_py3.py`)
- Autorest v4: Two gigantic model files, one called `_models.py` and the second one `_models_py3.py`
- Autorest v5: `paged` file will import base classes from `azure.core` and not `msrest`

#### Basics of Generation

A basic autorest command line will looks like this:

```shell
autorest readme.md --python --use="@microsoft.azure/autorest.python@~4.0.71" --python-mode=update --python-sdks-folder=<root of sdk clone>/sdks/ --no-async
```

Which means "Generate the Python code for the Swagger mentioned in this readme, using autorest for Python v4.0.71 or above (but not v5), do not generate async files, and assume the package was already generated and it's an update"

In practical terms, this is not necessary since the Python SDK has the necessary tooling to simplify to just specify the readme.md:

- Checkout the branch
- Checkout the RestAPI specs repo
- Call the tool: `python -m packaging_tools.generate_sdk -v -m restapi_path/readme.md` changing the last path to the readme you want to generate.

The common configuration to pass to all generation are located in the [swagger_to_sdk.json file](https://github.com/Azure/azure-sdk-for-python/blob/main/swagger_to_sdk_config.json)

#### Automation Bot

If the automation is doing its job correctly, you should not have to build the SDK, but look for an integration PR for the service in question. This link will give you for instance [the list of all integration PRs](https://github.com/Azure/azure-sdk-for-python/labels/ServicePR).

### Using Raw Autorest

If you want to use raw autorest and nothing else, not even Readme, a few tips:

If you're doing basic testing and want to minimal set of parameters:
- To call Autorest, you need the following options:

  - Required parameter: `--payload-flattening-threshold=2`
  - About the generator:

     - If your endpoint is ARM, add `--python --azure-arm=true`
     - If not, add `--python`. If your client _might_ ask authentication, add `--add-credentials`

And that's it! You should now have Python code ready to test. Note that this generation is for testing only and should not be sent to a customer or published to PyPI.

This command generate code only. If you want to generate a [wheel](https://pythonwheels.com/) file to share this code, add the `--basic-setup-py` option to generate a basic `setup.py` file and call `python setup.py bdist_wheel`.

#### Examples

ARM management Swagger:

`autorest --version=latest --python --azure-arm=true --payload-flattening-threshold=2 --input-file=myswagger.json`

Not-ARM Swagger:

`autorest --version=latest --python --payload-flattening-threshold=2 --add-credentials --input-file=myswagger.json`

If you want something closed to a real generation:

Let's assume for now that your Swagger is in `specification/compute/resource-manager`

To call Autorest, you need the following options:

  - Required parameters:

      `--payload-flattening-threshold=2 --license-header=MICROSOFT_MIT_NO_VERSION --namespace=azure.mgmt.compute --package-name=azure-mgmt-compute --package-version=0.1.0`

  - About the generator:

     - If your endpoint is ARM, add `--python --azure-arm=true`
     - If not, add `--python`. If your client _might_ ask authentication, add `--add-credentials`

#### More Examples

ARM Swagger with MD (preferred syntax):

`autorest --version=latest specifications/storage/resource-manager/readme.md --python --azure-arm=true --payload-flattening-threshold=2 --license-header=MICROSOFT_MIT_NO_VERSION --namespace=azure.mgmt.storage --package-name=azure-mgmt-storage --package-version=0.1.0 `

ARM Swagger without MD (if you have an excellent reason):

`autorest --version=latest --python --azure-arm=true --payload-flattening-threshold=2 --license-header=MICROSOFT_MIT_NO_VERSION --namespace=azure.mgmt.storage --package-name=azure-mgmt-storage --package-version=0.1.0 --input-file=specifications/storage/resource-manager/Microsoft.Storage/2016-12-01/storage.json`
