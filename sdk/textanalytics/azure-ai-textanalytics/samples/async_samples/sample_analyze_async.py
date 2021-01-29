# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_asynct.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis, which consists of a variety
    of text analysis actions, such as Entity Recognition, PII Entity Recognition, Entity Linking, Sentiment Analysis,
    or Key Phrase Extraction.  The response will contain results from each of the individual actions specified in the request.

USAGE:
    python sample_analyze_async.py

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
        from azure.ai.textanalytics import RecognizeEntitiesAction, \
            RecognizePiiEntitiesAction, \
            ExtractKeyPhrasesAction

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
                recognize_entities_actions=[RecognizeEntitiesAction()],
                recognize_pii_entities_actions=[RecognizePiiEntitiesAction()],
                extract_key_phrases_actions=[ExtractKeyPhrasesAction()]
            )

            result = await poller.result()

            async for page in result:
                for results in page.recognize_entities_results:
                    print("Results of Entities Recognition action:")

                    docs = [doc for doc in results if not doc.is_error]
                    for idx, doc in enumerate(docs):
                        print("\nDocument text: {}".format(documents[idx]))
                        for entity in doc.entities:
                            print("Entity: {}".format(entity.text))
                            print("...Category: {}".format(entity.category))
                            print("...Confidence Score: {}".format(entity.confidence_score))
                            print("...Offset: {}".format(entity.offset))
                        print("------------------------------------------")

                for results in page.recognize_pii_entities_results:
                    print("Results of PII Entities Recognition action:")

                    docs = [doc for doc in results if not doc.is_error]
                    for idx, doc in enumerate(docs):
                        print("Document text: {}".format(documents[idx]))
                        for entity in doc.entities:
                            print("Entity: {}".format(entity.text))
                            print("Category: {}".format(entity.category))
                            print("Confidence Score: {}\n".format(entity.confidence_score))
                        print("------------------------------------------")

                for results in page.extract_key_phrases_results:
                    print("Results of Key Phrase Extraction action:")

                    docs = [doc for doc in results if not doc.is_error]
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