# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_actions.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which consists of a variety
    of text analysis actions, such as Entity Recognition, PII Entity Recognition, Linked Entity Recognition,
    Sentiment Analysis, or Key Phrase Extraction.  The response will contain results from each of the individual
    actions specified in the request.

USAGE:
    python sample_analyze_actions.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


def sample_analyze_actions():
    # [START analyze]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import (
        TextAnalyticsClient,
        RecognizeEntitiesAction,
        RecognizeLinkedEntitiesAction,
        RecognizePiiEntitiesAction,
        ExtractKeyPhrasesAction,
        AnalyzeSentimentAction,
    )

    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    documents = [
        'We went to Contoso Steakhouse located at midtown NYC last week for a dinner party, and we adore the spot!'\
        'They provide marvelous food and they have a great menu. The chief cook happens to be the owner (I think his name is John Doe)'\
        'and he is super nice, coming out of the kitchen and greeted us all.'\
        ,

        'We enjoyed very much dining in the place!'\
        'The Sirloin steak I ordered was tender and juicy, and the place was impeccably clean. You can even pre-order from their'\
        'online menu at www.contososteakhouse.com, call 312-555-0176 or send email to order@contososteakhouse.com!'\
        'The only complaint I have is the food didn\'t come fast enough. Overall I highly recommend it!'\
    ]

    poller = text_analytics_client.begin_analyze_actions(
        documents,
        display_name="Sample Text Analysis",
        actions=[
            RecognizeEntitiesAction(),
            RecognizePiiEntitiesAction(),
            ExtractKeyPhrasesAction(),
            RecognizeLinkedEntitiesAction(),
            AnalyzeSentimentAction()
        ],
    )

    document_results = poller.result()
    for doc, action_results in zip(documents, document_results):
        print("\nDocument text: {}".format(doc))
        recognize_entities_result = action_results[0]
        print("...Results of Recognize Entities Action:")
        if recognize_entities_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                recognize_entities_result.code, recognize_entities_result.message
            ))
        else:
            for entity in recognize_entities_result.entities:
                print("......Entity: {}".format(entity.text))
                print(".........Category: {}".format(entity.category))
                print(".........Confidence Score: {}".format(entity.confidence_score))
                print(".........Offset: {}".format(entity.offset))

        recognize_pii_entities_result = action_results[1]
        print("...Results of Recognize PII Entities action:")
        if recognize_pii_entities_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                recognize_pii_entities_result.code, recognize_pii_entities_result.message
            ))
        else:
            for entity in recognize_pii_entities_result.entities:
                print("......Entity: {}".format(entity.text))
                print(".........Category: {}".format(entity.category))
                print(".........Confidence Score: {}".format(entity.confidence_score))

        extract_key_phrases_result = action_results[2]
        print("...Results of Extract Key Phrases action:")
        if extract_key_phrases_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                extract_key_phrases_result.code, extract_key_phrases_result.message
            ))
        else:
            print("......Key Phrases: {}".format(extract_key_phrases_result.key_phrases))

        recognize_linked_entities_result = action_results[3]
        print("...Results of Recognize Linked Entities action:")
        if recognize_linked_entities_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                recognize_linked_entities_result.code, recognize_linked_entities_result.message
            ))
        else:
            for linked_entity in recognize_linked_entities_result.entities:
                print("......Entity name: {}".format(linked_entity.name))
                print(".........Data source: {}".format(linked_entity.data_source))
                print(".........Data source language: {}".format(linked_entity.language))
                print(".........Data source entity ID: {}".format(linked_entity.data_source_entity_id))
                print(".........Data source URL: {}".format(linked_entity.url))
                print(".........Document matches:")
                for match in linked_entity.matches:
                    print("............Match text: {}".format(match.text))
                    print("............Confidence Score: {}".format(match.confidence_score))
                    print("............Offset: {}".format(match.offset))
                    print("............Length: {}".format(match.length))

        analyze_sentiment_result = action_results[4]
        print("...Results of Analyze Sentiment action:")
        if analyze_sentiment_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                analyze_sentiment_result.code, analyze_sentiment_result.message
            ))
        else:
            print("......Overall sentiment: {}".format(analyze_sentiment_result.sentiment))
            print("......Scores: positive={}; neutral={}; negative={} \n".format(
                analyze_sentiment_result.confidence_scores.positive,
                analyze_sentiment_result.confidence_scores.neutral,
                analyze_sentiment_result.confidence_scores.negative,
            ))
        print("------------------------------------------")

    # [END analyze]


if __name__ == "__main__":
    sample_analyze_actions()
