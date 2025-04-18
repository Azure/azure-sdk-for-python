using Http;
using Rest;
using OpenAPI;
using Azure.ResourceManager.Foundations;
using Azure.ResourceManager.Private;
using Azure.ResourceManager.CommonTypes;
using Azure.ResourceManager.CommonTypes.Private;

namespace Azure.ResourceManager;

/**
 * The default api-version parameter type.
 */
alias ApiVersionParameter = CommonTypes.ApiVersionParameter;

/**
 * The default subscriptionId parameter type.
 */
alias SubscriptionIdParameter = CommonTypes.SubscriptionIdParameter;

/**
 * The default ResourceGroup parameter type.
 */
alias ResourceGroupParameter = CommonTypes.ResourceGroupNameParameter;

/**
 * The default LocationResource parameter type.
 */
alias LocationResourceParameter = CommonTypes.LocationResourceParameter;

/**
 * DEPRECATED - DO NOT USE
 * The default location parameter type.
 */
@doc("The default location parameter type.")
model LocationParameter {
  @path
  @minLength(1)
  @segment("locations")
  @doc("The location name.")
  @armCommonParameter("LocationParameter", Azure.ResourceManager.CommonTypes.Versions.v3)
  @armCommonParameter("LocationParameter", Azure.ResourceManager.CommonTypes.Versions.v4)
  @armCommonParameter("LocationParameter", Azure.ResourceManager.CommonTypes.Versions.v5)
  @resourceParameterBaseFor([ResourceHome.Location])
  location: string;
}

/**
 * The location resource for tenant-based locations.  This can be used as a parent
 * resource for resource types that are homed in a tenant-based location.
 */
model TenantLocationResource is ArmLocationResource<"Tenant">;

/**
 * The location resource for subscription-based locations.  This can be used as a parent
 * resource for resource types that are homed in a subscription-based location.
 */
model SubscriptionLocationResource is ArmLocationResource<"Subscription">;

/**
 * The location resource for resourceGroup-based locations.  This can be used as a parent
 * resource for resource types that are homed in a resourceGroup-based location.
 */
model ResourceGroupLocationResource is ArmLocationResource<"ResourceGroup">;

/**
 * Template for ARM location resources.  Use the parameter to specify
 */
@friendlyName("Location")
@armVirtualResource
@resourceBaseType(BaseType)
model ArmLocationResource<BaseType extends
  | "Tenant"
  | "Subscription"
  | "ResourceGroup"
  | "Location"
  | "Extension" = never> {
  ...LocationResourceParameter;
}

/**
 * The default resourceUri parameter type.
 */
@doc("The default resourceUri parameter type.")
model ResourceUriParameter {
  @path(#{ allowReserved: true })
  @doc("The fully qualified Azure Resource manager identifier of the resource.")
  @resourceParameterBaseFor([ResourceHome.Extension])
  resourceUri: string;
}

/**
 * The dynamic parameters of a resource instance - pass in the proper base type to indicate
 * where the resource is based.  The default is in a resource group
 * @template Resource The resource to get parameters for
 * @template BaseParameters The parameters representing the base Uri of the resource
 */
model ResourceInstanceParameters<
  Resource extends {},
  BaseParameters = DefaultBaseParameters<Resource>
> {
  ...BaseParameters;
  ...ProviderNamespace<Resource>;
  ...KeysOf<Resource>;
}

/**
 * The dynamic parameters of a list call for a resource instance - pass in the proper base type to indicate
 * where the list should take place.  The default is in a resource group
 * @template Resource The resource to get parameters for
 * @template BaseParameters The parameters representing the base Uri of the resource
 */
model ResourceParentParameters<
  Resource extends Foundations.Resource,
  BaseParameters = DefaultBaseParameters<Resource>
> {
  ...BaseParameters;
  ...ProviderNamespace<Resource>;
  ...ParentKeysOf<Resource>;
}

/**
 * The dynamic parameters of a list call for an extension resource instance.
 * @template Resource The extension resource
 */
alias ExtensionResourceInstanceParameters<Resource extends Foundations.Resource> = ResourceInstanceParameters<
  Resource,
  ExtensionBaseParameters
>;

/**
 * The dynamic parameters of a list call for a tenant resource instance.
 * @template Resource the tenant resource
 */
alias TenantInstanceParameters<Resource extends Foundations.Resource> = ResourceInstanceParameters<
  Resource,
  TenantBaseParameters
>;

/**
 * Template used by ArmProviderAction templates.
 */
@armVirtualResource
@subscriptionResource
model SubscriptionActionScope {
  @doc("Symbolic name of scope")
  @path
  @visibility(Lifecycle.Read)
  @key
  @segment("subscription")
  name: string;
}

/**
 * Template used by ArmTenantAction templates.
 */
@armVirtualResource
@tenantResource
model TenantActionScope {
  @doc("Symbolic name of scope")
  @path
  @visibility(Lifecycle.Read)
  @key
  @segment("tenant")
  name: string;
}
