export const fullGitSha = "abc123abc123abc123abc123abc123abc123abc1";

export const swaggerHandWritten = JSON.stringify({});

export const swaggerTypeSpecGenerated = JSON.stringify({
  info: {
    "x-typespec-generated": [{ emitter: "@azure-tools/typespec-autorest" }],
  },
});

export const contosoTspConfig = `
parameters:
  "service-dir":
    default: "sdk/contosowidgetmanager"
  "dependencies":
    default: ""
emit:
  - "@azure-tools/typespec-autorest"
linter:
  extends:
    - "@azure-tools/typespec-azure-rulesets/data-plane"
options:
  "@azure-tools/typespec-autorest":
    azure-resource-provider-folder: "data-plane"
    emit-lro-options: "none"
    emitter-output-dir: "{project-root}/.."
    output-file: "{azure-resource-provider-folder}/{service-name}/{version-status}/{version}/widgets.json"
  "@azure-tools/typespec-python":
    package-dir: "azure-contoso-widgetmanager"
    namespace: "azure.contoso.widgetmanager"
    generate-test: true
    generate-sample: true
    flavor: azure
  "@azure-tools/typespec-csharp":
    package-dir: "Azure.Template.Contoso"
    clear-output-folder: true
    model-namespace: false
    namespace: "{package-dir}"
    flavor: azure
  "@azure-tools/typespec-ts":
    package-dir: "contosowidgetmanager-rest"
    package-details:
      name: "@azure-rest/contoso-widgetmanager-rest"
    flavor: azure
  "@azure-tools/typespec-java":
    package-dir: "azure-contoso-widgetmanager"
    namespace: com.azure.contoso.widgetmanager
    flavor: azure
  "@azure-tools/typespec-go":
    module: "github.com/Azure/azure-sdk-for-go/{service-dir}/{package-dir}"
    service-dir: "sdk/contosowidget"
    package-dir: "azmanager"
    module-version: "0.0.1"
    generate-fakes: true
    inject-spans: true
    single-client: true
    slice-elements-byval: true
  "@azure-tools/typespec-client-generator-cli":
    additionalDirectories:
      - "specification/contosowidgetmanager/Contoso.WidgetManager.Shared/"
`;

export const contosoReadme = `
# contosowidgetmanager

> see https://aka.ms/autorest
This is the AutoRest configuration file for Contoso.

## Getting Started

To build the SDKs for My API, simply install AutoRest via \`npm\` (\`npm install -g autorest\`) and then run:

> \`autorest readme.md\`
To see additional help and options, run:

> \`autorest --help\`
For other options on installation see [Installing AutoRest](https://aka.ms/autorest/install) on the AutoRest github page.

---

## Configuration

### Basic Information

These are the global settings for the containerstorage.

\`\`\`yaml
openapi-type: arm
openapi-subtype: rpaas
tag: package-2021-11-01
\`\`\`

### Tag: package-2021-11-01

These settings apply only when \`--tag=package-2021-11-01\` is specified on the command line.

\`\`\`yaml $(tag) == 'package-2021-11-01'
input-file:
  - Microsoft.Contoso/stable/2021-11-01/contoso.json
\`\`\`

### Tag: package-2021-10-01-preview

These settings apply only when \`--tag=package-2021-10-01-preview\` is specified on the command line.

\`\`\`yaml $(tag) == 'package-2021-10-01-preview'
input-file:
  - Microsoft.Contoso/preview/2021-10-01-preview/contoso.json
\`\`\`

---
`;
