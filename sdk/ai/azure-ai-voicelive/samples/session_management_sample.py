# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: session_management_sample.py
DESCRIPTION:
    This sample demonstrates using the SessionResource class and proper error handling
    with the VoiceLive SDK.
USAGE:
    python session_management_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_API_KEY - The API key for your VoiceLive resource.
"""

import os
import logging
import time
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import (
    VoiceLiveClient, 
    VoiceLiveConnectionError,
    VoiceLiveConnectionClosed
)
from azure.ai.voicelive.models import (
    VoiceLiveServerEventSessionUpdated,
    VoiceLiveServerEventError
)

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function demonstrating session management and error handling."""
    # Get the API key from environment variables
    api_key = os.environ.get("AZURE_VOICELIVE_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Set the AZURE_VOICELIVE_API_KEY environment variable.")

    # Initialize the client
    client = VoiceLiveClient(
        credential=AzureKeyCredential(api_key),
        endpoint="wss://api.voicelive.com/v1"
    )

    try:
        # Connect to the VoiceLive WebSocket API with error handling
        with client.connect(
            model="gpt-4o-realtime-preview",
            websocket_connection_options={"max_size": 10 * 1024 * 1024}  # 10MB max message size
        ) as connection:
            # Demonstrate sequential session updates with different configurations
            
            # First update: Configure for text only
            logger.info("Updating session for text-only mode...")
            connection.session.update(
                session={
                    "modalities": ["text"],
                    "turn_detection": {"type": "server_vad"}
                },
                event_id="config-update-1"
            )
            
            # Wait for the session update confirmation
            session_updated = False
            for event in connection:
                if isinstance(event, VoiceLiveServerEventSessionUpdated):
                    session_updated = True
                    logger.info(f"Session updated (text-only): {event.session.id}")
                    logger.info(f"Current modalities: {event.session.modalities}")
                    break
                elif isinstance(event, VoiceLiveServerEventError):
                    logger.error(f"Session update failed: {event.error.message}")
                    raise VoiceLiveConnectionError(f"Session update failed: {event.error.message}")
            
            if not session_updated:
                logger.warning("Did not receive session update confirmation")
            
            time.sleep(1)  # Small delay between updates
            
            # Second update: Update to include audio
            logger.info("Updating session to include audio...")
            connection.session.update(
                session={
                    "modalities": ["text", "audio"],
                    "voice": "alloy"
                },
                event_id="config-update-2"
            )
            
            # Process events again
            for event in connection:
                if isinstance(event, VoiceLiveServerEventSessionUpdated):
                    logger.info(f"Session updated (with audio): {event.session.id}")
                    logger.info(f"Current modalities: {event.session.modalities}")
                    logger.info(f"Voice: {event.session.voice}")
                    break
                elif isinstance(event, VoiceLiveServerEventError):
                    logger.error(f"Session update failed: {event.error.message}")
                    raise VoiceLiveConnectionError(f"Session update failed: {event.error.message}")
            
            # Clean up by closing the connection manually
            logger.info("Closing connection...")
            connection.close(code=1000, reason="Session management demo completed")
            
    except ImportError as e:
        logger.error(f"Required package not installed: {e}")
        logger.info("Please install the 'websockets' package with 'pip install websockets'")
    except VoiceLiveConnectionClosed as e:
        logger.warning(f"Connection closed: Code {e.code}, Reason: {e.reason}")
    except VoiceLiveConnectionError as e:
        logger.error(f"Connection error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

if __name__ == "__main__":
    main()