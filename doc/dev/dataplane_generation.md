# Dataplane SDK Generation Quick Start (TypeSpec)

## Support

For more questions and general overview of the process, please refer to <https://aka.ms/azsdk/dpcodegen>

## Prerequisites

- Python 3.10 or later is required
  - [download for windows](https://www.python.org/downloads/windows/)
  - linux
    - sudo apt install python3
    - sudo apt install python3-pip
    - sudo apt install python3.{?}-venv explicitly if needed

- [Node.js 20.x LTS](https://nodejs.org/en/download/) or later is required

## Setup your repo

- Fork and clone the [azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python) repo (we call its name `SDK repo` and its absolute path)

- Create a branch in SDK repo to work in

- Make sure your typespec definition is merged into `main` branch of [public rest repo](https://github.com/Azure/azure-rest-api-specs) (we call it `rest repo`) or you already make a PR in `rest repo` so that you could get the github link of your typespec definition which contains commit id (e.g. https://github.com/Azure/azure-rest-api-specs/blob/46ca83821edd120552403d4d11cf1dd22360c0b5/specification/contosowidgetmanager/Contoso.WidgetManager/tspconfig.yaml)

## Project service name and namespace

Two key pieces of information for your project are the `service_name` and `namespace`.

The `service_name` is the short name for the Azure service. The `service_name` should match across all the SDK language repos
and should be name of the directory in the specification folder of the azure-rest-api-specs repo that contains the REST API definition file.
An example is Service Bus, whose API definitions are in the `specification/servicebus` folder of the azure-rest-api-specs repo,
and uses the `service_name` "servicebus".
Not every service follows this convention, but it should be the standard unless there are strong reasons to deviate.

In Python, a project's `package name` is the name used to publish the package in [PyPI](https://pypi.org/). By default, the package name is derived from the `namespace`, just swapping the `.`s for `-`s. You can override the default `package-name` by passing in a different value in your `tspconfig.yaml`.
For data plane libraries (management plane uses a different convention), the package name could be just `azure-{service_name}`.
An example is "azure-servicebus".

Some services may need several different packages. For these cases a third component, the `module_name`, is added to the `namespace`,
as `azure.{service_name}.{module_name}`. This change affects the default package name as well, which is needed in these cases.
The `module_name` usually comes from the name of the REST API file itself or one of the directories toward the end of the file path.
An example is the Synapse service, with packages `azure-synapse`, `azure-synapse-accesscontrol`, `azure-synapse-artifacts`, etc.

## Project folder structure

Before we start, we probably should get to know the project folder for [SDK repo](https://github.com/Azure/azure-sdk-for-python).

Normally, the folder structure would be something like:

- `sdk/{service_name}/{package_name}`: **the PROJECT_ROOT folder**
  - `/azure/{service_name}/{module_name}`: folder where generated code is.
  - `/tests`: folder of test files
  - `/samples`: folder of sample files
  - `azure-{service_name}-{module_name}`: package name. Usually, package name is same with part of **${PROJECT_ROOT} folder**. After release, you can find it in pypi. For example: you can find [azure-messaging-webpubsubservice](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice) in [pypi](https://pypi.org/project/azure-messaging-webpubsubservice/).
  - there are also some other files (like setup.py, README.md, etc.) which are necessary for a complete package.

More details on the structure of Azure SDK repos is available in the [Azure SDK common repo](https://github.com/Azure/azure-sdk/blob/main/docs/policies/repostructure.md#sdk-directory-layout).

## How to generate SDK code with Dataplane Codegen

We are working on to automatically generate everything right now, but currently we still need some manual work to get a releasable package. Here are the steps of how to get the package.

### 1. Configure python emitter in tspconfig.yaml

In `rest repo`, there shall be `tspconfig.yaml` where `main.tsp` of your service is. Make sure there are configuration for Python SDK like:

```yaml
parameters:
  "service-dir":
    default: "YOUR-SERVICE-DIRECTORY"

emit: [
  "@azure-tools/typespec-autorest", // this value does not affect python code generation
]

options:
  "@azure-tools/typespec-python":
    emitter-output-dir: "{output-dir}/{service-dir}/YOUR-PACKAGE-DIR"
    namespace: "YOUR.NAMESPACE.NAME"
    flavor: "azure"
```

`YOUR.NAMESPACE.NAME` is your namespace name; `YOUR-PACKAGE-DIR` is your package directory; `YOUR-SERVICE-DIRECTORY` is SDK directory name. For example, assume that namespace is "azure.ai.anomalydetector" and you want to put it in folder "azure-sdk-for-python/sdk/anomalydetector", then "YOUR.NAMESPACE.NAME" is "azure.ai.anomalydetector", "YOUR_PACKAGE_DIR" is "azure-ai-anomalydetector" and "YOUR-SERVICE-DIRECTORY" is "sdk/anomalydetector"

### 2. Run cmd to generate the SDK

Install `tsp-client` CLI tool:

```shell
npm install -g @azure-tools/typespec-client-generator-cli
```

For initial set up, from the root of the SDK repo, call:

```shell
tsp-client init -c YOUR_REMOTE_TSPCONFIG_URL
```

> An example of YOUR_REMOTE_TSPCONFIG_URL is https://github.com/Azure/azure-rest-api-specs/blob/6bbc511b0a42f9ca9992ef16146a12f5cc2a171a/specification/contosowidgetmanager/Contoso.WidgetManager/tspconfig.yaml

To update your TypeSpec generated SDK, go to your SDK folder where your tsp-location.yaml is located, call:

```shell
tsp-client update
```

tsp-client will look for a `tsp-location.yaml` file in your local directory. `tsp-location.yaml` contains the configuration information that will be used to sync your TypeSpec project and generate your SDK. Please make sure that the commit is targeting the correct TypeSpec project updates you wish to generate your SDK from.

## Post-Generation Steps

The generated code is not enough to release directly. Follow these steps regardless of whether you generated from TypeSpec or Swagger.

### Write README.md

Write informative content in README.md for customers. See [webpubsub](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubservice/README.md) for an example.

### Write Tests

You should write tests that ensure all APIs fulfil their contract. This is a requirement of the [Azure SDK Guidelines](https://azure.github.io/azure-sdk/general_implementation.html#testing). See the [Python SDK testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for details.

### Write Samples

Add samples in the `samples` directory under the project root. Each sample should contain a `README.md` ([example](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice/samples/Readme.md)).

### Create/Update `ci.yml`

If there's no `ci.yml` file in `sdk/{service_name}/`, add the following template:

```yaml
# DO NOT EDIT THIS FILE
# This file is generated automatically and any changes will be lost.

trigger:
  branches:
    include:
    - main
    - hotfix/*
    - release/*
    - restapi*
  paths:
    include:
    - sdk/{service_name}/

pr:
  branches:
    include:
    - main
    - feature/*
    - hotfix/*
    - release/*
    - restapi*
  paths:
    include:
    - sdk/{service_name}/

extends:
  template: ../../eng/pipelines/templates/stages/archetype-sdk-client.yml
  parameters:
    ServiceDirectory: {service_name}
    Artifacts:
    - name: {package_name}
      safeName: {safeName}
```

Replace `{service_name}`, `{package_name}`, and `{safeName}` with your values. Usually, `safeName` is derived from the package name by removing all `-`.

If a `ci.yml` already exists, just add your package's `name` and `safeName` entry.

### Configure CODEOWNERS

If adding a new module group (new sub-folder under `sdk/`), add an entry to [CODEOWNERS](https://github.com/Azure/azure-sdk-for-python/blob/main/.github/CODEOWNERS) so GitHub auto-assigns reviewers.

### Release

See the [Release Checklist](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/8/Release-Checklist?anchor=prepare-release-script). Before submitting a PR:

- **Update CHANGELOG.md** with the changes for the new version and an approximate release date (e.g., `1.0.0b1 (2022-02-02)`).
- **Update the version number** according to the [package version rule](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/package_version/package_version_rule.md).
- **Fix CI failures** — see [CI Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md).
