using Reflection;

namespace Azure.ResourceManager.Legacy;

/**
 * This decorator is used on resources that do not satisfy the definition of a resource
 * but need to be identified as such.
 */
extern dec customAzureResource(target: Model);

/**
 * Specify an external reference that should be used when emitting this type.
 * @param jsonRef - External reference(e.g. "../../common.json#/definitions/Foo")
 */
extern dec externalTypeRef(entity: Model | ModelProperty, jsonRef: valueof string);
