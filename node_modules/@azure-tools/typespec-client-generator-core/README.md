# @azure-tools/typespec-client-generator-core

TypeSpec Data Plane Generation library

## Install

```bash
npm install @azure-tools/typespec-client-generator-core
```

## Usage

1. Via the command line

```bash
tsp compile . --emit=@azure-tools/typespec-client-generator-core
```

2. Via the config

```yaml
emit:
  - "@azure-tools/typespec-client-generator-core"
```

The config can be extended with options as follows:

```yaml
emit:
  - "@azure-tools/typespec-client-generator-core"
options:
  "@azure-tools/typespec-client-generator-core":
    option: value
```

## Emitter options

### `emitter-name`

**Type:** `string`

Set `emitter-name` to output TCGC code models for specific language's emitter.

### `generate-protocol-methods`

**Type:** `boolean`

When set to `true`, the emitter will generate low-level protocol methods for each service operation if `@protocolAPI` is not set for an operation. Default value is `true`.

### `generate-convenience-methods`

**Type:** `boolean`

When set to `true`, the emitter will generate low-level protocol methods for each service operation if `@convenientAPI` is not set for an operation. Default value is `true`.

### `api-version`

**Type:** `string`

Use this flag if you would like to generate the sdk only for a specific version. Default value is the latest version. Also accepts values `latest` and `all`.

### `license`

**Type:** `object`

License information for the generated client code.

### `examples-dir`

**Type:** `string`

Specifies the directory where the emitter will look for example files. If the flag isn’t set, the emitter defaults to using an `examples` directory located at the project root.

### `namespace`

**Type:** `string`

Specifies the namespace you want to override for namespaces set in the spec. With this config, all namespace for the spec types will default to it.

## Usage

Add the following in `tspconfig.yaml`:

```yaml
linter:
  extends:
    - "@azure-tools/typespec-client-generator-core/all"
```

## RuleSets

Available ruleSets:

- `@azure-tools/typespec-client-generator-core/all`
- `@azure-tools/typespec-client-generator-core/best-practices:csharp`

## Rules

