# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_healthcare_with_fhir.py

DESCRIPTION:
    This sample demonstrates how to analyze a text document and generate the FHIR bundle for it.
    It requires the fhirclient library: pip install fhirclient

USAGE:
    python sample_analyze_healthcare_with_fhir.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""


import os


def sample_analyze_healthcare_with_fhir() -> None:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient, HealthcareDocumentType
    import fhirclient.models.bundle as b

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    documents = [
        "RECORD #333582770390100 | MH | 85986313 | | 054351 | 2/14/2001 12:00:00 AM | \
        CORONARY ARTERY DISEASE | Signed | DIS | \nAdmission Date: 5/22/2001 \
        Report Status: Signed Discharge Date: 4/24/2001 ADMISSION DIAGNOSIS: \
        CORONARY ARTERY DISEASE. \nHISTORY OF PRESENT ILLNESS: \
        The patient is a 54-year-old gentleman with a history of progressive angina over the past several months. \
        The patient had a cardiac catheterization in July of this year revealing total occlusion of the RCA and \
        50% left main disease, with a strong family history of coronary artery disease with a brother dying at \
        the age of 52 from a myocardial infarction and another brother who is status post coronary artery bypass grafting. \
        The patient had a stress echocardiogram done on July, 2001, which showed no wall motion abnormalities,\
        but this was a difficult study due to body habitus. The patient went for six minutes with minimal ST depressions \
        in the anterior lateral leads, thought due to fatigue and wrist pain, his anginal equivalent. Due to the patient's \
        increased symptoms and family history and history left main disease with total occasional of his RCA was referred \
        for revascularization with open heart surgery."
    ]

    poller = text_analytics_client.begin_analyze_healthcare_entities(
        documents,
        fhir_version="4.0.1",
        document_type=HealthcareDocumentType.DISCHARGE_SUMMARY
    )

    healthcare_result = poller.result()

    for result in healthcare_result:
        bundle = b.Bundle(result.fhir_bundle)
        for entry in bundle.entry:
            resource = entry.resource
            if resource.resource_type == "Patient":
                print(f"Patient birth date: {resource.birthDate.date}")
                print(f"Patient gender: {resource.gender}")
            elif resource.resource_type == "Encounter":
                print(f"Encounter period: {resource.period.start.date} - {resource.period.end.date}")
                print(f"Encounter status: {resource.status}")
            elif resource.resource_type == "Condition":
                print(f"Code: {resource.code.text}")
                if resource.onsetString:
                    print(f"Onset: {resource.onsetString}")
            elif resource.resource_type == "Composition":
                print(f"Title: {resource.title}")
                print(f"Admission date: {resource.date.date}")
            elif resource.resource_type == "Observation":
                print(f"Procedure: {resource.code.text}")
            elif resource.resource_type == "FamilyMemberHistory":
                for cond in resource.condition:
                    print(f"Family member history: {cond.code.text}")
            elif resource.resource_type == "Procedure":
                print(f"Procedure: {resource.code.text}")


if __name__ == "__main__":
    sample_analyze_healthcare_with_fhir()
