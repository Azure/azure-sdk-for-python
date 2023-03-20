## Python

These settings apply only when `--python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(python)
title: AzureMachineLearningWorkspaces
azure-arm: true
license-header: MICROSOFT_MIT_NO_VERSION
namespace: azure.mgmt.machinelearningservices
package-name: azure-mgmt-machinelearningservices
package-version: 1.0.0b1
clear-output-folder: true
no-namespace-folders: true
```

``` yaml $(python)
no-namespace-folders: true
output-folder: $(python-sdks-folder)/v2023_02_01_preview
```

``` yaml $(python)
modelerfour:
  lenient-model-deduplication: true
```
