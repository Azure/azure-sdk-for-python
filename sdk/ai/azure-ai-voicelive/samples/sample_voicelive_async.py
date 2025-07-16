#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_voicelive_async.py

DESCRIPTION:
    This sample demonstrates how to use the Azure VoiceLive async client
    to interact with the VoiceLive API.

USAGE:
    python sample_voicelive_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_KEY - The Azure VoiceLive key.
"""

import os
import asyncio
import base64
import time
import argparse
from typing import Optional, List, Dict, Any
import wave
import sys

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from samples.utils import load_env_vars, check_samples_prerequisites

# Check prerequisites
check_samples_prerequisites()

# Load environment variables from .env file if available
load_env_vars()

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from azure.ai.voicelive.aio import AsyncVoiceLiveClient


async def main():
    parser = argparse.ArgumentParser(
        description="Connect to Azure VoiceLive API and converse with an AI model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--api-key",
        help="Azure VoiceLive API key. If not provided, will use the AZURE_VOICELIVE_KEY environment variable.",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_KEY"),
    )
    parser.add_argument(
        "--use-token-credential",
        help="Use Azure token credential instead of API key",
        action="store_true",
    )
    parser.add_argument(
        "--model",
        help="VoiceLive model to use",
        type=str,
        default=os.environ.get("VOICELIVE_MODEL", "gpt-4o-realtime-preview"),
    )
    parser.add_argument(
        "--voice",
        help="Voice to use for the assistant",
        type=str,
        default=os.environ.get("VOICELIVE_VOICE", "alloy"),
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    )
    parser.add_argument(
        "--endpoint",
        help="Azure VoiceLive endpoint",
        type=str,
        default=os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://api.voicelive.com/v1"),
    )
    parser.add_argument(
        "--instructions",
        help="System instructions for the AI model",
        type=str,
        default=os.environ.get("VOICELIVE_INSTRUCTIONS", "You are a helpful assistant. Keep your responses concise."),
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.api_key and not args.use_token_credential:
        raise ValueError(
            "Please provide an API key using --api-key or set the AZURE_VOICELIVE_KEY environment variable, "
            "or use --use-token-credential to use Azure authentication."
        )
    
    # Create client with the appropriate credential
    if args.use_token_credential:
        credential = DefaultAzureCredential()
    else:
        credential = AzureKeyCredential(args.api_key)
    
    # Initialize the client
    client = AsyncVoiceLiveClient(
        credential=credential,
        endpoint=args.endpoint,
    )
    
    # Connect to the WebSocket API
    print(f"Connecting to {args.endpoint} with model {args.model}")
    async with client.connect(
        model=args.model,
        websocket_connection_options={
            "max_size": 10 * 1024 * 1024,  # 10 MB
            "ping_interval": 20,  # 20 seconds
            "ping_timeout": 20,  # 20 seconds
        }
    ) as connection:
        # Set up the session
        print("Setting up session...")
        await connection.session.update(
            session={
                "instructions": args.instructions,
                "voice": args.voice,
                "modalities": ["text"],  # Using text-only for this example
                "turn_detection": {"type": "server_vad"}  # Server-side voice activity detection
            }
        )
        
        # Process events
        print("Processing events...")
        async for event in connection:
            print(f"Received event: {event.type}")
            
            if event.type == "session.updated":
                print(f"Session initialized with ID: {event.session.id}")
                
                # Create a user message
                await connection.conversation.item.create(
                    item={
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "text", "text": "Hello! Tell me about Azure VoiceLive in a brief paragraph."}]
                    }
                )
                
            elif event.type == "conversation.item.created":
                print(f"Item created with ID: {event.item.id}")
                
                # If it's a user message that was created, request a response
                if hasattr(event, "item") and event.item.role == "user":
                    print("Requesting model response...")
                    await connection.response.create()
                
            elif event.type == "response.text.delta":
                print(event.delta, end="", flush=True)
                
            elif event.type == "response.done":
                print("\nResponse complete")
                print("Conversation completed. Exiting...")
                break


if __name__ == "__main__":
    asyncio.run(main())