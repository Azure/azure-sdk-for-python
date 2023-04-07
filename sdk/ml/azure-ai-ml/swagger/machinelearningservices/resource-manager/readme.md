# MachineLearningServices

> see <https://aka.ms/autorest>

This is an autorest configuration file for the SDK vNext effort. It is a modified
version of the file used for AzureML's ARM APIs, which is defined [here](https://github.com/Azure/azure-rest-api-specs/blob/master/specification/machinelearningservices/resource-manager/readme.md).

---

## Configuration

### Basic Information

These are the global settings for the Machine Learning Services API.

```yaml
openapi-type: arm
```

### Transformation

### Tag: model-dataplane

These settings apply only when `--tag=model-dataplane` is specified on the command line.

```yaml $(tag) == 'model-dataplane'
input-file:
  - Microsoft.MachineLearningServices/stable/model-dataplane/swagger.json
output-folder: $(python-sdks-folder)/model_dataplane
```

### Tag: dataset-dataplane

These settings apply only when `--tag=dataset-dataplane` is specified on the command line.

```yaml $(tag) == 'dataset-dataplane'
input-file:
  - Microsoft.MachineLearningServices/stable/dataset-dataplane/swagger.json
output-folder: $(python-sdks-folder)/dataset_dataplane
```

### Tag: v2022-05-01

These settings apply only when `--tag=v2022-05-01` is specified on the command line.

```yaml $(tag) == 'v2022-05-01'
input-file:
  - Microsoft.MachineLearningServices/stable/2022-05-01/mfe.json
  - Microsoft.MachineLearningServices/stable/2022-05-01/machineLearningServices.json
  - Microsoft.MachineLearningServices/stable/2022-05-01/workspaceFeatures.json
output-folder: $(python-sdks-folder)/v2022_05_01
```

### Tag: v2022-02-01-preview

These settings apply only when `--tag=v2022-02-01-preview` is specified on the command line.

```yaml $(tag) == 'v2022-02-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2022-02-01-preview/mfe.json
output-folder: $(python-sdks-folder)/v2022_02_01_preview
```

### Tag: v2022-01-01-preview

These settings apply only when `--tag=v2022-01-01-preview` is specified on the command line.

```yaml $(tag) == 'v2022-01-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2022-01-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2022-01-01-preview/workspaceFeatures.json
output-folder: $(python-sdks-folder)/v2022_01_01_preview
```

### Tag: mfe-dataplane-preview

These settings apply only when `--v2020-09-01-dataplanepreview` is specified on the command line.

```yaml $(tag) == 'v2020-09-01-dataplanepreview'
input-file:
  - Microsoft.MachineLearningServices/preview/2020-09-01-dataplanepreview/mfe.json
output-folder: $(python-sdks-folder)/v2020_09_01_dataplanepreview
```

### Tag: mfe-dataplane-preview-10-01

These settings apply only when `--v2021-10-01-dataplanepreview` is specified on the command line.

```yaml $(tag) == 'v2021-10-01-dataplanepreview'
input-file:
  - Microsoft.MachineLearningServices/preview/2021-10-01-dataplanepreview/mfe.json
output-folder: $(python-sdks-folder)/v2021_10_01_dataplanepreview
```

### Tag: runhistory

These settings apply only when `--tag=runhistory` is specified on the command line.

```yaml $(tag) == 'runhistory'
input-file:
  - Microsoft.MachineLearningServices/preview/runhistory/run-history.json
output-folder: $(python-sdks-folder)/runhistory
```

### Tag: registry-discovery

These settings apply only when `--tag=registry-discovery` is specified on the command line.

```yaml $(tag) == 'registry-discovery'
input-file:
    - Microsoft.MachineLearningServices/preview/registry-discovery/registry-discovery.json
output-folder: $(python-sdks-folder)/registry_discovery
```

### Tag: v2022-10-01-preview

These settings apply only when `--tag=v2022-10-01-preview` is specified on the command line.

```yaml $(tag) == 'v2022-10-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2022-10-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2022-10-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2022-10-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2022-10-01-preview/mfe.json
output-folder: $(python-sdks-folder)/v2022_10_01_preview
```

### Tag: v2023-02-01-preview

These settings apply only when `--tag=v2023-0201-preview` is specified on the command line.

```yaml $(tag) == 'v2023-02-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2023-02-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2023-02-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2023-02-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2023-02-01-preview/mfe.json
output-folder: $(python-sdks-folder)/v2023_02_01_preview
```

### Tag: v2022-12-01-preview

These settings apply only when `--tag=v2022-12-01-preview` is specified on the command line.

```yaml $(tag) == 'v2022-12-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2022-12-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2022-12-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2022-12-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2022-12-01-preview/mfe.json
output-folder: $(python-sdks-folder)/v2022_12_01_preview
```

### Tag: v2023-04-01-preview

These settings apply only when `--tag=v2023-04-01-preview` is specified on the command line.

```yaml $(tag) == 'v2023-04-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2023-04-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2023-04-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2023-04-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2023-04-01-preview/mfe.json
output-folder: $(python-sdks-folder)/v2023_04_01_preview
```

### Tag: multiapi

These settings apply only when `--multiapi` is specified on the command line.

```yaml $(multiapi)
clear-output-folder: true
batch:
  - tag: model-dataplane
  - tag: dataset-dataplane
  - tag: v2022-05-01
  - tag: v2022-02-01-preview
  - tag: v2022-01-01-preview
  - tag: runhistory
  - tag: v2020-09-01-dataplanepreview
  - tag: registry-discovery
  - tag: v2022-10-01-preview
  - tag: v2022-12-01-preview
  - tag: v2023-02-01-preview
  - tag: v2023-04-01-preview
  #unstable tags
  - tag: v2021-10-01-dataplanepreview
  - multiapiscript: true
```

### Multi API Script

```yaml $(multiapiscript)
clear-output-folder: false
output-folder: $(python-sdks-folder)
perform-load: false
```

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
version-tolerant: false
modelerfour:
  lenient-model-deduplication: true
```
