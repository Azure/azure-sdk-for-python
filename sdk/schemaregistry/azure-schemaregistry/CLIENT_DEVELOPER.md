# Azure Schema Registry Client Library Developer Guide

This guide is intended for developers contributing to the Azure Schema Registry Python client library. It provides information on setting up your development environment, regenerating the client from TypeSpec, understanding the code structure, running tests, and contributing to the codebase.

## Setting Up Development Environment

### Prerequisites

- Python version [supported by the client library](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)
- Git
- pip and setuptools
- Node.js and npm (for TypeSpec client generation)
- Azure subscription to create Schema Registry resources

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Azure/azure-sdk-for-python.git
   cd azure-sdk-for-python/sdk/schemaregistry/azure-schemaregistry
   ```

2. Create a virtual environment:
   ```bash
   # Linux/macOS
   python -m venv .venv && source .venv/bin/activate && pip install -r dev_requirements.txt

   # Windows PowerShell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r dev_requirements.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Regenerating the Client from TypeSpec

The Azure Schema Registry client is generated from TypeSpec definitions. The TypeSpec files are maintained in the [Azure REST API Specs repository](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/schemaregistry/SchemaRegistry).

### Prerequisites for Code Generation

1. Install the TypeSpec client generator:
   ```bash
   npm install -g @azure-tools/typespec-client-generator-cli
   ```

2. Ensure you have the latest TypeSpec definitions by checking the [specification directory](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/schemaregistry/SchemaRegistry).

### Regeneration Process

The client regeneration is controlled by the `tsp-location.yaml` file in the root of this package directory. This file specifies:
- The TypeSpec specification repository (`Azure/azure-rest-api-specs`)
- The specific commit hash to use
- The directory path (`specification/schemaregistry/SchemaRegistry`)

