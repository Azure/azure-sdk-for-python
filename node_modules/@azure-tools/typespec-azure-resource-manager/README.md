# @azure-tools/typespec-azure-resource-manager

TypeSpec Azure Resource Manager library

## Install

```bash
npm install @azure-tools/typespec-azure-resource-manager
```

## Usage

Add the following in `tspconfig.yaml`:

```yaml
linter:
  extends:
    - "@azure-tools/typespec-azure-resource-manager/all"
```

## RuleSets

Available ruleSets:

- `@azure-tools/typespec-azure-resource-manager/all`

## Rules

| Name                                                                                                                                                                                                     | Description                                                                                                                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`@azure-tools/typespec-azure-resource-manager/arm-no-record`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/arm-no-record)                                         | Don't use Record types for ARM resources.                                                                                                                                                                                                             |
| `@azure-tools/typespec-azure-resource-manager/arm-common-types-version`                                                                                                                                  | Specify the ARM common-types version using @armCommonTypesVersion.                                                                                                                                                                                    |
| [`@azure-tools/typespec-azure-resource-manager/arm-delete-operation-response-codes`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/delete-operation-response-codes) | Ensure delete operations have the appropriate status codes.                                                                                                                                                                                           |
| [`@azure-tools/typespec-azure-resource-manager/arm-put-operation-response-codes`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/put-operation-response-codes)       | Ensure put operations have the appropriate status codes.                                                                                                                                                                                              |
| [`@azure-tools/typespec-azure-resource-manager/arm-post-operation-response-codes`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/post-operation-response-codes)     | Ensure post operations have the appropriate status codes.                                                                                                                                                                                             |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-action-no-segment`                                                                                                                            | `@armResourceAction` should not be used with `@segment`.                                                                                                                                                                                              |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-duplicate-property`                                                                                                                           | Warn about duplicate properties in resources.                                                                                                                                                                                                         |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-invalid-envelope-property`                                                                                                                    | Check for invalid resource envelope properties.                                                                                                                                                                                                       |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-invalid-version-format`                                                                                                                       | Check for valid versions.                                                                                                                                                                                                                             |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-key-invalid-chars`                                                                                                                            | Arm resource key must contain only alphanumeric characters.                                                                                                                                                                                           |
| [`@azure-tools/typespec-azure-resource-manager/arm-resource-name-pattern`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/resource-name-pattern)                     | The resource name parameter should be defined with a 'pattern' restriction.                                                                                                                                                                           |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-operation-response`                                                                                                                           | [RPC 008]: PUT, GET, PATCH & LIST must return the same resource schema.                                                                                                                                                                               |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-path-segment-invalid-chars`                                                                                                                   | Arm resource name must contain only alphanumeric characters.                                                                                                                                                                                          |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-provisioning-state`                                                                                                                           | Check for properly configured provisioningState property.                                                                                                                                                                                             |
| `@azure-tools/typespec-azure-resource-manager/arm-custom-resource-usage-discourage`                                                                                                                      | Verify the usage of @customAzureResource decorator.                                                                                                                                                                                                   |
| `@azure-tools/typespec-azure-resource-manager/beyond-nesting-levels`                                                                                                                                     | Tracked Resources must use 3 or fewer levels of nesting.                                                                                                                                                                                              |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-operation`                                                                                                                                    | Validate ARM Resource operations.                                                                                                                                                                                                                     |
| `@azure-tools/typespec-azure-resource-manager/no-resource-delete-operation`                                                                                                                              | Check for resources that must have a delete operation.                                                                                                                                                                                                |
| `@azure-tools/typespec-azure-resource-manager/empty-updateable-properties`                                                                                                                               | Should have updateable properties.                                                                                                                                                                                                                    |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-interface-requires-decorator`                                                                                                                 | Each resource interface must have an @armResourceOperations decorator.                                                                                                                                                                                |
| [`@azure-tools/typespec-azure-resource-manager/arm-resource-invalid-action-verb`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/arm-resource-invalid-action-verb)   | Actions must be HTTP Post or Get operations.                                                                                                                                                                                                          |
| `@azure-tools/typespec-azure-resource-manager/improper-subscription-list-operation`                                                                                                                      | Tenant and Extension resources should not define a list by subscription operation.                                                                                                                                                                    |
| [`@azure-tools/typespec-azure-resource-manager/lro-location-header`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/lro-location-header)                             | A 202 response should include a Location response header.                                                                                                                                                                                             |
| [`@azure-tools/typespec-azure-resource-manager/missing-x-ms-identifiers`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/missing-x-ms-identifiers)                   | Array properties should describe their identifying properties with x-ms-identifiers. Decorate the property with @OpenAPI.extension("x-ms-identifiers", #[id-prop]) where "id-prop" is a list of the names of identifying properties in the item type. |
| [`@azure-tools/typespec-azure-resource-manager/no-response-body`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/no-response-body)                                   | Check that the body is empty for 202 and 204 responses, and not empty for other success (2xx) responses.                                                                                                                                              |
| `@azure-tools/typespec-azure-resource-manager/missing-operations-endpoint`                                                                                                                               | Check for missing Operations interface.                                                                                                                                                                                                               |
| `@azure-tools/typespec-azure-resource-manager/patch-envelope`                                                                                                                                            | Patch envelope properties should match the resource properties.                                                                                                                                                                                       |
| `@azure-tools/typespec-azure-resource-manager/arm-resource-patch`                                                                                                                                        | Validate ARM PATCH operations.                                                                                                                                                                                                                        |
| `@azure-tools/typespec-azure-resource-manager/resource-name`                                                                                                                                             | Check the resource name.                                                                                                                                                                                                                              |
| `@azure-tools/typespec-azure-resource-manager/retry-after`                                                                                                                                               | Check if retry-after header appears in response body.                                                                                                                                                                                                 |
| [`@azure-tools/typespec-azure-resource-manager/unsupported-type`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/unsupported-type)                                   | Check for unsupported ARM types.                                                                                                                                                                                                                      |
| [`@azure-tools/typespec-azure-resource-manager/no-empty-model`](https://azure.github.io/typespec-azure/docs/libraries/azure-resource-manager/rules/no-empty-model)                                       | ARM Properties with type:object that don't reference a model definition are not allowed. ARM doesn't allow generic type definitions as this leads to bad customer experience.                                                                         |

## Decorators

### Azure.ResourceManager

- [`@armCommonTypesVersion`](#@armcommontypesversion)
- [`@armLibraryNamespace`](#@armlibrarynamespace)
- [`@armProviderNamespace`](#@armprovidernamespace)
- [`@armProviderNameValue`](#@armprovidernamevalue)
- [`@armResourceAction`](#@armresourceaction)
- [`@armResourceCollectionAction`](#@armresourcecollectionaction)
- [`@armResourceCreateOrUpdate`](#@armresourcecreateorupdate)
- [`@armResourceDelete`](#@armresourcedelete)
- [`@armResourceList`](#@armresourcelist)
- [`@armResourceOperations`](#@armresourceoperations)
- [`@armResourceRead`](#@armresourceread)
- [`@armResourceUpdate`](#@armresourceupdate)
- [`@armVirtualResource`](#@armvirtualresource)
- [`@extensionResource`](#@extensionresource)
- [`@identifiers`](#@identifiers)
- [`@locationResource`](#@locationresource)
- [`@resourceBaseType`](#@resourcebasetype)
- [`@resourceGroupResource`](#@resourcegroupresource)
- [`@singleton`](#@singleton)
- [`@subscriptionResource`](#@subscriptionresource)
- [`@tenantResource`](#@tenantresource)
- [`@useLibraryNamespace`](#@uselibrarynamespace)

#### `@armCommonTypesVersion`

This decorator is used either on a namespace or a version enum value to indicate
the version of the Azure Resource Manager common-types to use for refs in emitted Swagger files.

```typespec
@Azure.ResourceManager.armCommonTypesVersion(version: valueof string | EnumMember)
```

##### Target

`Namespace | EnumMember`

##### Parameters

| Name    | Type                           | Description                                                                                                                  |
| ------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| version | `valueof string \| EnumMember` | The Azure.ResourceManager.CommonTypes.Versions for the desired common-types version or an equivalent string value like "v5". |

#### `@armLibraryNamespace`

`@armLibraryNamespace` designates a namespace as containign Azure Resource Manager Provider information.

```typespec
@Azure.ResourceManager.armLibraryNamespace
```

##### Target

`Namespace`

##### Parameters

None

##### Examples

```typespec
@armLibraryNamespace
namespace Microsoft.Contoso;
```

#### `@armProviderNamespace`

`@armProviderNamespace` sets the Azure Resource Manager provider name. It will default to use the
Namespace element value unless an override value is specified.

```typespec
@Azure.ResourceManager.armProviderNamespace(providerNamespace?: valueof string)
```

##### Target

`Namespace`

##### Parameters

| Name              | Type             | Description        |
| ----------------- | ---------------- | ------------------ |
| providerNamespace | `valueof string` | Provider namespace |

##### Examples

```typespec
@armProviderNamespace
namespace Microsoft.Contoso;
```

```typespec
@armProviderNamespace("Microsoft.Contoso")
namespace Microsoft.ContosoService;
```

#### `@armProviderNameValue`

`@armResourceType` sets the value fo the decorated string
property to the type of the Azure Resource Manager resource.

```typespec
@Azure.ResourceManager.armProviderNameValue
```

##### Target

`Operation`

##### Parameters

None

#### `@armResourceAction`

```typespec
@Azure.ResourceManager.armResourceAction(resourceType: Model)
```

##### Target

`Operation`

##### Parameters

| Name         | Type    | Description    |
| ------------ | ------- | -------------- |
| resourceType | `Model` | Resource model |

#### `@armResourceCollectionAction`

Marks the operation as being a collection action

```typespec
@Azure.ResourceManager.armResourceCollectionAction
```

##### Target

`Operation`

##### Parameters

None

#### `@armResourceCreateOrUpdate`

```typespec
@Azure.ResourceManager.armResourceCreateOrUpdate(resourceType: Model)
```

##### Target

`Operation`

##### Parameters

| Name         | Type    | Description    |
| ------------ | ------- | -------------- |
| resourceType | `Model` | Resource model |

#### `@armResourceDelete`

```typespec
@Azure.ResourceManager.armResourceDelete(resourceType: Model)
```

##### Target

`Operation`

##### Parameters

| Name         | Type    | Description    |
| ------------ | ------- | -------------- |
| resourceType | `Model` | Resource model |

#### `@armResourceList`

```typespec
@Azure.ResourceManager.armResourceList(resourceType: Model)
```

##### Target

`Operation`

##### Parameters

| Name         | Type    | Description    |
| ------------ | ------- | -------------- |
| resourceType | `Model` | Resource model |

#### `@armResourceOperations`

This decorator is used to identify interfaces containing resource operations.
When applied, it marks the interface with the `@autoRoute` decorator so that
all of its contained operations will have their routes generated
automatically.

It also adds a `@tag` decorator bearing the name of the interface so that all
of the operations will be grouped based on the interface name in generated
clients.

```typespec
@Azure.ResourceManager.armResourceOperations(_?: unknown)
```

##### Target

`Interface`

##### Parameters

| Name | Type      | Description |
| ---- | --------- | ----------- |
| \_   | `unknown` | DEPRECATED  |

#### `@armResourceRead`

```typespec
@Azure.ResourceManager.armResourceRead(resourceType: Model)
```

##### Target

`Operation`

##### Parameters

| Name         | Type    | Description    |
| ------------ | ------- | -------------- |
| resourceType | `Model` | Resource model |

#### `@armResourceUpdate`

```typespec
@Azure.ResourceManager.armResourceUpdate(resourceType: Model)
```

##### Target

`Operation`

##### Parameters

| Name         | Type    | Description    |
| ------------ | ------- | -------------- |
| resourceType | `Model` | Resource model |

#### `@armVirtualResource`

This decorator is used on Azure Resource Manager resources that are not based on
Azure.ResourceManager common types.

```typespec
@Azure.ResourceManager.armVirtualResource
```

##### Target

`Model`

##### Parameters

None

#### `@extensionResource`

`@extensionResource` marks an Azure Resource Manager resource model as an Extension resource.
Extension resource extends other resource types. URL path is appended
to another segment {scope} which refers to another Resource URL.

`{resourceUri}/providers/Microsoft.Contoso/accessPermissions`

See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)

```typespec
@Azure.ResourceManager.extensionResource
```

##### Target

`Model`

##### Parameters

None

#### `@identifiers`

This decorator is used to indicate the identifying properties of objects in the array, e.g. size
The properties that are used as identifiers for the object needs to be provided as a list of strings.

```typespec
@Azure.ResourceManager.identifiers(properties: valueof string[])
```

##### Target

`ModelProperty`

##### Parameters

| Name       | Type               | Description                                                                                                         |
| ---------- | ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| properties | `valueof string[]` | The list of properties that are used as identifiers for the object. This needs to be provided as a list of strings. |

##### Examples

```typespec
model Pet {
  @identifiers(#["size"])
  dog: Dog;
}
```

#### `@locationResource`

`@locationResource` marks an Azure Resource Manager resource model as a location based resource.

Location based resources have REST API paths like
`/subscriptions/{subscriptionId}/locations/{location}/providers/Microsoft.Contoso/employees`

See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)

```typespec
@Azure.ResourceManager.locationResource
```

##### Target

`Model`

##### Parameters

None

#### `@resourceBaseType`

This decorator sets the base type of the given resource.

```typespec
@Azure.ResourceManager.resourceBaseType(baseType: "Tenant" | "Subscription" | "ResourceGroup" | "Location" | "Extension")
```

##### Target

`Model`

##### Parameters

| Name     | Type                                                                         | Description                                                                                                            |
| -------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| baseType | `"Tenant" \| "Subscription" \| "ResourceGroup" \| "Location" \| "Extension"` | The built-in parent of the resource, this can be "Tenant", "Subscription", "ResourceGroup", "Location", or "Extension" |

#### `@resourceGroupResource`

`@resourceGroupResource` marks an Azure Resource Manager resource model as a resource group level resource.
This is the default option for Azure Resource Manager resources. It is provided for symmetry and clarity, and
you typically do not need to specify it.

`/subscription/{id}/resourcegroups/{rg}/providers/Microsoft.Contoso/employees`

See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)

```typespec
@Azure.ResourceManager.resourceGroupResource
```

##### Target

`Model`

##### Parameters

None

#### `@singleton`

`@singleton` marks an Azure Resource Manager resource model as a singleton resource.

Singleton resources only have a single instance with a fixed key name.
`.../providers/Microsoft.Contoso/monthlyReports/default`

See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)

```typespec
@Azure.ResourceManager.singleton(keyValue?: valueof string | "default")
```

##### Target

`Model`

##### Parameters

| Name     | Type                          | Description                                                    |
| -------- | ----------------------------- | -------------------------------------------------------------- |
| keyValue | `valueof string \| "default"` | The name of the singleton resource. Default name is "default". |

#### `@subscriptionResource`

`@subscriptionResource` marks an Azure Resource Manager resource model as a subscription resource.

Subscription resources have REST API paths like:
`/subscription/{id}/providers/Microsoft.Contoso/employees`

See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)

```typespec
@Azure.ResourceManager.subscriptionResource
```

##### Target

`Model`

##### Parameters

None

#### `@tenantResource`

`@tenantResource` marks an Azure Resource Manager resource model as a Tenant resource/Root resource/Top-Level resource.

Tenant resources have REST API paths like:
`/provider/Microsoft.Contoso/FooResources`

See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)

```typespec
@Azure.ResourceManager.tenantResource
```

##### Target

`Model`

##### Parameters

None

#### `@useLibraryNamespace`

Declare the Azure Resource Manager library namespaces used in this provider.
This allows sharing Azure Resource Manager resource types across specifications

```typespec
@Azure.ResourceManager.useLibraryNamespace(...namespaces: Namespace[])
```

##### Target

`Namespace`

##### Parameters

| Name       | Type          | Description                                                              |
| ---------- | ------------- | ------------------------------------------------------------------------ |
| namespaces | `Namespace[]` | The namespaces of Azure Resource Manager libraries used in this provider |

### Azure.ResourceManager.Legacy

- [`@customAzureResource`](#@customazureresource)
- [`@externalTypeRef`](#@externaltyperef)

#### `@customAzureResource`

This decorator is used on resources that do not satisfy the definition of a resource
but need to be identified as such.

```typespec
@Azure.ResourceManager.Legacy.customAzureResource
```

##### Target

`Model`

##### Parameters

None

#### `@externalTypeRef`

Specify an external reference that should be used when emitting this type.

```typespec
@Azure.ResourceManager.Legacy.externalTypeRef(jsonRef: valueof string)
```

##### Target

`Model | ModelProperty`

##### Parameters

| Name    | Type             | Description                                                   |
| ------- | ---------------- | ------------------------------------------------------------- |
| jsonRef | `valueof string` | External reference(e.g. "../../common.json#/definitions/Foo") |
