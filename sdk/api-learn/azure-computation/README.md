# Azure Computation client library for Python SDK Training

This is a demonstration API for the API design training tutorial.
We will use this example "Computation" service to practice recognizing common API patterns and applying the design guidelines.

## Tutorial Task

The objective of this tutorial is to design a "public API" or "customization layer" for this example service.
An SDK namespace, `azure-computation`, has already been set up, with directory structure and packaging scripts in place.
The swagger specification (found at `swagger/computation.json`), and the auto-generated layer has already been pre-generated, and can be found in the `_generated` directory.

1. Follow the steps in the [API Design tutorial Setup](https://github.com/Azure/azure-sdk-pr/blob/1aa822c70286933fac59af902685943637f0177b/training/azure-sdk-apis/tutorials/api-design-intro/setup/setup-python.md#setup-for-api-design-tutorial-python) for setting up the environment for this project.
2. Follow the steps in the [API Design tutorial](https://github.com/Azure/azure-sdk-pr/blob/1aa822c70286933fac59af902685943637f0177b/training/azure-sdk-apis/tutorials/api-design-intro/api-design-intro/api-design-intro-python.md#create-the-public-api-python) for considering hero scenarios, and using them to build a public API.
3. Remember the common-patterns that we covered in the API Design presentation and see whether and how they can be applied to the API. If you wish to use one of these patterns - take a look through the [Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html#) for specifics.
    - [Service Client](https://azure.github.io/azure-sdk/python_design.html#clients)
    - [Authentication and `azure-identity`](https://azure.github.io/azure-sdk/python_design.html#authentication)
    - [HTTP Abractions](https://azure.github.io/azure-sdk/python_design.html#service-operations)
    - [Paged Collections](https://azure.github.io/azure-sdk/python_implementation.html#paged)
    
      Examples:
      - [Azure Search](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/search/azure-search-documents)
        - [`list_index_names`](https://github.com/Azure/azure-sdk-for-python/blob/19db374e7ea80f1d034f547e02750b7e3b3264a7/sdk/search/azure-search-documents/azure/search/documents/indexes/_internal/_search_index_client.py#L98)
        - [async `list_index_names`](https://github.com/Azure/azure-sdk-for-python/blob/19db374e7ea80f1d034f547e02750b7e3b3264a7/sdk/search/azure-search-documents/azure/search/documents/indexes/_internal/aio/_search_index_client.py#L99)
      - [Form Recognizer](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer)
        - [`list_custom_models`](https://github.com/Azure/azure-sdk-for-python/blob/19db374e7ea80f1d034f547e02750b7e3b3264a7/sdk/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_form_training_client.py#L208) 
        - [async `list_custom_models`](https://github.com/Azure/azure-sdk-for-python/blob/19db374e7ea80f1d034f547e02750b7e3b3264a7/sdk/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/aio/_form_training_client_async.py#L224)

    - [Long Running Operations](https://azure.github.io/azure-sdk/python_implementation.html#lropoller)

      Examples:
      - [Form Recognizer](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer)
        - [`begin_recognize_receipts`](https://github.com/Azure/azure-sdk-for-python/blob/f451b9ec96a8317b8a292bbc664653c04cc62b2c/sdk/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_form_recognizer_client.py#L91)
        - [async `begin_recognize_receipts`](https://github.com/Azure/azure-sdk-for-python/blob/f451b9ec96a8317b8a292bbc664653c04cc62b2c/sdk/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/aio/_form_recognizer_client_async.py#L96)
      - [KeyVault Secrets](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets)
        - [`begin_delete_secret`](https://github.com/Azure/azure-sdk-for-python/blob/f451b9ec96a8317b8a292bbc664653c04cc62b2c/sdk/keyvault/azure-keyvault-secrets/azure/keyvault/secrets/_client.py#L296)
        - [async `begin_delete_secret`](https://github.com/Azure/azure-sdk-for-python/blob/f451b9ec96a8317b8a292bbc664653c04cc62b2c/sdk/keyvault/azure-keyvault-secrets/azure/keyvault/secrets/aio/_client.py#L266)

4. If you wish to make adjustments to the swagger specification, follow the instructions in the [API Design tutorial Review](https://github.com/Azure/azure-sdk-pr/blob/1aa822c70286933fac59af902685943637f0177b/training/azure-sdk-apis/tutorials/api-design-intro/review-the-api/review-the-api-python.md#regenerate-the-code) for regenerating the code.
5. Follow the instructions in the [API Design tutorial Review](https://github.com/Azure/azure-sdk-pr/blob/1aa822c70286933fac59af902685943637f0177b/training/azure-sdk-apis/tutorials/api-design-intro/review-the-api/review-the-api-python.md#regenerate-the-code) for generating an API stubfile and uploading it to APIView.

## API Review

We will follow-up this tutorial activity with a "mock arch board review" of the APIs. For this session, have an example hero scenario ready (they need not be functioning code) and your API layout in APIView.

## Structure of the example Computation service API

### Operations in the Computation service

This service has 5 APIs.

- GET `/ComputeNodes`

  Get a list of available compute nodes.
- GET `/ComputeNodes/{nodeName}`

  Get the properties of a single compute node.
- PUT `/ComputeNodes/{nodeName}`

  Create a new compute node.
- POST `/ComputeNodes/{nodeName}/computePi`

  Start a compute pi operation on a compute node.
- GET `/operation/{operationId}`

  Get the compute operation status.

### Model types
- `ComputeNode`

  Base compute node object.
- `LinuxComputeNote`

  A Linux flavour of the compute node object.

- `WindowsComputeNode`

  A Windows flavour of the compute node object.

- `PageOfComputeNodes`

  A collection type that holds a list of compute nodes.

- `Operation`

  Properties, including the status on a service-side operation.
- `Error`

  A complex error structure that contains information for a failed request.

