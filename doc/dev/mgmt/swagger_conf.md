# Swagger configuration

All management SDK comes from a Swagger, processed by [autorest](https://github.com/Azure/autorest.python). This page explains how to use autorest to generated Python code.

## Overview

Nowadays, swagger files are actually not the input for Autorest, the input is _readme.md_ file. This file contains all the configuration necessary in order to generate a correct Python code, making the generation as simple as:

```shell
autorest readme.md --python
```

In practical terms, we want to control the version of Autorest used, the output folder, etc. but this article will focus on Swagger and Readme. For more details about generation, see the [generation page](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/generation.md).

## Writing the readme

Writing the readme is the responsibility of the Python SDK team. There is currently one type of template for Python readmes:
- Readme that handles only one API version, and generates packages that handle one API version only

Templates can be found in the [single_api](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/swagger/single_api) folder.


### Single API readmes

This one is the most simple:
- Copy the [readme.python.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/swagger/single_api/readme.python.md) and replace `servicetoreplace` by your service name
- Be sure the main [readme.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/swagger/single_api/readme.md) contains a "swagger-to-sdk" section with Python



