# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_query_knowledgebase_async.py

DESCRIPTION:
    Async knowledge base query using flattened parameters.

USAGE:
    python sample_query_knowledgebase_async.py
"""

from __future__ import annotations
import asyncio


async def sample_query_knowledgebase():
    # [START query_knowledgebase_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
    from azure.ai.language.questionanswering.models import (
        AnswersOptions,
        ShortAnswerOptions,
    )

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    project = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]
    deployment = os.environ.get("AZURE_QUESTIONANSWERING_DEPLOYMENT", "production")

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    async with client:
        question = "How long should my Surface battery last?"
        options = AnswersOptions(
            question=question,
            top=3,
            confidence_threshold=0.2,
            include_unstructured_sources=True,
            short_answer_options=ShortAnswerOptions(enable=True, confidence_threshold=0.2, top=1),
        )
        output = await client.get_answers(
            options,
            project_name=project,
            deployment_name=deployment,
        )
        best_candidate = next(
            (a for a in (output.answers or []) if a.confidence and a.confidence > 0.7),
            None,
        )
        if best_candidate:
            print(f"Q: {question}")
            print(f"A: {best_candidate.answer}")
        else:
            print(f"No answers for '{question}'")
    # [END query_knowledgebase_async]


if __name__ == "__main__":
    asyncio.run(sample_query_knowledgebase())
