using Reflection;

namespace Azure.ClientGenerator.Core;

/**
 * Changes the name of a method, parameter, property, or model generated in the client SDK
 * @param rename The rename you want applied to the object
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * @clientName("nameInClient")
 * op nameInService: void;
 * ```
 *
 * @example
 * ```typespec
 * @clientName("nameForJava", "java")
 * @clientName("name_for_python", "python")
 * @clientName("nameForCsharp", "csharp")
 * @clientName("nameForJavascript", "javascript")
 * op nameInService: void;
 * ```
 */
extern dec clientName(target: unknown, rename: valueof string, scope?: valueof string);

/**
 * Whether you want to generate an operation as a convenient operation.
 * @param value Whether to generate the operation as convenience method or not.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * @convenientAPI(false)
 * op test: void;
 * ```
 */
extern dec convenientAPI(target: Operation, value?: valueof boolean, scope?: valueof string);

/**
 * Whether you want to generate an operation as a protocol operation.
 * @param value Whether to generate the operation as protocol or not.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * @protocolAPI(false)
 * op test: void;
 * ```
 */
extern dec protocolAPI(target: Operation, value?: valueof boolean, scope?: valueof string);

/**
 * Create a ClientGenerator.Core client out of a namespace or interface
 * @param value Optional configuration for the service.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example Basic client setting
 * ```typespec
 * @client
 * namespace MyService {}
 * ```
 *
 * @example Setting with other service
 * ```typespec
 * namespace MyService {}
 *
 * @client({service: MyService})
 * interface MyInterface {}
 * ```
 *
 * @example Changing client name if you don't want <Interface/Namespace>Client
 * ```typespec
 * @client({client: MySpecialClient})
 * interface MyInterface {}
 * ```
 *
 * @example
 */
extern dec client(target: Namespace | Interface, value?: Model, scope?: valueof string);

/**
 * Create a ClientGenerator.Core operation group out of a namespace or interface
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * @operationGroup
 * interface MyInterface{}
 * ```
 */
extern dec operationGroup(target: Namespace | Interface, scope?: valueof string);

/**
 * Usage value.
 */
enum Usage {
  /**
   * Used in request
   */
  input: 2,

  /**
   * Used in response
   */
  output: 4,
}

/**
 * Override usage for models/enums.
 * A model/enum's default usage info is always calculated by the operations that use it.
 * You could use this decorator to override the default usage info.
 * When setting usage for namespaces,
 * the usage info will be propagated to the models defined in the namespace.
 * If the model has an usage override, the model override takes precedence.
 * For example, with operation definition `op test(): OutputModel`,
 * the model `OutputModel` has default usage `Usage.output`.
 * After adding decorator `@@usage(OutputModel, Usage.input | Usage.output)`,
 * the final usage result for `OutputModel` is `Usage.input | Usage.output`.
 * The usage info for models will be propagated to models' properties,
 * parent models, discriminated sub models.
 * The override usage should not be narrow than the usage calculated by operation,
 * and different override usage should not conflict with each other,
 * otherwise a warning will be added to diagnostics list.
 * @param value The usage info you want to set for this model.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example Expand usage for model
 * ```typespec
 * op test(): OutputModel;
 *
 * // usage result for `OutputModel` is `Usage.input | Usage.output`
 * @usage(Usage.input)
 * model OutputModel {
 *   prop: string
 * }
 * ```
 *
 * @example Propagation of usage
 * ```typespec
 * // Usage.output
 * @discriminator("kind")
 * model Fish {
 *   age: int32;
 * }
 *
 * // Usage.input | Usage.output
 * @discriminator("sharktype")
 * @usage(Usage.input)
 * model Shark extends Fish {
 *   kind: "shark";
 *   origin: Origin;
 * }
 *
 * // Usage.output
 * model Salmon extends Fish {
 *   kind: "salmon";
 * }
 *
 * // Usage.output
 * model SawShark extends Shark {
 *   sharktype: "saw";
 * }
 *
 * // Usage.output
 * model Origin {
 *   country: string;
 *   city: string;
 *   manufacture: string;
 * }
 *
 * @get
 * op getModel(): Fish;
 * ```
 */
