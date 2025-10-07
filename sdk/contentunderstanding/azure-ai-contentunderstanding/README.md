# Azure AI Content Understanding client library for Python

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
- An existing Azure AI Content Understanding resource.

## Examples

### Content Analyzers
Analyze documents and extract structured information:

- **`content_analyzers_analyze_binary_raw_json.py`** - Extract content from PDF using begin_analyze_binary and save raw JSON response
- **`content_analyzers_analyze_binary.py`** - Extract content from PDF file, print markdown content and document information
- **`content_analyzers_analyze_url.py`** - Extract content from public URL using prebuilt-documentAnalyzer
- **`content_analyzers_analyze_url_prebuilt_invoice.py`** - Extract invoice fields from URL using prebuilt-invoice analyzer
- **`content_analyzers_create_or_replace.py`** - Create custom analyzer with field schema for extracting company information
- **`content_analyzers_get_analyzer.py`** - Retrieve analyzer configuration details
- **`content_analyzers_list.py`** - List all available analyzers with detailed information and summary statistics
- **`content_analyzers_update.py`** - Update analyzer description and tags
- **`content_analyzers_delete_analyzer.py`** - Delete custom analyzer
- **`content_analyzers_get_result_file.py`** - Download result files (keyframe images) from video analysis operations

### Advanced Features
- **`custom_poller_demo.py`** - Demonstrate custom LROPoller classes with operation ID details and continuation token support

### Content Classifiers
Classify content into categories:

- **`content_classifiers_classify.py`** - Classify documents from URL and binary data using custom classifier
- **`content_classifiers_classify_binary.py`** - Classify binary PDF document with categories (Loan, Invoice, Bank Statement)
- **`content_classifiers_create_or_replace.py`** - Create custom classifier with defined categories and wait for completion
- **`content_classifiers_get_classifier.py`** - Retrieve classifier details including categories and configuration
- **`content_classifiers_list.py`** - List all available classifiers with detailed information and summary statistics
- **`content_classifiers_update.py`** - Update classifier description and tags
- **`content_classifiers_delete_classifier.py`** - Delete custom classifier

### Face Recognition & Person Management
Comprehensive face recognition capabilities:

#### **Directory Management**
- **`person_directories_create.py`** - Create person directory with description and tags
- **`person_directories_get.py`** - Retrieve directory details and display information
- **`person_directories_list.py`** - List all person directories with detailed information
- **`person_directories_update.py`** - Update directory with new description and tags
- **`person_directories_delete.py`** - Delete person directory

#### **Person Management**
- **`person_directories_add_person.py`** - Add person to directory with tags
- **`person_directories_get_person.py`** - Get person details using person ID
- **`person_directories_list_persons.py`** - List all persons in a directory with details
- **`person_directories_update_person.py`** - Update person tags and face associations
- **`person_directories_delete_person.py`** - Delete person from directory

#### **Face Management**
- **`person_directories_get_face.py`** - Retrieve face details from person directory
- **`person_directories_list_faces.py`** - List all faces in directory with person associations
- **`person_directories_update_face.py`** - Update face to reassign to different person
- **`person_directories_delete_face.py`** - Delete face from person directory

#### **Face Recognition**
- **`person_directories_find_similar_faces.py`** - Find similar faces with positive and negative test cases
- **`person_directories_identify_person.py`** - Identify persons in group photo using enrolled faces
- **`faces_detect.py`** - Detect faces in local image files with bounding boxes
- **`faces_detect_url.py`** - Detect faces in images from remote URLs

#### **Enhanced Face Similarity Demo**
`person_directories_find_similar_faces.py` provides a comprehensive demonstration:

- **Test 1 (Positive Case)**: Enrolls Bill's faces (Dad1 & Dad2), queries with Dad3 → finds high-confidence matches
- **Test 2 (Negative Case)**: Queries with Clare's face (Mom1) → finds no matches
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
