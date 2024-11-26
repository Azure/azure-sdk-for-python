## Pre-requisites

Conda environment is required to run this sample. If you don't have conda installed, you can download it from [here](https://docs.conda.io/en/latest/miniconda.html).
```commandline
conda create -n myenv python=3.11

conda activate myenv

pip install opentelemetry-api opentelemetry-sdk
pip install python-dotenv
pip install azure-monitor-opentelemetry

pip install opentelemetry-instrumentation-openai-v2
pip install httpx
pip install openai
pip install azure-ai-evaluation

# needed for ask wikipedia sample
pip install bs4
```

## Key Points
- `ask_wiki` folder has the sample app that talks to wikipedia and returns the summary of the article.
- `gen_ai_trace` folder has decorator that captures inputs and outputs of the function and sends and logs traces in a way that is compatible with Gen AI Convention. Without this Azure AI studio cannot show the traces in readable format.
- `test_app_telemetry.py` has the sample app that uses the decorator from `gen_ai_trace` to capture traces and send them to Azure AI studio.

## How to run the sample

- This sample needs some environment variables to be set. Create a `.env` file in the root of the project and add the following values to it.
````commandline
OPENAI_API_TYPE="azure"
OPENAI_API_VERSION="2024-02-15-preview"
OPENAI_API_BASE="<>"
AZURE_OPENAI_ENDPOINT="<>"
AZURE_OPENAI_API_KEY="<>"
OPENAI_ASSISTANT_MODEL="GPT-4-Prod"
AZURE_OPENAI_DEPLOYMENT="GPT-4-Prod"
OPENAI_ANALYST_CHAT_MODEL="GPT-4-Prod"
APPINSIGHTS_CONNECTION_STRING="<>"
AZURE_SUBSCRIPTION_ID="<>"
AZURE_RESOURCE_GROUP="<>"
AZURE_PROJECT_NAME="<>"
AZURE_OPENAI_API_VERSION="<>"
````
- Run the `test_app_telemetry.py` file to see the traces in Azure AI studio.
```commandline
python test_app_telemetry.py --query "What is the capital of India?"
```