# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_critical_result_inference.py

DESCRIPTION:
The sample_critical_result_inference.py module processes a sample radiology document with the Radiology Insights service.
It will initialize a RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display the Critical Results description.     


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_critical_result_inference.py
   
"""
import datetime
import os
import uuid


from azure.identity import DefaultAzureCredential
from azure.healthinsights.radiologyinsights import RadiologyInsightsClient
from azure.healthinsights.radiologyinsights import models


def radiology_insights_sync() -> None:
    credential = DefaultAzureCredential()
    ENDPOINT = os.environ["AZURE_HEALTH_INSIGHTS_ENDPOINT"]

    job_id = str(uuid.uuid4())

    radiology_insights_client = RadiologyInsightsClient(endpoint=ENDPOINT, credential=credential)

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

    # Health Insights Radiology Insights
    try:
        poller = radiology_insights_client.begin_infer_radiology_insights(
            id=job_id,
            resource=patient_data,
        )
        radiology_insights_result = poller.result()
        display_critical_results(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_critical_results(radiology_insights_result):
    for patient_result in radiology_insights_result.patient_results:
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.CRITICAL_RESULT:
                critical_result = ri_inference.result
                print(f"Critical Result Inference found: {critical_result.description}")


if __name__ == "__main__":
    radiology_insights_sync()
