import "@azure-tools/typespec-client-generator-core";

using Azure.ClientGenerator.Core;

@usage(Usage.input)
namespace ModelTest;
/** A scratch model for testing purposes */

model Scratch {
    /** A string property */
    prop: string;
}

/**
 * Model with one level of flattening
 */
model FlattenModel {
  name: string;

  #suppress "deprecated" "@flattenProperty decorator is not recommended to use."
  @flattenProperty
  properties: PropertiesModel;
}

/**
 * Properties model
 */
model PropertiesModel {
  description: string;
  age: int32;
}

/**
 * Model with a property that has a client name
 */
model ClientNamedPropertyModel {
  @clientName("propClientName")
  propServiceName: string;
}

/**
 * Model with a readonly property
 */
model ReadonlyModel {
  @visibility(Lifecycle.Read)
  id: int32;
}
