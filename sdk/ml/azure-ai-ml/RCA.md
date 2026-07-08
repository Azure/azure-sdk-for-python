# ICM 829788361 — `az ml datastore create` JSON serialization failure

## Summary

`az ml datastore create` fails with `TypeError: Object of type Datastore is not JSON serializable` on `az ml` extension **v2.44.0** (bundles `azure-ai-ml` **1.34.0**). It works on **v2.43.0** (`azure-ai-ml` **1.33.0**).

## Symptom

```text
ERROR: Met error <class 'TypeError'>: Object of type Datastore is not JSON serializable
```

Raised by the generated REST client at `json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)`.

## Root cause

PR #47349 (`azure-ai-ml` 1.34.0) switched the datastore **operation** to the TypeSpec client (`v2024_10_01_preview_tsp`, later renamed `arm_ml_service`). Its `SdkJSONEncoder` only serializes TypeSpec models. The datastore **entity** `_to_rest_object()` was **not** migrated — it still builds a legacy msrest model (`v2023_04_01_preview.models.Datastore`). `SdkJSONEncoder` sees a non-TypeSpec object (`_is_model()` is `False`), falls through to `json.JSONEncoder.default`, and raises `TypeError`. Still unfixed on `main`.

Key files:

- `sdk/ml/azure-ai-ml/azure/ai/ml/operations/_datastore_operations.py` — `create_or_update`
- `sdk/ml/azure-ai-ml/azure/ai/ml/entities/_datastore/azure_storage.py` — `_to_rest_object`
- `sdk/ml/azure-ai-ml/azure/ai/ml/_restclient/arm_ml_service/_utils/model_base.py` — `SdkJSONEncoder`

## Fix (Option A — minimal bridge)

Implement in **azure-sdk-for-python** (`azure-ai-ml`), **not** azure-cli-extensions. The `az ml` extension is a thin wrapper and only needs to bump its bundled `azure-ai-ml` to the fixed release.

In `_datastore_operations.py` `create_or_update`, pass the serialized wire dict instead of the msrest model (the TSP op accepts `Union[Datastore, JSON, IO[bytes]]`):

```python
ds_request = datastore._to_rest_object()
datastore_resource = self._operation.create_or_update(
    name=datastore.name,
    resource_group_name=self._operation_scope.resource_group_name,
    workspace_name=self._workspace_name,
    body=ds_request.serialize(),  # msrest model -> camelCase wire dict
    skip_validation=True,
)
```

## Validation

- Offline wire net: `sdk/ml/azure-ai-ml/tests/smoke_serialization/test_datastore_wire.py` — 6 cases pass today; must stay byte-identical after the change.
- Add before shipping: identity/None creds (customer case), certificate, on-prem; plus a `_from_rest_object()` round-trip.

## Workaround

Pin the extension: `az extension add --name ml --version 2.43.0`.
