# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_age_mismatch_inference_async.py

DESCRIPTION:
The sample_age_mismatch_inference_async.py module processes a sample radiology document with the Radiology Insights service.
It will initialize an asynchronous RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display 
-the Age Mismatch patient ID,
-the Age Mismatch url extension,
-the Age Mismatch offset extension,
-the Age Mismatch length extension, and
-the Age Mismatch evidence


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_age_mismatch_inference_async.py
"""

import asyncio
import datetime
import os
import uuid
from azure.healthinsights.radiologyinsights import models


async def radiology_insights_async() -> None:

    from azure.identity.aio import DefaultAzureCredential
    from azure.healthinsights.radiologyinsights.aio import RadiologyInsightsClient

    # [START create_radiology_insights_client]
    credential = DefaultAzureCredential()
    ENDPOINT = os.environ["AZURE_HEALTH_INSIGHTS_ENDPOINT"]

    job_id = str(uuid.uuid4())

    radiology_insights_client = RadiologyInsightsClient(endpoint=ENDPOINT, credential=credential)
    # [END create_radiology_insights_client]

    # [START create_radiology_insights_request]
    doc_content1 = """CLINICAL HISTORY:   
    20-year-old female presenting with abdominal pain. Surgical history significant for appendectomy.
    COMPARISON:   
    Right upper quadrant sonographic performed 1 day prior.
    TECHNIQUE:   
    Transabdominal grayscale pelvic sonography with duplex color Doppler and spectral waveform analysis of the ovaries.
    FINDINGS:   
    The uterus is unremarkable given the transabdominal technique with endometrial echo complex within physiologic normal limits. The ovaries are symmetric in size, measuring 2.5 x 1.2 x 3.0 cm and the left measuring 2.8 x 1.5 x 1.9 cm.\n On duplex imaging, Doppler signal is symmetric.
    IMPRESSION:   
    1. Normal pelvic sonography. Findings of testicular torsion.
    A new US pelvis within the next 6 months is recommended.
    These results have been discussed with Dr. Jones at 3 PM on November 5 2020."""

    # Create ordered procedure
    procedure_coding = models.Coding(
        system="Http://hl7.org/fhir/ValueSet/cpt-all",
        code="USPELVIS",
        display="US PELVIS COMPLETE",
    )
    procedure_code = models.CodeableConcept(coding=[procedure_coding])
    ordered_procedure = models.OrderedProcedure(description="US PELVIS COMPLETE", code=procedure_code)
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

    try:
        async with radiology_insights_client:
            poller = await radiology_insights_client.begin_infer_radiology_insights(
                id=job_id,
                resource=patient_data,
            )
            radiology_insights_result = await poller.result()
            display_age_mismatch(radiology_insights_result, doc_content1)
    except Exception as ex:
        raise ex


def display_age_mismatch(radiology_insights_result, doc_content1):
    # [START display_age_mismatch]
    for patient_result in radiology_insights_result.patient_results:
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.AGE_MISMATCH:
                print(f"Age Mismatch Inference found")
                print(f"Age Mismatch: Patient ID: {patient_result.patient_id}")
                Tokens = ""
                for extension in ri_inference.extension:
                    for attribute in dir(extension):
                        if attribute == "extension":
                            offset = -1
                            length = -1
                            for sub_extension in extension.extension:
                                for sub_attribute in dir(sub_extension):
                                    if sub_attribute == "url":
                                        if sub_extension.url.startswith("http"):
                                            continue
                                        elif sub_extension.url == "offset":
                                            offset = sub_extension.value_integer
                                        elif sub_extension.url == "length":
                                            length = sub_extension.value_integer
                                    if offset > 0 and length > 0:
                                        evidence = doc_content1[offset : offset + length]
                                        if not evidence in Tokens:
                                            Tokens = Tokens + " " + evidence
                print(f"Age Mismatch: Evidence: {Tokens}")


# [END display_age_mismatch]

if __name__ == "__main__":
    try:
        asyncio.run(radiology_insights_async())
    except Exception as ex:
        raise ex
