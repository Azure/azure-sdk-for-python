# Contoso.WidgetManager

> see https://aka.ms/autorest

This is the AutoRest configuration file for Contoso.WidgetManager.

## Configuration

### Basic Information

This is a TypeSpec project so we only want to readme to default the default tag and point to the outputted swagger file.
This is used for some tools such as doc generation and swagger apiview generation it isn't used for SDK code gen as we
use the native TypeSpec code generation configured in the tspconfig.yaml file.

```yaml
openapi-type: data-plane
tag: package-2022-12-01
```

### Tag: package-2022-12-01

These settings apply only when `--tag=package-2022-12-01` is specified on the command line.

```yaml $(tag) == 'package-2022-12-01'
input-file:
  - Azure.Contoso.WidgetManager/stable/2022-12-01/widgets.json
```

Define the tag twice to test code that handles duplicate tag definitions.

```yaml $(tag) == 'package-2022-12-01'
input-file:
  - Azure.Contoso.WidgetManager/stable/2022-12-01/widgets.json
```

### Suppress non-TypeSpec SDK related linting rules

These set of linting rules aren't applicable to the new TypeSpec SDK code generators so suppressing them here. Eventually we will
opt-out these rules from running in the linting tools for TypeSpec generated swagger files.

```yaml
suppressions:
  - code: AvoidAnonymousTypes
  - code: PatchInOperationName
  - code: OperationIdNounVerb
  - code: RequiredReadOnlyProperties
  - code: SchemaNamesConvention
  - code: SchemaDescriptionOrTitle
```

### Tag: package-2022-11-01-preview

These settings apply only when `--tag=package-2022-11-01-preview` is specified on the command line.

```yaml $(tag) == 'package-2022-11-01-preview'
input-file:
  - Azure.Contoso.WidgetManager/preview/2022-11-01-preview/widgets.json
```

### Suppress non-TypeSpec SDK related linting rules

These set of linting rules aren't applicable to the new TypeSpec SDK code generators so suppressing them here. Eventually we will
opt-out these rules from running in the linting tools for TypeSpec generated swagger files.

```yaml
suppressions:
  - code: AvoidAnonymousTypes
  - code: PatchInOperationName
  - code: OperationIdNounVerb
  - code: RequiredReadOnlyProperties
  - code: SchemaNamesConvention
  - code: SchemaDescriptionOrTitle
```

### Suppress rules that might be fixed

These set of linting rules we expect to fixed in typespec-autorest emitter but for now suppressing.
Github issue filed at https://github.com/Azure/typespec-azure/issues/2762

```yaml
suppressions:
  - code: LroExtension
  - code: SchemaTypeAndFormat
  - code: PathParameterSchema
```
