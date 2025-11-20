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

**Reason**: Swagger automatically converts numeric names to words during code generation, while TypeSpec preserves the original naming. This affects all type names, including enums, models, and operations.

**Spec Pattern**:

Find the type definition by examining the names from the addition entries in the changelog (pattern: `Enum '<type name>' added member xxx`):

```tsp
union Minute {
  int32,
  `0`: 0,
  `30`: 30,
}
```

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

**Reason**: TypeSpec may generate different operation names than Swagger to avoid naming collisions.

**Spec Pattern**:

Locate the interface and operation using the name from the addition entries.

```tsp
interface StorageTaskAssignment {
  op storageTaskAssignmentList(xxx): xxx;
}
```

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

**Reason**: Swagger has directive ways to change the naming.

**Spec Pattern**:

Find the type definition by examining the names from the addition entries in the changelog (pattern: `Added model '<type name>'`):

```tsp
model RedisResource {
  ...
}
```

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

**Reason**: TypeSpec generates client names based on the `namespace` name rather than the title annotation in the `@service` decorator.

**Spec Pattern**:

Find the name from namespace:

```tsp
@service(#{ title: "iotDpsClient" })
namespace Microsoft.Devices;
```

**Resolution**:

Update it to the correct client name using `@@clientName`:

```tsp
@@clientName(Microsoft.Devices, "IotDpsClient", "python");
```

## 5. Reorder of Parameters

Entry showing the parameters get re-ordered for an operation:

```md
- Method `IotDpsResourceOperations.get` re-ordered its parameters from `['self', 'provisioning_service_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'provisioning_service_name', 'kwargs']`
```

**Reason**: TypeSpec generally uses generic to generate operations. An unified parameters' order will be widely shared in one operation group, and may make difference comparing to what defined in swagger.

**Spec Pattern**:

Operation extends parameters from type `ProvisioningServiceDescription`:

```tsp
@armResourceOperations
interface ProvisioningServiceDescriptions {
  get is ArmResourceRead<ProvisioningServiceDescription, Error = ErrorDetails>;
}
```

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

**Reason**: Common types are upgraded to their latest versions during TypeSpec migration.

**Impact**: Low impact since these are common infrastructure types rarely used directly by users.

**Resolution**: Accept these breaking changes.

## 7. Removal of Unreferenced Models

**Changelog Pattern**:

Multiple removals of unreferenced models that are typically not used in the SDK:

```md
- Deleted or renamed model `ProxyResourceWithoutSystemData`
- Deleted or renamed model `Resource`
```

**Reason**: Unreferenced models are removed during TypeSpec migration.

**Impact**: Low impact since these models are typically not used directly by users.

**Resolution**: Accept these breaking changes.

## 8. Removal of Pageable Models

**Changelog Pattern**:

Multiple removals of models following the pattern `xxxList`:

```md
- Deleted or renamed model `ElasticSanList`
- Deleted or renamed model `SkuInformationList`
- Deleted or renamed model `SnapshotList`
- Deleted or renamed model `VolumeGroupList`
- Deleted or renamed model `VolumeList`
```

**Reason**: Python will not expose pageable models for list APIs.

**Impact**: Low impact since these models are typically not used directly by users.

**Resolution**: Accept these breaking changes.

## 9. Parameters Changed to Keyword-only

**Changelog Pattern**:

Entries showing the usage of passing parameters positionally is disabled:

```md
- Method `DpsCertificateOperations.delete` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
```

**Reason**: Query and header parameters in operation methods have been changed from positional to keyword-only by the new operation design.

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

**Reason**: Header signatures `if_match/if_none_match` is replaced by `etag/match_condition` by the new operation design.

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

**Reason**: Typespec no longer supports multi-level flattening and will always preserve the actual REST API hierarchy. For more detailed information about model hierarchy, please refer to https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/hybrid_model_migration.md#model-hierarchy-reflects-rest-api-structure

**Impact**: Users can only get the property following the actual model structure which matches the REST API documentation.

**Resolution**: Accept these breaking changes.
