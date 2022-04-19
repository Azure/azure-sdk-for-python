# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_orchestration_app_qna_response.py

DESCRIPTION:
    This sample demonstrates how to analyze user query using an orchestration project.
    In this sample, orchestration project's top intent will map to a Qna project.

    For more info about how to setup a CLU orchestration project, see the README.

USAGE:
    python sample_analyze_orchestration_app_qna_response.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME     - project name for your CLU orchestration project.
    4) AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME  - deployment name for your CLU orchestration project.
"""

def sample_analyze_orchestration_app_qna_response():
    # [START analyze_orchestration_app_qna_response]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient
    from azure.ai.language.conversations.models import (
        CustomConversationalTask,
        ConversationAnalysisOptions,
        CustomConversationTaskParameters,
        TextConversationItem
    )

    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME"]

    # analyze query
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    with client:
        query = "How are you?"
        result = client.analyze_conversation(
                task=CustomConversationalTask(
                    analysis_input=ConversationAnalysisOptions(
                        conversation_item=TextConversationItem(
                            text=query
                        )
                    ),
                    parameters=CustomConversationTaskParameters(
                        project_name=project_name,
                        deployment_name=deployment_name
                    )
                )
            )

    # view result
    print("query: {}".format(result.results.query))
    print("project kind: {}\n".format(result.results.prediction.project_kind))

    # top intent
    top_intent = result.results.prediction.top_intent
    print("top intent: {}".format(top_intent))
    top_intent_object = result.results.prediction.intents[top_intent]
    print("confidence score: {}".format(top_intent_object.confidence))
    print("project kind: {}".format(top_intent_object.target_kind))

    if top_intent_object.target_kind == "question_answering":
        print("\nview qna result:")
        qna_result = top_intent_object.result
        for answer in qna_result.answers:
            print("\nanswer: {}".format(answer.answer))
            print("answer: {}".format(answer.confidence))

    # [END analyze_orchestration_app_qna_response]

if __name__ == '__main__':
    sample_analyze_orchestration_app_qna_response()