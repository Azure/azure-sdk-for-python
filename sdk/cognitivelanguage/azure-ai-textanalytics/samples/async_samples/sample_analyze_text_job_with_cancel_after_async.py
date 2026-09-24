# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_text_job_with_cancel_after_async.py

DESCRIPTION:
    This sample demonstrates how to cancel a PII analysis job automatically if it does not
    complete within a specified duration using the async client.

USAGE:
    python sample_analyze_text_job_with_cancel_after_async.py

REQUIRED ENV VARS:
    AZURE_TEXT_ENDPOINT
"""

# [START analyze_text_job_with_cancel_after_async]
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextOperationState,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiEntityRecognitionOperationResult,
    PiiLROTask,
)


def deserialize_job_state(pipeline_response, _, __):
    return AnalyzeTextOperationState(pipeline_response.http_response.json())


async def sample_analyze_text_job_with_cancel_after_async():
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    async with credential, TextAnalysisClient(endpoint, credential=credential) as client:
        text_input = MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(
                    id="1",
                    text="My name is John Doe. My SSN is 123-45-6789.",
                    language="en",
                ),
                MultiLanguageInput(
                    id="2",
                    text="Contact Jane Doe at jane@example.com.",
                    language="en",
                ),
            ]
        )

        poller = await client.begin_analyze_text_job(
            text_input=text_input,
            actions=[PiiLROTask(name="PiiWithCancelAfter")],
            cancel_after=30,
            cls=deserialize_job_state,
        )
        job_state = await poller.result()

        print(f"Job ID: {job_state.job_id}")
        print(f"Status: {job_state.status}")
        if job_state.actions and job_state.actions.items_property:
            for action_result in job_state.actions.items_property:
                if isinstance(action_result, PiiEntityRecognitionOperationResult):
                    for document in action_result.results.documents:
                        print(f'Document "{document.id}" redacted text: {document.redacted_text}')


# [END analyze_text_job_with_cancel_after_async]


if __name__ == "__main__":
    asyncio.run(sample_analyze_text_job_with_cancel_after_async())
