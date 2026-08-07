# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_read_conversation_audio.py

DESCRIPTION:
    This sample demonstrates reading the persisted audio of a voice conversation,
    both the merged whole-call recording and a single turn's audio segment. For
    each it reads the metadata first, then streams the WAV bytes to a local file.
    The merged recording is stereo: the caller on the left channel and the agent
    on the right.

    Audio is available only after the session has ended and only when the agent
    was configured with `store = true`. For bring-your-own-storage (BYOS)
    accounts the metadata carries a `blob_uri` instead, and the bytes are read
    from your own storage rather than streamed here.

USAGE:
    python sample_read_conversation_audio.py

    Set these environment variables before running the sample:
    1) AZURE_VOICE_AGENTS_ENDPOINT - the Foundry project endpoint, in the form
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) AZURE_VOICE_AGENTS_AGENT_NAME - the name of the voice agent.
    3) AZURE_VOICE_AGENTS_CONVERSATION_ID - the id of a persisted conversation.

    The sample authenticates with DefaultAzureCredential, so sign in first
    (for example, with `az login`).
"""

import os
from typing import Final

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys


def read_conversation_audio() -> None:
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    agent_name = os.environ["AZURE_VOICE_AGENTS_AGENT_NAME"]
    conversation_id = os.environ["AZURE_VOICE_AGENTS_CONVERSATION_ID"]
    preview: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

    with VoiceAgentsClient(endpoint=endpoint, credential=DefaultAzureCredential()) as client:
        conversations = client.agent_endpoint_conversations
        try:
            read_merged_recording(conversations, agent_name, conversation_id, preview)
            read_first_item_audio(conversations, agent_name, conversation_id, preview)
        except HttpResponseError as e:
            # 404: not persisted / not ready. 409: session still in progress.
            print(f"Service responded with an error: {e.status_code} {e.reason}")


def stream_to_wav(stream, output_path) -> None:
    """Write a streamed audio-content response to a local WAV file.

    :param stream: An iterable of audio byte chunks.
    :param output_path: The local output path.
    :type stream: collections.abc.Iterable[bytes]
    :type output_path: str
    """
    with open(output_path, "wb") as f:
        for chunk in stream:
            f.write(chunk)
    print(f"Wrote {output_path}")


def read_merged_recording(conversations, agent_name, conversation_id, preview) -> None:
    """Read the merged whole-call stereo recording (left=user, right=agent).

    :param conversations: The conversation operations client.
    :param agent_name: The voice agent name.
    :param conversation_id: The persisted conversation id.
    :param preview: The preview feature opt-in value.
    :type conversations: azure.ai.voiceagents.operations.AgentEndpointConversationsOperations
    :type agent_name: str
    :type conversation_id: str
    :type preview: azure.ai.voiceagents.models.AgentDefinitionOptInKeys
    """
    recording = conversations.get_agent_conversation_audio(agent_name, conversation_id, foundry_features=preview)
    print(
        f"Recording: format={recording.format}, sample_rate={recording.sample_rate}, "
        f"channels={recording.channels}, duration_ms={recording.duration_ms}"
    )

    if recording.blob_uri:
        # Bring-your-own-storage: download from your own storage using the returned URI.
        print(f"Recording is stored in your own storage at: {recording.blob_uri}")
        return

    # Foundry-managed storage: stream the bytes and write them to a local WAV file.
    stream = conversations.get_agent_conversation_audio_content(agent_name, conversation_id, foundry_features=preview)
    stream_to_wav(stream, f"{conversation_id}.wav")


def read_first_item_audio(conversations, agent_name, conversation_id, preview) -> None:
    """Read the audio segment of the first conversation item that has one.

    :param conversations: The conversation operations client.
    :param agent_name: The voice agent name.
    :param conversation_id: The persisted conversation id.
    :param preview: The preview feature opt-in value.
    :type conversations: azure.ai.voiceagents.operations.AgentEndpointConversationsOperations
    :type agent_name: str
    :type conversation_id: str
    :type preview: azure.ai.voiceagents.models.AgentDefinitionOptInKeys
    """
    for item in conversations.list_agent_conversation_items(agent_name, conversation_id, foundry_features=preview):
        item_id = item.get("id")
        if not item_id:
            continue
        try:
            metadata = conversations.get_agent_conversation_item_audio(
                agent_name, conversation_id, item_id, foundry_features=preview
            )
        except HttpResponseError as e:
            # A 404 means this item has no persisted audio (for example, a text-only turn).
            if e.status_code == 404:
                continue
            raise

        print(f"Item {item_id}: role={metadata.role}, duration_ms={metadata.duration_ms}")
        if metadata.blob_uri:
            print(f"Item audio is stored in your own storage at: {metadata.blob_uri}")
            return

        stream = conversations.get_agent_conversation_item_audio_content(
            agent_name, conversation_id, item_id, foundry_features=preview
        )
        stream_to_wav(stream, f"{conversation_id}_{item_id}.wav")
        return

    print("No conversation item with audio was found.")


if __name__ == "__main__":
    read_conversation_audio()
