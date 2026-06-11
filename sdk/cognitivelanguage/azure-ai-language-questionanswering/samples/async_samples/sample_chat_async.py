# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_chat_async.py

DESCRIPTION:
    Async follow-up (contextual) question with answer_context.

USAGE:
    python sample_chat_async.py
"""

from __future__ import annotations
import asyncio


async def sample_chit_chat():
    # [START chit_chat_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
    from azure.ai.language.questionanswering.models import (
        AnswersOptions,
        ShortAnswerOptions,
        KnowledgeBaseAnswerContext,
    )

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    project = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]
    deployment = os.environ.get("AZURE_QUESTIONANSWERING_DEPLOYMENT", "production")

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    async with client:
        first_question = "How long should my Surface battery last?"
        first_options = AnswersOptions(
            question=first_question,
            top=3,
            confidence_threshold=0.2,
            include_unstructured_sources=True,
            short_answer_options=ShortAnswerOptions(enable=True, confidence_threshold=0.2, top=1),
        )
        first_output = await client.get_answers(
            first_options,
            project_name=project,
            deployment_name=deployment,
        )
        best_candidate = next(
            (a for a in (first_output.answers or []) if a.confidence and a.confidence > 0.7),
            None,
        )
        if not best_candidate:
            print(f"No answers for '{first_question}'")
            return

        print(f"Q: {first_question}")
        print(f"A: {best_candidate.answer}")

        if best_candidate.qna_id:
            followup_question = "How long does it take to charge a Surface?"
            followup_options = AnswersOptions(
                question=followup_question,
                top=3,
                confidence_threshold=0.2,
                answer_context=KnowledgeBaseAnswerContext(
                    previous_question=first_question,
                    previous_qna_id=best_candidate.qna_id,
                ),
                short_answer_options=ShortAnswerOptions(enable=True, confidence_threshold=0.2, top=1),
                include_unstructured_sources=True,
            )
            follow_output = await client.get_answers(
                followup_options,
                project_name=project,
                deployment_name=deployment,
            )
            follow_best = next(
                (a for a in (follow_output.answers or []) if a.confidence and a.confidence > 0.2),
                None,
            )
            if follow_best:
                print(f"Q: {followup_question}")
                print(f"A: {follow_best.answer}")
            else:
                print(f"No answers for follow-up '{followup_question}'")
    # [END chit_chat_async]


if __name__ == "__main__":
    asyncio.run(sample_chit_chat())
