# pylint: disable=line-too-long,useless-suppression
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_scoring_and_assessment_inference_async.py

DESCRIPTION:
The sample_scoring_and_assessment_inference_async.py module processes a sample radiology document with the Radiology Insights service.
It will initialize an asynchronous RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display 
- the Scoring and Assessment Inference
- the Category
- the Category Description
- the value as a Single Value or
- the value a Range Value   


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_scoring_and_assessment_inference_async.py
   
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
    print(f"ENDPOINT: {ENDPOINT}")

    job_id = str(uuid.uuid4())

    radiology_insights_client = RadiologyInsightsClient(endpoint=ENDPOINT, credential=credential)
    # [END create_radiology_insights_client]

    # [START create_radiology_insights_request]
    doc_content1 = """Exam: US THYROID

    Clinical History: Thyroid nodules. 76 year old patient.

    Comparison: none.

    Findings:
    Right lobe: 4.8 x 1.6 x 1.4 cm
    Left Lobe: 4.1 x 1.3 x 1.3 cm

    Isthmus: 4 mm

    There are multiple cystic and partly cystic sub-5 mm nodules noted within the right lobe (TIRADS 2).
    In the lower pole of the left lobe there is a 9 x 8 x 6 mm predominantly solid isoechoic nodule (TIRADS 3).
    
    CADRADS 3/4
    
    Impression:
    Multiple bilateral small cystic benign thyroid nodules. A low suspicion 9 mm left lobe thyroid nodule (TI-RADS 3) which, given its small size, does not warrant follow-up."""

    # Create ordered procedure
    procedure_coding = models.Coding(
        system="http://www.ama-assn.org/go/cpt",
        code="USTHY",
        display="US THYROID",
    )

    procedure_code = models.CodeableConcept(coding=[procedure_coding])
    ordered_procedure = models.OrderedProcedure(description="CT CHEST WO CONTRAST", code=procedure_code)

    # Create encounter
    start = datetime.datetime(2014, 2, 20, 0, 0, 0, 0)
    end = datetime.datetime(2014, 2, 20, 0, 0, 0, 0)
    encounter = models.PatientEncounter(
        id="encounterid1",
        class_property=models.EncounterClass.IN_PATIENT,
        period=models.TimePeriod(start=start, end=end),
    )

    # Create patient info
    birth_date = datetime.date(1939, 5, 25)
    patient_info = models.PatientDetails(sex=models.PatientSex.FEMALE, birth_date=birth_date)
    # Create author
    author = models.DocumentAuthor(id="authorid1", full_name="authorname1")

    create_date_time = datetime.datetime(2014, 2, 20, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
    patient_document1 = models.PatientDocument(
        type=models.DocumentType.NOTE,
        clinical_type=models.ClinicalDocumentType.RADIOLOGY_REPORT,
        id="docid1",
        content=models.DocumentContent(source_type=models.DocumentContentSourceType.INLINE, value=doc_content1),
        created_at=create_date_time,
        specialty_type=models.SpecialtyType.RADIOLOGY,
        administrative_metadata=models.DocumentAdministrativeMetadata(
            ordered_procedures=[ordered_procedure], encounter_id="encounterid1"
        ),
        authors=[author],
        language="en",
    )

    # Construct patient
    patient1 = models.PatientRecord(
        id="Samantha Jones",
        details=patient_info,
        encounters=[encounter],
        patient_documents=[patient_document1],
    )

    # Set followup recommendation options
    followup_recommendation_options = models.FollowupRecommendationOptions(
        include_recommendations_with_no_specified_modality=True,
        include_recommendations_in_references=True,
        provide_focused_sentence_evidence=True,
    )

    # Set finding options
    finding_options = models.FindingOptions(provide_focused_sentence_evidence=True)

    # Create inference options
    inference_options = models.RadiologyInsightsInferenceOptions(
        followup_recommendation_options=followup_recommendation_options,
        finding_options=finding_options,
    )

    # Create a configuration
    configuration = models.RadiologyInsightsModelConfiguration(
        verbose=True, include_evidence=True, locale="en-US", inference_options=inference_options
    )

    # Construct the request with the patient and configuration
    patient_data = models.RadiologyInsightsJob(
        job_data=models.RadiologyInsightsData(patients=[patient1], configuration=configuration)
    )
    # [END create_radiology_insights_request]

    # Health Insights Radiology Insights
    try:
        async with radiology_insights_client:
            poller = await radiology_insights_client.begin_infer_radiology_insights(
                id=job_id,
                resource=patient_data,
            )
            radiology_insights_result = await poller.result()
            display_scoring_and_assessment(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_scoring_and_assessment(radiology_insights_result):
    # [START display_scoring_and_assessment]
    for patient_result in radiology_insights_result.patient_results:
        counter = 0
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.SCORING_AND_ASSESSMENT:
                counter += 1
                print(f"Scoring and assesment {counter} Inference found")

                # Print Category
                if ri_inference.category:
                    print(f"Category : {ri_inference.category}")

                # Print Compliance Type
                if ri_inference.category_description:
                    print(f"Category Description: {ri_inference.category_description}")

                # Print Quality Criteria
                if ri_inference.single_value:
                    print(f"Single Value: {ri_inference.single_value}")

                # Print Range Value
                if ri_inference.range_value:
                    display_range_value(ri_inference.range_value)
    # [END display_scoring_and_assessment]


def display_range_value(range_value):
    if range_value.minimum and range_value.maximum:
        print(f"Range Value: Low = {range_value.minimum}, High = {range_value.maximum}")
    else:
        print("Range Value: Not available")


if __name__ == "__main__":
    try:
        asyncio.run(radiology_insights_async())
    except Exception as ex:
        raise ex
