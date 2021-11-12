# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_query_knowledgebase.py

DESCRIPTION:
    This sample demonstrates how to ask a question from a knowledge base.

USAGE:
    python sample_query_knowledgebase.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
    3) AZURE_QUESTIONANSWERING_PROJECT - the name of a knowledge base project.
"""


def sample_query_knowledgebase():
    # [START query_knowledgebase]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering import QuestionAnsweringClient
    from azure.ai.language.questionanswering import models as qna

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    knowledge_base_project = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    with client:
        question="How long should my Surface battery last?"
        output = client.get_answers(
            question=question,
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
        best_candidate = [a for a in output.answers if a.confidence > 0.9][0]
        print("Q: {}".format(question))
        print("A: {}".format(best_candidate.answer))

    # [END query_knowledgebase]


if __name__ == '__main__':
    sample_query_knowledgebase()
