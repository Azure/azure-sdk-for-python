# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    Download generated, unheard audio from an existing interrupted Realtime
    reply. This GA, read-only REST sample never creates or deletes resources.
    The item must already have a generated-audio artifact; a stored conversation
    alone is insufficient, and cancelling a response does not guarantee an artifact.

USAGE:
    python sample_voice_agent_read_generated_audio.py
    pip install "azure-ai-projects>=2.11.0" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME (required) - Agent owning the conversation.
    3) FOUNDRY_VOICE_CONVERSATION_ID (required) - Completed, stored conversation.
    4) FOUNDRY_VOICE_ITEM_ID (required) - Stored assistant item ID from REST.
    5) FOUNDRY_VOICE_RECORDING_OUTPUT_PATH (optional) - New WAV output filename.
       The file contains generated conversation content.

    Uses DefaultAzureCredential. The artifact must already exist; otherwise
    the service returns an error. Use the item ID from REST list_items,
    not a WebSocket item ID. Existing output files are never overwritten.
"""

import io
import os
from pathlib import Path
import wave

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from live_sample_utils import recording_output


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_VOICE_AGENT_NAME"]
    conversation_id = os.environ["FOUNDRY_VOICE_CONVERSATION_ID"]
    item_id = os.environ["FOUNDRY_VOICE_ITEM_ID"]
    output = os.environ.get("FOUNDRY_VOICE_RECORDING_OUTPUT_PATH")
    if output and Path(output).exists():
        raise FileExistsError(f"The recording output already exists: {output}")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as client,
    ):
        conversations = client.voice_agents.conversations
        metadata = conversations.get_generated_audio_item(agent_name, conversation_id, item_id)
        print(f"Generated audio metadata: format={metadata.format}, duration={metadata.duration_ms}.")
        if metadata.blob_uri:
            print("Generated audio is in customer storage; download it using your own storage credentials.")
            return
        content = b"".join(conversations.download_generated_audio_item(agent_name, conversation_id, item_id))
        if content[:4] != b"RIFF" or content[8:12] != b"WAVE":
            raise ValueError("The generated audio download is not a WAV file.")
        with wave.open(io.BytesIO(content), "rb") as recording:
            if recording.getnframes() == 0:
                raise ValueError("The generated audio download contains no audio frames.")
        print(f"Downloaded {len(content)} generated WAV bytes.")
        if output:
            with recording_output(Path(output)) as destination:
                destination.write(content)


if __name__ == "__main__":
    main()