extern dec usage(
  target: Model | Enum | Union | Namespace,
  value: EnumMember | Union,
  scope?: valueof string
);

/**
 * Access value.
 */
enum Access {
  /**
   * Open to user
   */
  public: "public",

  /**
   * Hide from user
   */
  internal: "internal",
}

/**
 * Override access for operations, models, enums and model property.
 * When setting access for namespaces,
 * the access info will be propagated to the models and operations defined in the namespace.
 * If the model has an access override, the model override takes precedence.
 * When setting access for an operation,
 * it will influence the access info for models/enums that are used by this operation.
 * Models/enums that are used in any operations with `@access(Access.public)` will be set to access "public"
 * Models/enums that are only used in operations with `@access(Access.internal)` will be set to access "internal".
 * The access info for models will be propagated to models' properties,
 * parent models, discriminated sub models.
 * The override access should not be narrow than the access calculated by operation,
 * and different override access should not conflict with each other,
 * otherwise a warning will be added to diagnostics list.
 * Model property's access will default to public unless there is an override.
 * @param value The access info you want to set for this model or operation.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example Set access
 * ```typespec
 * // Access.internal
 * @access(Access.internal)
 * model ModelToHide {
 *   prop: string;
 * }
 * // Access.internal
 * @access(Access.internal)
 * op test: void;
 * ```
 * @example Access propagation
 * ```typespec
 * // Access.internal
 * @discriminator("kind")
 * model Fish {
 *   age: int32;
 * }
 *
 * // Access.internal
 * @discriminator("sharktype")
 * model Shark extends Fish {
 *   kind: "shark";
 *   origin: Origin;
 * }
 *
 * // Access.internal
 * model Salmon extends Fish {
 *   kind: "salmon";
 * }
 *
 * // Access.internal
 * model SawShark extends Shark {
 *   sharktype: "saw";
 * }
 *
 * // Access.internal
 * model Origin {
 *   country: string;
 *   city: string;
 *   manufacture: string;
 * }
 *
 * // Access.internal
 * @get
 * @access(Access.internal)
 * op getModel(): Fish;
 * ```
 * @example Access influence from operation
 * ```typespec
 * // Access.internal
 * model Test1 {
 * }
 *
 * // Access.internal
 * @access(Access.internal)
 * @route("/func1")
 * op func1(
 *   @body body: Test1
 * ): void;
 *
 * // Access.public
 * model Test2 {
 * }
 *
 * // Access.public
 * @route("/func2")
 * op func2(
 *   @body body: Test2
 * ): void;
 *
 * // Access.public
 * model Test3 {
 * }
 *
 * // Access.public
 * @access(Access.public)
 * @route("/func3")
 * op func3(
 *   @body body: Test3
 * ): void;
 *
 * // Access.public
 * model Test4 {
 * }
 *
 * // Access.internal
 * @access(Access.internal)
 * @route("/func4")
 * op func4(
 *   @body body: Test4
 * ): void;
 *
 * // Access.public
 * @route("/func5")
 * op func5(
 *   @body body: Test4
 * ): void;
 *
 * // Access.public
 * model Test5 {
 * }
 *
 * // Access.internal
 * @access(Access.internal)
 * @route("/func6")
 * op func6(
 *   @body body: Test5
 * ): void;
 *
 * // Access.public
 * @route("/func7")
 * op func7(
 *   @body body: Test5
 * ): void;
 *
 * // Access.public
 * @access(Access.public)
 * @route("/func8")
 * op func8(
 *   @body body: Test5
 * ): void;
 * ```
 */
extern dec access(
  target: ModelProperty | Model | Operation | Enum | Union | Namespace,
  value: EnumMember,
  scope?: valueof string
);

/**
 * Set whether a model property should be flattened or not.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * model Foo {
 *    @flattenProperty
 *    prop: Bar;
 * }
 * model Bar {
 * }
 * ```
 */
