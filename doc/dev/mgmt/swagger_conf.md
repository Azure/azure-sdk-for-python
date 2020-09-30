# Swagger configuration

All management SDK comes from a Swagger, processed by [autorest](https://github.com/Azure/autorest.python). This page explains how to use autorest to generated Python code.

## Overview

Nowadays, swagger files are actually not the input for Autorest, the input is _readme.md_ file. This file contains all the configuration necessary in order to generate a correct Python code, making the generation as simple as:

```shell
autorest readme.md --python
```

In practical terms, we want to control the version of Autorest used, the output folder, etc. but this article will focus on Swagger and Readme. For more details about generation, see the [generation page](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/generation.md).

## Writing the readme

Writing the readme is the responsibility of the Python SDK team. There is currently two types of templates for Python readmes:
- Readme that handles only one API version, and generates packages that handle one API version only
- Readme that handles several API versions, and generates packages with multiples API and profile supports

These templates can be found in the [single_api](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/single_api) and the [multi_api](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api) folders.


### Single API readmes

This one is the most simple:
- Copy the [readme.python.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/single_api/readme.python.md) and replace `servicetoreplace` by your service name
- Be sure the main [readme.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/single_api/readme.md) contains a "swagger-to-sdk" section with Python

### Multi API readmes

When doing multi-api packages, it means you have shipping several "tags" of the main readme as one package. Autorest is calling this process a "batch" call, and this is the purpose of the "batch" section in [readme.python.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api/readme.python.md).

In order to be sure the correct tags exist, you can use the following script:
```shell
python ./scripts/multi_api_readme_help.py /azure-rest-api-specs/specification/service/resource-manager/
```

This script will analyze the Swaggers available, and suggests on stdout:
- A list of tags for the main [readme.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api/readme.md)
- A batch declaration for the [readme.python.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api/readme.python.md)

This script is not perfect that it *does* require manual review of the output and not a direct copy/paste.

It's important for Python that tags represents only *ONE* unique API version. It's why it's pretty common that Python uses a set of tags that other languages don't use.

Once you know the list of tags you need to generate:

- Copy the [readme.python.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api/readme.python.md) and replace `servicetoreplace` by your service name
- Update the batch list of [readme.python.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api/readme.python.md)
- Be sure you have one tag section for each batch entry in [readme.python.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api/readme.python.md)
- Be sure the main [readme.md](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/mgmt/swagger/multi_api/readme.md) contains a "swagger-to-sdk" section with Python with an `afterscripts` section like the one in the template.

The `afterscripts` will execute a Jinja template to create a client to link together all the batch generated autorest ([example](https://github.com/Azure/azure-sdk-for-python/blob/4a7c67189591b052fe2b5769847ff68f7845386d/sdk/storage/azure-mgmt-storage/azure/mgmt/storage/_storage_management_client.py))

This script will infer a default `LATEST_PROFILE`. You can change this behavior and force the default API version if necessary ([example](https://github.com/Azure/azure-rest-api-specs/blob/49238f0b2917452311e71dd43c4164de70af3721/specification/authorization/resource-manager/readme.md#swagger-to-sdk))

