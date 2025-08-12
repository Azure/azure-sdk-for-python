# Azure AI Content Understanding client library for Python
<!-- write necessary description of service -->

## Key concepts
Content Understanding is a solution that analyzes and comprehends various media content—such as documents, images, audio, and video—transforming it into structured, organized, and searchable data.

This table shows the relationship between SDK versions and supported API service versions:

| SDK version | Supported API service version |
| ----------- | ----------------------------- |
| 1.0.0b1     | 2025-05-31                    |

## Getting started

### Azure Content Understanding Resource
- To get started, you need **an active Azure subscription**. If you don't have an Azure account, [create one for free](https://azure.microsoft.com/free/).
- Once you have your Azure subscription, create an [Azure AI Foundry resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry) in the Azure portal. Be sure to create it in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support).
- For more information, see: https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=document

### Install the package

```bash
python -m pip install azure-ai-contentunderstanding
```

#### Prerequisites

- Python 3.10 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure AI Content Understanding instance.

## Examples

### Comprehensive API Samples

This SDK includes comprehensive samples that demonstrate API-level usage of all Azure AI Content Understanding capabilities. These samples show you exactly how to call each API endpoint with proper authentication, error handling, and resource management.

## Sample Categories

### Content Analyzers
Analyze documents and extract structured information:

- **`content_analyzers_analyze.py`** - Analyze text content for layout and structure
- **`content_analyzers_analyze_binary.py`** - Analyze binary files (PDFs, images, documents)
- **`content_analyzers_create_or_replace.py`** - Create or update custom analyzers
- **`content_analyzers_get_analyzer.py`** - Retrieve analyzer configurations
- **`content_analyzers_list.py`** - List all available analyzers
- **`content_analyzers_update.py`** - Update existing analyzers
- **`content_analyzers_delete_analyzer.py`** - Delete custom analyzers
- **`content_analyzers_get_operation_status.py`** - Check analysis operation status
- **`content_analyzers_get_result.py`** - Retrieve analysis results
- **`content_analyzers_get_result_file.py`** - Download result files

### Content Classifiers
Classify content into categories:

- **`content_classifiers_classify.py`** - Classify text content
- **`content_classifiers_classify_binary.py`** - Classify binary files
- **`content_classifiers_create_or_replace.py`** - Create or update classifiers
- **`content_classifiers_get_classifier.py`** - Retrieve classifier configurations
- **`content_classifiers_list.py`** - List all available classifiers
- **`content_classifiers_update.py`** - Update existing classifiers
- **`content_classifiers_delete_classifier.py`** - Delete custom classifiers
- **`content_classifiers_get_operation_status.py`** - Check classification operation status
- **`content_classifiers_get_result.py`** - Retrieve classification results

### Face Recognition & Person Management
Comprehensive face recognition capabilities:

#### **Directory Management**
- **`person_directories_create.py`** - Create person directories
- **`person_directories_get.py`** - Retrieve directory information
- **`person_directories_list.py`** - List all directories
- **`person_directories_update.py`** - Update directory properties
- **`person_directories_delete.py`** - Delete directories

#### **Person Management**
- **`person_directories_add_person.py`** - Add persons to directories
- **`person_directories_get_person.py`** - Retrieve person information
- **`person_directories_list_persons.py`** - List all persons in a directory
- **`person_directories_update_person.py`** - Update person properties
- **`person_directories_delete_person.py`** - Delete persons

#### **Face Management**
- **`person_directories_get_face.py`** - Retrieve face information
- **`person_directories_list_faces.py`** - List all faces in a directory
- **`person_directories_update_face.py`** - Update face associations
- **`person_directories_delete_face.py`** - Delete faces

#### **Face Recognition**
- **`person_directories_find_similar_faces.py`** - Find similar faces (Enhanced Demo)
- **`faces_detect.py`** - Detect faces in images

#### **Enhanced Face Similarity Demo**
`person_directories_find_similar_faces.py` provides a comprehensive demonstration:

- **Test 1 (Positive Case)**: Enrolls Dad1 & Dad2 faces, queries with Dad3 → should find matches
- **Test 2 (Negative Case)**: Queries with Mom1 (different person) → should find no matches
- **Educational Output**: Clear explanations of expected results and confidence scores
- **Real-world Scenarios**: Demonstrates both successful and failed face matching

## **Quick Start with Samples**

1. **Set up authentication**:
   ```bash
   # Copy sample environment file
   cd samples
   cp env.sample .env
   
   # Edit .env with your endpoint (required)
   # AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource-name.services.ai.azure.com/  
   # Leave AZURE_CONTENT_UNDERSTANDING_KEY empty unless using key-based authentication (not recommended for production)
   # AZURE_CONTENT_UNDERSTANDING_KEY=
   
   # Use Azure CLI for authentication (recommended - secure)
   az login
   ```
   
   **Security Note**: Only set `AZURE_CONTENT_UNDERSTANDING_KEY` if you need key-based authentication for testing. **Azure CLI (`az login`) or DefaultAzureCredential is recommended** as it eliminates the need to manage secrets, reduces the risk of credential leaks, and enables secure, auditable, and least-privilege access to resources through Azure AD.

2. **Install dependencies**:
   ```bash
   pip install azure-ai-contentunderstanding python-dotenv
   ```

3. **Run any sample**:
   ```bash
   python content_analyzers_analyze_binary.py       # Analyze binary files (PDFs, images, documents)
   python content_analyzers_create_or_replace.py    # Create custom analyzer using begin_create_or_replace API
   ```

## Troubleshooting

### Azure AI Foundry Resource and Regional Support

Azure AI Content Understanding requires an [Azure AI Foundry resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry) and is only available in certain [supported regions](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support). Make sure to:

- Create an Azure AI Foundry resource in the Azure portal under **AI Foundry** > **AI Foundry**
- Select a supported region when creating the resource

For detailed setup instructions and current supported regions, see: **[Azure AI Content Understanding Quickstart Guide](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)**

## Next steps
For more information about Azure AI Content Understanding, see the following additional resources:
- **[Azure AI Content Understanding Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)**
- **[REST API Reference](https://learn.microsoft.com/rest/api/content-understanding/)**
- **[Quickstart Guide](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)**

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
