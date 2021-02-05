# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_entities.py

DESCRIPTION:
    This sample demonstrates how to detect healthcare entities in a batch of documents.
    Each entity found in the document will have a link associated with it from a
    data source.  Relations between entities will also be included in the response.

USAGE:
    python sample_analyze_healthcare_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


class AnalyzeHealthcareEntitiesSample(object):

    def analyze_healthcare_entities(self):
        # [START analyze_healthcare_entities]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

        documents = [
            "Subject is taking 100mg of ibuprofen twice daily"
        ]

        poller = text_analytics_client.begin_analyze_healthcare_entities(documents, show_stats=True)
        result = poller.result()

        docs = [doc for doc in result if not doc.is_error]

        print("Results of Healthcare Entities Analysis:")
        for idx, doc in enumerate(docs):
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

        # [END analyze_healthcare_entities]

if __name__ == "__main__":
    sample = AnalyzeHealthcareEntitiesSample()
    sample.analyze_healthcare_entities()
