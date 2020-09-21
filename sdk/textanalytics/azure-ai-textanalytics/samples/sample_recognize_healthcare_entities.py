# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_healthcare_entities.py

DESCRIPTION:
    This sample demonstrates how to detect healthcare entities in a batch of documents.
    Each entity found in the document will have a link associated with it from a
    data source.  Relations between entities will also be included in the response.

USAGE:
    python sample_recognize_healthcare_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


class RecognizeHealthcareEntitiesSample(object):

    def recognize_healthcare_entities(self):
        # [START recognize_healthcare_entities]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        documents = [
            "Subject is taking 100mg of ibuprofen twice daily."
        ]

        poller = text_analytics_client.begin_health(documents)
        result = poller.result()

        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("...Category: {}".format(entity.category))
                print("...Subcategory: {}".format(entity.subcategory))
                print("...Offset: {}".format(entity.offset))
                print("...Length: {}".format(entity.length))
                print("...Confidence score: {}".format(entity.confidence_score))
                print("...Links:")
                for link in entity.links:
                    print("......ID: {}".format(link.id))
                    print("......Data source: {}".format(link.datasource))
            for relation in doc.relations:
                print("Relation:")
                print("...Source: {}".format(relation.source))
                print("...Target: {}".format(relation.target))
                print("...Type: {}".format(relation.type))
                print("...Bidirectional: {}".format(relation.bidirectional))
            print("------------------------------------------")


if __name__ == "__main__":
    sample = RecognizeHealthcareEntitiesSample()
    sample.recognize_healthcare_entities()


