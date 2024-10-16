# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_radiology_procedure_inference_async.py

DESCRIPTION:
The sample_radiology_procedure_inference_async.py module processes a sample radiology document with the Radiology Insights service.
It will initialize an asynchronous RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display
- the Procedure code, 
- the Imaging Procedure anatomy and modality, 
- Ordered Procedure code and description  


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_radiology_procedure_inference_async.py
   
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
    doc_content1 = """
    Exam:  Head CT with Contrast
    History:  Headaches for 2 months
    Technique: Axial, sagittal, and coronal images were reconstructed from helical CT through the head without IV contrast.
    IV contrast:  100 mL IV Omnipaque 300.
    Findings: There is no mass effect. There is no abnormal enhancement of the brain or within injuries with IV contrast.\
    However, there is no evidence of enhancing lesion in either internal auditory canal.
    Impression: Negative CT of the brain without IV contrast.
    I recommend a new brain CT within nine months."""

    # Create ordered procedure
    procedure_coding = models.Coding(
        system="Https://loinc.org",
        code="24727-0",
        display="CT HEAD W CONTRAST IV",
    )
    procedure_code = models.CodeableConcept(coding=[procedure_coding])
    ordered_procedure = models.OrderedProcedure(description="CT HEAD W CONTRAST IV", code=procedure_code)
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

    try:
        async with radiology_insights_client:
            poller = await radiology_insights_client.begin_infer_radiology_insights(
                id=job_id,
                resource=patient_data,
            )
            radiology_insights_result = await poller.result()

            display_radiology_procedure(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_radiology_procedure(radiology_insights_result):
    # [START display_radiology_procedure]
    for patient_result in radiology_insights_result.patient_results:
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.RADIOLOGY_PROCEDURE:
                print(f"Radiology Procedure Inference found")
                for proccod in ri_inference.procedure_codes:
                    print(f"\nRadiology Procedure: PROCEDURE CODES:")
                    for coding in proccod.coding:
                        print(
                            f"Radiology Procedure: PROCEDURE CODES: Code: {coding.system} {coding.code} {coding.display}"
                        )
                for improc in ri_inference.imaging_procedures:
                    print(f"\nRadiology Procedure: IMAGING PROCEDURE:")
                    for attribute in improc:
                        if (
                            hasattr(improc, attribute)
                            and not attribute.startswith("_")
                            and not callable(getattr(improc, attribute))
                        ):
                            if attribute == "anatomy":
                                if improc.anatomy is not None:
                                    for coding in improc.anatomy.coding:
                                        print(
                                            f"Radiology Procedure: IMAGING PROCEDURE: Anatomy Code: {coding.system} {coding.code} {coding.display}"
                                        )
                                else:
                                    print(f"Radiology Procedure: IMAGING PROCEDURE: Anatomy: none")
                            elif attribute == "modality":
                                if improc.modality is not None:
                                    for coding in improc.modality.coding:
                                        print(
                                            f"Radiology Procedure: IMAGING PROCEDURE: Modality Code: {coding.system} {coding.code} {coding.display}"
                                        )
                                else:
                                    print(f"Radiology Procedure: IMAGING PROCEDURE: Modality: none")
                ordered_procedure = ri_inference.ordered_procedure
                print(f"\nRadiology Procedure: ORDERED PROCEDURE:")
                if ordered_procedure.description is not None:
                    print(f"Radiology Procedure: ORDERED PROCEDURE: Description: {ordered_procedure.description}")
                if ordered_procedure.code is not None:
                    for coding in ordered_procedure.code.coding:
                        print(
                            f"Radiology Procedure: ORDERED PROCEDURE: Code: {coding.system} {coding.code} {coding.display}"
                        )


# [END display_radiology_procedure]

if __name__ == "__main__":
    try:
        asyncio.run(radiology_insights_async())
    except Exception as ex:
        raise ex
