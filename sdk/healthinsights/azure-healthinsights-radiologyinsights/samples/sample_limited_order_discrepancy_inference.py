# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_limited_order_discrepancy_inference.py

DESCRIPTION:
The sample_limited_order_discrepancy_inference.py module processes a sample radiology document with the Radiology Insights service.
It will initialize a RadiologyInsightsClient, build a Radiology Insights request with the sample document,
submit it to the client, RadiologyInsightsClient, and display the Order Type code, Present Body Part code and measurement.     
    


USAGE:

1. Set the environment variables with your own values before running the sample:
    - AZURE_HEALTH_INSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
    - For more details how to use DefaultAzureCredential, please take a look at https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential

2. python sample_limited_order_discrepancy_inference.py
   
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

    doc_content1 = """HISTORY: 49-year-old male with a history of tuberous sclerosis presenting with epigastric pain and diffuse tenderness. The patient was found to have pericholecystic haziness on CT; evaluation for acute cholecystitis.
    TECHNIQUE: Ultrasound evaluation of the abdomen was performed. Comparison is made to the prior abdominal ultrasound (2004) and to the enhanced CT of the abdomen and pelvis (2014).
    FINDINGS:
    The liver is elongated, measuring 19.3 cm craniocaudally, and is homogeneous in echotexture without evidence of focal mass lesion. The liver contour is smooth on high resolution images. There is no appreciable intra- or extrahepatic biliary ductal dilatation, with the visualized extrahepatic bile duct measuring up to 6 mm. There are multiple shadowing gallstones, including within the gallbladder neck, which do not appear particularly mobile. In addition, there is thickening of the gallbladder wall up to approximately 7 mm with probable mild mural edema. There is no pericholecystic fluid. No sonographic Murphy's sign was elicited; however the patient reportedly received pain medications in the emergency department.
    The pancreatic head, body and visualized portions of the tail are unremarkable. The spleen is normal in size, measuring 9.9 cm in length.
    The kidneys are normal in size. The right kidney measures 11.5 x 5.2 x 4.3 cm and the left kidney measuring 11.8 x 5.3 x 5.1 cm. There are again multiple bilateral echogenic renal masses consistent with angiomyolipomas, in keeping with the patient's history of tuberous sclerosis. The largest echogenic mass on the right is located in the upper pole and measures 1.2 x 1.3 x 1.3 cm. The largest echogenic mass on the left is located within the renal sinus and measures approximately 2.6 x 2.7 x 4.6 cm. Additional indeterminate renal lesions are present bilaterally and are better characterized on CT. There is no hydronephrosis.
    No ascites is identified within the upper abdomen.
    The visualized portions of the upper abdominal aorta and IVC are normal in caliber.
    IMPRESSION:
    1. Numerous gallstones associated with gallbladder wall thickening and probable gallbladder mural edema, highly suspicious for acute cholecystitis in this patient presenting with epigastric pain and pericholecystic hazy density identified on CT. Although no sonographic Murphy sign was elicited, evaluation is limited secondary to reported prior administration of pain medication. Thus, clinical correlation is required. No evidence of biliary ductal dilation.
    2. There are again multiple bilateral echogenic renal masses consistent with angiomyolipomas, in keeping with the patient's history of tuberous sclerosis. Additional indeterminate renal lesions are present bilaterally and are better characterized on CT and MR.
    These findings were discussed with Dr. Doe at 5:05 p.m. on 1/1/15."""

    # Create ordered procedure
    procedure_coding = models.Coding(
        system="Https://loinc.org",
        code="30704-1",
        display="US ABDOMEN LIMITED",
    )
    procedure_code = models.CodeableConcept(coding=[procedure_coding])
    ordered_procedure = models.OrderedProcedure(description="US ABDOMEN LIMITED", code=procedure_code)
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
        display_limited_order_discrepancy(radiology_insights_result)
    except Exception as ex:
        raise ex


def display_limited_order_discrepancy(radiology_insights_result):
    for patient_result in radiology_insights_result.patient_results:
        for ri_inference in patient_result.inferences:
            if ri_inference.kind == models.RadiologyInsightsInferenceType.LIMITED_ORDER_DISCREPANCY:
                print(f"Limited Order Discrepancy Inference found")
                ordertype = ri_inference.order_type
                for coding in ordertype.coding:
                    print(f"Limited Order Discrepancy: Order Type: {coding.system} {coding.code} {coding.display}")
                if not ri_inference.present_body_parts:
                    print(f"Limited Order Discrepancy: Present Body Parts: empty list")
                else:
                    for presentbodypart in ri_inference.present_body_parts:
                        for coding in presentbodypart.coding:
                            print(
                                f"Limited Order Discrepancy: Present Body Part: {coding.system} {coding.code} {coding.display}"
                            )
                if not ri_inference.present_body_part_measurements:
                    print(f"Limited Order Discrepancy: Present Body Part Measurements: empty list")
                else:
                    for presentbodypartmeasurement in ri_inference.present_body_part_measurements:
                        for coding in presentbodypartmeasurement.coding:
                            print(
                                f"Limited Order Discrepancy: Present Body Part Measurement: {coding.system} {coding.code} {coding.display}"
                            )


if __name__ == "__main__":
    radiology_insights_sync()
