# Generating Python SDK Integration Test

Integration test can be generated from swagger examples using **autorest**.

## Prerequisites

You can install autorest following generic autorest documentation.
The best way of using **autorest.cli** is Docker container.

You need to clone following directories locally. I have added Python SDK here as well, it's not necessary, but may be useful.

    git clone https://github.com/Azure/azure-rest-api-specs.git
    git clone https://github.com/Azure/azure-sdk-for-python.git

For simplicity let's assume they are cloned under **c:\dev** directory on Windows machine.

The easiest way to use **autorest.cli** is the container:

    docker run -it --rm -v c:\dev:/_ mcr.microsoft.com/azure-cli/tools

You can also use the container without mapping your local folders:

    docker run -it --rm mcr.microsoft.com/azure-cli/tools

but you will need to make sure embedded copy of repositories are up to date:

    cd /_/azure-sdk-for-python; git pull
    cd /_/azure-rest-api-specs; git pull

## Configuration in **readme.cli.md** File

>NOTE: The same configuration will be used to generate Azure CLI commands tests.

In order to generate Python integration test you will need to create **readme.cli.md** file next to **readme.md** file in Azure REST API specification repository:

The minimal file should have following format:

    ## CLI

    These settings apply only when `--cli` is specified on the command line.

    ``` yaml $(cli)
    cli:
      namespace: azure.mgmt.attestation
    ```

## Generating Test

Run:

    autorest --cli --use-extension="{'@autorest/cli':'latest'}" --python-integration-test --output-folder=/_/azure-sdk-for-python /_/azure-rest-api-specs/specification/attestation/resource-manager/readme.md

You will get output like this:

    AutoRest code generation utility [version: 2.0.4407; node: v10.15.0]
    (C) 2018 Microsoft Corporation.
    https://aka.ms/autorest
    Loading AutoRest core      '/root/.autorest/@microsoft.azure_autorest-core@2.0.4407/node_modules/@microsoft.azure/autorest-core/dist' (2.0.4407)
    Loading AutoRest extension '@autorest/cli' (latest->0.1.889)
    Loading AutoRest extension '@microsoft.azure/autorest.modeler' (2.3.45->2.3.45)
    WARNING:
    WARNING: NO TEST SCENARIO PROVIDED - DEFAULT WILL BE USED
    WARNING: ADD FOLLOWING SECTION TO readme.cli.md FILE TO MODIFY IT
    WARNING: --------------------------------------------------------
    WARNING:   test-scenario:
    WARNING:     - name: AttestationProviders_Create
    WARNING:     - name: AttestationProviders_Get
    WARNING:     - name: AttestationProviders_ListByResourceGroup
    WARNING:     - name: AttestationProviders_List
    WARNING:     - name: Operations_List
    WARNING:     - name: AttestationProviders_Delete
    WARNING: --------------------------------------------------------

Default test-scenario was generated, you can copy and paste it into **readme.cli.md** file:


    ## CLI

    These settings apply only when `--cli` is specified on the command line.

    ``` yaml $(cli)
    cli:
      namespace: azure.mgmt.attestation
    test-scenario:
    - name: AttestationProviders_Create
    - name: AttestationProviders_Get
    - name: AttestationProviders_ListByResourceGroup
    - name: AttestationProviders_List
    - name: Operations_List
    - name: AttestationProviders_Delete
    ```

Now you can rerun **autorest** command and warning won't be visible any longer.
You can rearrange sequence or disable particular tests.

## Running Test

To run tests, refer to the documentation at
[/doc/dev/mgmt/tests.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/tests.md). Most test
suites in the Azure SDK have been migrated to use the Azure SDK test proxy, but some libraries that have inactive tests
may still be using an older, deprecated system. The
[test proxy migration guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md)
describes the differences between the systems and their requirements.

## Fixing Test

It's obvious that when running test for the first time something is not going to work.

The best approach is to:
- fix the test manually
- when the test is fully working backpropagate any changes to readme file and examples in swagger.
