# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_conversation_app.py

DESCRIPTION:
    This sample demonstrates how to analyze user query for intents and entities using
    a conversation project with a language parameter.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_analyze_conversation_app.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_PROJECT_NAME     - project name for your CLU conversations project.
    4) AZURE_CONVERSATIONS_DEPLOYMENT_NAME  - deployment name for your CLU conversations project.
"""

def sample_analyze_conversation_app():
    # [START analyze_conversation_app]
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
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    # analyze quey
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    with client:
        query = "Send an email to Carol about the tomorrow's demo"
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

    print("top intent: {}".format(result.results.prediction.top_intent))
    print("category: {}".format(result.results.prediction.intents[0].category))
    print("confidence score: {}\n".format(result.results.prediction.intents[0].confidence))

    print("entities:")
    for entity in result.results.prediction.entities:
        print("\ncategory: {}".format(entity.category))
        print("text: {}".format(entity.text))
        print("confidence score: {}".format(entity.confidence))
        if entity.resolutions:
            print("resolutions")
            for resolution in entity.resolutions:
                print("kind: {}".format(resolution.resolution_kind))
                print("value: {}".format(resolution.additional_properties["value"]))
        if entity.extra_information:
            print("extra info")
            for data in entity.extra_information:
                print("kind: {}".format(data.extra_information_kind))
                if data.extra_information_kind == "ListKey":
                    print("key: {}".format(data.key))
                if data.extra_information_kind == "EntitySubtype":
                    print("value: {}".format(data.value))

    # [END analyze_conversation_app]


if __name__ == '__main__':
    sample_analyze_conversation_app()
