# MachineLearningServices

> see [https://aka.ms/autorest](https://aka.ms/autorest)

This is an autorest configuration file for the SDK vNext effort. It is a modified
version of the file used for AzureML's ARM APIs, which is defined [here](https://github.com/Azure/azure-rest-api-specs/blob/master/specification/machinelearningservices/resource-manager/readme.md).

---

## Usage

For instructions for regenerating the _restclient using these arguments, see the `docs/dev_setup.md` in the AML CLI repo.
For a quick example, Run this command from azure-sdk-for-python/sdk/ml/azure-ai-ml/:

```
python ./scripts/regenerate_restclient.py -a v2022-01-01-preview
```

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

These settings apply only when `--tag=v2020-09-01-dataplanepreview` is specified on the command line.

```yaml $(tag) == 'v2020-09-01-dataplanepreview'
input-file:
  - Microsoft.MachineLearningServices/preview/2020-09-01-dataplanepreview/mfe.json
output-folder: $(python-sdks-folder)/v2020_09_01_dataplanepreview
```

### Tag: mfe-dataplane-preview-10-01

These settings apply only when `--tag=v2021-10-01-dataplanepreview` is specified on the command line.

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

### Tag: workspace-dataplane

These settings apply only when `--tag=workspace-dataplane` is specified on the command line.

```yaml $(tag) == 'workspace-dataplane'
input-file:
  - Microsoft.MachineLearningServices/preview/workspace-dataplane/swagger.json
output-folder: $(python-sdks-folder)/workspace_dataplane
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

These settings apply only when `--tag=v2023-02-01-preview` is specified on the command line.

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

### Tag: v2023-04-01

These settings apply only when `--tag=v2023-04-01` is specified on the command line.

```yaml $(tag) == 'v2023-04-01'
input-file:
  - Microsoft.MachineLearningServices/stable/2023-04-01/machineLearningServices.json
  - Microsoft.MachineLearningServices/stable/2023-04-01/registries.json
  - Microsoft.MachineLearningServices/stable/2023-04-01/workspaceFeatures.json
  - Microsoft.MachineLearningServices/stable/2023-04-01/mfe.json
output-folder: $(python-sdks-folder)/v2023_04_01
```

### Tag: v2023-06-01-preview

These settings apply only when `--tag=v2023-06-01-preview` is specified on the command line.

```yaml $(tag) == 'v2023-06-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2023-06-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2023-06-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2023-06-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2023-06-01-preview/mfe.json
  - Microsoft.MachineLearningServices/preview/2023-06-01-preview/workspaceRP.json
output-folder: $(python-sdks-folder)/v2023_06_01_preview
```

### Tag: v2023-08-01-preview

These settings apply only when `--tag=v2023-08-01-preview` is specified on the command line.

```yaml $(tag) == 'v2023-08-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2023-08-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2023-08-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2023-08-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2023-08-01-preview/mfe.json
  - Microsoft.MachineLearningServices/preview/2023-08-01-preview/workspaceRP.json
output-folder: $(python-sdks-folder)/v2023_08_01_preview
```

### Tag: v2023-10-01

These settings apply only when `--tag=v2023-10-01` is specified on the command line.

```yaml $(tag) == 'v2023-10-01'
input-file:
  - Microsoft.MachineLearningServices/stable/2023-10-01/machineLearningServices.json
  - Microsoft.MachineLearningServices/stable/2023-10-01/registries.json
  - Microsoft.MachineLearningServices/stable/2023-10-01/workspaceFeatures.json
  - Microsoft.MachineLearningServices/stable/2023-10-01/mfe.json
output-folder: $(python-sdks-folder)/v2023_10_01
```

### Tag: v2024-01-01-preview

These settings apply only when `--tag=v2024-01-01-preview` is specified on the command line.

```yaml $(tag) == 'v2024-01-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2024-01-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2024-01-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2024-01-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2024-01-01-preview/mfe.json
  - Microsoft.MachineLearningServices/preview/2024-01-01-preview/workspaceRP.json
output-folder: $(python-sdks-folder)/v2024_01_01_preview
```

### Tag: v2024-04-01-preview

These settings apply only when `--tag=v2024-04-01-preview` is specified on the command line.

```yaml $(tag) == 'v2024-04-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2024-04-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2024-04-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2024-04-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2024-04-01-preview/mfe.json
  - Microsoft.MachineLearningServices/preview/2024-04-01-preview/workspaceRP.json
output-folder: $(python-sdks-folder)/v2024_04_01_preview
```

### Tag: v2024-07-01-preview

These settings apply only when `--tag=v2024-07-01-preview` is specified on the command line.

```yaml $(tag) == 'v2024-07-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2024-07-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2024-07-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2024-07-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2024-07-01-preview/mfe.json
  - Microsoft.MachineLearningServices/preview/2024-07-01-preview/workspaceRP.json
output-folder: $(python-sdks-folder)/v2024_07_01_preview
```

### Tag: v2024-10-01-preview

These settings apply only when `--tag=v2024-10-01-preview` is specified on the command line.

```yaml $(tag) == 'v2024-10-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2024-10-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2024-10-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2024-10-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2024-10-01-preview/mfe.json
  - Microsoft.MachineLearningServices/preview/2024-10-01-preview/workspaceRP.json
output-folder: $(python-sdks-folder)/v2024_10_01_preview
```

### Tag: v2025-01-01-preview

These settings apply only when `--tag=v2025-01-01-preview` is specified on the command line.

```yaml $(tag) == 'v2025-01-01-preview'
input-file:
  - Microsoft.MachineLearningServices/preview/2025-01-01-preview/machineLearningServices.json
  - Microsoft.MachineLearningServices/preview/2025-01-01-preview/registries.json
  - Microsoft.MachineLearningServices/preview/2025-01-01-preview/workspaceFeatures.json
  - Microsoft.MachineLearningServices/preview/2025-01-01-preview/mfe.json
  - Microsoft.MachineLearningServices/preview/2025-01-01-preview/workspaceRP.json
output-folder: $(python-sdks-folder)/v2025_01_01_preview
```

### Tag: v2024-04-01-dataplanepreview

These settings apply only when `--tag=v2024-04-01-dataplanepreview` is specified on the command line.

```yaml $(tag) == 'v2024-04-01-dataplanepreview'
input-file:
  - Microsoft.MachineLearningServices/preview/2024-04-01-dataplanepreview/azure-ai-assets.json
output-folder: $(python-sdks-folder)/v2024_04_01_dataplanepreview
```

---

## Code Generation

### Swagger to SDK

This section describes what SDK should be generated by the automatic system.
This is not used by Autorest itself.

```yaml
swagger-to-sdk:
  - repo: azure-sdk-for-python
```
