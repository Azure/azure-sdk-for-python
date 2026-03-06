# MaaP on Foundry – SDK Design Document

## 1. Overview

SDK changes for MaaP on Foundry across two packages:

| Package | Role | Work type |
|---------|------|-----------|
| `azure-ai-ml` | Publisher: DT + Model entities | Manual — new fields on existing entities |
| `azure-mgmt-cognitiveservices` | Consumer: deploy to Foundry | Autorest regen from updated swagger |

### Blocking Prerequisites

| Prerequisite | Blocking |
|-------------|----------|
| MRS RP: accept `acceleratorMaps` on DeploymentTemplate | **Yes** |
| MRS RP: accept `allowedDeploymentTemplates` on Model | **Yes** |
| CogSvc RP: accept `deploymentTemplate` + `acceleratorType` on DeploymentProperties | **Yes** |
| CogSvc RP: accept `azureml://` URIs in `DeploymentModel.source` (currently documented as ARM resource ID only) | **Yes** |
| Both RPs: publish updated swagger specs | **Yes** |
| `azure-ai-ml`: generate and add new API-version `_restclient` for whichever MRS API version carries these changes | **Yes** |

### Out of Scope

API/RP contract design · CLI implementation · Backend orchestration · UI changes

---

## 2. Publisher – `azure-ai-ml`

### 2.1 New Entity: `AcceleratorMap`

New file: `entities/_deployment/accelerator_map.py` — `@experimental` data class.

| Field | Type | Required | REST key |
|-------|------|----------|----------|
| `accelerator_type` | `str` | Yes | `acceleratorType` |
| `number_of_accelerators_per_model_instance` | `int` | Yes | `numberOfAcceleratorsPerModelInstance` |
| `default` | `bool` | No | `default` |

Follows existing pattern (`_to_rest_dict` / `_from_rest_dict`) used by `OnlineRequestSettings` and `ProbeSettings`.

### 2.2 DeploymentTemplate: add `accelerator_maps`

Add `accelerator_maps: Optional[List[AcceleratorMap]]` — serialized as `acceleratorMaps`.

| File | Change |
|------|--------|
| `entities/_deployment/deployment_template.py` | Add to `__init__`, `_to_rest_object`, `_from_rest_object`, `dump` |
| `_schema/_deployment/template/deployment_template.py` | Add `AcceleratorMapSchema` + `accelerator_maps` field |
| `entities/__init__.py` | Export `AcceleratorMap` |

### 2.3 Model: add `allowed_deployment_templates`

Add `allowed_deployment_templates: Optional[List[DefaultDeploymentTemplate]]` — serialized as `allowedDeploymentTemplates`.

Reuses the existing `DefaultDeploymentTemplate` class (single `asset_id` field). Add `DeploymentTemplateReference` as an alias for proposal-consistent naming.

| File | Change |
|------|--------|
| `entities/_assets/_artifacts/model.py` | Add to `__init__`, `_to_rest_object`, `_from_rest_object` |
| `_schema/_assets/model.py` | Add `allowed_deployment_templates` list field |
| `entities/_assets/_default_deployment_template.py` | Add `DeploymentTemplateReference` alias |
| `_restclient/.../models/_models.py` | Add to `ModelVersionDetails` (or regen from swagger) |
| `entities/__init__.py` | Export `DeploymentTemplateReference` |

### 2.4 No Operations or CLI Changes

- `DeploymentTemplateOperations.create_or_update()` and `ModelOperations.create_or_update()` are entity-agnostic — they call `_to_rest_object()` and pass the result. **No changes needed.**
- `az ml` CLI uses `load_deployment_template()` / `load_model()` which delegate to SDK schemas. **Only a version bump in `setup.py` is needed.**

### 2.5 Validation

SDK does **type checks only** (items are correct class instances). Value validation of `accelerator_type` happens server-side at deployment time (MRS → Singularity SKU Translation API).

### 2.6 YAML Examples

**Deployment template:**
```yaml
accelerator_maps:
  - accelerator_type: H100_80GB
    number_of_accelerators_per_model_instance: 4
    default: true
  - accelerator_type: H200_141GB
    number_of_accelerators_per_model_instance: 2
```

**Model:**
```yaml
default_deployment_template:
  asset_id: "azureml://registries/reg1/deploymenttemplates/dt1/labels/latest"
allowed_deployment_templates:
  - asset_id: "azureml://registries/reg1/deploymenttemplates/dt1/labels/latest"
  - asset_id: "azureml://registries/reg1/deploymenttemplates/dt2/labels/latest"
```

