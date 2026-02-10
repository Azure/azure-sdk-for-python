# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_query_knowledgebase.py

DESCRIPTION:
    Ask a question against a deployed knowledge base (flattened parameter style).

USAGE:
    python sample_query_knowledgebase.py

Environment variables:
    1) AZURE_QUESTIONANSWERING_ENDPOINT   - endpoint for the resource
    2) AZURE_QUESTIONANSWERING_KEY        - API key
    3) AZURE_QUESTIONANSWERING_PROJECT    - knowledge base project name
    4) AZURE_QUESTIONANSWERING_DEPLOYMENT - (optional) deployment name (defaults to 'production')
"""


def sample_query_knowledgebase():
    # [START query_knowledgebase]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering import QuestionAnsweringClient
    from azure.ai.language.questionanswering.models import AnswersOptions, ShortAnswerOptions

    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    project = os.environ["AZURE_QUESTIONANSWERING_PROJECT"]
    deployment = os.environ.get("AZURE_QUESTIONANSWERING_DEPLOYMENT", "production")

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    with client:
        question = "How long should my Surface battery last?"

        options = AnswersOptions(
            question=question,
            top=3,
            confidence_threshold=0.2,
            include_unstructured_sources=True,
            short_answer_options=ShortAnswerOptions(enable=True, confidence_threshold=0.2, top=1),
        )
        output = client.get_answers(
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

    # [END query_knowledgebase]


if __name__ == "__main__":
    sample_query_knowledgebase()
