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

    In this sample we will be a newly-hired engineer working in a pharmacy. We are going to
    comb through all of the prescriptions our pharmacy has fulfilled so we can catalog how
    much inventory we have.

    As a usage note: healthcare is currently in gated preview. Your subscription needs to
    be allow-listed before you can use this endpoint. More information about that here:
    https://aka.ms/text-analytics-health-request-access

USAGE:
    python sample_analyze_healthcare_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""



class AnalyzeHealthcareEntitiesSample(object):

    def analyze_healthcare_entities(self):

        # [START analyze_healthcare_entities]
        import os
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

        documents = [
            """
            Patient needs to take 100 mg of ibuprofen, and 3 mg of potassium. Also needs to take
            10 mg of Zocor.
            """,
            """
            Patient needs to take 50 mg of ibuprofen, and 2 mg of Coumadin.
            """
        ]

        poller = text_analytics_client.begin_analyze_healthcare_entities(documents)
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
            for relation in doc.entity_relations:
                print("Relation of type: {} has the following roles".format(relation.relation_type))
                for role in relation.roles:
                    print("...Role '{}' with entity '{}'".format(role.name, role.entity.text))
            print("------------------------------------------")
        # [END analyze_healthcare_entities]

if __name__ == "__main__":
    sample = AnalyzeHealthcareEntitiesSample()
    sample.analyze_healthcare_entities()
