# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_advanced_rehydrate_operation_async.py

DESCRIPTION:
    This sample demonstrates how to use continuation tokens to persist the state of a
    long-running analysis operation and resume polling from a different process or after
    a restart. This is the async version of the sample.

    About rehydration / continuation tokens:
    When you start an analysis with begin_analyze, the returned poller has a
    continuation_token() method that captures the full operation state. You can persist
    this token (e.g., to a database, queue, or file) and later resume polling from a
    different process using begin_analyze with the continuation_token parameter.

    This is useful when:
    - The analysis takes a long time and you can't keep the process alive
    - You need to start the operation in one service (e.g., a web API) and poll for
      completion in another (e.g., a background worker)
    - You want to persist the operation state across application restarts

    This sample runs as two separate subprocesses to demonstrate a realistic handoff:
    - Process A starts the analysis, saves the continuation token to a temp file, and exits.
    - Process B reads the token, resumes polling, and prints the extracted markdown.

USAGE:
    python sample_advanced_rehydrate_operation_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import asyncio
import os
import sys
import subprocess
import tempfile

from dotenv import load_dotenv

load_dotenv()


async def process_a(token_file: str) -> None:
    """Process A: Start analysis and save the continuation token to a file."""
    from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
    from azure.ai.contentunderstanding.models import AnalysisInput
    from azure.core.credentials import AzureKeyCredential
    from azure.identity.aio import DefaultAzureCredential

    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client:
        document_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        # [START rehydrate_process_a_async]
        # Start a long-running analysis. The poller returns immediately.
        poller = await client.begin_analyze(
            analyzer_id="prebuilt-read",
            inputs=[AnalysisInput(url=document_url)],
        )
        print(f"Process A: Operation started. Status: {poller.status()}")

        # Get the continuation token — captures the full operation state.
        token = poller.continuation_token()
        print(f"Process A: Continuation token obtained ({len(token)} chars)")

        # Save the token to a file. In production, you might use a database or message queue.
        with open(token_file, "w") as f:
            f.write(token)
        print(f"Process A: Token saved to {token_file}")
        print("Process A: Exiting. The operation continues running on the server.")
        # [END rehydrate_process_a_async]


async def process_b(token_file: str) -> None:
    """Process B: Read the continuation token and resume polling."""
    from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
    from azure.ai.contentunderstanding.models import (
        AnalysisInput,
        AnalysisResult,
        DocumentContent,
    )
    from azure.core.credentials import AzureKeyCredential
    from azure.identity.aio import DefaultAzureCredential

    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client:
        # [START rehydrate_process_b_async]
        # Read the saved continuation token from file.
        with open(token_file, "r") as f:
            saved_token = f.read()
        print(f"Process B: Token loaded from file ({len(saved_token)} chars)")

        # Resume the operation using the continuation_token parameter.
        # The SDK reconstructs the polling state and resumes where Process A left off.
        # Note: analyzer_id and inputs are required parameters but are ignored when
        # continuation_token is provided — the token contains the full original request.
        resumed_poller = await client.begin_analyze(
            analyzer_id="prebuilt-read",
            inputs=[],
            continuation_token=saved_token,
        )

        # Wait for the operation to complete and get the result.
        result: AnalysisResult = await resumed_poller.result()
        print(
            f"Process B: Operation completed! Contents: {len(result.contents) if result.contents else 0}"
        )

        # Access the extracted markdown content.
        if result.contents and len(result.contents) > 0:
            content: DocumentContent = result.contents[0]  # type: ignore
            markdown = content.markdown or ""
            print(f"Process B: Markdown length: {len(markdown)} chars")
            print(f"Process B: First 200 chars:\n{markdown[:200]}")
        # [END rehydrate_process_b_async]

        # Clean up.
        os.remove(token_file)


def main() -> None:
    """Orchestrate the two-process demo."""
    token_file = os.path.join(tempfile.gettempdir(), "cu-continuation-token-async.txt")

    if len(sys.argv) > 1:
        # Called as a subprocess
        role = sys.argv[1]
        if role == "--process-a":
            asyncio.run(process_a(token_file))
        elif role == "--process-b":
            asyncio.run(process_b(token_file))
        else:
            print(f"Unknown role: {role}")
            sys.exit(1)
    else:
        # Main orchestrator — spawn two separate subprocesses
        print("=== Two-Process Rehydration Demo (Async) ===\n")

        # Spawn Process A
        print("--- Spawning Process A ---")
        result_a = subprocess.run(
            [sys.executable, __file__, "--process-a"],
            env=os.environ,
            capture_output=True,
            text=True,
        )
        print(result_a.stdout)
        if result_a.returncode != 0:
            print(f"Process A failed:\n{result_a.stderr}")
            sys.exit(1)

        # Spawn Process B (a completely separate process)
        print("--- Spawning Process B ---")
        result_b = subprocess.run(
            [sys.executable, __file__, "--process-b"],
            env=os.environ,
            capture_output=True,
            text=True,
        )
        print(result_b.stdout)
        if result_b.returncode != 0:
            print(f"Process B failed:\n{result_b.stderr}")
            sys.exit(1)

        print("=== Demo complete ===")


if __name__ == "__main__":
    main()
