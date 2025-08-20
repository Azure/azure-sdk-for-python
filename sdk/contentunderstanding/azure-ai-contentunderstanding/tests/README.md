# Testing Guide for Azure AI Content Understanding

This guide explains how to run tests for the Azure AI Content Understanding SDK.

## Key concepts

The tests cover all major Azure AI Content Understanding capabilities including:
- Content analysis and extraction
- Content classification
- Face recognition and person management
- Directory and person operations
- Face detection and similarity matching

## Getting started

### Azure Content Understanding Resource

To run tests, you need an Azure AI Foundry resource with Content Understanding capabilities enabled. The tests will use this resource to validate the SDK functionality.

### Running Samples

To run the samples in the `samples/` directory:

1. **Install dependencies:**
   ```bash
   cd samples
   # Option A: Use the helper script (recommended)
   python install_deps.py
   
   # Option B: Install manually
   pip install -r requirements.txt
   ```

2. **Set up authentication** (see sections below)

3. **Run any sample:**
   ```bash
   python person_directories_get_face.py
   ```

### Install the package

#### Prerequisites

- Python 3.8+
- Virtual environment with required dependencies
- Azure credentials configured

#### Dependencies

1. **Install dependencies:**
   ```bash
   pip install -r dev_requirements.txt
   pip install -e .
   ```

2. **Configure credentials** by setting one of these options:

   **Option A: API Key (Recommended for testing)**
   ```bash
   export AZURE_CONTENT_UNDERSTANDING_KEY="your_api_key"
   export AZURE_CONTENT_UNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
   ```

   **Option B: DefaultAzureCredential (Recommended)**
   - Use Azure CLI (interactive):
     ```bash
     az login
     export AZURE_CONTENT_UNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
     ```
   - Or set environment variables for a Service Principal:
     ```bash
     export AZURE_TENANT_ID="your_tenant_id"
     export AZURE_CLIENT_ID="your_client_id"
     export AZURE_CLIENT_SECRET="your_client_secret"
     export AZURE_CONTENT_UNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
     ```

### Using a .env file

Tests automatically load environment variables from a `.env` file.

- Copy the sample to a `.env` file at the repository root (preferred) or this package directory:
  ```bash
  # From repository root
  cp sdk/contentunderstanding/azure-ai-contentunderstanding/samples/env.sample .env
  ```

- Update `.env` with the following keys (minimal):
  ```bash
  # Required
  AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource-name.services.ai.azure.com/

  # Optional (only for key-based auth; DefaultAzureCredential is recommended)
  AZURE_CONTENT_UNDERSTANDING_KEY=

  # Test runtime controls
  # Use playback when false; use live when true
  AZURE_TEST_RUN_LIVE=false
  # When running live, set to true to skip recording new assets
  AZURE_SKIP_LIVE_RECORDING=false
  ```

### Quick Start with Tests

1. **Set up authentication**:
   ```bash
   # Use Azure CLI for authentication (recommended - secure)
   az login
   
   # Or set environment variables for API key authentication
   export AZURE_CONTENT_UNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
   export AZURE_CONTENT_UNDERSTANDING_KEY="your_api_key"  # Optional, not recommended for production
   ```

2. **Install dependencies**:
   ```bash
   pip install -r dev_requirements.txt
   pip install -e .
   ```

3. **Run tests**:
   ```bash
   # Run all tests
   pytest tests/
   ```

### Running Tests

#### Playback Tests (from recordings)
```bash
export AZURE_TEST_RUN_LIVE=false
pytest tests/
```

#### Live Tests (with recording)
```bash
export AZURE_TEST_RUN_LIVE=true
unset AZURE_SKIP_LIVE_RECORDING
pytest tests/
```

#### Live Tests (skip recording new assets)
```bash
export AZURE_TEST_RUN_LIVE=true
export AZURE_SKIP_LIVE_RECORDING=true
pytest tests/
```

#### Test Options
```bash
# Show print statements
pytest tests/ -s

# Run with multiple processes
pytest tests/ -n auto

# Run tests matching a pattern
pytest tests/ -k "add_person"
```

### Test Structure

- **Synchronous tests**: `test_content_understanding_*.py`
- **Asynchronous tests**: `test_content_understanding_*_async.py`
- **Test data**: `tests/test_data/`
- **Test helpers**: `tests/test_helpers.py`

### Test Proxy

Tests use the Azure SDK Test Proxy for recording HTTP interactions. The proxy automatically:
- Records live test runs
- Sanitizes sensitive information
- Enables playback testing

## Examples

### Comprehensive API Tests

The test suite provides comprehensive testing of all Azure AI Content Understanding API operations, demonstrating proper authentication, error handling, and resource management.

## Sample Categories

### Content Analyzers

Tests validate content analysis operations including:
- Document analysis and structure extraction
- Binary file processing (PDFs, images, documents)
- Custom analyzer creation and management
- Analysis result retrieval and file downloads

### Content Classifiers

Tests cover content classification functionality:
- Text and binary content classification
- Classifier creation, updates, and deletion
- Classification operation monitoring
- Result retrieval and validation

### Face Recognition & Person Management

Comprehensive testing of face recognition capabilities:

#### **Directory Management**
- Person directory creation, retrieval, listing, updates, and deletion
- Directory metadata and tag management
- Resource cleanup and validation

#### **Person Management**
- Person addition, retrieval, listing, updates, and deletion
- Person metadata and tag management
- Person association with faces

#### **Face Management**
- Face addition using various parameter patterns (body, face_source, positional, mixed)
- Face retrieval, listing, updates, and deletion
- Face quality and association management

#### **Face Recognition**
- Face detection in images
- Similar face finding with confidence scoring
- Person identification from face data

#### **Enhanced Face Similarity Demo**
Tests demonstrate both positive and negative face matching scenarios:
- **Positive Case**: Enrolling multiple faces of the same person and finding matches
- **Negative Case**: Testing with different person faces to verify no false matches
- **Educational Output**: Clear explanations of expected results and confidence scores

## Troubleshooting

### Azure AI Foundry Resource and Regional Support

Tests require an [Azure AI Foundry resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry) and are only available in certain [supported regions](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support). Make sure to:

- Create an Azure AI Foundry resource in the Azure portal under **AI Foundry** > **AI Foundry**
- Select a supported region when creating the resource
- Ensure Content Understanding capabilities are enabled

### Common Test Issues

- **Import errors**: Ensure you've installed the package with `pip install -e .`
- **Credential errors**: Verify your environment variables are set correctly
- **Test failures**: Check that your Azure resource is accessible and has the required permissions

## Next steps

For detailed testing information, see the [Azure SDK Testing Guide](../../../../doc/dev/tests.md).

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution.

<!-- LINKS -->