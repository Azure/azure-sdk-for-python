# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_chat.py

DESCRIPTION:
    This sample demonstrates how to ask a follow-up question (chit-chat) from a knowledge base.

USAGE:
    python sample_chat.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
    3) AZURE_QUESTIONANSWERING_PROJECT - the name of a knowledge base project.
"""


def sample_chit_chat():
    # [START chit_chat]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering import QuestionAnsweringClient
    from azure.ai.language.questionanswering import models as qna

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    knowledge_base_project = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    with client:
        first_question = qna.KnowledgeBaseQueryOptions(
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

        output = client.query_knowledge_base(
            first_question,
            project_name=knowledge_base_project,
            deployment_name="test"
        )
        best_candidate = [a for a in output.answers if a.confidence_score > 0.9][0]
        print("Q: {}".format(first_question.question))
        print("A: {}".format(best_candidate.answer))

        followup_question = qna.KnowledgeBaseQueryOptions(
            question="How long it takes to charge Surface?",
            top=3,
            confidence_score_threshold=0.2,
            context=qna.KnowledgeBaseAnswerRequestContext(
                previous_user_query="How long should my Surface battery last?",
                previous_qna_id=best_candidate.id
            ),
            answer_span_request=qna.AnswerSpanRequest(
                enable=True,
                confidence_score_threshold=0.2,
                top_answers_with_span=1
            ),
            include_unstructured_sources=True
        )

        output = client.query_knowledge_base(
            followup_question,
            project_name=knowledge_base_project,
            deployment_name="test"
        )
        print("Q: {}".format(followup_question.question))
        print("A: {}".format(output.answers[0].answer))

    # [END chit_chat]


if __name__ == '__main__':
    sample_chit_chat()