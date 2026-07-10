# Azure Python SDK Breaking Changes Review and Resolution Guide for TypeSpec Migration

The Azure Python SDK generally prohibits breaking changes unless they result from service behavior modifications. This guide helps you identify, review, and resolve breaking changes that may occur in new SDK versions due to migration of service specifications from Swagger to TypeSpec.

Breaking changes can be resolved by:

1. Client Customizations

Client customizations should be implemented in a file named `client.tsp` located in the service's specification directory alongside the main entry point `main.tsp`. This `client.tsp` becomes the new specification entry point, so import `main.tsp` in the `client.tsp` file. **Do not** import `client.tsp` in the `main.tsp` file.

```tsp
import "./main.tsp";
import "@azure-tools/typespec-client-generator-core";

using Azure.ClientGenerator.Core;

// Add your customizations here
```

2. TypeSpec Configuration Changes

TypeSpec configuration changes should be made in the `tspconfig.yaml` file located in the service's specification directory. This file is used to configure the TypeSpec compiler and client generator options. For example:

```yaml
options:
  "@azure-tools/typespec-python":
```

## 1. Naming Changes with Numbers

**Changelog Pattern**:

Paired removal and addition entries showing naming changes from words to numbers:

```md
- Enum `Minute` deleted or renamed its member `ZERO`
- Enum `Minute` deleted or renamed its member `THIRTY`
- Enum `Minute` added member `ENUM_0`
- Enum `Minute` added member `ENUM_30`
```

**Spec Pattern**:

Find the type definition by examining the names from the addition entries in the changelog (pattern: `Enum '<type name>' added member xxx`):

```tsp
union Minute {
  int32,
  `0`: 0,
  `30`: 30,
}
```

**Breaking**: Enum members are renamed (e.g. `ZERO` becomes `ENUM_0`, `THIRTY` becomes `ENUM_30`), so existing code referencing the old members breaks.

**Reason**: Emitter change. The Swagger emitter automatically converts numeric names to words during code generation, while the TypeSpec emitter preserves the original naming. This affects all type names, including enums, models, and operations.

**Resolution**:

Use client customization to restore the original names from the removal entries:

```tsp
@@clientName(Minute.`0`, "ZERO", "python");
@@clientName(Minute.`30`, "THIRTY", "python");
```

## 2. Operation Naming Changes

**Changelog Pattern**:

Removal of an operation and addition of a similarly named operation for the same operation group:

```md
- Added operation StorageTaskAssignmentOperations.storage_task_assignment_list
- Removed operation StorageTaskAssignmentOperations.list
```

**Spec Pattern**:

Locate the interface and operation using the name from the addition entries.

```tsp
interface StorageTaskAssignment {
  op storageTaskAssignmentList(xxx): xxx;
}
```

**Breaking**: An operation method is renamed (e.g. `list` becomes `storage_task_assignment_list`), so existing calls to the old method name break.

**Reason**: Emitter change. The TypeSpec emitter may generate different operation names than Swagger to avoid naming collisions.

**Resolution**:

Use client naming to restore the original operation name from the removal entries:

```tsp
@@clientName(StorageTaskAssignment.storageTaskAssignmentList, "list", "python");
```

## 3. Naming Changes from Directive

**Changelog Pattern**:

Paired removal and addition entries showing naming changes for structs:

```md
- Added model `RedisResource`
- Deleted or renamed model `ResourceInfo`
```

Also, in the legacy config for swagger under the spec folder: `specification/<service>/resource-manager/readme.python.md`, the renaming directives could be found:

```md
directive:

- rename-model:
  from: 'RedisResource'
  to: 'ResourceInfo'
```

**Spec Pattern**:

Find the type definition by examining the names from the addition entries in the changelog (pattern: `Added model '<type name>'`):

```tsp
model RedisResource {
  ...
}
```

**Breaking**: A model is renamed (e.g. `ResourceInfo` becomes `RedisResource`), so existing code referencing the old model name breaks.

**Reason**: Spec directive. Swagger applied a `rename-model` directive in the legacy `readme.python.md` config; TypeSpec uses the original spec name unless the same rename is re-applied.

**Resolution**:

Use client customization to do the same renaming as the directives in the legacy config:

```tsp
@@clientName(RedisResource, "ResourceInfo", "python");
```

## 4. Client Naming Changes

**Changelog Pattern**:

