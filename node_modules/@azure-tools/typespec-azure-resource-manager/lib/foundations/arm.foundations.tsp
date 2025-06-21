import "@typespec/openapi";
import "@typespec/http";
import "@typespec/rest";

import "./backcompat.tsp";
import "./deprecation.tsp";
import "../common-types/common-types.tsp";
import "../decorators.tsp";
import "../responses.tsp";
import "../private.decorators.tsp";
import "../parameters.tsp";

using Http;
using OpenAPI;
using Azure.ResourceManager.Private;

namespace Azure.ResourceManager.Foundations;

/**
 * Base parameters for a resource.
 *
 * @template Resource The type of the resource.
 */
alias BaseParameters<Resource extends {}> = DefaultBaseParameters<Resource>;

/**
 * Base parameters for a resource.
 * @template Resource The type of the resource.
 */
@resourceBaseParametersOf(Resource)
model DefaultBaseParameters<Resource extends {}> {
  ...ApiVersionParameter;

  // unless tenant or extension
  ...SubscriptionIdParameter;

  // deprecated, should not be used
  ...LocationParameter;

  // unless tenant, subscription, location, or extension
  ...ResourceGroupParameter;

  // unless tenant, subscription, location, or resourceGroup
  ...ResourceUriParameter;
}

/**
 * Standard type definition for Azure Resource Manager Tags property.
 *
 * It is included in the TrackedResource template definition.
 */
/** The Azure Resource Manager Resource tags. */
model ArmTagsProperty {
  /** Resource tags. */
  tags?: Record<string>;
}

/**
 * The static parameters for a tenant-based resource
 */
model TenantBaseParameters {
  ...ApiVersionParameter;
}

/**
 * The static parameters for a subscription based resource
 */
model SubscriptionBaseParameters is TenantBaseParameters {
  ...SubscriptionIdParameter;
}

/**
 * The static parameters for a location-based resource
 */
model LocationBaseParameters is SubscriptionBaseParameters {
  ...LocationParameter;
}

/**
 * The static parameters for a resource-group based resource
 */
model ResourceGroupBaseParameters is SubscriptionBaseParameters {
  ...ResourceGroupParameter;
}

/**
 * The static parameters for an extension resource
 */
model ExtensionBaseParameters is TenantBaseParameters {
  ...ResourceUriParameter;
}

/**
 * Defines a properties type used to create named resource update models.
 * This type is not used directly, it is referenced by ResourceUpdateModel.
 * @template Resource The type of the resource.
 * @template Properties The type of the properties.
 */
@doc("The updatable properties of the {name}.", Resource)
@friendlyName("{name}UpdateProperties", Resource)
model ResourceUpdateModelProperties<
  Resource extends Foundations.Resource,
  Properties extends TypeSpec.Reflection.Model
> is OptionalProperties<UpdateableProperties<Properties>>;

/**
 * Defines a model type used to create named resource update models
 * e.g. `model MyResourceUpdate is ResourceUpdate<MyResourceProperties> {}`
 * @template Resource The type of the resource.
 * @template Properties The type of the properties.
 */
@doc("The type used for update operations of the {name}.", Resource)
@friendlyName("{name}Update", Resource)
@omitIfEmpty("properties")
model ResourceUpdateModel<
  Resource extends Foundations.Resource,
  Properties extends TypeSpec.Reflection.Model
>
  is OptionalProperties<UpdateableProperties<OmitProperties<
    Resource,
    "Name" | "name" | "properties"
  >>> {
  /** The resource-specific properties for this resource. */
  @conditionalClientFlatten
  properties?: ResourceUpdateModelProperties<Resource, Properties>;
}

/**
 * The type used for updating tags in resources.
 * @template Resource The type of the resource.
 */
@doc("The type used for updating tags in {name} resources.", Resource)
@friendlyName("{name}TagsUpdate", Resource)
model TagsUpdateModel<Resource extends Foundations.Resource> {
  ...ArmTagsProperty;
}

// Tenant resource operation definitions

alias TenantParentScope<Resource extends Foundations.Resource> = TenantScope<Resource>;

/**
 * Parameter model for listing a resource at the tenant scope
 * @template Resource The type of the resource.
 */
model TenantScope<Resource extends Foundations.Resource>
  is ResourceParentParameters<Resource, TenantBaseParameters>;

