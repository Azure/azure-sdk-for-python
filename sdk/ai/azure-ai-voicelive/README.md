# Azure Ai Voicelive client library for Python

Azure AI VoiceLive provides real-time voice and audio processing capabilities through WebSocket connections, allowing applications to perform bi-directional streaming of audio data and receive real-time responses.

## Getting started

### Install the package

```bash
python -m pip install azure-ai-voicelive
```

For WebSocket support, install with websockets extras:

```bash
python -m pip install azure-ai-voicelive[websockets]
```

#### Prequisites

- Python 3.10 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure Ai Voicelive instance.

### Authentication

VoiceLive uses API keys for authentication. You can obtain your API key from the Azure portal.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import VoiceLiveClient

# Create a VoiceLive client
client = VoiceLiveClient(
    credential=AzureKeyCredential("<your-api-key>"),
    endpoint="<your-endpoint>"
)
```

## Key concepts

### HTTP-based API

The VoiceLive client provides HTTP-based APIs for non-streaming operations.

### WebSocket-based streaming

For real-time, bi-directional communication, VoiceLive supports WebSocket connections. This enables:

- Real-time audio streaming
- Low-latency processing
- Bidirectional communication
- Event-based communication

### Typed Events

The SDK provides typed event classes for easier handling of server responses:

- `VoiceLiveServerEvent`: Base class for all server events
- `VoiceLiveClientEvent`: Base class for all client events
- Specific event types like `VoiceLiveServerEventSessionUpdated` and `VoiceLiveServerEventError`

### Resource Classes

The SDK provides resource classes to simplify common operations:

- `VoiceLiveSessionResource`: Manages session configuration

## Examples

### Create a WebSocket connection with Typed Events

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import VoiceLiveClient
from azure.ai.voicelive.models import (
    VoiceLiveServerEventSessionUpdated, 
    VoiceLiveServerEventError
)

# Create client
client = VoiceLiveClient(
    credential=AzureKeyCredential("<your-api-key>"),
    endpoint="<your-endpoint>"
)

# Connect to the WebSocket API
with client.connect(model="gpt-4o-realtime-preview") as connection:
    # Update session using the session resource
    connection.session.update(
        session={
            "modalities": ["audio", "text"],
            "turn_detection": {"type": "server_vad"}
        }
    )
    
    # Receive typed events
    for event in connection:
        print(f"Received event type: {event.type}")
        
        # Type-specific handling
        if isinstance(event, VoiceLiveServerEventSessionUpdated):
            print(f"Session updated with ID: {event.session.id}")
            break
            
        elif isinstance(event, VoiceLiveServerEventError):
            print(f"Error: {event.error.message}")
            break
```

### Session Management

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import VoiceLiveClient
from azure.ai.voicelive.models import VoiceLiveServerEventSessionUpdated

# Create client
client = VoiceLiveClient(
    credential=AzureKeyCredential("<your-api-key>"),
    endpoint="<your-endpoint>"
)

with client.connect(model="gpt-4o-realtime-preview") as connection:
    # Update session configuration using the session resource
    connection.session.update(
        session={
            "modalities": ["text", "audio"],
            "voice": "alloy",
            "turn_detection": {"type": "server_vad"},
            "input_audio_noise_reduction": {"type": "near_field"}
        },
        event_id="config-update-1"  # Optional ID for tracking this event
    )
    
    # Wait for confirmation
    for event in connection:
        if isinstance(event, VoiceLiveServerEventSessionUpdated):
            print(f"Session updated with ID: {event.session.id}")
            print(f"Current modalities: {event.session.modalities}")
            print(f"Voice: {event.session.voice}")
            break
```

### Error Handling

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import (
    VoiceLiveClient,
    VoiceLiveConnectionError,
    VoiceLiveConnectionClosed
)

try:
    client = VoiceLiveClient(
        credential=AzureKeyCredential("<your-api-key>"),
        endpoint="<your-endpoint>"
    )
    
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Your code here
        pass
        
except ImportError as e:
    print(f"Required package not installed: {e}")
    print("Please install the 'websockets' package with 'pip install websockets'")
except VoiceLiveConnectionClosed as e:
    print(f"Connection closed: Code {e.code}, Reason: {e.reason}")
except VoiceLiveConnectionError as e:
    print(f"Connection error: {e}")
```

### Stream audio data

```python
import base64

# Inside your WebSocket connection context
with client.connect(model="gpt-4o-realtime-preview") as connection:
    # Initialize session
    connection.session.update(
        session={
            "modalities": ["audio"],
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16"
        }
    )
    
    # Wait for session to be established...
    
    # Stream audio chunks
    for audio_chunk in audio_stream:
        # Send audio data
        connection.send({
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(audio_chunk).decode('utf-8')
        })
        
        # Process any received events
        for event in connection:
            print(f"Received event type: {event.type}")
            # Process specific event types as needed
            if event.type == "input_audio_buffer.speech_stopped":
                # Commit the buffer when speech is detected as stopped
                connection.send({"type": "input_audio_buffer.commit"})
```

More examples can be found in the [samples](samples/) directory.

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