### 2.7 SDK Usage

```python
from azure.ai.ml import MLClient
from azure.ai.ml.entities import DeploymentTemplate, AcceleratorMap, Model, DefaultDeploymentTemplate
from azure.identity import DefaultAzureCredential

ml_client = MLClient(DefaultAzureCredential(), sub_id, registry_name="reg1")

# Create DT with accelerator maps
dt = DeploymentTemplate(
    name="dt1", version="1",
    environment="azureml://registries/reg1/environments/env1/versions/1",
    allowed_instance_types="Standard_ND96isr_H100_v5 Standard_ND96isr_H200_v5",
    accelerator_maps=[
        AcceleratorMap(accelerator_type="H100_80GB", number_of_accelerators_per_model_instance=4, default=True),
        AcceleratorMap(accelerator_type="H200_141GB", number_of_accelerators_per_model_instance=2),
    ],
)
ml_client.deployment_templates.create_or_update(dt)

# Create Model with allowed DTs
model = Model(
    name="model1", version="1", path="models/", type="custom_model",
    default_deployment_template=DefaultDeploymentTemplate(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/labels/latest"),
    allowed_deployment_templates=[
        DefaultDeploymentTemplate(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/labels/latest"),
        DefaultDeploymentTemplate(asset_id="azureml://registries/reg1/deploymenttemplates/dt2/labels/latest"),
    ],
)
ml_client.models.create_or_update(model)
```

---

## 3. Consumer – `azure-mgmt-cognitiveservices`

This is an **autorest-generated** SDK. Changes come from swagger regeneration, not manual edits.

### 3.1 What Already Works (No SDK Changes Needed)

| Feature | Why |
|---------|-----|
| `DeploymentModel.format` optional | Already defaults to `None` |
| `Sku.name = "GlobalManagedCompute"` | `name` is free-form `str`, accepts any value |

### 3.2 Needs RP Confirmation (Blocked on CogSvc RP Swagger)

`DeploymentModel.source` field exists as a free-form `str`, but its docstring says **"Deployment model source ARM resource ID"** — it was designed for ARM IDs, not `azureml://` registry URIs. The CogSvc RP must confirm it will accept `azureml://` URIs in this field (or introduce a new field like `model_id`).

| Field | Current state | What's needed | CLI param |
|-------|--------------|---------------|----------|
| `DeploymentModel.source` | Exists — documented for ARM resource IDs only | RP must accept `azureml://` URIs | `--model-id` |
| `DeploymentProperties.deployment_template` | **Does not exist** | New field | `--deployment-template` |
| `DeploymentProperties.accelerator_type` | **Does not exist** | New field | `--accelerator-type` |

**Action:** Regenerate SDK after CogSvc RP publishes updated swagger. No manual SDK code changes — all fields come from autorest.
- If possible, also add validation of globalmanagedcompute sku

### 3.3 SDK Usage (After Regen)

```python
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Deployment, DeploymentProperties, DeploymentModel, Sku

client = CognitiveServicesManagementClient(credential, subscription_id)
client.deployments.begin_create_or_update("rg1", "account1", "dep1", Deployment(
    properties=DeploymentProperties(
        model=DeploymentModel(source="azureml://registries/reg1/models/model1/versions/1"),
        deployment_template="azureml://registries/reg1/deploymenttemplates/dt1/versions/1",
        accelerator_type="A100_80GB",
    ),
    sku=Sku(name="GlobalManagedCompute", capacity=4),
))
```

---

## 4. Dependency Chain

```
MRS RP swagger ──► azure-ai-ml (manual) ──► az ml CLI (version bump)
CogSvc RP swagger ──► azure-mgmt-cognitiveservices (autorest regen) ──► az cognitiveservices CLI (3 files)
```

## 6. Open Items

| Item | Owner | Blocking? |
|------|-------|-----------|
| MRS swagger: `acceleratorMaps` on DT | Anthony / MRS | Yes |
| MRS swagger: `allowedDeploymentTemplates` on Model | Anthony / MRS | Yes |
| CogSvc swagger: `deploymentTemplate` + `acceleratorType` | Chunyu / CogSvc | Yes |
| CogSvc: confirm `DeploymentModel.source` accepts `azureml://` URIs (or new field needed) | Chunyu / CogSvc | Yes |
