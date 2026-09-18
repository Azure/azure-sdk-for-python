# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates reading the persisted audio of a voice
    conversation via `project_client.beta.voice_agents.conversations`, both the
    merged whole-call recording and a single turn's audio segment. For each it
    reads the metadata first, then streams the WAV bytes to a local file. The
    merged recording is stereo: the caller on the left channel and the agent
    on the right.

    Audio is available only after the session has ended and only when the
    agent was configured with `store=True`. For bring-your-own-storage (BYOS)
    accounts the metadata carries a `blob_uri` instead, and the bytes are read
    from your own storage rather than streamed here.

    Runs with no setup beyond the endpoint: if FOUNDRY_VOICE_CONVERSATION_ID is
    not set, this sample creates a temporary voice agent, holds one short
    realtime text turn to produce a real conversation, then reads its audio
    back -- the agent's reply is real synthesized speech either way, so both
    the merged recording and the reply's own audio segment are available even
    though the turn itself was typed. Set FOUNDRY_VOICE_AGENT_NAME to hold that
    conversation against your own existing agent instead -- it is never
    created, modified, or deleted by this sample. Additionally set
    FOUNDRY_VOICE_CONVERSATION_ID to skip holding a new conversation entirely
    and just read back the audio of one your agent already produced.

USAGE:
    python sample_voice_agent_read_conversation_audio.py

    Before running the sample:

    pip install "azure-ai-projects[voice]>=2.7.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME - Optional. The name of an existing voice
       agent (configured with `store=True`) to hold or read a conversation on.
       Defaults to a temporary agent, created and deleted by this sample, when
       unset.
    3) FOUNDRY_VOICE_CONVERSATION_ID - Optional. The id of a persisted
       conversation owned by FOUNDRY_VOICE_AGENT_NAME. If unset, this sample
       holds one short realtime text turn to produce one; see
       voice_sample_util.py in this folder and
       sample_voice_agent_live_text_conversation.py for a full interactive
       version.
    4) FOUNDRY_VOICE_MODEL - Optional. The realtime model deployment name,
       used only when creating the temporary agent. Defaults to "gpt-realtime".
"""

import os
from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceModelType,
    VoiceOutputModality,
    VoiceType,
)

from voice_sample_util import hold_sample_conversation

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
    :type conversations: azure.ai.projects.operations.BetaVoiceAgentsConversationsOperations
    :type agent_name: str
    :type conversation_id: str
    """
    try:
        recording = conversations.get_audio(agent_name, conversation_id)
    except HttpResponseError as e:
        # A 404 means no merged recording exists for this conversation, for example because the
        # agent was configured with `store=False`, or the session has not finished finalizing yet.
        if e.status_code == 404:
            print("No merged whole-call recording is available for this conversation.")
            return
        raise

    print(
        f"Recording: format={recording.format}, sample_rate={recording.sample_rate}, "
        f"channels={recording.channels}, duration_ms={recording.duration_ms}"
    )

    if recording.blob_uri:
        # Bring-your-own-storage: download from your own storage using the returned URI.
        print(f"Recording is stored in your own storage at: {recording.blob_uri}")
        return

    # Foundry-managed storage: stream the bytes and write them to a local WAV file.
    stream = conversations.download_audio(agent_name, conversation_id)
    stream_to_wav(stream, f"{conversation_id}.wav")


def read_first_item_audio(conversations, agent_name, conversation_id) -> None:
    """Read the audio segment of the first conversation item that has one.

    :param conversations: The conversation operations client.
    :param agent_name: The voice agent name.
    :param conversation_id: The persisted conversation id.
    :type conversations: azure.ai.projects.operations.BetaVoiceAgentsConversationsOperations
    :type agent_name: str
    :type conversation_id: str
    """
    for item in conversations.list_items(agent_name, conversation_id):
        item_id = item.get("id")
        if not item_id:
            continue
        try:
            metadata = conversations.get_audio_item(agent_name, conversation_id, item_id)
        except HttpResponseError as e:
            # A 404 means this item has no persisted audio (for example, a text-only turn).
            if e.status_code == 404:
                continue
            raise

        print(f"Item {item_id}: role={metadata.role}, duration_ms={metadata.duration_ms}")
        if metadata.blob_uri:
            print(f"Item audio is stored in your own storage at: {metadata.blob_uri}")
            return

        stream = conversations.download_audio_item(agent_name, conversation_id, item_id)
        stream_to_wav(stream, f"{conversation_id}_{item_id}.wav")
        return

    print("No conversation item with audio was found.")


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME")
    conversation_id = os.environ.get("FOUNDRY_VOICE_CONVERSATION_ID")
    model = os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
    # Only create (and later clean up) a temporary agent when the caller didn't name their own --
    # creating a version on someone's existing agent could unexpectedly mutate it, and deleting
    # that version afterward could delete the agent entirely if it was its only version.
    owns_agent = not agent_name
    agent_name = agent_name or "sample-read-conversation-audio-agent"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        conversations = project_client.beta.voice_agents.conversations
        created_version = None
        try:
            if not conversation_id:
                print(
                    f"No FOUNDRY_VOICE_CONVERSATION_ID set; holding a short conversation with "
                    f"'{agent_name}' first..."
                )
                if owns_agent:
                    created_version = project_client.agents.create_version(
                        agent_name=agent_name,
                        definition=VoiceAgentDefinition(
                            model_type=VoiceModelType.MANAGED,
                            model=model,
                            instructions="You are a friendly voice assistant. Keep replies short and natural.",
                            audio=VoiceAgentAudioConfig(
                                output=VoiceAgentAudioOutputConfig(
                                    voice="en-US-AvaNeural", voice_type=VoiceType.AZURE_STANDARD
                                ),
                            ),
                            output_modalities=[VoiceOutputModality.AUDIO],
                            store=True,
                        ),
                    )
                conversation_id = hold_sample_conversation(project_client, agent_name)
                print(f"Created conversation: {conversation_id}")

            read_merged_recording(conversations, agent_name, conversation_id)
            read_first_item_audio(conversations, agent_name, conversation_id)
        except HttpResponseError as e:
            # 404: not persisted / not ready. 409: session still in progress.
            print(f"Service responded with an error: {e.status_code} {e.reason}")
        finally:
            if created_version is not None:
                project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
                print(f"Deleted temporary voice agent version: {created_version.version}")


if __name__ == "__main__":
    main()
