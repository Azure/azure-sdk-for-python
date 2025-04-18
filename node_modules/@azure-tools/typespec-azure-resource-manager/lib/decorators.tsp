using Reflection;

namespace Azure.ResourceManager;

/**
 * `@armProviderNamespace` sets the Azure Resource Manager provider name. It will default to use the
 * Namespace element value unless an override value is specified.
 *
 * @example
 *
 * ```typespec
 * @armProviderNamespace
 *  namespace Microsoft.Contoso;
 * ```
 *
 * ```typespec
 * @armProviderNamespace("Microsoft.Contoso")
 *  namespace Microsoft.ContosoService;
 * ```
 *
 * @param providerNamespace Provider namespace
 * @param libraryNamespaces a library namespace containing types for this namespace
 *
 */
extern dec armProviderNamespace(target: Namespace, providerNamespace?: valueof string);

/**
 * Declare the Azure Resource Manager library namespaces used in this provider.
 * This allows sharing Azure Resource Manager resource types across specifications
 * @param namespaces The namespaces of Azure Resource Manager libraries used in this provider
 */
extern dec useLibraryNamespace(target: Namespace, ...namespaces: Namespace[]);

/**
 * `@armLibraryNamespace` designates a namespace as containign Azure Resource Manager Provider information.
 *
 * @example
 *
 * ```typespec
 * @armLibraryNamespace
 *  namespace Microsoft.Contoso;
 * ```
 *
 */
extern dec armLibraryNamespace(target: Namespace);

/**
 * `@singleton` marks an Azure Resource Manager resource model as a singleton resource.
 *
 * Singleton resources only have a single instance with a fixed key name.
 *  `.../providers/Microsoft.Contoso/monthlyReports/default`
 *
 * See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)
 *
 * @param keyValue The name of the singleton resource. Default name is "default".
 */
extern dec singleton(target: Model, keyValue?: valueof string | "default");

/**
 * `@tenantResource` marks an Azure Resource Manager resource model as a Tenant resource/Root resource/Top-Level resource.
 *
 * Tenant resources have REST API paths like:
 *   `/provider/Microsoft.Contoso/FooResources`
 *
 * See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)
 */
extern dec tenantResource(target: Model);

/**
 * `@subscriptionResource` marks an Azure Resource Manager resource model as a subscription resource.
 *
 * Subscription resources have REST API paths like:
 *  `/subscription/{id}/providers/Microsoft.Contoso/employees`
 *
 * See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)
 */
extern dec subscriptionResource(target: Model);

/**
 * `@locationResource` marks an Azure Resource Manager resource model as a location based resource.
 *
 * Location based resources have REST API paths like
 *   `/subscriptions/{subscriptionId}/locations/{location}/providers/Microsoft.Contoso/employees`
 *
 * See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)
 */
extern dec locationResource(target: Model);

/**
 * `@resourceGroupResource` marks an Azure Resource Manager resource model as a resource group level resource.
 * This is the default option for Azure Resource Manager resources. It is provided for symmetry and clarity, and
 * you typically do not need to specify it.
 *
 *   `/subscription/{id}/resourcegroups/{rg}/providers/Microsoft.Contoso/employees`
 *
 * See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)
 */
extern dec resourceGroupResource(target: Model);

/**
 * `@extensionResource` marks an Azure Resource Manager resource model as an Extension resource.
 * Extension resource extends other resource types. URL path is appended
 * to another segment {scope} which refers to another Resource URL.
 *
 *   `{resourceUri}/providers/Microsoft.Contoso/accessPermissions`
 *
 * See more details on [different Azure Resource Manager resource type here.](https://azure.github.io/typespec-azure/docs/howtos/ARM/resource-type)
 */
extern dec extensionResource(target: Model);

/**
 * `@armResourceType` sets the value fo the decorated string
 * property to the type of the Azure Resource Manager resource.
 * @param resource The resource to get the type of
 */
extern dec armProviderNameValue(target: Operation);

/**
 * Marks the operation as being a collection action
 */
extern dec armResourceCollectionAction(target: Operation);

/**
 * @param resourceType Resource model
 */
extern dec armResourceAction(target: Operation, resourceType: Model);

/**
 * @param resourceType Resource model
 */
extern dec armResourceCreateOrUpdate(target: Operation, resourceType: Model);

/**
 * @param resourceType Resource model
 */
extern dec armResourceRead(target: Operation, resourceType: Model);

/**
 * @param resourceType Resource model
 */
extern dec armResourceUpdate(target: Operation, resourceType: Model);

/**
 * @param resourceType Resource model
 */
extern dec armResourceDelete(target: Operation, resourceType: Model);

/**
 * @param resourceType Resource model
 */
extern dec armResourceList(target: Operation, resourceType: Model);

/**
 * This decorator is used to identify interfaces containing resource operations.
 * When applied, it marks the interface with the `@autoRoute` decorator so that
 * all of its contained operations will have their routes generated
 * automatically.
 *
 * It also adds a `@tag` decorator bearing the name of the interface so that all
 * of the operations will be grouped based on the interface name in generated
 * clients.
 * @param _ DEPRECATED
 */
extern dec armResourceOperations(target: Interface, _?: unknown);

/**
 * This decorator is used either on a namespace or a version enum value to indicate
 * the version of the Azure Resource Manager common-types to use for refs in emitted Swagger files.
 *
 * @param version The Azure.ResourceManager.CommonTypes.Versions for the desired common-types version or an equivalent string value like "v5".
 */
extern dec armCommonTypesVersion(
  target: Namespace | EnumMember,
  version: valueof string | EnumMember
);

/**
 * This decorator is used on Azure Resource Manager resources that are not based on
 * Azure.ResourceManager common types.
 *
 * @param propertiesType: The type of the resource properties.
 */
extern dec armVirtualResource(target: Model);

/**
 * This decorator sets the base type of the given resource.
 *
 * @param baseType The built-in parent of the resource, this can be "Tenant", "Subscription", "ResourceGroup", "Location", or "Extension"
 */
extern dec resourceBaseType(
  target: Model,
  baseType: "Tenant" | "Subscription" | "ResourceGroup" | "Location" | "Extension"
);

/**
 * This decorator is used to indicate the identifying properties of objects in the array, e.g. size
 * The properties that are used as identifiers for the object needs to be provided as a list of strings.
 *
 * @param properties The list of properties that are used as identifiers for the object. This needs to be provided as a list of strings.
 *
 * @example
 * ```typespec
 * model Pet {
 *  @identifiers(#["size"])
 *  dog: Dog;
 * }
 * ```
 */
extern dec identifiers(entity: ModelProperty, properties: valueof string[]);
