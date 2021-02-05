# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_entities_async.py

DESCRIPTION:
    This sample demonstrates how to detect healthcare entities in a batch of documents.
    Each entity found in the document will have a link associated with it from a
    data source.  Relations between entities will also be included in the response.

USAGE:
    python sample_analyze_healthcare_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os
import asyncio


class AnalyzeHealthcareEntitiesSampleAsync(object):

    async def analyze_healthcare_entities_async(self):
        # [START analyze_healthcare_entities_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

        documents = [
            "Subject is taking 100mg of ibuprofen twice daily"
        ]

        async with text_analytics_client:
            poller = await text_analytics_client.begin_analyze_healthcare_entities(documents)
            result = await poller.result()
            docs = [doc async for doc in result if not doc.is_error]

        print("Results of Healthcare Entities Analysis:")
        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("...Category: {}".format(entity.category))
                print("...Subcategory: {}".format(entity.subcategory))
                print("...Offset: {}".format(entity.offset))
                print("...Confidence score: {}".format(entity.confidence_score))
                if entity.data_sources is not None:
                    print("...Data Sources:")
                    for data_source in entity.data_sources:
                        print("......Entity ID: {}".format(data_source.entity_id))
                        print("......Name: {}".format(data_source.name))
                if len(entity.related_entities) > 0:
                    print("...Related Entities:")
                    for related_entity, relation_type in entity.related_entities.items():
                        print("......Entity Text: {}".format(related_entity.text))
                        print("......Relation Type: {}".format(relation_type))
            print("------------------------------------------")

        # [END analyze_healthcare_entities_async]


async def main():
    sample = AnalyzeHealthcareEntitiesSampleAsync()
    await sample.analyze_healthcare_entities_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