/**
 * Parameter model for listing a resource at the subscription scope
 * @template Resource The type of the resource.
 */
model SubscriptionScope<Resource extends Foundations.Resource>
  is ResourceParentParameters<Resource, SubscriptionBaseParameters>;

/**
 * Parameter model for listing a resource at the location scope
 * @template Resource The type of the resource.
 */
model LocationScope<Resource extends Foundations.Resource>
  is ResourceParentParameters<Resource, LocationBaseParameters>;

/**
 * Parameter model for listing an extension resource
 * @template Resource The type of the resource.
 */
model ExtensionScope<Resource extends Foundations.Resource>
  is ResourceParentParameters<Resource, ExtensionBaseParameters>;

/**
 * Parameter model for listing a resource at the resource group scope
 * @template Resource The type of the resource.
 */
model ResourceGroupScope<Resource extends Foundations.Resource>
  is ResourceParentParameters<Resource>;

/**
 * The type used for update operations of the resource.
 * @template Resource The type of the resource.
 * @template Properties The type of the properties.
 */
@doc("The type used for update operations of the {name}.", Resource)
@friendlyName("{name}Update", Resource)
model ProxyResourceUpdateModel<
  Resource extends Foundations.Resource,
  Properties extends TypeSpec.Reflection.Model
> {
  @conditionalClientFlatten
  properties?: ResourceUpdateModelProperties<Resource, Properties>;
}

alias DefaultProviderNamespace = {
  @path
  @TypeSpec.Rest.segment("providers")
  @doc("The provider namespace for the resource.")
  provider: "Microsoft.ThisWillBeReplaced";
};

/**
 * Adds check name availability operation, normally used if
 * a resource name must be globally unique (for example, if the resource
 * exposes an endpoint that uses the resource name in the url)
 * @template ScopeParameters A parameter model with properties representing the scope of the resource
 * @template Request The operation request body
 * @template Response The operation response
 * @template AdditionalParams A parameter model with properties representing non-path parameters
 */
@TypeSpec.Rest.autoRoute
@armResourceCollectionAction
@armProviderNameValue
@doc("Implements global CheckNameAvailability operations")
@TypeSpec.Rest.action("checkNameAvailability")
@post
op checkNameAvailability<
  ScopeParameters extends TypeSpec.Reflection.Model,
  Request extends TypeSpec.Reflection.Model = Azure.ResourceManager.Foundations.CheckNameAvailabilityRequest,
  Response extends TypeSpec.Reflection.Model = CheckNameAvailabilityResponse,
  AdditionalParams extends TypeSpec.Reflection.Model = {}
>(
  ...ApiVersionParameter,
  ...ScopeParameters,
  ...AdditionalParams,

  @doc("The CheckAvailability request")
  @body
  body: Request,
): Response | ErrorResponse;

/**
 * @dev The base template for Azure Resource Manager GET and HEAD Operations.
 * @param Parameters The parameter object for the operation.
 * @param Response The response or union of responses for success.
 * @param ErrorResponse The error response.
 */
op ArmReadOperation<Parameters extends {}, Response extends {}, ErrorResponse extends {}>(
  ...Parameters,
): Response | ErrorResponse;

/**
 * @dev The base template for Azure Resource Manager PUT Operations.
 * @param HttpParameters The parameter object for the operation.
 * @param BodyParameter The body parameter
 * @param Response The response or union of responses for success.
 * @param ErrorResponse The error response.
 */
op ArmCreateOperation<
  HttpParameters extends {},
  BodyParameter extends {},
  Response extends {},
  ErrorResponse extends {}
>(
  ...HttpParameters,
  @doc("Resource create parameters.") @bodyRoot resource: BodyParameter,
): Response | ErrorResponse;

/**
 * @dev The base template for Azure Resource Manager PATCH Operations.
 * @param HttpParameters The parameter object for the operation.
 * @param BodyParameter The body parameter
 * @param Response The response or union of responses for success.
 * @param ErrorResponse The error response.
 */
op ArmUpdateOperation<
  HttpParameters extends {},
  BodyParameter extends {},
  Response extends {},
  ErrorResponse extends {}
>(
  ...HttpParameters,
  @doc("The resource properties to be updated.") @bodyRoot properties: BodyParameter,
): Response | ErrorResponse;
