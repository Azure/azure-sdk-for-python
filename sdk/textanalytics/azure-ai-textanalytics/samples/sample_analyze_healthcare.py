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
            api_version="v3.2-preview.1")

        documents = [
            "RECORD #333582770390100 | MH | 85986313 | | 054351 | 2/14/2001 12:00:00 AM | \
            CORONARY ARTERY DISEASE | Signed | DIS | Admission Date: 5/22/2001 \
            Report Status: Signed Discharge Date: 4/24/2001 ADMISSION DIAGNOSIS: \
            CORONARY ARTERY DISEASE. HISTORY OF PRESENT ILLNESS: \
            The patient is a 54-year-old gentleman with a history of progressive angina over the past several months. \
            The patient had a cardiac catheterization in July of this year revealing total occlusion of the RCA and \
            50% left main disease , with a strong family history of coronary artery disease with a brother dying at \
            the age of 52 from a myocardial infarction and another brother who is status post coronary artery bypass grafting. \
            The patient had a stress echocardiogram done on July , 2001 , which showed no wall motion abnormalities ,\
            but this was a difficult study due to body habitus. The patient went for six minutes with minimal ST depressions \
            in the anterior lateral leads , thought due to fatigue and wrist pain , his anginal equivalent. Due to the patient's \
            increased symptoms and family history and history left main disease with total occasional of his RCA was referred \
            for revascularization with open heart surgery."
        ]

        poller = text_analytics_client.begin_analyze_healthcare(documents, show_stats=True)
        result = poller.result()
        
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            print(doc.statistics)
            exit(0)
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
    sample.analyze_health()