Removal entry showing naming change of the client:

```md
- Deleted or renamed client `IotDpsClient`
```

**Spec Pattern**:

Find the name from namespace:

```tsp
@service(#{ title: "iotDpsClient" })
namespace Microsoft.Devices;
```

**Breaking**: The client class is renamed (e.g. `IotDpsClient` is removed), so existing code constructing the old client breaks.

**Reason**: Naming convention difference. TypeSpec generates client names based on the `namespace` name rather than the title annotation in the `@service` decorator.

**Resolution**:

Update it to the correct client name using `@@clientName`:

```tsp
@@clientName(Microsoft.Devices, "IotDpsClient", "python");
```

## 5. Reorder of Parameters

**Changelog Pattern**:

Entry showing the parameters get re-ordered for an operation:

```md
- Method `IotDpsResourceOperations.get` re-ordered its parameters from `['self', 'provisioning_service_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'provisioning_service_name', 'kwargs']`
```

**Spec Pattern**:

Operation extends parameters from type `ProvisioningServiceDescription`:

```tsp
@armResourceOperations
interface ProvisioningServiceDescriptions {
  get is ArmResourceRead<ProvisioningServiceDescription, Error = ErrorDetails>;
}
```

**Breaking**: The positional order of method parameters changes, so existing positional calls bind arguments to the wrong parameters.

**Reason**: Operation design change. TypeSpec generally uses generics to generate operations. A unified parameter order is widely shared within an operation group and may differ from what is defined in Swagger.

**Resolution**:

Override the operation by a customized one with a manually designed order of parameters:

```tsp
op IotDpsResourceGetCustomized(
  @path
  provider: "Microsoft.ThisWillBeReplaced",

  @path
  provisioningServiceName: string,

  ...Azure.ResourceManager.CommonTypes.ResourceGroupNameParameter,
): ProvisioningServiceDescription;

@@override(ProvisioningServiceDescriptions.get,
  IotDpsResourceGetCustomized,
  "python"
);
```

## 6. Common Types Upgrade

**Changelog Pattern**:

Multiple changes related to common infrastructure types such as `SystemData` and `IdentityType`:

```md
- Deleted or renamed model `IdentityType`
```

**Breaking**: A common infrastructure type is renamed or removed, so code referencing the old type breaks.

**Reason**: Common types upgrade. Common types are upgraded to their latest versions during TypeSpec migration.

**Impact**: Low impact since these are common infrastructure types rarely used directly by users.

**Resolution**: Accept these breaking changes.

## 7. Removal of Unreferenced Models

**Changelog Pattern**:

Multiple removals of unreferenced models that are typically not used in the SDK:

```md
- Deleted or renamed model `ProxyResourceWithoutSystemData`
- Deleted or renamed model `Resource`
```

**Breaking**: Unreferenced models are removed from the SDK, so code referencing them breaks.

**Reason**: Spec structure change. Unreferenced models are removed during TypeSpec migration.

**Impact**: Low impact since these models are typically not used directly by users.

**Resolution**: Accept these breaking changes.

## 8. Removal of Pageable Models

**Changelog Pattern**:

Multiple removals of pageable models. A pageable model is a response wrapper for a list/paging operation whose only properties are `value`, or `next_link` plus `value`. Their names usually end with `List` but not always — verify by checking the model definition in `_models.py` or `_models_py3.py`.

```md
- Deleted or renamed model `ElasticSanList`
- Deleted or renamed model `SkuInformationList`
- Deleted or renamed model `SnapshotList`
- Deleted or renamed model `VolumeGroupList`
- Deleted or renamed model `VolumeList`
```

**Breaking**: Pageable wrapper models are no longer generated, so code referencing them breaks.

**Reason**: Emitter change. Python will not expose pageable models for list APIs.

**Impact**: Low impact since these models are typically not used directly by users.

**Resolution**: Accept these breaking changes.

## 9. Parameters Changed to Keyword-only

**Changelog Pattern**:

Entries showing the usage of passing parameters positionally is disabled:

```md
- Method `DpsCertificateOperations.delete` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
```

**Breaking**: Query and header parameters can no longer be passed positionally, so existing positional calls break.

**Reason**: Operation design change. Query and header parameters in operation methods have been changed from positional to keyword-only by the new operation design.

**Impact**: Users should convert all positional parameters to keyword arguments

**Resolution**: Accept these breaking changes.

## 10. Removal of Parameter `if_match`

**Changelog Pattern**:

Removal of parameter `if_match` and addition of `etag/match_condition` for the same operation:

```md
- Model `DpsCertificateOperations` added parameter `etag` in method `create_or_update`
- Model `DpsCertificateOperations` added parameter `match_condition` in method `create_or_update`
- Method `DpsCertificateOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
```

**Breaking**: The parameter `if_match` is removed and replaced by `etag`/`match_condition`, so existing calls passing `if_match` break.

**Reason**: Operation design change. The header signatures `if_match`/`if_none_match` are replaced by `etag`/`match_condition` by the new operation design.

**Impact**: Replace `if_match="<specific etag>"` with `etag="<specific etag>", match_condition=MatchConditions.IfNotModified`.

**Resolution**: Accept these breaking changes.

## 11. Removal of multi-level flattened properties

**Changelog Pattern**:

Removal of multiple parameters and addition of parameters `properties` entries for the same model:

```md
- Model `VaultExtendedInfoResource` added property `properties`
- Model `VaultExtendedInfoResource` deleted or renamed its instance variable `integrity_key`
- Model `VaultExtendedInfoResource` deleted or renamed its instance variable `encryption_key`
- Model `VaultExtendedInfoResource` deleted or renamed its instance variable `encryption_key_thumbprint`
- Model `VaultExtendedInfoResource` deleted or renamed its instance variable `algorithm`
```

**Breaking**: Flattened convenience properties are removed and replaced by a single `properties` property, so code accessing the flattened properties directly breaks.

**Reason**: Spec structure change. TypeSpec no longer supports multi-level flattening and will always preserve the actual REST API hierarchy. For more detailed information about model hierarchy, please refer to https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/hybrid_model_migration.md#model-hierarchy-reflects-rest-api-structure

**Impact**: Users can only get the property following the actual model structure which matches the REST API documentation.

**Resolution**: Accept these breaking changes.

## 12. Renaming of Properties That Conflict with Base Model Methods

**Changelog Pattern**:

Removal of a property and addition of a corresponding property with `_property` suffix:

```md
- Model `ExceptionEntry` deleted or renamed its instance variable `values`
- Model `ExceptionEntry` added property `values_property`
```

**Breaking**: A property is renamed with a `_property` suffix (e.g. `values` becomes `values_property`), so existing code accessing the original property name breaks.

**Reason**: Emitter change. In the base model class of TypeSpec-based SDKs, the following names are native method names: `keys`, `items`, `values`, `popitem`, `clear`, `update`, `setdefault`, `pop`, `get`, `copy`. To avoid name conflicts, properties using any of these names are automatically renamed with a `_property` suffix (e.g., `values` becomes `values_property`, `items` becomes `items_property`).

**Impact**: Users need to update property access to use the `_property` suffix (e.g., `.values` to `.values_property`, `.keys` to `.keys_property`, `.items` to `.items_property`).

**Resolution**: Accept these breaking changes.

## 13. Renamed Model or Enum

**Changelog Pattern**:

Entries showing a model or enum has been renamed:

```md
- Renamed model `OldModelName` to `NewModelName`
- Renamed enum `OldEnumName` to `NewEnumName`
```

**Spec Pattern**:

Find the type definition by examining the new name from the changelog entry:

```tsp
model NewModelName {
  ...
}

union NewEnumName {
  string,
  ...
}
```

**Breaking**: A model or enum is renamed (e.g. `OldModelName` becomes `NewModelName`), so existing code referencing the old name breaks.

**Reason**: Naming convention difference. TypeSpec may produce different model or enum names than Swagger (for example, due to namespace changes or naming convention differences).

**Resolution**:

Use `@clientName` to restore the original name from the removal entry:

```tsp
@@clientName(NewModelName, "OldModelName", "python");
@@clientName(NewEnumName, "OldEnumName", "python");
```

**Note**: Some renamed models are defined in common types (e.g., `Azure.ResourceManager.CommonTypes`) rather than the current service's TypeSpec. In that case, you may not find the type definition in the local spec — import the relevant library and reference the type by its fully qualified name. For example:

```tsp
import "@azure-tools/typespec-azure-resource-manager";
...

@@clientName(
  Azure.ResourceManager.CommonTypes.OperationDisplay,
  "OperationInfo",
  "python"
);
```
