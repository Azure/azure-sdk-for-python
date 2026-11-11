# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_rehydrate_operation_async.py

DESCRIPTION:
    This sample demonstrates how to use LRO continuation tokens to persist the state of a
    long-running analysis operation and resume polling later — for example from another process
    or after a restart.

    ## When to use rehydration

    - You can't keep the calling process alive for the full analysis duration.
    - You need cross-process handoff (start in a web API, finish in a worker).
    - You want crash resilience by persisting operation state.

    ## How it works (Python)

    1. Start analysis with ``begin_analyze`` (do not call ``result()`` yet).
    2. Call ``poller.continuation_token()`` and persist the returned string.
    3. Later, call ``begin_analyze(..., continuation_token=saved_token)`` to reconstruct the
       poller and resume polling with ``result()``.

USAGE:
    python sample_rehydrate_operation_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults_async.py for model deployment setup guidance.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput, AnalysisResult
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    token_file_path: Optional[Path] = None
    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        try:
            # [START rehydrate_start_and_save_token]
            # Start a long-running analysis without waiting for completion.
            document_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"
            poller = await client.begin_analyze(
                analyzer_id="prebuilt-read",
                inputs=[AnalysisInput(url=document_url)],
            )

            operation_id = poller.operation_id
            print(f"Operation started with ID: {operation_id}")

            # Capture the continuation token so polling can resume later.
            continuation_token = poller.continuation_token()
            print(f"Continuation token obtained ({len(continuation_token)} chars)")

            # Persist the token. In a real app, store this in a database, queue message, or durable store.
            token_file_path = Path(tempfile.gettempdir()) / f"cu-operation-{operation_id}.token"
            token_file_path.write_text(continuation_token, encoding="utf-8")
            print(f"Token saved to {token_file_path}")
            # Process A can now exit. The operation continues running on the server.
            # [END rehydrate_start_and_save_token]

            # [START rehydrate_resume_polling]
            # Simulate Process B: read the saved token and resume polling.
            saved_token = token_file_path.read_text(encoding="utf-8")
            print(f"Token loaded from file ({len(saved_token)} chars)")

            # Reconstruct the poller from the continuation token without re-sending the analyze request.
            # analyzer_id is still required by the method signature; the continuation token drives resume.
            # continuation_token is an LRO kwargs accepted by the poller infrastructure, not a typed overload.
            rehydrated_poller = await client.begin_analyze(  # type: ignore[call-overload]
                analyzer_id="prebuilt-read",
                continuation_token=saved_token,
            )
            print(f"Operation rehydrated. Done: {rehydrated_poller.done()}")

            result: AnalysisResult = await rehydrated_poller.result()
            print(f"Operation completed: {rehydrated_poller.done()}")

            for content in result.contents or []:
                print(f"--- Content (MIME: {content.mime_type}) ---")
                print(content.markdown)

            token_file_path.unlink(missing_ok=True)
            # [END rehydrate_resume_polling]
        finally:
            if token_file_path is not None and token_file_path.exists():
                token_file_path.unlink()

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
