# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare.py

DESCRIPTION:
    This sample demonstrates how to detect healthcare entities in a batch of documents.
    Each entity found in the document will have a link associated with it from a
    data source.  Relations between entities will also be included in the response.

USAGE:
    python sample_analyze_healthcare.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


class AnalyzeHealthcareSample(object):

    def analyze_healthcare(self):
        # [START analyze_healthcare]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key),
            api_version="v3.1-preview.3")

        documents = [
            "Subject is taking 100mg of ibuprofen twice daily"
        ]

        poller = text_analytics_client.begin_analyze_healthcare(documents, show_stats=True)
        result = poller.result()
        
        docs = [doc for doc in result if not doc.is_error]

        print("Results of Healthcare Analysis:")
        for idx, doc in enumerate(docs):
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

        # [END analyze_health]

if __name__ == "__main__":
    sample = AnalyzeHealthcareSample()
    sample.analyze_healthcare()