#deprecated "@flattenProperty decorator is not recommended to use."
extern dec flattenProperty(target: ModelProperty, scope?: valueof string);

/**
 * Override the default client method generated by TCGC from your service definition
 * @param original: The original service definition
 * @param override: The override method definition that specifies the exact client method you want
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * // main.tsp
 * namespace MyService;
 *
 * model Params {
 *  foo: string;
 *  bar: string;
 * }
 * op myOperation(...Params): void; // by default, we generate the method signature as `op myOperation(foo: string, bar: string)`;
 *
 * // client.tsp
 * namespace MyCustomizations;
 *
 * op myOperationCustomization(params: MyService.Params): void;
 *
 * @@override(MyService.myOperation, myOperationCustomization);
 *
 * // method signature is now `op myOperation(params: Params)`
 * ```
 *
 * @example
 * ```typespec
 * // main.tsp
 * namespace MyService;
 *
 * model Params {
 *  foo: string;
 *  bar: string;
 * }
 * op myOperation(...Params): void; // by default, we generate the method signature as `op myOperation(foo: string, bar: string)`;
 *
 * // client.tsp
 * namespace MyCustomizations;
 *
 * op myOperationCustomization(params: MyService.Params): void;
 *
 * @@override(MyService.myOperation, myOperationCustomization, "csharp")
 *
 * // method signature is now `op myOperation(params: Params)` just for csharp
 * ```
 */
extern dec override(original: Operation, override: Operation, scope?: valueof string);

/**
 * Whether a model needs the custom JSON converter, this is only used for backward compatibility for csharp.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * @useSystemTextJsonConverter
 * model MyModel {
 *   prop: string;
 * }
 * ```
 */
extern dec useSystemTextJsonConverter(target: Model, scope?: valueof string);

/**
 * InitializedBy value.
 */
enum InitializedBy {
  /**
   * The client could be initialized individually.
   */
  individually: 1,

  /**
   * The client could be initialized by parent client.
   */
  parent: 2,
}

/**
 * Customize the client initialization way.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * // main.tsp
 * namespace MyService;
 *
 * op upload(blobName: string): void;
 * op download(blobName: string): void;
 *
 * // client.tsp
 * namespace MyCustomizations;
 * model MyServiceClientOptions {
 *   blobName: string;
 * }
 *
 * @@clientInitialization(MyService, {parameters: MyServiceClientOptions})
 * // The generated client will have `blobName` on its initialization method. We will also
 * // elevate the existing `blobName` parameter from method level to client level.
 * ```
 */
extern dec clientInitialization(
  target: Namespace | Interface,
  options: ClientInitializationOptions,
  scope?: valueof string
);

/**
 * Client initialization customization options.
 */
model ClientInitializationOptions {
  /**
   * Redefine the client initialization parameters you would like to add to the client.
   * By default, we apply endpoint, credential, and api-version parameters. If you specify parameters model, we will append the properties of the model to the parameters list of the client initialization.
   */
  parameters?: Model;

  /**
   * Determines how the client could be initialized. Use `InitializedBy` enum to set the value. The value could be `InitializedBy.individually`, `InitializedBy.parent` or `InitializedBy.individually | InitializedBy.parent`.
   */
  initializedBy?: EnumMember | Union;
}

/**
 * Alias the name of a client parameter to a different name. This permits you to have a different name for the parameter in client initialization then on individual methods and still refer to the same parameter.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * // main.tsp
 * namespace MyService;
 *
 * op upload(blobName: string): void;
 *
 * // client.tsp
 * namespace MyCustomizations;
 * model MyServiceClientOptions {
 *   blob: string;
 * }
 *
 * @@clientInitialization(MyService, MyServiceClientOptions)
 * @@paramAlias(MyServiceClientOptions.blob, "blobName")
 *
 * // The generated client will have `blobName` on it. We will also
 * // elevate the existing `blob` parameter to the client level.
 * ```
 */
extern dec paramAlias(original: ModelProperty, paramAlias: valueof string, scope?: valueof string);

