## AZ

These settings apply only when `--az` is specified on the command line.

``` yaml $(az)
az:
  extensions: ml
  namespace: azure.mgmt.machinelearningservices
  package-name: azure-mgmt-machinelearningservices
az-output-folder: $(azure-cli-extension-folder)/src/machinelearningservices
python-sdk-output-folder: "$(az-output-folder)/azext_mlv2/vendored_sdks/machinelearningservices"

cli:
    cli-directive:
      - where:
            param: workspaceName
        set:
            default-config-key: workspace
      - where:
          type: CodeJobProperties
          property: environmentConfiguration
        flatten: false
      - where: # Block all group/operations to avoid accidental group/operation to show up
          group: "*"
          op: "*"
        hidden: true

directive:
  - where:
      group: ml virtual-machine-size
    set:
      group: ml vm-size
```