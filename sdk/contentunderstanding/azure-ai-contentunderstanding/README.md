# Azure AI Content Understanding client library for Python
<!-- write necessary description of service -->

## Getting started

### Install the package

```bash
python -m pip install azure-ai-contentunderstanding
```

#### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure AI Content Understanding instance.

## API Usage Examples

### 📁 Comprehensive API Samples

This SDK includes **35+ comprehensive samples** that demonstrate API-level usage of all Azure AI Content Understanding capabilities. These samples show you exactly how to call each API endpoint with proper authentication, error handling, and resource management.

**👉 [View All API Samples](generated_samples/README.md)**

The samples cover three main API categories:

#### **🎯 Content Analysis APIs**
- Document analysis and structure extraction
- Binary file processing (PDFs, images, documents)
- Custom analyzer creation and management
- Operation status tracking and result retrieval

#### **🏷️ Content Classification APIs** 
- Content categorization and classification
- Custom classifier creation and training
- Classification operation management

#### **👤 Face Recognition APIs**
- Person directory management
- Face enrollment and management
- Face similarity detection and person verification
- Complete person/face lifecycle workflows

### 🌟 **Featured: Enhanced Face Similarity Demo**

Try `generated_samples/person_directories_find_similar_faces.py` for a comprehensive API demonstration:

```bash
cd generated_samples
python person_directories_find_similar_faces.py
```

This sample demonstrates:
- **Real-world API usage patterns** with proper error handling
- **Positive test case**: Finding matches between related faces (Dad1, Dad2, Dad3)
- **Negative test case**: No matches when searching different people (Mom vs Dad)
- **Complete API workflow**: Create → Enroll → Search → Verify → Cleanup

### 🚀 **Quick Start with Samples**

1. **Set up authentication**:
   ```bash
   # Copy sample environment file
   cp generated_samples/env.sample .env
   
   # Edit .env with your endpoint (required)
   AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource-name.services.ai.azure.com/
   
   # Leave AZURE_CONTENT_UNDERSTANDING_KEY empty by default
   AZURE_CONTENT_UNDERSTANDING_KEY=
   
   # Use Azure CLI for authentication (recommended - secure)
   az login
   ```
   
   **⚠️ Security Note**: Only set `AZURE_CONTENT_UNDERSTANDING_KEY` if you need key-based authentication for testing. **Key-based authentication is not secure** and should not be used in production. Always prefer Azure CLI (`az login`) or DefaultAzureCredential for secure authentication.

2. **Install dependencies**:
   ```bash
   pip install azure-ai-contentunderstanding python-dotenv
   ```

3. **Run any sample**:
   ```bash
   cd generated_samples
   python person_directories_create.py              # Simple directory creation
   python person_directories_find_similar_faces.py  # Comprehensive face demo
   python content_analyzers_list.py                 # List available analyzers
   ```

### 📚 **API Pattern Examples**

All samples demonstrate consistent API usage patterns:

- **Async-first design** with proper resource management
- **Smart authentication** (Azure CLI → Key → DefaultAzureCredential)
- **Comprehensive error handling** and cleanup
- **Real test data** and expected outcomes
- **Detailed logging** with progress indicators

**[→ Explore all API samples](generated_samples/README.md)** to see complete API usage patterns for your specific use case.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
