# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_followup_recommendation_inference.py

DESCRIPTION:
The sample_followup_recommendation_inference.py module processes a sample radiology document with the Radiology Insights service.
It will initialize a RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display
- the Finding category code
- the Finding code
- the Finding ID
- the Finding resource type
- the Finding boolean is_conditional
- the Finding boolean is_guideline
- the Finding boolean is_hedging
- the Finding boolean is_option
- the Recommended Procedure code
- the Imaging procedure anatomy code
- the Imaging procedure anatomy extension url
- the Imaging procedure anatomy extension reference
- the Imaging procedure anatomy extension offset
- the Imaging procedure anatomy extension length
- the Imaging procedure modality code
- the Imaging procedure modality extension url
- the Imaging procedure modality extension reference
- the Imaging procedure modality extension offset
- the Imaging procedure modality extension length       


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_followup_recommendation_inference.py
   
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
        poller = radiology_insights_client.begin_infer_radiology_insights(id=job_id, resource=patient_data)
        radiology_insights_result = poller.result()
        display_followup_recommendation(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_followup_recommendation(radiology_insights_result):
    for patient_result in radiology_insights_result.patient_results:
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.FOLLOWUP_RECOMMENDATION:
                print(f"Follow-up Recommendation Inference found")
                for finding in ri_inference.findings:
                    for attribute in dir(finding):
                        if (
                            hasattr(finding, attribute)
                            and not attribute.startswith("_")
                            and not callable(getattr(finding, attribute))
                        ):
                            if attribute == "finding":
                                print(f"\nFollow-up Recommendation: FINDING :")
                                find = finding.finding
                                for attr in dir(find):
                                    if (
                                        hasattr(find, attr)
                                        and not attr.startswith("_")
                                        and not callable(getattr(find, attr))
                                    ):
                                        if getattr(find, attr) is not None:
                                            if attr == "category":
                                                for category in find.category:
                                                    for code in category.coding:
                                                        print(
                                                            f"Follow-up Recommendation: FINDING: Category: {code.system} {code.code} {code.display}"
                                                        )
                                            elif attr == "code":
                                                for code in find.code.coding:
                                                    print(
                                                        f"Follow-up Recommendation: FINDING: Code: {code.system} {code.code} {code.display}"
                                                    )
                                            elif attr == "id":
                                                print(f"Follow-up Recommendation: FINDING: ID: {find.id}")
                                            elif attr == "resource_type":
                                                print(
                                                    f"Follow-up Recommendation: FINDING: Resource Type: {find.resource_type}"
                                                )
                print(f"\nFollow-up Recommendation: BOOLEANS:")
                condition = ri_inference.is_conditional
                print(f"Follow-up Recommendation: BOOLEANS: is_conditional: {condition}")
                guideline = ri_inference.is_guideline
                print(f"Follow-up Recommendation: BOOLEANS: is_guideline: {guideline}")
                hedging = ri_inference.is_hedging
                print(f"Follow-up Recommendation: BOOLEANS: is_hedging: {hedging}")
                option = ri_inference.is_option
                print(f"Follow-up Recommendation: BOOLEANS: is_option: {option}")
                recproc = ri_inference.recommended_procedure
                for proccod in recproc.procedure_codes:
                    print(f"\nFollow-up Recommendation: PROCEDURE CODES:")
                    for coding in proccod.coding:
                        print(
                            f"Follow-up Recommendation: PROCEDURE CODES: {coding.system} {coding.code} {coding.display}"
                        )
                for improc in recproc.imaging_procedures:
                    print(f"\nFollow-up Recommendation: IMAGING PROCEDURE:")
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
                                            f"Follow-up Recommendation: IMAGING PROCEDURE: Anatomy Code: {coding.system} {coding.code} {coding.display}"
                                        )
                                    for extension in improc.anatomy.extension:
                                        print(
                                            f"Follow-up Recommendation: IMAGING PROCEDURE: Anatomy Url: {extension.url}"
                                        )
                                        for subext in extension.extension:
                                            if subext.url == "reference":
                                                print(
                                                    f"Follow-up Recommendation: IMAGING PROCEDURE: Anatomy Url: {subext.url} {subext.value_reference}"
                                                )
                                            elif subext.url == "offset":
                                                print(
                                                    f"Follow-up Recommendation: IMAGING PROCEDURE: Anatomy Url: {subext.url} {subext.value_integer}"
                                                )
                                            elif subext.url == "length":
                                                print(
                                                    f"Follow-up Recommendation: IMAGING PROCEDURE: Anatomy Url: {subext.url} {subext.value_integer}"
                                                )
                                else:
                                    print(f"Follow-up Recommendation: IMAGING PROCEDURE: Anatomy: none")
                            elif attribute == "modality":
                                if improc.modality is not None:
                                    for coding in improc.modality.coding:
                                        print(
                                            f"Follow-up Recommendation: IMAGING PROCEDURE: Modality Code: {coding.system} {coding.code} {coding.display}"
                                        )
                                    for extension in improc.modality.extension:
                                        print(
                                            f"Follow-up Recommendation: IMAGING PROCEDURE: Modality Url: {extension.url}"
                                        )
                                        for subext in extension.extension:
                                            if subext.url == "reference":
                                                print(
                                                    f"Follow-up Recommendation: IMAGING PROCEDURE: Modality Url: {subext.url} {subext.value_reference}"
                                                )
                                            elif subext.url == "offset":
                                                print(
                                                    f"Follow-up Recommendation: IMAGING PROCEDURE: Modality Url: {subext.url} {subext.value_integer}"
                                                )
                                            elif subext.url == "length":
                                                print(
                                                    f"Follow-up Recommendation: IMAGING PROCEDURE: Modality Url: {subext.url} {subext.value_integer}"
                                                )
                                else:
                                    print(f"Follow-up Recommendation: IMAGING PROCEDURE: Modality: none")


if __name__ == "__main__":
    radiology_insights_sync()