To regenerate the client, follow the [`tsp-client` docs](https://github.com/Azure/azure-sdk-tools/tree/main/tools/tsp-client/README.md).

## Code Structure

The Azure Schema Registry client library follows a hybrid approach with both generated and handwritten code:

### Generated Code

The following files are automatically generated from TypeSpec and should **not** be manually edited:
- `_client.py` - Main client implementation
- `_configuration.py` - Client configuration
- `_model_base.py` - Base classes for models
- `_operations/` - Generated operation classes
- `_serialization.py` - Serialization utilities
- `_vendor.py` - Vendored dependencies
- `models/*.py` (except `_patch.py`) - Data models
- `aio/_client.py` - Async client implementation
- `aio/_configuration.py` - Async client configuration

### Handwritten Code

The following files contain handwritten customizations and extensions:

#### `_patch.py` Files
- `azure/schemaregistry/_patch.py` - Sync client customizations
- `azure/schemaregistry/aio/_patch.py` - Async client customizations
- `azure/schemaregistry/models/_patch.py` - Model customizations

These files allow you to:
- Add custom methods to generated classes
- Override generated method implementations
- Add custom models and enums
- Extend functionality while preserving generated code

#### Encoder Implementation
- `azure/schemaregistry/encoder/jsonencoder/` - Complete handwritten JSON Schema encoder implementation
  - `_json_encoder.py` - Main encoder/decoder logic
  - `_exceptions.py` - Custom exceptions
  - `__init__.py` - Public API

The encoder directory contains entirely handwritten code that provides schema-based encoding and decoding capabilities using the Schema Registry client.

### Code Customization Guidelines

When adding handwritten code:
1. Use `_patch.py` files for extending generated classes
2. Follow the existing patterns for method signatures and documentation
3. Import required types from generated modules
4. Use the `patch_sdk()` function to register customizations
5. Ensure async and sync implementations remain consistent

## Related Libraries

### Azure Schema Registry Avro Encoder

The [azure-schemaregistry-avroencoder](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroencoder) is an extension library that provides Avro-specific encoding and decoding capabilities. It builds on top of this Schema Registry client to provide:

- Avro schema-based serialization and deserialization
- Integration with Apache Avro
- Optimized performance for Avro payloads

For detailed usage and examples, see the [Avro Encoder README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroencoder/README.md).

## Running Tests

### Live Tests

1. Login to Azure:
   ```bash
   az login
   ```

2. Set required environment variables (or create a `.env` file):

   The following need to be set to run live tests locally:
   ```
   SCHEMAREGISTRY_AVRO_FULLY_QUALIFIED_NAMESPACE
   SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE
   SCHEMAREGISTRY_CUSTOM_FULLY_QUALIFIED_NAMESPACE
   SCHEMAREGISTRY_GROUP
   AZURE_TEST_RUN_LIVE=true
   ```
  * Each namespace is Standard tier. Each namespace has one schema group, with schema type set as per namespace.
  * The schema group name is the same across namespaces. 
  
   If using CLI:
   ```
   AZURE_TEST_USE_CLI_AUTH=true
   ```

   OR

   If using pwsh:
   ```
   AZURE_TEST_USE_PWSH_AUTH=true
   ```

   Note: To run tests in playback mode instead of live mode, set:
   ```
   AZURE_TEST_RUN_LIVE=false
   ```
3. Install test dependencies and the package in editable mode:
   ```bash
   pip install -r dev_requirements.txt
   pip install -e .
   ```

   **Note**: If the azure-schemaregistry-avroencoder package is installed, you may encounter import errors due to issues identifying separate packages with shared namespace. To work around this, you will need to install the client library in non-editable mode:
   ```bash
   pip install .
   ```
   Note: You'll need to rerun this command after making changes to the package.

4. Run tests:
   ```bash
   # Run all tests
   pytest tests

   # Run specific test
   pytest tests/test_specific_test.py::test_specific_function
   ```

5. Updating recordings:

   To pull test recordings from assets repo:
   ```bash
   python azure-sdk-for-python/scripts/manage_recordings.py restore -p sdk/schemaregistry/azure-schemaregistry/assets.json
   ```

   To push after recording tests in live mode:
   ```bash
   python scripts/manage_recordings.py push -p sdk/schemaregistry/azure-schemaregistry/assets.json
   ```

### Common Test Issues

- **Authentication errors**: Ensure Azure CLI is logged in (`az login`) or service principal credentials are correctly set
- **Resource not found**: Verify that the Schema Registry namespace and group exist
- **Permission errors**: Ensure the authentication principal has appropriate Schema Registry permissions

## Performance Testing

Performance tests are located in `tests/perfstress_tests/` and help measure client library performance under various conditions.

### Setup for Performance Tests

1. Install performance test dependencies:
   ```bash
   pip install -r dev_requirements.txt
   pip install -e .
   ```

2. Set environment variables:
   ```bash
   SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE=<your-namespace>.servicebus.windows.net
   SCHEMAREGISTRY_GROUP=<your-schema-group>
   ```

### Running Performance Tests

1. Navigate to the tests directory:
   ```bash
   cd tests/
   ```

2. List available performance tests:
   ```bash
   perfstress
   ```

3. Run specific performance tests:
   ```bash
   # Example: Run schema registration test
   perfstress RegisterSchemaTest --duration=30 --parallel=5

   # Example: Run schema retrieval test
   perfstress GetSchemaByIdTest --duration=30 --parallel=10 --num-schemas=100
   ```

### Performance Test Options

Common options for all performance tests:
- `--duration=30` - Number of seconds to run operations (default: 10)
- `--iterations=1` - Number of test iterations (default: 1)
- `--parallel=1` - Number of parallel operations (default: 1)
- `--warm-up=5` - Warm-up time in seconds (default: 5)
- `--sync` - Run synchronous tests instead of async (default: async)

Schema Registry specific options:
- `--schema-size=150` - Size of each schema in bytes (default: 150)
- `--num-schemas=10` - Number of schemas to use in tests (default: 10)

For detailed performance testing setup and resource requirements, see the [Performance Tests README](tests/perfstress_tests/README.md).

## Additional Resources

- [Azure Schema Registry Documentation](https://docs.microsoft.com/azure/event-hubs/schema-registry-overview)
- [Azure SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [TypeSpec Documentation](https://typespec.io/)
- [Schema Registry Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry/samples)
- [Azure Schema Registry REST API Reference](https://docs.microsoft.com/rest/api/schemaregistry/)
- [Event Hubs and Schema Registry Quickstart](https://learn.microsoft.com/azure/event-hubs/create-schema-registry)