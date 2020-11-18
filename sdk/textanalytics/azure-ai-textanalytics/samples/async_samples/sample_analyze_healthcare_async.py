# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_async.py

DESCRIPTION:
    This sample demonstrates how to detect healthcare entities in a batch of documents.
    Each entity found in the document will have a link associated with it from a
    data source.  Relations between entities will also be included in the response.

USAGE:
    python sample_analyze_healthcare_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os
import asyncio


class AnalyzeHealthcareSampleAsync(object):

    async def analyze_healthcare_async(self):
        # [START analyze_healthcare_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key),
            api_version="v3.1-preview.3")

        documents = [
            "Subject is taking 100mg of ibuprofen twice daily"
        ]

        async with text_analytics_client:
            poller = await text_analytics_client.begin_analyze_healthcare(documents)
            result = await poller.result()
            docs = [doc async for doc in result if not doc.is_error]

        print("Results of Healthcare Analysis:")
        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("...Category: {}".format(entity.category))
                print("...Subcategory: {}".format(entity.subcategory))
                print("...Offset: {}".format(entity.offset))
                print("...Confidence score: {}".format(entity.confidence_score))
                if entity.links is not None:
                    print("...Links:")
                    for link in entity.links:
                        print("......ID: {}".format(link.id))
                        print("......Data source: {}".format(link.data_source))
            for relation in doc.relations:
                print("Relation:")
                print("...Source: {}".format(relation.source.text))
                print("...Target: {}".format(relation.target.text))
                print("...Type: {}".format(relation.relation_type))
                print("...Bidirectional: {}".format(relation.is_bidirectional))
            print("------------------------------------------")

        # [END analyze_healthcare_async]


async def main():
    sample = AnalyzeHealthcareSampleAsync()
    await sample.analyze_healthcare_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


