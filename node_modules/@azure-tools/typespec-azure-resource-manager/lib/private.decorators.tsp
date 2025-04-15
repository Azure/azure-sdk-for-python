import "../dist/src/private.decorators.js";

namespace Azure.ResourceManager.Private;

using Reflection;

/**
 * Update the Azure Resource Manager provider namespace for a given entity.
 */
extern dec armUpdateProviderNamespace(target: Reflection.Operation);

/**
 * @param resource Resource model
 */
extern dec assignProviderNameValue(target: ModelProperty, resource: Model);

/**
 * This decorator is used to identify Azure Resource Manager resource types and extract their
 * metadata.  It is *not* meant to be used directly by a spec author, it instead
 * gets implicitly applied when the spec author defines a model type in this form:
 *
 *   `model Server is TrackedResource<ServerProperties>;`
 *
 * The `TrackedResource<Resource>` type (and other associated base types) use the
 * `@armResource` decorator, so it also gets applied to the type which absorbs the
 * `TrackedResource<Resource>` definition by using the `is` keyword.
 *
 * @param properties Azure Resource Manager resource properties
 */
extern dec armResourceInternal(target: Model, properties: Model);

/**
 * Omit a property in the target model.
 * @internal
 * @param propertyName Name of the property to omit
 */
extern dec omitIfEmpty(target: Model, propertyName: valueof string);

/**
 * @param propertyName Name of the property to omit
 */
extern dec resourceBaseParametersOf(target: Model, propertyName: Model);
/**
 * @param values Values
 */
extern dec resourceParameterBaseFor(target: ModelProperty, values: unknown[]);

/**
 * Provides default name decoration on resource name property with
 * camelcased and pluralized key and segment name
 */
extern dec defaultResourceKeySegmentName(
  target: ModelProperty,
  armResource: Model,
  keyName: valueof string,
  segment: valueof string
);

/**
 * Provides strict contraint type check.
 *
 * Due to TypeSpec language and all optional properties of `Foundations.Resource`,
 * the `Resource extends Foundations.Resource` on many of the standard ARM templates is
 * essentially equal to `Resource extends {}` and does not enforce the containt.
 *
 * Note, this is intended for internal use only for now.
 */
extern dec enforceConstraint(target: Operation | Model, sourceType: Model, constraintType: Model);

/**
 * This decorator is used to identify Azure Resource Manager resource. In generated
 * swagger definition, it will be marked with `x-ms-azure-resource`.
 *
 * It is *not* meant to be used directly by a spec author,
 */
extern dec azureResourceBase(target: Model);

/**
 * Please DO NOT USE in RestAPI specs.
 * Internal decorator that deprecated direct usage of `x-ms-client-flatten` OpenAPI extension.
 * It will programatically enabled/disable client flattening with @flattenProperty with autorest
 * emitter flags to maintain compatibility in swagger.
 */
extern dec conditionalClientFlatten(target: ModelProperty);

/**
 * Marks the operation as being a collection action
 * @param resourceType Resource
 * @param parentTypeName: Parent type name.
 * @param parentFriendlyTypeName Friendly name for parent.
 * @param applyOperationRename If true, apply both doc and operation name update
 */
extern dec armRenameListByOperation(
  target: Operation,
  resourceType: Model,
  parentTypeName?: valueof string,
  parentFriendlyTypeName?: valueof string,
  applyOperationRename?: valueof boolean
);

/**
 * Please DO NOT USE in RestAPI specs.
 * This decorator is used to adjust optionality on ARM Resource's `properties` field for brownfield service conversion.
 */
extern dec armResourcePropertiesOptionality(target: ModelProperty, isOptional: valueof boolean);
