# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_chat_async.py

DESCRIPTION:
    This sample demonstrates how to ask a follow-up question (chit-chat) from a knowledge base.

USAGE:
    python sample_chat_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
    3) AZURE_QUESTIONANSWERING_PROJECT - the name of a knowledge base project.
"""

import asyncio


async def sample_chit_chat():
    # [START chit_chat_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
    from azure.ai.language.questionanswering import models as qna

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    knowledge_base_project = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    async with client:
        first_question="How long should my Surface battery last?"
        output = await client.get_answers(
            question=first_question,
            top=3,
            confidence_threshold=0.2,
            include_unstructured_sources=True,
            short_answer_options=qna.ShortAnswerOptions(
                confidence_threshold=0.2,
                top=1
            ),
            project_name=knowledge_base_project,
            deployment_name="test"
        )
        best_candidate = [a for a in output.answers if a.confidence > 0.7][0]
        print("Q: {}".format(first_question))
        print("A: {}".format(best_candidate.answer))

        followup_question = "How long it takes to charge Surface?"

        output = await client.get_answers(
            question=followup_question,
            top=3,
            confidence_threshold=0.2,
            answer_context=qna.KnowledgeBaseAnswerContext(
                previous_question=first_question,
                previous_qna_id=best_candidate.qna_id
            ),
            short_answer_options=qna.ShortAnswerOptions(
                confidence_threshold=0.2,
                top=1
            ),
            include_unstructured_sources=True,
            project_name=knowledge_base_project,
            deployment_name="test"
        )
        print("Q: {}".format(followup_question))
        print("A: {}".format(output.answers[0].answer))

    # [END chit_chat_async]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample_chit_chat())
