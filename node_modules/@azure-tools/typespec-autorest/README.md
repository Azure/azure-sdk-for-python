# @azure-tools/typespec-autorest

TypeSpec library for emitting openapi from the TypeSpec REST protocol binding

## Install

```bash
npm install @azure-tools/typespec-autorest
```

## Usage

1. Via the command line

```bash
tsp compile . --emit=@azure-tools/typespec-autorest
```

2. Via the config

```yaml
emit:
  - "@azure-tools/typespec-autorest"
```

The config can be extended with options as follows:

```yaml
emit:
  - "@azure-tools/typespec-autorest"
options:
  "@azure-tools/typespec-autorest":
    option: value
```

## Emitter options

### `output-dir`

**Type:** `string`

Deprecated DO NOT USE. Use built-in emitter-output-dir instead

### `output-file`

**Type:** `string`

Name of the output file.
Output file will interpolate the following values:

- service-name: Name of the service if multiple
- version: Version of the service if multiple
- azure-resource-provider-folder: Value of the azure-resource-provider-folder option
- version-status: Only enabled if azure-resource-provider-folder is set. `preview` if version contains preview, stable otherwise.

Default: `{azure-resource-provider-folder}/{service-name}/{version-status}/{version}/openapi.json`

Example: Single service no versioning

- `openapi.yaml`

Example: Multiple services no versioning

- `openapi.Org1.Service1.yaml`
- `openapi.Org1.Service2.yaml`

Example: Single service with versioning

- `openapi.v1.yaml`
- `openapi.v2.yaml`

Example: Multiple service with versioning

- `openapi.Org1.Service1.v1.yaml`
- `openapi.Org1.Service1.v2.yaml`
- `openapi.Org1.Service2.v1.0.yaml`
- `openapi.Org1.Service2.v1.1.yaml`

Example: azureResourceProviderFolder is provided

- `arm-folder/AzureService/preview/2020-01-01.yaml`
- `arm-folder/AzureService/preview/2020-01-01.yaml`

### `examples-dir`

**Type:** `string`

Directory where the examples are located. Default: `{project-root}/examples`.

### `examples-directory`

**Type:** `string`

DEPRECATED. Use examples-dir instead

### `version`

**Type:** `string`

### `azure-resource-provider-folder`

**Type:** `string`

### `arm-types-dir`

**Type:** `string`

Path to the common-types.json file folder. Default: '${project-root}/../../common-types/resource-management'

### `new-line`

**Type:** `"crlf" | "lf"`

Set the newline character for emitting files.

### `omit-unreachable-types`

**Type:** `boolean`

Omit unreachable types. By default all types declared under the service namespace will be included. With this flag on only types references in an operation will be emitted.

### `version-enum-strategy`

**Type:** `string`

Decide how to deal with the Version enum when when `omit-unreachable-types` is not set. Default to 'omit'

### `include-x-typespec-name`

**Type:** `"inline-only" | "never"`

If the generated openapi types should have the `x-typespec-name` extension set with the name of the TypeSpec type that created it.
This extension is meant for debugging and should not be depended on.

### `use-read-only-status-schema`

**Type:** `boolean`

Create read-only property schema for lro status

### `emit-lro-options`

**Type:** `"none" | "final-state-only" | "all"`

Determine whether and how to emit x-ms-long-running-operation-options for lro resolution

### `arm-resource-flattening`

**Type:** `boolean`

Back-compat flag. If true, continue to emit `x-ms-client-flatten` in for some of the ARM resource properties.

### `emit-common-types-schema`

**Type:** `"never" | "for-visibility-changes"`

Determine whether and how to emit schemas for common-types rather than referencing them

## Decorators

### Autorest

- [`@example`](#@example)
- [`@useRef`](#@useref)

#### `@example`

`@example` - attaches example files to an operation. Multiple examples can be specified.

`@example` can be specified on Operations.

```typespec
@Autorest.example(pathOrUri: valueof string, title: valueof string)
```

##### Target

`Operation`

##### Parameters

| Name      | Type             | Description                              |
| --------- | ---------------- | ---------------------------------------- |
| pathOrUri | `valueof string` | path or Uri to the example file.         |
| title     | `valueof string` | name or description of the example file. |

#### `@useRef`

`@useRef` - is used to replace the TypeSpec model type in emitter output with a pre-existing named OpenAPI schema such as Azure Resource Manager common types.

`@useRef` can be specified on Models and ModelProperty.

```typespec
@Autorest.useRef(jsonRef: valueof string)
```

##### Target

`Model | ModelProperty`

##### Parameters

| Name    | Type             | Description                       |
| ------- | ---------------- | --------------------------------- |
| jsonRef | `valueof string` | path or Uri to an OpenAPI schema. |
