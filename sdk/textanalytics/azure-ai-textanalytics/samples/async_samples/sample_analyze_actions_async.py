# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_actions_async.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which consists of a variety
    of text analysis actions, such as Entity Recognition, PII Entity Recognition, Linked Entity Recognition,
    Sentiment Analysis, Key Phrase Extraction and more.
    The response will contain results from each of the individual actions specified in the request.

USAGE:
    python sample_analyze_actions_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""


import os
import asyncio


async def sample_analyze_async() -> None:
    # [START analyze_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient
    from azure.ai.textanalytics import (
        RecognizeEntitiesAction,
        RecognizeLinkedEntitiesAction,
        RecognizePiiEntitiesAction,
        ExtractKeyPhrasesAction,
        AnalyzeSentimentAction,
    )

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    documents = [
        'We went to Contoso Steakhouse located at midtown NYC last week for a dinner party, and we adore the spot! '
        'They provide marvelous food and they have a great menu. The chief cook happens to be the owner (I think his name is John Doe) '
        'and he is super nice, coming out of the kitchen and greeted us all.'
        ,

        'We enjoyed very much dining in the place! '
        'The Sirloin steak I ordered was tender and juicy, and the place was impeccably clean. You can even pre-order from their '
        'online menu at www.contososteakhouse.com, call 312-555-0176 or send email to order@contososteakhouse.com! '
        'The only complaint I have is the food didn\'t come fast enough. Overall I highly recommend it!'
    ]

    async with text_analytics_client:
        poller = await text_analytics_client.begin_analyze_actions(
            documents,
            display_name="Sample Text Analysis",
            actions=[
                RecognizeEntitiesAction(),
                RecognizePiiEntitiesAction(),
                ExtractKeyPhrasesAction(),
                RecognizeLinkedEntitiesAction(),
                AnalyzeSentimentAction(),
            ]
        )

        pages = await poller.result()

        # To enumerate / zip for async, unless you install a third party library,
        # you have to read in all of the elements into memory first.
        # If you're not looking to enumerate / zip, we recommend you just asynchronously
        # loop over it immediately, without going through this step of reading them into memory
        document_results = []
        async for page in pages:
            document_results.append(page)

    for doc, action_results in zip(documents, document_results):
        print(f"\nDocument text: {doc}")
        for result in action_results:
            if result.kind == "EntityRecognition":
                print("...Results of Recognize Entities Action:")
                for entity in result.entities:
                    print(f"......Entity: {entity.text}")
                    print(f".........Category: {entity.category}")
                    print(f".........Confidence Score: {entity.confidence_score}")
                    print(f".........Offset: {entity.offset}")

            elif result.kind == "PiiEntityRecognition":
                print("...Results of Recognize PII Entities action:")
                for entity in result.entities:
                    print(f"......Entity: {entity.text}")
                    print(f".........Category: {entity.category}")
                    print(f".........Confidence Score: {entity.confidence_score}")

            elif result.kind == "KeyPhraseExtraction":
                print("...Results of Extract Key Phrases action:")
                print(f"......Key Phrases: {result.key_phrases}")

            elif result.kind == "EntityLinking":
                print("...Results of Recognize Linked Entities action:")
                for linked_entity in result.entities:
                    print(f"......Entity name: {linked_entity.name}")
                    print(f".........Data source: {linked_entity.data_source}")
                    print(f".........Data source language: {linked_entity.language}")
                    print(
                        f".........Data source entity ID: {linked_entity.data_source_entity_id}"
                    )
                    print(f".........Data source URL: {linked_entity.url}")
                    print(".........Document matches:")
                    for match in linked_entity.matches:
                        print(f"............Match text: {match.text}")
                        print(f"............Confidence Score: {match.confidence_score}")
                        print(f"............Offset: {match.offset}")
                        print(f"............Length: {match.length}")

            elif result.kind == "SentimentAnalysis":
                print("...Results of Analyze Sentiment action:")
                print(f"......Overall sentiment: {result.sentiment}")
                print(
                    f"......Scores: positive={result.confidence_scores.positive}; \
                    neutral={result.confidence_scores.neutral}; \
                    negative={result.confidence_scores.negative} \n"
                )

            elif result.kind == "DocumentError":
                print(
                    f"...Is an error with code '{result.code}' and message '{result.message}'"
                )

        print("------------------------------------------")

    # [END analyze_async]


async def main():
    await sample_analyze_async()


if __name__ == '__main__':
    asyncio.run(main())
