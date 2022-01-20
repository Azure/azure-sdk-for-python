# Getting Started - Generate SDK With Dataplane Codegen

## Prerequisites

- [Python 3.7](https://www.python.org/downloads/windows/) or later is required

- [Nodejs 14.x.x](https://nodejs.org/download/release/latest-v14.x/) or later is required

- [Autorest][https://github.com/Azure/autorest/blob/main/docs/install/readme.md]

## Setup your repo

- Fork and clone the azure-sdk-for-python repo.

- Create a branch to work in.

## Project service name, module name, and package name

Three key pieces of information for your project are the `service_name`, `module_name`, and `package_name`.

The `service_name` is the short name for the Azure service. The `service_name` should match across all the SDK language repos
and is generally name of the directory in the specification folder of the azure-rest-api-specs repo that contains the REST API definition file.

The `module_name` is the name for the specific feature or function of the REST API that underlies this SDK.
Usually this name comes from the name of the REST API file itself or one of the directories toward the end of the file path.

In Python, a project's `package name` will normally be `azure-{service_name}-{module_name}`. After release, you can find it in PyPI.
For example: you can find [azure-messaging-webpubsubservice](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice) in [pypi](https://pypi.org/project/azure-messaging-webpubsubservice/).

## Project folder structure

Before we start, we probably should get to know the project folder for [SDK repo](https://github.com/Azure/azure-sdk-for-python).

All the files for your SDK will reside in the **${PROJECT_ROOT} folder**, where

```sh
${PROJECT_ROOT}=sdk/{service_name}/azure-{service_name}-{module_name}
```

Normally, the folder structure would be something like:

- **${PROJECT_ROOT}**
  - `azure/{service_name}/{module_name}` : folder where generated code is.
  - `swagger`: folder of configuration file which is used to generate SDK code with autorest
  - `tests`: folder of test files
  - `samples`: folder of sample files

More details on the structure of Azure SDK repos is available in the [Azure SDK common repo](https://github.com/Azure/azure-sdk/blob/main/docs/policies/repostructure.md#sdk-directory-layout).

## How to generate SDK code with Dataplane Codegen

We are working on to automatically generate everything right now, but currently we still need some manual work to get a releasable package. Here're the steps of how to get the package.

1. **Create the ${PROJECT_ROOT} folder if it does not already exist**

2. **Create a README.md file under ${PROJECT_ROOT}/swagger**

   This README.md file will hold the options to be passed to autorest to generate the code. Storing these options in a file in the
   SDK repo helps make SDK generation reproducible.

   ````markdown
   # Azure Purview for Python
  
   > see https://aka.ms/autorest
  
   ### Settings
  
   ```yaml
   input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/webpubsub/data-plane/WebPubSub/stable/2021-10-01/webpubsub.json
   output-folder: ../azure/messaging/webpubsubservice
   namespace: azure.messaging.webpubsubservice
   package-name: azure-messaging-webpubsubservice
   license-header: MICROSOFT_MIT_NO_VERSION
   clear-output-folder: true
   no-namespace-folders: true
   python: true
   title: WebPubSubServiceClient
   version-tolerant: true
   package-version: 1.0.0b1
   add-credential: true
   credential-scopes: https://webpubsub.azure.com/.default
   ```
   ````

   **Reviewers: which of the above can we remove?  We should keep only those needed for the "common" case. And if any could just be the default (e.g. license-header), we should remove those too. Then we should document whatever remains.**

   There are some configuration in the template and you could reference [autorest/flags](https://github.com/Azure/autorest/blob/main/docs/generate/flags.md) to get more info. We need to replace the value in `package-name`, `title`,  `input-file`, `package-version`, `credential-scopes`, `output-folder` into **your own service's** `package-name`, `title`etc.

3. **Run autorest to generate the SDK**

   Now you can run this command in swagger folder you just created.

   ```sh
   autorest --version=latest --python --use=@autorest/python@latest  README.md
   ```

4. **Add necessary files under  ${PROJECT_ROOT}**

   For a complete package, there are some other files you need to add:

   - `CHANGELOG.md`: introduce the release history and important change for each release.

   - `LICENSE`: license file

   - `README.md`: import files which introduce what the service is and how to use this package

   - `dev_requirements.txt`: claims some package which is needed to run test

   - `sdk_packaging.toml`: configuration file to decide which file will be included in package.

   - `setup.py`: most important files about dependency and supported version for Python.

   Here is [template files](https://github.com/Azure/azure-sdk-for-python/tree/main/scripts/quickstart_tooling_llc/template), and you at least need to edit item (like `{{package_name}}`, `{{package_pprint_name}}`, etc) in `CHANGELOG.md`, `README.md`, `setup.py`, `sdk_packaging.toml` according to specific info of your own service.  It is easier to understand how to edit the files with reference existing service: [webpubsub](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice)

   **Reviewers: I understand that work is in progress to generate all these files with a special "init" flag to autorest, so this item will probably go away in the near future.**

## How to add convenience code

**Reviewers: Somewhere, and here seems like as good a place as any, we need to tell teams how to add convenience / "grow up" code. There are certainly right and wrong ways to do this, so we need to give service teams some guidance on this. We could just give the basics here and then point to another document with full details, since most service teams won't bother to add convenience code, but we need the information here in case they do.**

## How to write tests

You should write tests that ensure all APIs fulfil their contract and algorithms work as specified.
This is a requirement of the [Azure SDK Guidelines](https://azure.github.io/azure-sdk/general_implementation.html#testing).

Here is the [Dataplane Codegen Quick Start for Test](https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start-for-Test) about how to write and run tests for the Python SDK.

**Reviewers: We may want to pull the content from this wiki page into here.**

## How to write samples

Samples can make it quicker and easier for customers to use the package. It could be simple which just shows how to use the package; Or it could be a complex scenario example for customers to create their own service quickly.

You should add samples in the `samples` directory under **${PROJECT_ROOT}**. Each sample should have its own folder and contain a `Readme.md`([example](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice/samples/Readme.md)) which introduces simply how to run the sample.

If you want to run sample with dev mode, just run `pip install -e .`([detail doc](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e)) under **${PROJECT_ROOT}** instead of `pip install azure.myservice`.

## How to create package

If you want to create a private package, go to **${PROJECT_ROOT} folder** and run:

```sh
python setup.py bdist_wheel
```

## Create/Update the `ci.yaml`

Now, if everything looks good to you, you can submit a PR in [azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python) repo with all the changes you made above. Before you do that, you need to add/update the `ci.yml` file. Depends on whether there's already one in `sdk/{service_name}` folder.

If there's no such file then you can add the following template.

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
    - name: azure-mgmt-webpubsub
      safeName: azuremgmtwebpubsub
    - name: azure-messaging-webpubsubservice
      safeName: azuremessagingwebpubsubservice
```

Please change the `{service_name}`, `Artifacts name` and `safeName` into yours.

If there's already a `ci.yml` file in your project path. then the only thing you need to do is to add the `Artifacts name` and `safeName` of yours into that `ci.yml`.

Usually, `Artifacts name` is same as `package name` and remove `-`  in `Artifacts name` to get `safeName`. Example: [webpubwub](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/ci.yml), [purview](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/purview/ci.yml)

## Next steps

It is a little troublesome when you generate code and add files manually for total new package. So just have a try to use tools to create LLC code very quickly. Here is the guidance: [Dataplane-Codegen-Quick-Start-with-tools](https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start-with-tools).
