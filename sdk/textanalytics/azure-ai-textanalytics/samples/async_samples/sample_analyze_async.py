# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_text.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which consists of a variety
    of text analysis tasks, such as Entity Recognition, PII Entity Recognition, Entity Linking, Sentiment Analysis,
    or Key Phrase Extraction.  The response will contain results from each of the individual tasks specified in the request.

USAGE:
    python sample_analyze_text.py

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
        from azure.ai.textanalytics import EntitiesRecognitionTask, \
            PiiEntitiesRecognitionTask, \
            KeyPhraseExtractionTask

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key),
            api_version="v3.1-preview.3"
        )

        documents = [
            "I had a wonderful trip to Seattle last week.",
            "I'm flying to NYC tomorrow. See you there."
        ]

        async with text_analytics_client:
            poller = await text_analytics_client.begin_analyze(
                documents,
                display_name="Sample Text Analysis",
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()]
            )

            result = await poller.result()

            async for page in result:
                for task in page.entities_recognition_results:
                    print("Results of task '{}':".format(task.name))
                    
                    docs = [doc for doc in task.results if not doc.is_error]
                    for idx, doc in enumerate(docs):
                        print("\nDocument text: {}".format(documents[idx]))
                        for entity in doc.entities:
                            print("Entity: {}".format(entity.text))
                            print("...Category: {}".format(entity.category))
                            print("...Confidence Score: {}".format(entity.confidence_score))
                            print("...Offset: {}".format(entity.offset))
                        print("------------------------------------------")

                for task in page.pii_entities_recognition_results:
                    print("Results of task '{}':".format(task.name))

                    docs = [doc for doc in task.results if not doc.is_error]
                    for idx, doc in enumerate(docs):
                        print("Document text: {}".format(documents[idx]))
                        for entity in doc.entities:
                            print("Entity: {}".format(entity.text))
                            print("Category: {}".format(entity.category))
                            print("Confidence Score: {}\n".format(entity.confidence_score))
                        print("------------------------------------------")

                for task in page.key_phrase_extraction_results:
                    print("Results of task '{}':".format(task.name))

                    docs = [doc for doc in task.results if not doc.is_error]
                    for idx, doc in enumerate(docs):
                        print("Document text: {}\n".format(documents[idx]))
                        print("Key Phrases: {}\n".format(doc.key_phrases))
                        print("------------------------------------------")

        # [END analyze_async]


async def main():
    sample = AnalyzeSampleAsync()
    await sample.analyze_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())