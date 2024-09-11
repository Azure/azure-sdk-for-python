# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_finding_inference.py

DESCRIPTION:
The sample_finding_inference.py module processes a sample radiology document with the Radiology Insights service.
It will initialize a RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display 
-the Finding resource type,
-the Finding ID,
-the Finding status,
-the Finding category code,
-the Finding code,
-the Finding interpretation,
-the Finding components,
-the Finding component code,
-the Finding component value codeable concept,
-the Finding component value coding,
-the Finding component value boolean,
-the Finding component value quantity,
-the Inference extensions,
-the Inference extension URL,
-the Inference extension value string,
-the Inference extension section   


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_finding_inference.py
   
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

    doc_content1 = """FINDINGS:
    In the right upper lobe, there is a new mass measuring 5.6 x 4.5 x 3.4 cm.
    A lobulated soft tissue mass is identified in the superior right lower lobe abutting the major fissure measuring 5.4 x 4.3 x 3.7 cm (series 3 image 94, coronal image 110).
    A 4 mm nodule in the right lower lobe (series 3, image 72) is increased dating back to 6/29/2012. This may represent lower lobe metastasis.
    IMPRESSION: 4 cm pulmonary nodule posterior aspect of the right upper lobe necessitating additional imaging as described."""

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

    # Health Insights Radiology Insights
    try:
        poller = radiology_insights_client.begin_infer_radiology_insights(
            id=job_id,
            resource=patient_data,
        )
        radiology_insights_result = poller.result()
        display_finding(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_finding(radiology_insights_result):
    for patient_result in radiology_insights_result.patient_results:
        counter = 0
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.FINDING:
                counter += 1
                print(f"Finding {counter} Inference found")
                fin = ri_inference.finding
                for attribute in dir(fin):
                    if attribute.startswith("_") or callable(getattr(fin, attribute)):
                        continue
                    elif attribute == "resource_type" and fin.resource_type is not None:
                        print(f"Finding {counter}: Resource Type: {fin.resource_type}")
                    elif attribute == "id" and fin.id is not None:
                        print(f"Finding {counter}: ID: {fin.id}")
                    elif attribute == "status" and fin.status is not None:
                        print(f"Finding {counter}: Status: {fin.status}")
                    elif attribute == "category" and fin.category is not None:
                        for cat in fin.category:
                            if cat.coding is not None:
                                for code in cat.coding:
                                    if code.code is not None and code.display is not None:
                                        print(
                                            f"Finding {counter}: Category Code: {code.system} {code.code} {code.display}"
                                        )
                    elif attribute == "code" and fin.code is not None:
                        for code in fin.code.coding:
                            if code.code is not None and code.display is not None:
                                print(f"Finding {counter}: Code: {code.system} {code.code} {code.display}")
                    elif attribute == "interpretation" and fin.interpretation is not None:
                        for interpretation in fin.interpretation:
                            for code in interpretation.coding:
                                if code.code is not None and code.display is not None:
                                    print(
                                        f"Finding {counter}: Interpretation: {code.system} {code.code} {code.display}"
                                    )
                    elif attribute == "component" and fin.component is not None:
                        print(f"Finding {counter}: COMPONENTS:")
                        for component in fin.component:
                            for attribute in dir(component):
                                if attribute.startswith("_") or callable(getattr(component, attribute)):
                                    continue
                                if attribute == "code" and component.code is not None:
                                    for code in component.code.coding:
                                        if code.code is not None and code.display is not None:
                                            print(
                                                f"Finding {counter}: COMPONENTS: Code: {code.system} {code.code} {code.display}"
                                            )
                                elif (
                                    attribute == "value_codeable_concept"
                                    and component.value_codeable_concept is not None
                                ):
                                    for code in component.value_codeable_concept.coding:
                                        if code.code is not None and code.display is not None:
                                            print(
                                                f"Finding {counter}: COMPONENTS: Value Codeable Concept: {code.system} {code.code} {code.display}"
                                            )
                                elif attribute == "value_coding" and component.value_coding is not None:
                                    for code in component.value_coding.coding:
                                        if code.code is not None and code.display is not None:
                                            print(
                                                f"Finding {counter}: COMPONENTS: Value Coding: {code.system} {code.code} {code.display}"
                                            )
                                elif attribute == "value_boolean" and component.value_boolean is not None:
                                    print(f"Finding {counter}: COMPONENTS: Value Boolean: {component.value_boolean}")
                                elif attribute == "value_quantity" and component.value_quantity is not None:
                                    for attribute in dir(component.value_quantity):
                                        if (
                                            not attribute.startswith("_")
                                            and not callable(getattr(component.value_quantity, attribute))
                                            and getattr(component.value_quantity, attribute) is not None
                                        ):
                                            print(
                                                f"Finding {counter}: COMPONENTS: Value Quantity: {attribute.capitalize()}: {getattr(component.value_quantity, attribute)}"
                                            )
                inference_extension = ri_inference.extension
                if inference_extension is not None:
                    print(f"Finding {counter}: INFERENCE EXTENSIONS:")
                    for extension in inference_extension:
                        for attribute in dir(extension):
                            if attribute.startswith("_") or callable(getattr(extension, attribute)):
                                continue
                            elif attribute == "extension" and extension.extension is not None:
                                for sub_extension in extension.extension:
                                    for sub_attribute in dir(sub_extension):
                                        if sub_attribute.startswith("_") or callable(
                                            getattr(sub_extension, sub_attribute)
                                        ):
                                            continue
                                        elif sub_attribute == "url":
                                            if (
                                                sub_extension.url == "code"
                                                or sub_extension.url == "codingSystem"
                                                or sub_extension.url == "codeSystemName"
                                                or sub_extension.url == "displayName"
                                            ):
                                                print(
                                                    f"Finding {counter}: INFERENCE EXTENSIONS: EXTENSION: {sub_attribute.capitalize()}: {sub_extension.url}"
                                                )
                                        elif sub_attribute == "value_string" and sub_extension.value_string is not None:
                                            print(
                                                f"Finding {counter}: INFERENCE EXTENSIONS: EXTENSION: {sub_attribute.capitalize()}: {sub_extension.value_string}"
                                            )
                            elif attribute == "url" and extension.url is not None:
                                if extension.url == "section":
                                    print(
                                        f"Finding {counter}: INFERENCE EXTENSIONS: {attribute.capitalize()}: {extension.url}"
                                    )


if __name__ == "__main__":
    radiology_insights_sync()
