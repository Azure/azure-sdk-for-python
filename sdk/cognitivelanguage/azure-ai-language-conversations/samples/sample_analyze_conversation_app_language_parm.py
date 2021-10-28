# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_conversation_app_language_parm.py

DESCRIPTION:
    This sample demonstrates how to analyze user query for intents and entities using a conversation project.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_analyze_conversation_app_language_parm.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT - the endpoint to your CLU resource.
    2) AZURE_CONVERSATIONS_KEY - your CLU API key.
    3) AZURE_CONVERSATIONS_PROJECT - the name of your CLU conversations project.
"""

def sample_analyze_conversation_app_language_parm():
    # [START analyze_conversation_app_language_parm]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient
    from azure.ai.language.conversations.models import ConversationAnalysisOptions

    # get secrets
    conv_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    conv_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    conv_project = os.environ["AZURE_CONVERSATIONS_PROJECT"]

    # prepare data
    query = "One california maki please."
    input = ConversationAnalysisOptions(
        query=query,
        language="en"
    )

    # analyze quey
    client = ConversationAnalysisClient(conv_endpoint, AzureKeyCredential(conv_key))
    with client:
        result = client.analyze_conversations(
            input,
            project_name=conv_project,
            deployment_name='production'
        )

    # view result
    print("query: {}".format(result.query))
    print("project kind: {}\n".format(result.prediction.project_kind))

    print("view top intent:")
    print("\ttop intent: {}".format(result.prediction.top_intent))
    print("\tcategory: {}".format(result.prediction.intents[0].category))
    print("\tconfidence score: {}\n".format(result.prediction.intents[0].confidence_score))

    print("view entities:")
    for entity in result.prediction.entities:
        print("\tcategory: {}".format(entity.category))
        print("\ttext: {}".format(entity.text))
        print("\tconfidence score: {}".format(entity.confidence_score))
    # [END analyze_conversation_app_language_parm]


if __name__ == '__main__':
    sample_analyze_conversation_app_language_parm()
