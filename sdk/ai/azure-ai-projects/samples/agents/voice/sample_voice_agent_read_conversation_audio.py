# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates reading the persisted audio of a voice
    conversation via `project_client.agent_endpoint_conversations`, both the
    merged whole-call recording and a single turn's audio segment. For each it
    reads the metadata first, then streams the WAV bytes to a local file. The
    merged recording is stereo: the caller on the left channel and the agent
    on the right.

    Audio is available only after the session has ended and only when the
    agent was configured with `store=True`. For bring-your-own-storage (BYOS)
    accounts the metadata carries a `blob_uri` instead, and the bytes are read
    from your own storage rather than streamed here.

USAGE:
    python sample_voice_agent_read_conversation_audio.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME - The name of the voice agent.
    3) FOUNDRY_VOICE_CONVERSATION_ID - The id of a persisted conversation.
"""

import os
from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()


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


def read_merged_recording(conversations, agent_name, conversation_id) -> None:
    """Read the merged whole-call stereo recording (left=user, right=agent).

    :param conversations: The conversation operations client.
    :param agent_name: The voice agent name.
    :param conversation_id: The persisted conversation id.
    :type conversations: azure.ai.projects.operations.AgentEndpointConversationsOperations
    :type agent_name: str
    :type conversation_id: str
    """
    recording = conversations.get_agent_conversation_audio(agent_name, conversation_id)
    print(
        f"Recording: format={recording.format}, sample_rate={recording.sample_rate}, "
        f"channels={recording.channels}, duration_ms={recording.duration_ms}"
    )

    if recording.blob_uri:
        # Bring-your-own-storage: download from your own storage using the returned URI.
        print(f"Recording is stored in your own storage at: {recording.blob_uri}")
        return

    # Foundry-managed storage: stream the bytes and write them to a local WAV file.
    stream = conversations.get_agent_conversation_audio_content(agent_name, conversation_id)
    stream_to_wav(stream, f"{conversation_id}.wav")


def read_first_item_audio(conversations, agent_name, conversation_id) -> None:
    """Read the audio segment of the first conversation item that has one.

    :param conversations: The conversation operations client.
    :param agent_name: The voice agent name.
    :param conversation_id: The persisted conversation id.
    :type conversations: azure.ai.projects.operations.AgentEndpointConversationsOperations
    :type agent_name: str
    :type conversation_id: str
    """
    for item in conversations.list_agent_conversation_items(agent_name, conversation_id):
        item_id = item.get("id")
        if not item_id:
            continue
        try:
            metadata = conversations.get_agent_conversation_item_audio(agent_name, conversation_id, item_id)
        except HttpResponseError as e:
            # A 404 means this item has no persisted audio (for example, a text-only turn).
            if e.status_code == 404:
                continue
            raise

        print(f"Item {item_id}: role={metadata.role}, duration_ms={metadata.duration_ms}")
        if metadata.blob_uri:
            print(f"Item audio is stored in your own storage at: {metadata.blob_uri}")
            return

        stream = conversations.get_agent_conversation_item_audio_content(agent_name, conversation_id, item_id)
        stream_to_wav(stream, f"{conversation_id}_{item_id}.wav")
        return

    print("No conversation item with audio was found.")


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_VOICE_AGENT_NAME"]
    conversation_id = os.environ["FOUNDRY_VOICE_CONVERSATION_ID"]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        conversations = project_client.agent_endpoint_conversations
        try:
            read_merged_recording(conversations, agent_name, conversation_id)
            read_first_item_audio(conversations, agent_name, conversation_id)
        except HttpResponseError as e:
            # 404: not persisted / not ready. 409: session still in progress.
            print(f"Service responded with an error: {e.status_code} {e.reason}")


if __name__ == "__main__":
    main()
