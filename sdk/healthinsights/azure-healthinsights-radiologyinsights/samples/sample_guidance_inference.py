# pylint: disable=line-too-long,useless-suppression
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_guidance_inference.py

DESCRIPTION:
The sample_guidance_inference.py module processes a sample radiology document with the Radiology Insights service.
It will initialize a RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display 
- the Guidance Identifier
- the Guidance Missing Information
- the Guidance Present Information
- the Guidance Ranking  


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_guidance_inference.py
   
"""

import datetime
import os
import uuid


from azure.identity import DefaultAzureCredential
from azure.healthinsights.radiologyinsights import RadiologyInsightsClient
from azure.healthinsights.radiologyinsights import models


def radiology_insights_sync() -> None:

    # [START create_radiology_insights_client]
    credential = DefaultAzureCredential()
    ENDPOINT = os.environ["AZURE_HEALTH_INSIGHTS_ENDPOINT"]

    job_id = str(uuid.uuid4())

    radiology_insights_client = RadiologyInsightsClient(endpoint=ENDPOINT, credential=credential)
    # [END create_radiology_insights_client]

    # [START create_radiology_insights_request]
    doc_content1 = "History: Left renal tumor with thin septations.\n\nFindings:\nThere is a right kidney tumor with nodular calcification."

    # Create ordered procedure
    procedure_coding = models.Coding(
        system="Https://loinc.org",
        code="24627-2",
        display="CT CHEST",
    )
    procedure_code = models.CodeableConcept(coding=[procedure_coding])
    ordered_procedure = models.OrderedProcedure(description="CT CHEST", code=procedure_code)
    # Create encounter
    start = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
    end = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
    encounter = models.PatientEncounter(
        id="encounter2",
        class_property=models.EncounterClass.IN_PATIENT,
        period=models.TimePeriod(start=start, end=end),
    )
    # Create patient info
    birth_date = datetime.date(1959, 11, 11)
    patient_info = models.PatientDetails(sex=models.PatientSex.FEMALE, birth_date=birth_date)
    # Create author
    author = models.DocumentAuthor(id="author2", full_name="authorName2")

    create_date_time = datetime.datetime(2024, 2, 19, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
    patient_document1 = models.PatientDocument(
        type=models.DocumentType.NOTE,
        clinical_type=models.ClinicalDocumentType.RADIOLOGY_REPORT,
        id="doc2",
        content=models.DocumentContent(source_type=models.DocumentContentSourceType.INLINE, value=doc_content1),
        created_at=create_date_time,
        specialty_type=models.SpecialtyType.RADIOLOGY,
        administrative_metadata=models.DocumentAdministrativeMetadata(
            ordered_procedures=[ordered_procedure], encounter_id="encounter2"
        ),
        authors=[author],
        language="en",
    )

    # Construct patient
    patient1 = models.PatientRecord(
        id="patient_id2",
        details=patient_info,
        encounters=[encounter],
        patient_documents=[patient_document1],
    )

    # Create a configuration
    configuration = models.RadiologyInsightsModelConfiguration(verbose=False, include_evidence=True, locale="en-US")

    # Construct the request with the patient and configuration
    patient_data = models.RadiologyInsightsJob(
        job_data=models.RadiologyInsightsData(patients=[patient1], configuration=configuration)
    )
    # [END create_radiology_insights_request]

    # Health Insights Radiology Insights
    try:
        poller = radiology_insights_client.begin_infer_radiology_insights(
            id=job_id,
            resource=patient_data,
        )
        radiology_insights_result = poller.result()
        display_guidance(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_guidance(radiology_insights_result):
    # [START display_guidance]
    for patient_result in radiology_insights_result.patient_results:
        counter = 0
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.GUIDANCE:
                counter += 1
                print(f"Guidance {counter} Inference found")
                identifier = ri_inference.identifier
                if identifier.coding is not None:
                    for code in identifier.coding:
                        if code.code is not None and code.display is not None:
                            print(f"Identifier: {code.display}")
                missing_infos = ri_inference.missing_guidance_information
                for info in missing_infos:
                    print(f"Missing Guidance Information: {info}")
                present_infos = ri_inference.present_guidance_information
                for info in present_infos:
                    item = info.present_guidance_item
                    print(f"Present Guidance Information: {item}")
                    values = info.present_guidance_values
                    for value in values:
                        print(f"Present Guidance Value: {value}")
                ranking = ri_inference.ranking
                print(f"Ranking: {ranking.value}")
    # [END display_guidance]


if __name__ == "__main__":
    radiology_insights_sync()
