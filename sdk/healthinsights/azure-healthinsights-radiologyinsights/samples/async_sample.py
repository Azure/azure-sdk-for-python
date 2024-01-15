# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import os
import datetime
import pytz
import json


from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.radiologyinsights.aio import RadiologyInsightsClient
from azure.healthinsights.radiologyinsights import models
from datetime import timezone

"""
FILE: async_sample.py

DESCRIPTION:
    


USAGE:
   
"""


class HealthInsightsSamples:
    async def radiology_insights_async(self) -> None:
        KEY = os.environ["HEALTHINSIGHTS_KEY"]
        ENDPOINT = os.environ["HEALTHINSIGHTS_ENDPOINT"]

        # Create a Radiology Insights client
        # <client>
        radiology_insights_client = RadiologyInsightsClient(endpoint=ENDPOINT,
                                                      credential=AzureKeyCredential(KEY))
        # </client>
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
        procedure_coding=models.Coding(system="Http://hl7.org/fhir/ValueSet/cpt-all",
                                       code="USPELVIS",
                                       display="US PELVIS COMPLETE")
        procedure_code = models.CodeableConcept(coding=[procedure_coding])
        ordered_procedure = models.OrderedProcedure(description="US PELVIS COMPLETE",
                                                    code=[procedure_code])
        # Create encounter
        target_tz = pytz.timezone('US/Eastern')
        start_tz = datetime.datetime(2021,8,28,0,0,0,0)
        start = start_tz.astimezone(target_tz)
        end_tz = datetime.datetime(2021,8,28,0,0,0,0)
        end = end_tz.astimezone(target_tz)
        encounter = models.Encounter(id="encounter2",
                                     class_property=models.EncounterClass.IN_PATIENT,
                                     period=models.TimePeriod(start=start,
                                                              end=end)
                                    )
        # Create patient info
        birth_date = datetime.date(1959, 11, 11)
        patient_info = models.PatientInfo(sex=models.PatientInfoSex.FEMALE, birth_date=birth_date)
        # Create author
        author=models.DocumentAuthor(id="author2",full_name="authorName2")
        # Create document
        created_time=datetime.datetime(2021,8,29,0,0,0,0)
        create_date_time=created_time.astimezone(target_tz)
        patient_document1 = models.PatientDocument(type=models.DocumentType.NOTE,
                                                    clinical_type=models.ClinicalDocumentType.RADIOLOGY_REPORT,
                                                    id="doc2",
                                                    content=models.DocumentContent(
                                                        source_type=models.DocumentContentSourceType.INLINE,
                                                        value=doc_content1),
                                                    created_date_time=create_date_time,
                                                    specialty_type=models.SpecialtyType.RADIOLOGY,
                                                    administrative_metadata=models.DocumentAdministrativeMetadata(
                                                        ordered_procedures=[ordered_procedure],
                                                        encounter_id="encounter2"),
                                                    authors=[author],
                                                    language="en")
            
        # Construct patient
        patient1 = models.PatientRecord(id="patient_id2", 
                                        info=patient_info, 
                                        encounters=[encounter], 
                                        patient_documents=[patient_document1])
        
        # Set configuration to include evidence for the inferences
        configuration = models.RadiologyInsightsModelConfiguration(verbose=False, include_evidence=True, locale="en-US")

        # Construct the request with the patient and configuration
        radiology_insights_data = models.RadiologyInsightsData(patients=[patient1], configuration=configuration)

        # Health Insights Radiology Insights
        try:
            poller = await radiology_insights_client.begin_infer_radiology_insights(radiology_insights_data)
            #poller = await radiology_insights_client.begin_infer_radiology_insights(radiology_insights_data,headers={"Repeatability-First-Sent":create_date_time.strftime('%a, %d %b %Y %H:%M:%S GMT')})
            radiology_insights_result = await poller.result()
            self.print_results(radiology_insights_result)
        except Exception as ex:
            print(str(ex))
            return

    # print critical result description
    @staticmethod
    def print_results(radiology_insights_result):
        if radiology_insights_result.status == models.JobStatus.SUCCEEDED:
            ri_results = radiology_insights_result.results
            for patient_result in ri_results.patients:
                print(f"Inferences of Patient {patient_result.id}")
                for ri_inferences in patient_result.inferences:
                   # if ri_inferences.type == models.CriticalResult()
                        print(f"Type: {str(ri_inferences.type)}")
                        print(f"Description {ri_inferences.description}")
        else:
            ri_errors = radiology_insights_result.errors
            if ri_errors is not None:
                for error in ri_errors:
                    print(f"{error.code} : {error.message}")

async def main():
    sample = HealthInsightsSamples()
    await sample.radiology_insights_async()

if __name__ == "__main__":
    asyncio.run(main())