/**
 * Changes the namespace of a client, model, enum or union generated in the client SDK.
 * By default, the client namespace for them will follow the TypeSpec namespace.
 * @param rename The rename you want applied to the object
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * @clientNamespace("ContosoClient")
 * namespace Contoso;
 * ```
 *
 * @example
 * ```typespec
 * @clientNamespace("ContosoJava", "java")
 * @clientNamespace("ContosoPython", "python")
 * @clientNamespace("ContosoCSharp", "csharp")
 * @clientNamespace("ContosoJavascript", "javascript")
 * namespace Contoso;
 * ```
 */
extern dec clientNamespace(
  target: Namespace | Interface | Model | Enum | Union,
  rename: valueof string,
  scope?: valueof string
);

/**
 * Set an alternate type for a model property, scalar, or function parameter. Note that `@encode` will be overridden by the one defined in alternate type.
 *
 * @param source The source type you want to apply the alternate type to. Only scalar types are supported.
 * @param alternate The alternate type you want applied to the target. Only scalar types are supported.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 * @example
 * ```typespec
 * model Foo {
 *    date: utcDateTime;
 * }
 * @@alternateType(Foo.date, string);
 * ```
 * @example
 * ```typespec
 * scalar storageDateTime extends utcDataTime;
 * @@alternateType(storageDateTime, string, "python");
 * ```
 * @example
 * ```typespec
 * op test(@param @alternateType(string) date: utcDateTime): void;
 * ```
 */
extern dec alternateType(source: ModelProperty | Scalar, alternate: Scalar, scope?: valueof string);

/**
 * To define the client scope of an operation.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * @scope("!csharp")
 * op test: void;
 * ```
 */
extern dec scope(target: Operation, scope?: valueof string);

/**
 * Use to override default assumptions on whether a parameter is an api-version parameter or not.
 * By default, we do matches with the `api-version` or `apiversion` string in the parameter name. Since api versions are
 * a client parameter, we will also elevate this parameter up onto the client.
 * @param value If true, we will treat this parameter as an api-version parameter. If false, we will not. Default is true.
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 * namespace Contoso;
 *
 * op test(
 *   @apiVersion
 *   @header("x-ms-version")
 *   version: string
 * ): void;
 * ```
 */
extern dec apiVersion(target: ModelProperty, value?: valueof boolean, scope?: valueof string);

/**
 * Specify additional API versions that the client can support. These versions should include those defined by the service's versioning configuration.
 * This decorator is useful for extending the API version enum exposed by the client.
 * It is particularly beneficial when generating a complete API version enum without requiring the entire specification to be annotated with versioning decorators, as the generation process does not depend on versioning details.
 *
 * @example
 * ```typespec
 * // main.tsp
 * @versioned(Versions)
 * namespace Contoso {
 *  enum Versions { v4, v5 }
 * }
 *
 * // client.tsp
 *
 * enum ClientApiVersions { v1, v2, v3, ...Contoso.Versions }
 *
 * @@clientApiVersions(Contoso, ClientApiVersions)
 * ```
 */
extern dec clientApiVersions(target: Namespace, value: Enum, scope?: valueof string);
/**
 * Indicates that a model property of type `string` or a `Scalar` type derived from `string` should be deserialized as `null` when its value is an empty string (`""`).
 * @param scope The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.
 * You can use "!" to specify negation such as "!(java, python)" or "!java, !python".
 *
 * @example
 * ```typespec
 *
 * model MyModel {
 *   scalar stringlike extends string;
 *
 *   @deserializeEmptyStringAsNull
 *   prop: string;
 *
 *   @deserializeEmptyStringAsNull
 *   prop: stringlike;
 * }
 * ```
 */
extern dec deserializeEmptyStringAsNull(target: ModelProperty, scope?: valueof string);

/**
 * Indicates that a HEAD operation should be modeled as Response<bool>. 404 will not raise an error, instead the service method will return `false`. 2xx will return `true`. Everything else will still raise an error.
 *
 * @example
 * ```typespec
 *
 * @responseAsBool
 * @head
 * op headOperation(): void;
 * ```
 */
extern dec responseAsBool(target: Operation, scope?: valueof string);
