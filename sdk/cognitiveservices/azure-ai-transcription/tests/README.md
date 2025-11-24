# Tests for Azure AI Transcription

This directory contains tests for the Azure AI Transcription SDK.

## Test Structure

Tests are organized by feature for easy navigation and maintenance:

### Core Files

- `conftest.py` - pytest configuration and test proxy sanitizers
- `preparer.py` - Test preparers and base test classes
- `assets/` - Test audio files and resources

### Synchronous Tests (14 tests)

- `test_transcription_basic.py` - Basic transcription functionality (3 tests)
- `test_transcription_url.py` - URL-based transcription scenarios (1 test)
- `test_transcription_file.py` - File-based transcription and audio formats (1 test)
- `test_transcription_options.py` - Configuration options and parameters (5 tests)
- `test_transcription_diarization.py` - Speaker diarization features (1 test)
- `test_transcription_enhanced_mode.py` - Enhanced mode and advanced features (1 test)
- `test_transcription_client_management.py` - Client lifecycle and management (2 tests)

### Asynchronous Tests (10 tests)

- `test_transcription_basic_async.py` - Basic async transcription functionality (3 tests)
- `test_transcription_url_async.py` - Async URL-based transcription (1 test)
- `test_transcription_file_async.py` - Async file-based transcription (1 test)
- `test_transcription_options_async.py` - Async configuration options (3 tests)
- `test_transcription_diarization_async.py` - Async speaker diarization (1 test)
- `test_transcription_client_management_async.py` - Async client lifecycle (1 test)

## Running Tests

### Prerequisites

1. Install the package and test dependencies:


   ```powershell
   cd sdk/cognitiveservices/azure-ai-transcription
   pip install -e .
   pip install -r dev_requirements.txt
   ```

2. Set up environment variables (for live tests):

   **Option A: Use .env file (recommended)**

   Copy the template and fill in your credentials:

   ```powershell
   # Copy the template
   Copy-Item tests\.env.template tests\.env
   
   # Edit tests\.env and add your actual endpoint and API key
   # The file is git-ignored to protect your credentials
   ```

   **Option B: Set environment variables manually**

   ```powershell
   $env:TRANSCRIPTION_ENDPOINT = "https://your-resource.cognitiveservices.azure.com/"
   $env:TRANSCRIPTION_API_KEY = "your-api-key"
   $env:TRANSCRIPTION_TEST_AUDIO_URL = "https://publicly-accessible-url.com/audio.wav"
   ```

### Run All Tests



```powershell
# From the package directory
pytest tests/

# With verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_transcription_basic.py

# Run specific test
pytest tests/test_transcription_basic.py::TestTranscriptionBasic::test_transcribe_url_basic

# Run all sync tests
pytest tests/test_transcription_*.py -k "not async"

# Run all async tests
pytest tests/test_transcription_*_async.py
```

### Run Tests in Different Modes

```powershell
# Playback mode (default, uses recordings)
pytest tests/

# Live mode (hits actual service, skips recording)
$env:AZURE_TEST_RUN_LIVE='true'; $env:AZURE_SKIP_LIVE_RECORDING='true'; pytest tests/ -v

# Record mode (record new interactions)
$env:AZURE_TEST_RUN_LIVE='true'; pytest tests/ -v
```

### Using Tox

```powershell
# Run tests with tox
tox run -e whl -c ../../../eng/tox/tox.ini --root .

# Run pylint
tox run -e pylint -c ../../../eng/tox/tox.ini --root .

# Run mypy
tox run -e mypy -c ../../../eng/tox/tox.ini --root .
```

## Test Proxy

Tests use the Azure SDK Test Proxy for recording and playback.

### Start Test Proxy (for recording mode)

From the repository root:

```powershell
./eng/common/testproxy/docker-start-proxy.ps1
```


## Environment Variables

The following environment variables are used in tests:

| Variable | Description | Required |
|----------|-------------|----------|
| `TRANSCRIPTION_ENDPOINT` | Azure Cognitive Services endpoint | Yes (for live tests) |
| `TRANSCRIPTION_API_KEY` | API key for authentication | Yes (for live tests) |
| `TRANSCRIPTION_SUBSCRIPTION_ID` | Azure subscription ID | No |
| `TRANSCRIPTION_TENANT_ID` | Azure tenant ID | No |
| `TRANSCRIPTION_CLIENT_ID` | Azure client ID (for service principal) | No |
| `TRANSCRIPTION_CLIENT_SECRET` | Azure client secret (for service principal) | No |

## Writing New Tests

1. Follow the pattern in existing test files
2. Use `@TranscriptionPreparer()` decorator to inject environment variables
3. Use `@recorded_by_proxy` decorator for tests that make HTTP requests
4. Add appropriate assertions to verify behavior
5. Ensure secrets are properly sanitized in `conftest.py`

## Test Coverage

Run tests with coverage:

```powershell
pytest tests/ --cov=azure.ai.transcription --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in a browser.
