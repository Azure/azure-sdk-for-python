---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-speech-services
urlFragment: azure-ai-speech-transcription-samples
---

# Azure AI Speech Transcription SDK Samples

These code samples demonstrate how to use the Azure AI Speech Transcription client library for Python.

## Prerequisites

- Python 3.9 or later
- An [Azure subscription](https://azure.microsoft.com/free/)
- An [Azure Speech Services resource](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-speech-to-text) or [Cognitive Services multi-service resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAllInOne)
- The Speech Services endpoint and API key for your resource

## Setup

1. Install the Azure AI Speech Transcription client library:

   ```bash
   pip install azure-ai-speech-transcription
   ```

2. Set the following environment variables:

   ```bash
   export AZURE_SPEECH_ENDPOINT="<your-speech-endpoint>"
   export AZURE_SPEECH_API_KEY="<your-api-key>"
   ```

   On Windows (PowerShell):

   ```powershell
   $env:AZURE_SPEECH_ENDPOINT="<your-speech-endpoint>"
   $env:AZURE_SPEECH_API_KEY="<your-api-key>"
   ```

   **Note:** For Azure AD authentication (recommended for production), install `azure-identity` and configure authentication as described in the [main README](../README.md#authenticate-the-client).

## Running the Samples

Each sample is a standalone Python script that can be run directly:

```bash
python sample_transcribe_audio_file.py
```

For async samples:

```bash
python async_samples/sample_transcribe_audio_file_async.py
```

## Available Samples

### Basic Samples

| Sample | Description |
|--------|-------------|
| [sample_transcribe_audio_file.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/sample_transcribe_audio_file.py) | Transcribe an audio file |
| [sample_transcribe_audio_file_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/async_samples/sample_transcribe_audio_file_async.py) | Transcribe an audio file (async) |
| [sample_transcribe_from_url.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/sample_transcribe_from_url.py) | Transcribe audio from a URL |
| [sample_transcribe_from_url_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/async_samples/sample_transcribe_from_url_async.py) | Transcribe audio from a URL (async) |

### Advanced Samples

| Sample | Description |
|--------|-------------|
| [sample_transcribe_with_diarization.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/sample_transcribe_with_diarization.py) | Transcribe with speaker diarization |
| [sample_transcribe_with_diarization_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/async_samples/sample_transcribe_with_diarization_async.py) | Transcribe with speaker diarization (async) |
| [sample_transcribe_multiple_languages.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/sample_transcribe_multiple_languages.py) | Transcribe with multiple language detection |
| [sample_transcribe_multiple_languages_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/async_samples/sample_transcribe_multiple_languages_async.py) | Transcribe with multiple language detection (async) |
| [sample_transcribe_with_profanity_filter.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/sample_transcribe_with_profanity_filter.py) | Transcribe with profanity filtering |
| [sample_transcribe_with_profanity_filter_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/async_samples/sample_transcribe_with_profanity_filter_async.py) | Transcribe with profanity filtering (async) |
| [sample_transcribe_with_phrase_list.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/sample_transcribe_with_phrase_list.py) | Transcribe with custom phrase list |
| [sample_transcribe_with_phrase_list_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/samples/async_samples/sample_transcribe_with_phrase_list_async.py) | Transcribe with custom phrase list (async) |

## Additional Resources

- [Azure AI Speech Transcription documentation](https://learn.microsoft.com/azure/ai-services/speech-service/)
- [Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription)
- [Package (PyPI)](https://pypi.org/project/azure-ai-speech-transcription/)
## Additional Resources

- [API reference documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices/azure-ai-speech-transcription/azure/ai/speech/transcription)
