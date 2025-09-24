# Azure AI Language Question Answering Authoring client library for Python

This package provides **authoring / management operations** for Azure AI Language Question Answering as a **standalone** package, separated from the runtime Q&A client (`azure-ai-language-questionanswering`). It lets you create, update, import/export, and deploy Question Answering projects and manage sources, QnAs, and synonyms.

> NOTE: This is an initial preview (`1.0.0b1`) and includes support for a preview service API version. Surface may change before GA.

## Getting Started

### Prerequisites
- Python 3.9+
- An Azure subscription
- An Azure AI Language resource with Question Answering enabled

### Install the package

```bash
python -m pip install azure-ai-language-questionanswering-authoring
```

#### Prequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure Ai Language Questionanswering Authoring instance.

```

### Create a client
```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com"
credential = AzureKeyCredential("<api-key>")
client = QuestionAnsweringAuthoringClient(endpoint, credential)
```

### List projects
```python
for proj in client.list_projects():
	print(proj.name, proj.last_modified_date)
```

### Create or update a project (simplified example)
```python
body = {"language": "en", "description": "FAQ project"}
client.create_project(project_name="FAQ", body=body)
```

### Export project (long-running operation)
```python
poller = client.begin_export(project_name="FAQ", format="json")
export = poller.result()
print(export.status)
```

### Authentication
This client supports either `AzureKeyCredential` (with an API key) or Azure Active Directory credentials (e.g. `DefaultAzureCredential`). For AAD you must use a custom sub‑domain endpoint (not the regional shared endpoint).

### Versioning
The client targets the latest GA API plus preview version `2025-05-15-preview` defined in the accompanying TypeSpec. Preview operations may change.

### Logging
Enable `azure.core` logging for diagnostics:
```python
import logging
logging.basicConfig(level=logging.INFO)
```
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
