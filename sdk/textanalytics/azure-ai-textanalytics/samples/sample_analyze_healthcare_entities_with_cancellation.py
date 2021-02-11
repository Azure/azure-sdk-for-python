# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_entities_with_cancellation.py

DESCRIPTION:
    This sample demonstrates how to cancel a Healthcare Entities Analysis job after it's been started.
    Since the Health API is currently only available in a gated preview, you need
    to have your subscription on the service's allow list. More information
    here: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-for-health?tabs=ner#request-access-to-the-public-preview.

USAGE:
    python sample_analyze_healthcare_entities_with_cancellation.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os
from azure.core.exceptions import HttpResponseError


class AnalyzeHealthcareEntitiesWithCancellationSample(object):

    def analyze_healthcare_entities_with_cancellation(self):
        # [START analyze_healthcare_entities_with_cancellation]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

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

        poller = text_analytics_client.begin_analyze_healthcare_entities(documents)
        
        try:
            cancellation_poller = poller.cancel()
            cancellation_poller.wait()
        
        except HttpResponseError as e:
            # If the operation has already reached a terminal state it cannot be cancelled.
            print(e)

        else:
            print("Healthcare entities analysis was successfully cancelled.")

        # [END analyze_healthcare_entities_with_cancellation]


if __name__ == "__main__":
    sample = AnalyzeHealthcareEntitiesWithCancellationSample()
    sample.analyze_healthcare_entities_with_cancellation()