| Name                                                                                                                                                                                      | Description                                                             |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [`@azure-tools/typespec-client-generator-core/require-client-suffix`](https://azure.github.io/typespec-azure/docs/libraries/typespec-client-generator-core/rules/require-client-suffix)   | Client names should end with 'Client'.                                  |
| [`@azure-tools/typespec-client-generator-core/property-name-conflict`](https://azure.github.io/typespec-azure/docs/libraries/typespec-client-generator-core/rules/property-name-conflict) | Avoid naming conflicts between a property and a model of the same name. |

## Decorators

### Azure.ClientGenerator.Core

- [`@access`](#@access)
- [`@alternateType`](#@alternatetype)
- [`@apiVersion`](#@apiversion)
- [`@client`](#@client)
- [`@clientApiVersions`](#@clientapiversions)
- [`@clientInitialization`](#@clientinitialization)
- [`@clientName`](#@clientname)
- [`@clientNamespace`](#@clientnamespace)
- [`@convenientAPI`](#@convenientapi)
- [`@deserializeEmptyStringAsNull`](#@deserializeemptystringasnull)
- [`@flattenProperty`](#@flattenproperty)
- [`@operationGroup`](#@operationgroup)
- [`@override`](#@override)
- [`@paramAlias`](#@paramalias)
- [`@protocolAPI`](#@protocolapi)
- [`@responseAsBool`](#@responseasbool)
- [`@scope`](#@scope)
- [`@usage`](#@usage)
- [`@useSystemTextJsonConverter`](#@usesystemtextjsonconverter)

#### `@access`

Override access for operations, models, enums and model property.
When setting access for namespaces,
the access info will be propagated to the models and operations defined in the namespace.
If the model has an access override, the model override takes precedence.
When setting access for an operation,
it will influence the access info for models/enums that are used by this operation.
Models/enums that are used in any operations with `@access(Access.public)` will be set to access "public"
Models/enums that are only used in operations with `@access(Access.internal)` will be set to access "internal".
The access info for models will be propagated to models' properties,
parent models, discriminated sub models.
The override access should not be narrow than the access calculated by operation,
and different override access should not conflict with each other,
otherwise a warning will be added to diagnostics list.
Model property's access will default to public unless there is an override.

```typespec
@Azure.ClientGenerator.Core.access(value: EnumMember, scope?: valueof string)
```

##### Target

`ModelProperty | Model | Operation | Enum | Union | Namespace`

##### Parameters

| Name  | Type             | Description                                                                                                                                                                                            |
| ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| value | `EnumMember`     | The access info you want to set for this model or operation.                                                                                                                                           |
| scope | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

###### Set access

```typespec
// Access.internal
@access(Access.internal)
model ModelToHide {
  prop: string;
}
// Access.internal
@access(Access.internal)
op test: void;
```

###### Access propagation

```typespec
// Access.internal
@discriminator("kind")
model Fish {
  age: int32;
}

// Access.internal
@discriminator("sharktype")
model Shark extends Fish {
  kind: "shark";
  origin: Origin;
}

// Access.internal
model Salmon extends Fish {
  kind: "salmon";
}

// Access.internal
model SawShark extends Shark {
  sharktype: "saw";
}

// Access.internal
model Origin {
  country: string;
  city: string;
  manufacture: string;
}

// Access.internal
@get
@access(Access.internal)
op getModel(): Fish;
```

###### Access influence from operation

```typespec
// Access.internal
model Test1 {}

// Access.internal
@access(Access.internal)
@route("/func1")
op func1(@body body: Test1): void;

// Access.public
model Test2 {}

// Access.public
@route("/func2")
op func2(@body body: Test2): void;

// Access.public
model Test3 {}

// Access.public
@access(Access.public)
@route("/func3")
op func3(@body body: Test3): void;

// Access.public
model Test4 {}

// Access.internal
@access(Access.internal)
@route("/func4")
op func4(@body body: Test4): void;

// Access.public
@route("/func5")
op func5(@body body: Test4): void;

// Access.public
model Test5 {}

// Access.internal
@access(Access.internal)
@route("/func6")
op func6(@body body: Test5): void;

// Access.public
@route("/func7")
op func7(@body body: Test5): void;

// Access.public
@access(Access.public)
@route("/func8")
op func8(@body body: Test5): void;
```

#### `@alternateType`

Set an alternate type for a model property, scalar, or function parameter. Note that `@encode` will be overridden by the one defined in alternate type.

```typespec
@Azure.ClientGenerator.Core.alternateType(alternate: Scalar, scope?: valueof string)
```

##### Target

The source type you want to apply the alternate type to. Only scalar types are supported.
`ModelProperty | Scalar`

##### Parameters

| Name      | Type             | Description                                                                                                                                                                                            |
| --------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| alternate | `Scalar`         | The alternate type you want applied to the target. Only scalar types are supported.                                                                                                                    |
| scope     | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
model Foo {
  date: utcDateTime;
}
@@alternateType(Foo.date, string);
```

```typespec
scalar storageDateTime extends utcDataTime;
@@alternateType(storageDateTime, string, "python");
```

```typespec
op test(@param @alternateType(string) date: utcDateTime): void;
```

#### `@apiVersion`

Use to override default assumptions on whether a parameter is an api-version parameter or not.
By default, we do matches with the `api-version` or `apiversion` string in the parameter name. Since api versions are
a client parameter, we will also elevate this parameter up onto the client.

```typespec
@Azure.ClientGenerator.Core.apiVersion(value?: valueof boolean, scope?: valueof string)
```

##### Target

`ModelProperty`

##### Parameters

| Name  | Type              | Description                                                                                                                                                                                            |
| ----- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| value | `valueof boolean` | If true, we will treat this parameter as an api-version parameter. If false, we will not. Default is true.                                                                                             |
| scope | `valueof string`  | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
namespace Contoso;

op test(
  @apiVersion
  @header("x-ms-version")
  version: string,
): void;
```

#### `@client`

Create a ClientGenerator.Core client out of a namespace or interface

```typespec
@Azure.ClientGenerator.Core.client(value?: Model, scope?: valueof string)
```

##### Target

`Namespace | Interface`

##### Parameters

| Name  | Type             | Description                                                                                                                                                                                            |
| ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| value | `Model`          | Optional configuration for the service.                                                                                                                                                                |
| scope | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

###### Basic client setting

```typespec
@client
namespace MyService {

}
```

###### Setting with other service

```typespec
namespace MyService {

}

@client({
  service: MyService,
})
interface MyInterface {}
```

###### Changing client name if you don't want <Interface/Namespace>Client

```typespec
@client({
  client: MySpecialClient,
})
interface MyInterface {}
```

#### `@clientApiVersions`

Specify additional API versions that the client can support. These versions should include those defined by the service's versioning configuration.
This decorator is useful for extending the API version enum exposed by the client.
It is particularly beneficial when generating a complete API version enum without requiring the entire specification to be annotated with versioning decorators, as the generation process does not depend on versioning details.

```typespec
@Azure.ClientGenerator.Core.clientApiVersions(value: Enum, scope?: valueof string)
```

##### Target

`Namespace`

##### Parameters

| Name  | Type             | Description |
| ----- | ---------------- | ----------- |
| value | `Enum`           |             |
| scope | `valueof string` |             |

##### Examples

```typespec
// main.tsp
@versioned(Versions)
namespace Contoso {
  enum Versions {
    v4,
    v5,
  }
}

// client.tsp

enum ClientApiVersions {
  v1,
  v2,
  v3,
  ...Contoso.Versions,
}

@@clientApiVersions(Contoso, ClientApiVersions);
```

#### `@clientInitialization`

Customize the client initialization way.

```typespec
@Azure.ClientGenerator.Core.clientInitialization(options: Azure.ClientGenerator.Core.ClientInitializationOptions, scope?: valueof string)
```

##### Target

`Namespace | Interface`

##### Parameters

| Name    | Type                                                          | Description                                                                                                                                                                                            |
| ------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| options | [`ClientInitializationOptions`](#clientinitializationoptions) |                                                                                                                                                                                                        |
| scope   | `valueof string`                                              | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
// main.tsp
namespace MyService;

op upload(blobName: string): void;
op download(blobName: string): void;

// client.tsp
namespace MyCustomizations;
model MyServiceClientOptions {
  blobName: string;
}

@@clientInitialization(MyService, {parameters: MyServiceClientOptions})
// The generated client will have `blobName` on its initialization method. We will also
// elevate the existing `blobName` parameter from method level to client level.
```

#### `@clientName`

Changes the name of a method, parameter, property, or model generated in the client SDK

```typespec
@Azure.ClientGenerator.Core.clientName(rename: valueof string, scope?: valueof string)
```

##### Target

`unknown`

##### Parameters

| Name   | Type             | Description                                                                                                                                                                                            |
| ------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| rename | `valueof string` | The rename you want applied to the object                                                                                                                                                              |
| scope  | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
@clientName("nameInClient")
op nameInService: void;
```

```typespec
@clientName("nameForJava", "java")
@clientName("name_for_python", "python")
@clientName("nameForCsharp", "csharp")
@clientName("nameForJavascript", "javascript")
op nameInService: void;
```

#### `@clientNamespace`

Changes the namespace of a client, model, enum or union generated in the client SDK.
By default, the client namespace for them will follow the TypeSpec namespace.

```typespec
@Azure.ClientGenerator.Core.clientNamespace(rename: valueof string, scope?: valueof string)
```

##### Target

`Namespace | Interface | Model | Enum | Union`

##### Parameters

| Name   | Type             | Description                                                                                                                                                                                            |
| ------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| rename | `valueof string` | The rename you want applied to the object                                                                                                                                                              |
| scope  | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
@clientNamespace("ContosoClient")
namespace Contoso;
```

```typespec
@clientNamespace("ContosoJava", "java")
@clientNamespace("ContosoPython", "python")
@clientNamespace("ContosoCSharp", "csharp")
@clientNamespace("ContosoJavascript", "javascript")
namespace Contoso;
```

#### `@convenientAPI`

Whether you want to generate an operation as a convenient operation.

```typespec
@Azure.ClientGenerator.Core.convenientAPI(value?: valueof boolean, scope?: valueof string)
```

##### Target

`Operation`

##### Parameters

| Name  | Type              | Description                                                                                                                                                                                            |
| ----- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| value | `valueof boolean` | Whether to generate the operation as convenience method or not.                                                                                                                                        |
| scope | `valueof string`  | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
@convenientAPI(false)
op test: void;
```

#### `@deserializeEmptyStringAsNull`

Indicates that a model property of type `string` or a `Scalar` type derived from `string` should be deserialized as `null` when its value is an empty string (`""`).

```typespec
@Azure.ClientGenerator.Core.deserializeEmptyStringAsNull(scope?: valueof string)
```

##### Target

`ModelProperty`

##### Parameters

| Name  | Type             | Description                                                                                                                                                                                            |
| ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| scope | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec

model MyModel {
  scalar stringlike extends string;

  @deserializeEmptyStringAsNull
  prop: string;

  @deserializeEmptyStringAsNull
  prop: stringlike;
}
```

#### `@flattenProperty`

_Deprecated: @flattenProperty decorator is not recommended to use._

Set whether a model property should be flattened or not.

```typespec
@Azure.ClientGenerator.Core.flattenProperty(scope?: valueof string)
```

##### Target

`ModelProperty`

##### Parameters

| Name  | Type             | Description                                                                                                                                                                                            |
| ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| scope | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
model Foo {
  @flattenProperty
  prop: Bar;
}
model Bar {}
```

#### `@operationGroup`

Create a ClientGenerator.Core operation group out of a namespace or interface

```typespec
@Azure.ClientGenerator.Core.operationGroup(scope?: valueof string)
```

##### Target

`Namespace | Interface`

##### Parameters

| Name  | Type             | Description                                                                                                                                                                                            |
| ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| scope | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
@operationGroup
interface MyInterface {}
```

#### `@override`

Override the default client method generated by TCGC from your service definition

```typespec
@Azure.ClientGenerator.Core.override(override: Operation, scope?: valueof string)
```

##### Target

: The original service definition
`Operation`

##### Parameters

| Name     | Type             | Description                                                                                                                                                                                            |
| -------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| override | `Operation`      | : The override method definition that specifies the exact client method you want                                                                                                                       |
| scope    | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
// main.tsp
namespace MyService;

model Params {
 foo: string;
 bar: string;
}
op myOperation(...Params): void; // by default, we generate the method signature as `op myOperation(foo: string, bar: string)`;

// client.tsp
namespace MyCustomizations;

op myOperationCustomization(params: MyService.Params): void;

@@override(MyService.myOperation, myOperationCustomization);

// method signature is now `op myOperation(params: Params)`
```

```typespec
// main.tsp
namespace MyService;

model Params {
 foo: string;
 bar: string;
}
op myOperation(...Params): void; // by default, we generate the method signature as `op myOperation(foo: string, bar: string)`;

// client.tsp
namespace MyCustomizations;

op myOperationCustomization(params: MyService.Params): void;

@@override(MyService.myOperation, myOperationCustomization, "csharp")

// method signature is now `op myOperation(params: Params)` just for csharp
```

#### `@paramAlias`

Alias the name of a client parameter to a different name. This permits you to have a different name for the parameter in client initialization then on individual methods and still refer to the same parameter.

```typespec
@Azure.ClientGenerator.Core.paramAlias(paramAlias: valueof string, scope?: valueof string)
```

##### Target

`ModelProperty`

##### Parameters

| Name       | Type             | Description                                                                                                                                                                                            |
| ---------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| paramAlias | `valueof string` |                                                                                                                                                                                                        |
| scope      | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
// main.tsp
namespace MyService;

op upload(blobName: string): void;

// client.tsp
namespace MyCustomizations;
model MyServiceClientOptions {
  blob: string;
}

@@clientInitialization(MyService, MyServiceClientOptions)
@@paramAlias(MyServiceClientOptions.blob, "blobName")

// The generated client will have `blobName` on it. We will also
// elevate the existing `blob` parameter to the client level.
```

#### `@protocolAPI`

Whether you want to generate an operation as a protocol operation.

```typespec
@Azure.ClientGenerator.Core.protocolAPI(value?: valueof boolean, scope?: valueof string)
```

##### Target

`Operation`

##### Parameters

| Name  | Type              | Description                                                                                                                                                                                            |
| ----- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| value | `valueof boolean` | Whether to generate the operation as protocol or not.                                                                                                                                                  |
| scope | `valueof string`  | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
@protocolAPI(false)
op test: void;
```

#### `@responseAsBool`

Indicates that a HEAD operation should be modeled as Response<bool>. 404 will not raise an error, instead the service method will return `false`. 2xx will return `true`. Everything else will still raise an error.

```typespec
@Azure.ClientGenerator.Core.responseAsBool(scope?: valueof string)
```

##### Target

`Operation`

##### Parameters

| Name  | Type             | Description |
| ----- | ---------------- | ----------- |
| scope | `valueof string` |             |

##### Examples

```typespec
@responseAsBool
@head
op headOperation(): void;
```

#### `@scope`

To define the client scope of an operation.

```typespec
@Azure.ClientGenerator.Core.scope(scope?: valueof string)
```

##### Target

`Operation`

##### Parameters

| Name  | Type             | Description                                                                                                                                                                                            |
| ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| scope | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
@scope("!csharp")
op test: void;
```

#### `@usage`

Override usage for models/enums.
A model/enum's default usage info is always calculated by the operations that use it.
You could use this decorator to override the default usage info.
When setting usage for namespaces,
the usage info will be propagated to the models defined in the namespace.
If the model has an usage override, the model override takes precedence.
For example, with operation definition `op test(): OutputModel`,
the model `OutputModel` has default usage `Usage.output`.
After adding decorator `@@usage(OutputModel, Usage.input | Usage.output)`,
the final usage result for `OutputModel` is `Usage.input | Usage.output`.
The usage info for models will be propagated to models' properties,
parent models, discriminated sub models.
The override usage should not be narrow than the usage calculated by operation,
and different override usage should not conflict with each other,
otherwise a warning will be added to diagnostics list.

```typespec
@Azure.ClientGenerator.Core.usage(value: EnumMember | Union, scope?: valueof string)
```

##### Target

`Model | Enum | Union | Namespace`

##### Parameters

| Name  | Type                  | Description                                                                                                                                                                                            |
| ----- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| value | `EnumMember \| Union` | The usage info you want to set for this model.                                                                                                                                                         |
| scope | `valueof string`      | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

###### Expand usage for model

```typespec
op test(): OutputModel;

// usage result for `OutputModel` is `Usage.input | Usage.output`
@usage(Usage.input)
model OutputModel {
  prop: string;
}
```

###### Propagation of usage

```typespec
// Usage.output
@discriminator("kind")
model Fish {
  age: int32;
}

// Usage.input | Usage.output
@discriminator("sharktype")
@usage(Usage.input)
model Shark extends Fish {
  kind: "shark";
  origin: Origin;
}

// Usage.output
model Salmon extends Fish {
  kind: "salmon";
}

// Usage.output
model SawShark extends Shark {
  sharktype: "saw";
}

// Usage.output
model Origin {
  country: string;
  city: string;
  manufacture: string;
}

@get
op getModel(): Fish;
```

#### `@useSystemTextJsonConverter`

Whether a model needs the custom JSON converter, this is only used for backward compatibility for csharp.

```typespec
@Azure.ClientGenerator.Core.useSystemTextJsonConverter(scope?: valueof string)
```

##### Target

`Model`

##### Parameters

| Name  | Type             | Description                                                                                                                                                                                            |
| ----- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| scope | `valueof string` | The language scope you want this decorator to apply to. If not specified, will apply to all language emitters.<br />You can use "!" to specify negation such as "!(java, python)" or "!java, !python". |

##### Examples

```typespec
@useSystemTextJsonConverter
model MyModel {
  prop: string;
}
```
