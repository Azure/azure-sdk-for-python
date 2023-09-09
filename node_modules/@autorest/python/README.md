# Generating with Autorest for Python

See [here](https://github.com/Azure/autorest.python/wiki/Generating-with-autorest-for-python-v5.0.0) for Python-specific docs, and [here] for general docs

# Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### Autorest plugin configuration

- Please don't edit this section unless you're re-configuring how the powershell extension plugs in to AutoRest
  AutoRest needs the below config to pick this up as a plug-in - see https://github.com/Azure/autorest/blob/master/docs/developer/architecture/AutoRest-extension.md

#### Python code gen

```yaml !$(multiapiscript) && !$(multiclientscript)
# default values for version tolerant and black
black: true
```

```yaml !$(low-level-client)
version-tolerant: true
```

```yaml !$(low-level-client) && !$(version-tolerant)
modelerfour:
  group-parameters: true
  flatten-models: true
  flatten-payloads: true
```

```yaml $(postprocess)
allow-no-input: true
```

```yaml !$(multiapiscript) && !$(multiclientscript)
pass-thru:
  - model-deduplicator
  - subset-reducer
version: ~3.8.1
use-extension:
  "@autorest/modelerfour": ~4.23.5

modelerfour:
  resolve-schema-name-collisons: true
  always-create-content-type-parameter: true
  multiple-request-parameter-flattening: false
  naming:
    parameter: snakecase
    property: snakecase
    operation: snakecase
    operationGroup: pascalcase
    choice: pascalcase
    choiceValue: uppercase
    constant: snakecase
    constantParameter: snakecase
    type: pascalcase
    local: _ + snakecase
    global: snakecase
    preserve-uppercase-max-length: 6
    override:
      $host: $host
      base64: base64
      IncludeAPIs: include_apis

pipeline:
  python:
    # Doesn't process anything, just makes it so that the 'python:' config section is loaded and available for the next plugins.
    pass-thru: true
    input: modelerfour/identity

  python/m2r:
    input: python

  python/m4reformatter:
    input: python/m2r

  python/preprocess:
    input: python/m4reformatter

  python/codegen:
    input: python/preprocess
    output-artifact: python-files

  python/codegen/emitter:
    input: codegen
    scope: scope-codegen/emitter

scope-codegen/emitter:
  input-artifact: python-files
  output-uri-expr: $key

output-artifact: python-files
```

# Multiapi script pipeline

```yaml $(multiapiscript)
pipeline:
  python/multiapiscript:
    scope: multiapiscript
    output-artifact: python-files

  python/multiapiscript/emitter:
    input: multiapiscript
    scope: scope-multiapiscript/emitter

scope-multiapiscript/emitter:
  input-artifact: python-files
  output-uri-expr: $key

output-artifact: python-files
```

# Black script pipeline

```yaml $(black)
pipeline:
  python/black:
    scope: black
    input: python/codegen
    output-artifact: python-files

  python/black/emitter:
    input: black
    scope: scope-black/emitter

scope-black/emitter:
  input-artifact: python-files
  output-uri-expr: $key

output-artifact: python-files
```

# Post-process customized code for mypy pipeline

```yaml $(postprocess)
pipeline:
  python/postprocess:
    scope: postprocess
    output-artifact: python-files

  python/postprocess/emitter:
    input: postprocess
    scope: scope-postprocess/emitter

scope-postprocess/emitter:
  input-artifact: python-files
  output-uri-expr: $key

output-artifact: python-files
```

# Multi Client pipeline

```yaml $(multiclientscript)
pipeline:
  python/multiclientscript:
    scope: multiclientscript
    output-artifact: python-files

  python/multiclientscript/emitter:
    input: multiclientscript
    scope: scope-multiclientscript/emitter

scope-multiclientscript/emitter:
  input-artifact: python-files
  output-uri-expr: $key

output-artifact: python-files
```

# Help

```yaml
help-content:
  python: # type: Help as defined in autorest-core/help.ts
    activationScope: python
    categoryFriendlyName: Python Generator
    settings:
      - key: python-sdks-folder
        description: The path to the root directory of your azure-sdk-for-python clone. Be sure to note that we include `sdk` in the folder path.
      - key: black
        description: Runs black formatting on your generated files. Defaults to `false`.
        type: string
      - key: basic-setup-py
        description: Whether to generate a build script for setuptools to package your SDK.  Defaults to `false`, generally not suggested if you are going to wrap the generated code
        type: bool
      - key: multiapi
        description: Whether to generate a multiapi client.
        type: bool
      - key: default-api
        description: In the case of `--multiapi`, you can override the default service API version with this flag. If not specified, we use the latest GA service version as the default API.
        type: string
      - key: no-namespace-folders
        description: Specify if you don't want pkgutil-style namespace folders. Defaults to `false`.
        type: bool
      - key: credential-default-policy-type
        description: Specify the default credential policy (authentication policy) for your client. Use in conjunction with `--add-credential`. Currently only supports `BearerTokenCredentialPolicy`, `ARMChallengeAuthenticationPolicy` and `AzureKeyCredentialPolicy`. Default value is `BearerTokenCredentialPolicy`(data-plan)/`ARMChallengeAuthenticationPolicy`(mgmt-plan). `--credential-scopes` is tied with `BearerTokenCredentialPolicy` and `ARMChallengeAuthenticationPolicy`, do not pass them in if you want `AzureKeyCredentialPolicy`.
        type: string
      - key: credential-key-header-name
        description: The name of the header which will pass the credential. Use if you have `--credential-default-policy-type` set to `AzureKeyCredentialPolicy`. For example, if generating cognitive services code, you might use `--credential-key-header-name=Ocp-Apim-Subscription-Key`
        type: string
```

<!-- LINKS -->

[python_docs]: https://github.com/Azure/autorest.python/tree/main/docs/readme.md
[main_docs]: https://github.com/Azure/autorest/tree/master/docs
