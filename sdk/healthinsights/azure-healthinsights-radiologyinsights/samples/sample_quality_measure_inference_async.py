# pylint: disable=line-too-long,useless-suppression
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_quality_measure_inference_async.py

DESCRIPTION:
The sample_quality_measure_inference_async.py module processes a sample radiology document with the Radiology Insights service.
It will initialize a asynchronous RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display 
- the Quality Measure Inference
- the Quality Measure Denominator
- the Compliance Type
- the Quality Criteria


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_quality_measure_inference_async.py
   
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
    doc_content1 = """EXAM: CT CHEST WO CONTRAST

    INDICATION: abnormal lung findings. History of emphysema.

    TECHNIQUE: Helical CT images through the chest, without contrast. This exam was performed using one or more of the following dose reduction techniques: Automated exposure control, adjustment of the mA and/or kV according to patient size, and/or use of iterative reconstruction technique. 

    COMPARISON: Chest CT dated 6/21/2022.
    Number of previous CT examinations or cardiac nuclear medicine (myocardial perfusion) examinations performed in the preceding 12-months: 2

    FINDINGS:
    Heart size is normal. No pericardial effusion. Thoracic aorta as well as pulmonary arteries are normal in caliber. There are dense coronary artery calcifications. No enlarged axillary, mediastinal, or hilar lymph nodes by CT size criteria. Central airways are widely patent. No bronchial wall thickening. No pneumothorax, pleural effusion or pulmonary edema. The previously identified posterior right upper lobe nodules are no longer seen. However, there are multiple new small pulmonary nodules. An 8 mm nodule in the right upper lobe, image #15 series 4. New posterior right upper lobe nodule measuring 6 mm, image #28 series 4. New 1.2 cm pulmonary nodule, right upper lobe, image #33 series 4. New 4 mm pulmonary nodule left upper lobe, image #22 series 4. New 8 mm pulmonary nodule in the left upper lobe adjacent to the fissure, image #42 series 4. A few new tiny 2 to 3 mm pulmonary nodules are also noted in the left lower lobe. As before there is a background of severe emphysema. No evidence of pneumonia.
    Limited evaluation of the upper abdomen shows no concerning abnormality.
    Review of bone windows shows no aggressive appearing osseous lesions.


    IMPRESSION:

    1. Previously identified small pulmonary nodules in the right upper lobe have resolved, but there are multiple new small nodules scattered throughout both lungs. Recommend short-term follow-up with noncontrast chest CT in 3 months as per current  Current guidelines (2017 Fleischner Society).
    2. Severe emphysema.

    Findings communicated to Dr. Jane Smith."""

    # Create ordered procedure
    procedure_coding = models.Coding(
        system="http://www.ama-assn.org/go/cpt",
        code="CTCHWO",
        display="CT CHEST WO CONTRAST",
    )

    procedure_code = models.CodeableConcept(coding=[procedure_coding])
    ordered_procedure = models.OrderedProcedure(description="CT CHEST WO CONTRAST", code=procedure_code)

    # Create encounter
    start = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
    end = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
    encounter = models.PatientEncounter(
        id="encounterid1",
        class_property=models.EncounterClass.IN_PATIENT,
        period=models.TimePeriod(start=start, end=end),
    )

    # Create patient info
    birth_date = datetime.date(1959, 11, 11)
    patient_info = models.PatientDetails(sex=models.PatientSex.FEMALE, birth_date=birth_date)
    # Create author
    author = models.DocumentAuthor(id="authorid1", full_name="authorname1")

    create_date_time = datetime.datetime(2021, 5, 31, 16, 0, 0, 0, tzinfo=datetime.timezone.utc)
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
        id="samantha jones",
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

    # Set quality measure options
    quality_measure_options = models.QualityMeasureOptions(
        measure_types=[
            models.QualityMeasureType.MIPS364,
            models.QualityMeasureType.MIPS360,
            models.QualityMeasureType.MIPS436,
            models.QualityMeasureType.ACRAD36,
        ]
    )

    # Create inference options
    inference_options = models.RadiologyInsightsInferenceOptions(
        followup_recommendation_options=followup_recommendation_options,
        finding_options=finding_options,
        quality_measure_options=quality_measure_options,
    )

    # Create configuration and set inference options
    configuration = models.RadiologyInsightsModelConfiguration(
        verbose=False, include_evidence=True, locale="en-US", inference_options=inference_options
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
            display_quality_measure(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_quality_measure(radiology_insights_result):
    # [START display_quality_measure]
    for patient_result in radiology_insights_result.patient_results:
        counter = 0
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.QUALITY_MEASURE:
                counter += 1
                print(f"Quality Measure {counter} Inference found")

                # Print Quality Measure Denominator
                if ri_inference.quality_measure_denominator:
                    print(f"Quality Measure Denominator: {ri_inference.quality_measure_denominator}")

                # Print Compliance Type
                if ri_inference.compliance_type:
                    print(f"Compliance Type: {ri_inference.compliance_type}")

                # Print Quality Criteria
                if ri_inference.quality_criteria:
                    for criteria in ri_inference.quality_criteria:
                        print(f"Quality Criterium: {criteria}")
    # [END display_quality_measure]


if __name__ == "__main__":
    try:
        asyncio.run(radiology_insights_async())
    except Exception as ex:
        raise ex
