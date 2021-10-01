# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_workflow_app.py

DESCRIPTION:
    This sample demonstrates how to analyze user query using an orchestration/workflow project.
    In this sample, workflow project's top intent will map to a Qna project.
    
    For more info about how to setup a CLU workflow project, see the README.

USAGE:
    python sample_analyze_workflow_app.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT - the endpoint to your CLU resource.
    2) AZURE_CONVERSATIONS_KEY - your CLU API key.
    3) AZURE_CONVERSATIONS_WORKFLOW_PROJECT - the name of your CLU workflow project.
"""

def sample_analyze_workflow_app():
    # [START analyze_workflow_app]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient
    from azure.ai.language.conversations.models import AnalyzeConversationOptions

    # get secrets
    conv_endpoint = os.environ.get("AZURE_CONVERSATIONS_ENDPOINT"),
    conv_key = os.environ.get("AZURE_CONVERSATIONS_KEY"),
    workflow_project = os.environ.get("AZURE_CONVERSATIONS_WORKFLOW_PROJECT")

    # prepare data
    query = "How do you make sushi rice?",
    input = AnalyzeConversationOptions(
        query=query
    )

    # analyze query
    client = ConversationAnalysisClient(conv_endpoint, AzureKeyCredential(conv_key))
    with client:
        result = client.analyze_conversations(
            input,
            project_name=workflow_project,
            deployment_name='production',
        )
    
    # view result
    print("query: {}".format(result.query))
    print("project kind: {}\n".format(result.prediction.project_kind))

    print("view top intent:")
    print("top intent: {}".format(result.prediction.top_intent))
    print("\tcategory: {}".format(result.prediction.intents[0].category))
    print("\tconfidence score: {}\n".format(result.prediction.intents[0].confidence_score))

    print("view qna result:")
    print("\tresult: {}\n".format(result.prediction.intents[0].result))
    # [END analyze_workflow_app]

if __name__ == '__main__':
    sample_analyze_workflow_app()