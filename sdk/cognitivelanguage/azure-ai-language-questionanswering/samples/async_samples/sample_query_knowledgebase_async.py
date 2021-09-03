# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_query_knowledgebase_async.py

DESCRIPTION:
    This sample demonstrates how to ask a question from a knowledge base.

USAGE:
    python sample_query_knowledgebase_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
    3) AZURE_QUESTIONANSWERING_PROJECT - the name of a knowledge base project.
"""

import asyncio


async def sample_query_knowledgebase():
    # [START query_knowledgebase_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
    from azure.ai.language.questionanswering import models as qna

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    knowledge_base_project = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    async with client:
        input = qna.KnowledgeBaseQueryOptions(
            question="How long should my Surface battery last?",
            top=3,
            confidence_score_threshold=0.2,
            include_unstructured_sources=True,
            answer_span_request=qna.AnswerSpanRequest(
                enable=True,
                confidence_score_threshold=0.2,
                top_answers_with_span=1
            ),
        )

        output = await client.query_knowledge_base(
            input,
            project_name=knowledge_base_project,
            deployment_name="test"
        )
        best_candidate = [a for a in output.answers if a.confidence_score > 0.9][0]
        print("Q: {}".format(input.question))
        print("A: {}".format(best_candidate.answer))

    # [END query_knowledgebase_async]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample_query_knowledgebase())
