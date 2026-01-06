import "@azure-tools/typespec-client-generator-core";

using Azure.ClientGenerator.Core;

@usage(Usage.input)
namespace ModelTypes;
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

  #suppress "@azure-tools/typespec-azure-core/no-legacy-usage" "Testing backcompat"
  @Azure.ClientGenerator.Core.Legacy.flattenProperty
  properties: PropertiesModel;
}

/**
 * Properties model
 */
model PropertiesModel {
  @encodedName("application/json", "modelDescription")
  description: string;
  age: int32;
}

/**
 * Model with a property that has a client name
 */
model ClientNameAndJsonEncodedNameModel {
    @doc("Pass in true")
    @encodedName("application/json", "wireName")
    clientName: string;
  }

/**
 * Model with a readonly property
 */
model ReadonlyModel {
  @visibility(Lifecycle.Read)
  id: int32;
}

@doc("This is base model for polymorphic multiple levels inheritance with a discriminator.")
@discriminator("kind")
model Fish {
  age: int32;
}

@doc("The second level model in polymorphic multiple levels inheritance and it defines a new discriminator.")
@discriminator("sharkType")
model Shark extends Fish {
  kind: "shark";
  sharkType: string;
}

@doc("The second level model in polymorphic multiple levels inheritance which contains references to other polymorphic instances.")
model Salmon extends Fish {
  kind: "salmon";
  friends?: Fish[];
  hate?: Record<Fish>;
  lifePartner?: Fish;
}

@doc("The third level model SawShark in polymorphic multiple levels inheritance.")
model SawShark extends Shark {
  sharkType: "saw";
}

@doc("The third level model GoblinShark in polymorphic multiple levels inheritance.")
model GoblinShark extends Shark {
  sharkType: "goblin";
}

model RecursiveElement extends Element {
  level: int8;
}

model Element {
  recursiveElement?: RecursiveElement[];
}

model BackcompatModel {
  keys: Record<string>;
}
