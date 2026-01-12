# Azure AI Speech Transcription client library for Python

Azure AI Speech Transcription is a service that provides advanced speech-to-text capabilities, allowing you to transcribe audio content into text with high accuracy. This client library enables developers to integrate speech transcription features into their Python applications.

Use the client library to:
- Transcribe audio files and audio URLs to text
- Support multiple languages with automatic language detection
- Customize transcription with domain-specific models
- Enable speaker diarization to identify different speakers
- Configure profanity filtering and channel separation

[Source code][source_code] | [Package (PyPI)][pypi_package] | [API reference documentation][api_reference] | [Product documentation][product_docs]

## Getting started

### Prerequisites

- Python 3.9 or later is required to use this package.
- You must have an [Azure subscription][azure_sub] to use this package.
- An [Azure AI Speech resource][speech_resource] in your Azure account.

### Install the package

Install the Azure AI Speech Transcription client library for Python with [pip][pip]:

```bash
pip install azure-ai-transcription
```

### Create an Azure AI Speech resource

You can create an Azure AI Speech resource using the [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

Here's an example using the Azure CLI:

```bash
az cognitiveservices account create \
    --name <your-resource-name> \
    --resource-group <your-resource-group> \
    --kind SpeechServices \
    --sku F0 \
    --location <region>
```

### Authenticate the client

In order to interact with the Azure AI Speech Transcription service, you'll need to create an instance of the [TranscriptionClient][transcription_client] class. The client supports two authentication methods:

1. **Azure Active Directory (Azure AD) Authentication** - Using `DefaultAzureCredential` or other token credentials from `azure-identity`
2. **API Key Authentication** - Using `AzureKeyCredential` with your Speech resource's API key

#### Get credentials

You can get the endpoint and API key from the Azure Portal or by running the following Azure CLI command:

```bash
az cognitiveservices account keys list \
    --name <your-resource-name> \
    --resource-group <your-resource-group>
```

The endpoint can be found in the "Keys and Endpoint" section of your Speech resource in the Azure Portal.

#### Create the client with API Key

Using an API key is the simplest authentication method:

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient

endpoint = os.environ.get("SPEECH_ENDPOINT")
api_key = os.environ.get("SPEECH_API_KEY")

credential = AzureKeyCredential(api_key)
client = TranscriptionClient(endpoint=endpoint, credential=credential)
```

#### Create the client with Azure AD (Recommended for Production)

Azure AD authentication provides better security and is recommended for production scenarios. First, install the `azure-identity` package:

```bash
pip install azure-identity
```

Then create the client using `DefaultAzureCredential`:

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.transcription import TranscriptionClient

endpoint = os.environ.get("SPEECH_ENDPOINT")

# DefaultAzureCredential will try multiple authentication methods
# including environment variables, managed identity, Azure CLI, etc.
credential = DefaultAzureCredential()
client = TranscriptionClient(endpoint=endpoint, credential=credential)
```

**Note:** When using Azure AD authentication, ensure your Azure identity has the appropriate role assigned (e.g., `Cognitive Services User` or `Cognitive Services Speech User`) on the Speech resource.

## Key concepts

### TranscriptionClient

The `TranscriptionClient` is the primary interface for developers using the Azure AI Speech Transcription client library. It provides the `transcribe` method to convert audio into text.

### Transcription Options

The service supports various transcription options including:
- **Language Detection**: Automatic detection from supported locales or specify candidate locales
- **Custom Models**: Map locales to custom model URIs for domain-specific vocabulary  
- **Diarization**: Identify and separate different speakers in the audio
- **Channel Separation**: Process up to two audio channels separately
- **Profanity Filtering**: Control how profanity appears in transcripts (None, Removed, Tags, Masked)
- **Enhanced Mode**: Additional processing capabilities
- **Phrase Lists**: Improve accuracy for specific terms and phrases

### Transcription Results

Results include:
- Full transcript text per channel
- Segmented phrases with timestamps
- Word-level details including confidence scores
- Duration information

## Examples

The following sections provide several code snippets covering common scenarios:

- [Transcribe an audio file](#transcribe-an-audio-file)
- [Transcribe from a URL](#transcribe-from-a-url)
- [Transcribe with enhanced mode](#transcribe-with-enhanced-mode)
- [Using async client](#using-async-client)

For more extensive examples including speaker diarization, multi-language detection, profanity filtering, and custom phrase lists, see the [samples][samples_directory] directory.

### Transcribe an audio file

<!-- SNIPPET:sample_transcribe_audio_file.transcribe_audio_file-->

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient
from azure.ai.transcription.models import TranscriptionContent, TranscriptionOptions

# Get configuration from environment variables
endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
api_key = os.environ["AZURE_SPEECH_API_KEY"]

# Create the transcription client
client = TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# Path to your audio file
import pathlib

audio_file_path = pathlib.Path(__file__).parent / "assets" / "audio.wav"

# Open and read the audio file
with open(audio_file_path, "rb") as audio_file:
    # Create transcription options
    options = TranscriptionOptions(locales=["en-US"])  # Specify the language

    # Create the request content
    request_content = TranscriptionContent(definition=options, audio=audio_file)

    # Transcribe the audio
    result = client.transcribe(request_content)

    # Print the transcription result
    print(f"Transcription: {result.combined_phrases[0].text}")

    # Print detailed phrase information
    if result.phrases:
        print("\nDetailed phrases:")
        for phrase in result.phrases:
            print(
                f"  [{phrase.offset_milliseconds}ms - "
                f"{phrase.offset_milliseconds + phrase.duration_milliseconds}ms]: "
                f"{phrase.text}"
            )
```

<!-- END SNIPPET -->

### Transcribe from a URL

<!-- SNIPPET:sample_transcribe_from_url.transcribe_from_url-->

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient
from azure.ai.transcription.models import TranscriptionOptions

# Get configuration from environment variables
endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
api_key = os.environ["AZURE_SPEECH_API_KEY"]

# Create the transcription client
client = TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# URL to your audio file (must be publicly accessible)
audio_url = "https://example.com/path/to/audio.wav"
# Configure transcription options
options = TranscriptionOptions(locales=["en-US"])

# Transcribe the audio from URL
# The service will access and transcribe the audio directly from the URL
result = client.transcribe_from_url(audio_url, options=options)

# Print the transcription result
print(f"Transcription: {result.combined_phrases[0].text}")

# Print duration information
if result.duration_milliseconds:
    print(f"Audio duration: {result.duration_milliseconds / 1000:.2f} seconds")
```

<!-- END SNIPPET -->

### Transcribe with enhanced mode

Enhanced mode provides advanced capabilities such as translation or summarization during transcription:

<!-- SNIPPET:sample_transcribe_with_enhanced_mode.transcribe_with_enhanced_mode-->

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient
from azure.ai.transcription.models import (
    TranscriptionContent,
    TranscriptionOptions,
    EnhancedModeProperties,
)

# Get configuration from environment variables
endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
api_key = os.environ["AZURE_SPEECH_API_KEY"]

# Create the transcription client
client = TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# Path to your audio file
import pathlib

audio_file_path = pathlib.Path(__file__).parent / "assets" / "audio.wav"

# Open and read the audio file
with open(audio_file_path, "rb") as audio_file:
    # Create enhanced mode properties
    # Enable enhanced mode for advanced processing capabilities
    enhanced_mode = EnhancedModeProperties(
        task="translation",  # Specify the task type (e.g., "translation", "summarization")
        target_language="es-ES",  # Target language for translation
        prompt=[
            "Translate the following audio to Spanish",
            "Focus on technical terminology",
        ],  # Optional prompts to guide the enhanced mode
    )

    # Create transcription options with enhanced mode
    options = TranscriptionOptions(locales=["en-US"], enhanced_mode=enhanced_mode)

    # Create the request content
    request_content = TranscriptionContent(definition=options, audio=audio_file)

    # Transcribe the audio with enhanced mode
    result = client.transcribe(request_content)

    # Print the transcription result
    print("Transcription with enhanced mode:")
    print(f"{result.combined_phrases[0].text}")

    # Print individual phrases if available
    if result.phrases:
        print("\nDetailed phrases:")
        for phrase in result.phrases:
            print(f"  [{phrase.offset_milliseconds}ms]: {phrase.text}")
```

<!-- END SNIPPET -->

### Using async client

The library also provides an async client for asynchronous operations:

<!-- SNIPPET:sample_transcribe_audio_file_async.transcribe_audio_file_async-->

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription.aio import TranscriptionClient
from azure.ai.transcription.models import TranscriptionContent, TranscriptionOptions

# Get configuration from environment variables
endpoint = os.environ["AZURE_SPEECH_ENDPOINT"]
api_key = os.environ["AZURE_SPEECH_API_KEY"]

# Create the transcription client
async with TranscriptionClient(endpoint=endpoint, credential=AzureKeyCredential(api_key)) as client:
    # Path to your audio file
    import pathlib

    audio_file_path = pathlib.Path(__file__).parent.parent / "assets" / "audio.wav"

    # Open and read the audio file
    with open(audio_file_path, "rb") as audio_file:
        # Create transcription options
        options = TranscriptionOptions(locales=["en-US"])  # Specify the language

        # Create the request content
        request_content = TranscriptionContent(definition=options, audio=audio_file)

        # Transcribe the audio
        result = await client.transcribe(request_content)

        # Print the transcription result
        print(f"Transcription: {result.combined_phrases[0].text}")

        # Print detailed phrase information
        if result.phrases:
            print("\nDetailed phrases:")
            for phrase in result.phrases:
                print(
                    f"  [{phrase.offset_milliseconds}ms - "
                    f"{phrase.offset_milliseconds + phrase.duration_milliseconds}ms]: "
                    f"{phrase.text}"
                )
```

<!-- END SNIPPET -->

## Troubleshooting

### General

Azure AI Speech Transcription client library will raise exceptions defined in [Azure Core][azure_core_exceptions] if you call `.raise_for_status()` on your responses.

### Logging

This library uses the standard [logging][python_logging] library for logging. Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted** headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

```python
import sys
import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Enable network trace logging
endpoint = "https://<your-region>.api.cognitive.microsoft.com"
credential = AzureKeyCredential("<your-api-key>")
client = TranscriptionClient(endpoint=endpoint, credential=credential, logging_enable=True)
```

### Errors and exceptions

When you interact with the Azure AI Speech Transcription client library using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for [REST API][rest_api] requests.

For example, if you try to use an invalid API key, a `401` error is returned, indicating "Unauthorized".

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient
from azure.core.exceptions import HttpResponseError

endpoint = "https://<your-region>.api.cognitive.microsoft.com"
credential = AzureKeyCredential("invalid_key")

client = TranscriptionClient(endpoint=endpoint, credential=credential)

try:
    # Attempt an operation
    pass
except HttpResponseError as e:
    print(f"Error: {e}")
```

## Next steps

### More sample code

For more extensive examples of using the Azure AI Speech Transcription client library, see the [samples][samples_directory] directory. These samples demonstrate:
- Basic transcription of audio files and URLs (sync and async)
- Speaker diarization to identify different speakers
- Multi-language detection and transcription
- Profanity filtering options
- Custom phrase lists for domain-specific terminology

Additional resources:
- Check the [Azure AI Speech documentation][speech_docs] for comprehensive tutorials and guides
- Explore the [Azure SDK for Python samples][azure_sdk_samples] repository

### Additional documentation

For more extensive documentation on Azure AI Speech, see the [Speech service documentation][speech_docs] on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [https://cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information, see the [Code of Conduct FAQ][code_of_conduct_faq] or contact [opencode@microsoft.com][opencode_email] with any additional questions or comments.

<!-- LINKS -->
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-transcription
[pypi_package]: https://pypi.org/project/azure-ai-transcription/
[api_reference]: https://learn.microsoft.com/python/api/azure-ai-transcription/azure.ai.transcription?view=azure-python-preview
[product_docs]: https://learn.microsoft.com/azure/ai-services/speech-service/
[azure_sub]: https://azure.microsoft.com/free/
[speech_resource]: https://learn.microsoft.com/azure/ai-services/speech-service/overview
[pip]: https://pypi.org/project/pip/
[azure_portal]: https://portal.azure.com
[azure_cli]: https://learn.microsoft.com/cli/azure
[transcription_client]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-transcription/azure/ai/transcription/_client.py
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[rest_api]: https://learn.microsoft.com/azure/ai-services/speech-service/rest-speech-to-text
[samples_directory]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-transcription/samples
[azure_sdk_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-transcription/samples
[speech_docs]: https://learn.microsoft.com/azure/ai-services/speech-service/
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[opencode_email]: mailto:opencode@microsoft.com

