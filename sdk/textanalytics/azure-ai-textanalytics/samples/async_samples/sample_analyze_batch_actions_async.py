# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_batch_actions_async.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which consists of a variety
    of text analysis actions, such as Entity Recognition, PII Entity Recognition,
    or Key Phrase Extraction.  The response will contain results from each of the individual actions specified in the request.

USAGE:
    python sample_analyze_batch_actions_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os
import asyncio

class AnalyzeSampleAsync(object):

    async def analyze_async(self):
        # [START analyze_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import (
            RecognizeEntitiesAction,
            RecognizeLinkedEntitiesAction,
            RecognizePiiEntitiesAction,
            ExtractKeyPhrasesAction,
            AnalyzeBatchActionsType
        )

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

        documents = [
            "We went to Contoso Steakhouse located at midtown NYC last week for a dinner party, and we adore the spot! \
            They provide marvelous food and they have a great menu. The chief cook happens to be the owner (I think his name is John Doe) \
            and he is super nice, coming out of the kitchen and greeted us all. We enjoyed very much dining in the place! \
            The Sirloin steak I ordered was tender and juicy, and the place was impeccably clean. You can even pre-order from their \
            online menu at www.contososteakhouse.com, call 312-555-0176 or send email to order@contososteakhouse.com! \
            The only complaint I have is the food didn't come fast enough. Overall I highly recommend it!"
        ]

        async with text_analytics_client:
            poller = await text_analytics_client.begin_analyze_batch_actions(
                documents,
                display_name="Sample Text Analysis",
                actions=[
                    RecognizeEntitiesAction(),
                    RecognizePiiEntitiesAction(),
                    ExtractKeyPhrasesAction(),
                    RecognizeLinkedEntitiesAction()
                ]
            )

            result = await poller.result()

            async for action_result in result:
                if action_result.is_error:
                    raise ValueError(
                        "Action has failed with message: {}".format(
                            action_result.error.message
                        )
                    )
                if action_result.action_type == AnalyzeBatchActionsType.RECOGNIZE_ENTITIES:
                    print("Results of Entities Recognition action:")
                    for idx, doc in enumerate(action_result.document_results):
                        print("\nDocument text: {}".format(documents[idx]))
                        for entity in doc.entities:
                            print("Entity: {}".format(entity.text))
                            print("...Category: {}".format(entity.category))
                            print("...Confidence Score: {}".format(entity.confidence_score))
                            print("...Offset: {}".format(entity.offset))
                        print("------------------------------------------")

                if action_result.action_type == AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES:
                    print("Results of PII Entities Recognition action:")
                    for idx, doc in enumerate(action_result.document_results):
                        print("Document text: {}".format(documents[idx]))
                        for entity in doc.entities:
                            print("Entity: {}".format(entity.text))
                            print("Category: {}".format(entity.category))
                            print("Confidence Score: {}\n".format(entity.confidence_score))
                        print("------------------------------------------")

                if action_result.action_type == AnalyzeBatchActionsType.EXTRACT_KEY_PHRASES:
                    print("Results of Key Phrase Extraction action:")
                    for idx, doc in enumerate(action_result.document_results):
                        print("Document text: {}\n".format(documents[idx]))
                        print("Key Phrases: {}\n".format(doc.key_phrases))
                        print("------------------------------------------")

                if action_result.action_type == AnalyzeBatchActionsType.RECOGNIZE_LINKED_ENTITIES:
                    print("Results of Linked Entities Recognition action:")
                    for idx, doc in enumerate(action_result.document_results):
                        print("Document text: {}\n".format(documents[idx]))
                        for linked_entity in doc.entities:
                            print("Entity name: {}".format(linked_entity.name))
                            print("...Data source: {}".format(linked_entity.data_source))
                            print("...Data source language: {}".format(linked_entity.language))
                            print("...Data source entity ID: {}".format(linked_entity.data_source_entity_id))
                            print("...Data source URL: {}".format(linked_entity.url))
                            print("...Document matches:")
                            for match in linked_entity.matches:
                                print("......Match text: {}".format(match.text))
                                print(".........Confidence Score: {}".format(match.confidence_score))
                                print(".........Offset: {}".format(match.offset))
                                print(".........Length: {}".format(match.length))
                        print("------------------------------------------")

        # [END analyze_async]


async def main():
    sample = AnalyzeSampleAsync()
    await sample.analyze_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())