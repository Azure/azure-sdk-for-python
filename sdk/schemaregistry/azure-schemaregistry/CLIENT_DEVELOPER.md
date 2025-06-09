# Azure Schema Registry Client Library Developer Guide

This guide is intended for developers contributing to the Azure Schema Registry Python client library. It provides information on setting up your development environment, regenerating the client from TypeSpec, understanding the codebase structure, running tests, and contributing to the codebase.

## Client Generation from TypeSpec

This client library is generated from TypeSpec definitions. The TypeSpec definition can be found at:
https://github.com/Azure/azure-rest-api-specs/tree/main/specification/schemaregistry/SchemaRegistry

### Prerequisites for Generation

Before regenerating the client, ensure you have the following installed:
- Node.js and npm
- Python 3.7 or later
- Git

### Installing tsp-client

Install the TypeSpec client generator CLI globally:
```bash
npm install -g @azure-tools/typespec-client-generator-cli
```

### Regenerating the Client

To regenerate the client from the latest TypeSpec definition:

1. Navigate to the package directory:
   ```bash
   cd sdk/schemaregistry/azure-schemaregistry
   ```

2. Run the TypeSpec client generator:
   ```bash
   tsp-client update
   ```

   This command will:
   - Read the `tsp-location.yaml` file to determine the TypeSpec source location
   - Download the latest TypeSpec definition from the specified commit
   - Generate the Python client code
   - Update all generated files while preserving handwritten code

3. Review the generated changes and ensure all tests pass after regeneration

### TypeSpec Configuration

The TypeSpec source configuration is stored in `tsp-location.yaml`:
- **repo**: Azure/azure-rest-api-specs
- **directory**: specification/schemaregistry/SchemaRegistry
- **commit**: The specific commit hash used for generation

## Generated vs Handwritten Code

Understanding which code is generated versus handwritten is crucial for development:

### Handwritten Code (Do NOT modify via TypeSpec generation)
- **All code under `azure/schemaregistry/encoder/jsonencoder`**: This is handwritten code for the JSON encoder extension library
- **`_patch.py` files**: These contain handwritten customizations and extensions to the generated client
- **Test files**: All test code is handwritten
- **Samples**: All sample code is handwritten

### Generated Code (Will be overwritten during regeneration)
- **All other Python files** in the main package directory, including:
  - `_client.py`
  - `_configuration.py`
  - `_model_base.py`
  - `_serialization.py`
  - `_types.py`
  - `_vendor.py`
  - Files in `_operations/` directory
  - Files in `models/` directory
  - Files in `aio/` directory (except handwritten patches)

**Important**: Never directly modify generated code files. Instead, use `_patch.py` files to add customizations.

## Extension Libraries

### Azure Schema Registry Avro Encoder

The `azure-schemaregistry-avroencoder` is an extension library that uses this client as a backend for Avro serialization and deserialization. This extension library provides:
- Avro-specific encoding and decoding capabilities
- Integration with the Schema Registry service for schema management
- Type-safe serialization for Avro schemas

For more information about the Avro encoder, see its [README](../azure-schemaregistry-avroencoder/README.md).

## Setting Up Development Environment

### Prerequisites

- Python version [supported by the client library](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)
- Git
- pip and setuptools
- Azure subscription with Schema Registry service

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

## Running Tests

### Unit Tests

Run unit tests (no Azure resources required):
```bash
# Run all unit tests
pytest tests/test_schema_registry.py tests/test_json_encoder.py

# Run specific test
pytest tests/test_schema_registry.py::TestSchemaRegistry::test_specific_method
```

### Async Tests

Run async unit tests:
```bash
# Run all async tests
pytest tests/async_tests/

# Run specific async test
pytest tests/async_tests/test_schema_registry_async.py::TestSchemaRegistryAsync::test_specific_method
```

### Live Tests

Live tests require an Azure Schema Registry resource:

1. Create test resources:
   ```bash
   # Login to Azure
   az login

   # Set up test resources (from repo root)
   eng/common/TestResources/New-TestResources.ps1 sdk/schemaregistry/test-resources.json -ServiceDirectory schemaregistry
   ```

2. Set environment variables:
   ```bash
   export AZURE_TEST_RUN_LIVE=true
   export AZURE_TEST_USE_CLI_AUTH=true
   export AZURE_SUBSCRIPTION_ID=<your-subscription-id>
   export SCHEMAREGISTRY_RESOURCE_GROUP=<your-resource-group>
   export SCHEMAREGISTRY_ENDPOINT=<your-schema-registry-endpoint>
   ```

3. Run live tests:
   ```bash
   # Run all live tests
   pytest tests/ --tb=short

   # Run live tests with output
   pytest -s tests/test_schema_registry.py::TestSchemaRegistry::test_register_schema
   ```

### Performance Tests

Performance tests are located in `tests/perfstress_tests/`. 

1. Navigate to the performance test directory:
   ```bash
   cd tests/perfstress_tests
   ```

2. Review the performance test README:
   ```bash
   cat README.md
   ```

3. Run performance tests:
   ```bash
   # Example: Run schema registration performance test
   python register_schema.py --duration=10 --parallel=5
   ```

For detailed performance testing instructions, see the [Performance Test README](tests/perfstress_tests/README.md).

## Testing Best Practices

- Always run unit tests before submitting changes
- Run async tests to ensure async compatibility
- For live tests, use test resources that can be safely modified
- Performance tests should be run when making changes that could affect performance
- Use the test proxy for recording and playback when applicable

For comprehensive testing guidance, refer to the [Azure SDK Testing Guide](../../../doc/dev/tests.md).

## Additional Resources

- [Azure Schema Registry Service Documentation](https://docs.microsoft.com/azure/event-hubs/schema-registry-overview)
- [Azure SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [TypeSpec Documentation](https://typespec.io/)
- [Schema Registry Samples](samples/)
- [Azure SDK for Python Contributing Guide](../../../CONTRIBUTING.md)
- [Azure Schema Registry REST API Reference](https://docs.microsoft.com/rest/api/schemaregistry/)

## Troubleshooting

### Common Issues

- **TypeSpec generation fails**: Ensure you have the latest version of `@azure-tools/typespec-client-generator-cli` installed
- **Test authentication errors**: Verify your Azure CLI authentication with `az account show`
- **Import errors**: Try reinstalling the package with `pip install -e .`
- **Schema Registry connection issues**: Verify your endpoint URL and authentication credentials

For additional support, refer to the [Azure SDK for Python support documentation](../../../SUPPORT.md).