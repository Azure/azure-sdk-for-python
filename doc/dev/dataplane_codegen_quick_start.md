Getting Started - Generate SDK With Dataplane Codegen
================================================================

# Prerequisites

- [Python 3.7](https://www.python.org/downloads/windows/) or later is required

- [Nodejs 14.x.x](https://nodejs.org/download/release/latest-v14.x/) or later is required

- create virtual environment

  ```
  python -m venv venv-dev
  .\venv-dev\Scripts\Activate.ps1
  ```

- prepare SDK repo if needed

  ```
  git clone https://github.com/Azure/azure-sdk-for-python.git
  ```

- prepare autorest

  ```
  npm install -g autorest
  ```

# Project folder and package name

Before we start, we probably should get to know the project folder for [SDK repo](https://github.com/Azure/azure-sdk-for-python). Normally, the folder structure would be something like:

- `sdk/{servicename}/azure-{servicename}-{modulename}`:  **${PROJECT_ROOT} folder**, there are also some other files(like setup.py, README.md, etc) which are necessary for a complete package.
- **${PROJECT_ROOT}**`/azure/{servicename}/{modulename}` : folder where generated code is.
- **${PROJECT_ROOT}** `/swagger`: folder of configuration file which is used to generate SDK code with autorest
- **${PROJECT_ROOT}**`/tests`: folder of test files 
- **${PROJECT_ROOT}**`/samples`: folder of sample files 
- `azure-{servicename}-{modulename}`: package name. Usually, package name is same with part of **${PROJECT_ROOT} folder**. After release, you can find it in pypi. For example: you can find [azure-messaging-webpubsubservice](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice) in [pypi](https://pypi.org/project/azure-messaging-webpubsubservice/).

# How to generate SDK code with Dataplane Codegen

We are working on to automatically generate everything right now, but currently we still need some manual work to get a releasable package. Here're the steps of how to get the package.

1. **Create a README.md file under ${PROJECT_ROOT}/swagger**
   We are using autorest to generate the code, but there's a lot of command options and in order to make the regenerate process easier in the cases of refresh the rest api input or change the code generator version. So it is better to document the command parameters.
   Here's an example of the `README.md`

   ````
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

   There are some configuration in the template and you could reference [autorest/flags](https://github.com/Azure/autorest/blob/main/docs/generate/flags.md) to get more info. We need to replace the value in `package-name`, `title`,  `input-file`, `package-version`, `credential-scopes`, `output-folder` into **your own service's** `package-name`, `title`etc.

2. **Run autorest to generate the SDK**

   Now you can run this command in swagger folder you just created.

```
autorest --version=latest --python --use=@autorest/python@latest  README.md
```

- **Add necessary files under  ${PROJECT_ROOT}**

  For a complete package, there are some other files you need to add:

  `CHANGELOG.md`: introduce the release history and important change for each release.

  `LICENSE`: license file

  `README.md`: import files which introduce what the service is and how to use this package

  `dev_requirements.txt`: claims some package which is needed to run test

  `sdk_packaging.toml`: configuration file to decide which file will be included in package.

  `setup.py`: most important files about dependency and supported version for Python.

  

  Here is [template files](https://github.com/Azure/azure-sdk-for-python/tree/main/scripts/quickstart_tooling_llc/template), and you at least need to edit item (like `{{pakcage_name}}`, `{{package_pprint_name}}`, etc) in `CHANGELOG.md`, `README.md`, `setup.py`, `sdk_packaging.toml` according to specific info of your own service.  It is easier to understand how to edit the files with reference existing service: [webpubsub](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice)

# How to write test

Here is the [Dataplane Codegen Quick Start for Test](https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start-for-Test) about how to write and run test.

# How to write sample

sample can make customers more easy and fast to use the package. It could be simple which just shows how to use the package; Or it could be complexed scenario example for customers to create their own service quicky. 

sample is very flexible but it should be an executive and easy to run and understand.

You could add sample under **${PROJECT_ROOT}/swagger**. It is better to contain `Readme.md`([example](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubservice/samples/Readme.md)) which introduces simply how to run the sample.

If you want to run sample with dev mode, just run `pip install -e .`([detail doc](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e)) under **${PROJECT_ROOT}** instead of `pip install azure.myservice`.

# How to create package

If you want to create a private package, go to **${PROJECT_ROOT} folder** and run :

```
python setup.py bdist_wheel
```

# Create/Update the `ci.yaml`

Now, if everything looks good to you, you can submit a PR in [azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python) repo with all the changes you made above. Before you do that, you need to add/update the `ci.yml` file. Depends on whether there's already one in `sdk/{servicename}` folder.

If there's no such file then you can add the following template.

```
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
    - sdk/{servicename}/

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
    - sdk/{servicename}/

extends:
  template: ../../eng/pipelines/templates/stages/archetype-sdk-client.yml
  parameters:
    ServiceDirectory: {servicename}
    Artifacts:
    - name: azure-mgmt-webpubsub
      safeName: azuremgmtwebpubsub
    - name: azure-messaging-webpubsubservice
      safeName: azuremessagingwebpubsubservice
```

Please change the `{servicename}`, `Artifacts name` and `safeName` into yours.

If there's already a `ci.yml` file in your project path. then the only thing you need to do is to add the `Artifacts name` and `safeName` of yours into that `ci.yml`. 

Usually, `Artifacts name` is same with `package name` and remove `-`  in `Artifacts name` to get `safeName`. Example: [webpubwub](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/ci.yml), [purview](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/purview/ci.yml)

# Next steps

It is a little troublesome when you generate code and add files manually for total new package. So just have a try to use tools to create LLC code very quickly. Here is the guidance: [Dataplane-Codegen-Quick-Start-with-tools](https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start-with-tools).