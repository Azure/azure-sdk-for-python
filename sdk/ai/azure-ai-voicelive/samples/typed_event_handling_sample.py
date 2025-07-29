# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: typed_event_handling_sample.py
DESCRIPTION:
    This sample demonstrates using the VoiceLive SDK with typed event handling and resource classes.
USAGE:
    python typed_event_handling_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_API_KEY - The API key for your VoiceLive resource.
"""

import os
import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import VoiceLiveClient
from azure.ai.voicelive.models import (
    ServerEventSessionUpdated,
    ServerEventError,
    ServerEventResponseTextDelta,
)

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main function with typed event handling example."""
    # Get the API key from environment variables
    api_key = os.environ.get("AZURE_VOICELIVE_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Set the AZURE_VOICELIVE_API_KEY environment variable.")

    # Initialize the client
    client = VoiceLiveClient(credential=AzureKeyCredential(api_key), endpoint="wss://api.voicelive.com/v1")

    # Connect to the VoiceLive WebSocket API
    with client.connect(model="gpt-4o-realtime-preview") as connection:
        # Update session configuration using the session resource
        connection.session.update(
            session={
                "modalities": ["text"],  # Use text-only mode for this example
                "turn_detection": {"type": "server_vad"},
            }
        )

        logger.info("Session update requested...")

        # Process events with proper typing
        for event in connection:
            logger.info(f"Received event: {event.type}")

            # Handle different event types with specific processing
            if isinstance(event, ServerEventSessionUpdated):
                logger.info(f"Session updated with ID: {event.session.id}")
                logger.info(f"Session modalities: {event.session.modalities}")

                # Send a simple text input
                connection.send(
                    {
                        "type": "conversation.item.create",
                        "conversation_item": {
                            "role": "user",
                            "content": [{"type": "text", "text": "Hello, tell me a brief joke."}],
                        },
                    }
                )

            elif isinstance(event, ServerEventResponseTextDelta):
                # Process text deltas with proper typing
                logger.info(f"Text delta: {event.delta}")

            elif isinstance(event, ServerEventError):
                logger.error(f"Error: {event.error.message}")
                break

            # You can exit after a specific condition is met
            elif event.type == "response.done":
                logger.info("Response complete, exiting...")
                break


if __name__ == "__main__":
    main()
