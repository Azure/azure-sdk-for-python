# Overview
This folder contains pipeline configuration to generate SDK, run live test and create pull request to 
[azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python)

## `PythonSdkLiveTest.yml`
The file defines [pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=2500&_a=summary) to
generate SDK, run live test and create pull request.

## `auto_private_package.py`
the script could help to generate private package quickly.

### Usage
```
python scripts/auto_release/auto_private_package.py
```