# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import os
import datetime

from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.cancerprofiling.models import *  # type: ignore
from azure.healthinsights.cancerprofiling.aio import CancerProfilingClient

"""
FILE: sample_infer_cancer_profiling.py

DESCRIPTION:
    Infer key cancer attributes such as tumor site, histology, clinical stage TNM categories and pathologic stage TNM 
    categories from a patient's unstructured clinical documents.
    
    OncoPhenotype model enables cancer registrars and clinical researchers to infer key cancer attributes from 
    unstructured clinical documents along with evidence relevant to those attributes. This model can help reduce the 
    manual time spent combing through large amounts of patient documentation. 


USAGE:
    python sample_infer_cancer_profiling.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHINSIGHTS_KEY - your source from Health Insights API key.
    2) HEALTHINSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
"""


class HealthInsightsSamples:
    async def infer_cancer_profiling(self):
        KEY = os.getenv("HEALTHINSIGHTS_KEY") or "0"
        ENDPOINT = os.getenv("HEALTHINSIGHTS_ENDPOINT") or "0"

        # Create an Onco Phenotype client
        # <client>
        cancer_profiling_client = CancerProfilingClient(endpoint=ENDPOINT,
                                                    credential=AzureKeyCredential(KEY))
        # </client>

        # Construct patient
        # <PatientConstructor>
        patient_info = PatientInfo(sex=PatientInfoSex.FEMALE, birth_date=datetime.date(1979, 10, 8))
        patient1 = PatientRecord(id="patient_id", info=patient_info)
        # </PatientConstructor>

        # Add document list
        # <DocumentList>
        doc_content1 = "15.8.2021" \
                       + "Jane Doe 091175-8967" \
                       + "42 year old female, married with 3 children, works as a nurse. " \
                       + "Healthy, no medications taken on a regular basis." \
                       + "PMHx is significant for migraines with aura, uses Mirena for contraception." \
                       + "Smoking history of 10 pack years (has stopped and relapsed several times)." \
                       + "She is in c/o 2 weeks of productive cough and shortness of breath." \
                       + "She has a fever of 37.8 and general weakness. " \
                       + "Denies night sweats and rash. She denies symptoms of rhinosinusitis, asthma, and heartburn. " \
                       + "On PE:" \
                       + "GENERAL: mild pallor, no cyanosis. Regular breathing rate. " \
                       + "LUNGS: decreased breath sounds on the base of the right lung. Vesicular breathing." \
                       + " No crackles, rales, and wheezes. Resonant percussion. " \
                       + "PLAN: " \
                       + "Will be referred for a chest x-ray. " \
                       + "======================================" \
                       + "CXR showed mild nonspecific opacities in right lung base. " \
                       + "PLAN:" \
                       + "Findings are suggestive of a working diagnosis of pneumonia. The patient is referred to a " \
                       + "follow-up CXR in 2 weeks. "

        patient_document1 = PatientDocument(type=DocumentType.NOTE,
                                            id="doc1",
                                            content=DocumentContent(source_type=DocumentContentSourceType.INLINE,
                                                                    value=doc_content1),
                                            clinical_type=ClinicalDocumentType.IMAGING,
                                            language="en",
                                            created_date_time=datetime.datetime(2021, 8, 15))

        doc_content2 = "Oncology Clinic " \
                       + "20.10.2021" \
                       + "Jane Doe 091175-8967" \
                       + "42-year-old healthy female who works as a nurse in the ER of this hospital. " \
                       + "First menstruation at 11 years old. First delivery- 27 years old. She has 3 children." \
                       + "Didn’t breastfeed. " \
                       + "Contraception- Mirena." \
                       + "Smoking- 10 pack years. " \
                       + "Mother- Belarusian. Father- Georgian. " \
                       + "About 3 months prior to admission, she stated she had SOB and was febrile. " \
                       + "She did a CXR as an outpatient which showed a finding in the base of the right lung- " \
                       + "possibly an infiltrate." \
                       + "She was treated with antibiotics with partial response. " \
                       + "6 weeks later a repeat CXR was performed- a few solid dense findings in the right lung. " \
                       + "Therefore, she was referred for a PET-CT which demonstrated increased uptake in the right " \
                       + "breast, lymph nodes on the right a few areas in the lungs and liver. " \
                       + "On biopsy from the lesion in the right breast- triple negative adenocarcinoma. Genetic " \
                       + "testing has not been done thus far. " \
                       + "Genetic counseling- the patient denies a family history of breast, ovary, uterus, " \
                       + "and prostate cancer. Her mother has chronic lymphocytic leukemia (CLL). " \
                       + "She is planned to undergo genetic tests because the aggressive course of the disease, " \
                       + "and her young age. " \
                       + "Impression:" \
                       + "Stage 4 triple negative breast adenocarcinoma. " \
                       + "Could benefit from biological therapy. " \
                       + "Different treatment options were explained- the patient wants to get a second opinion."

        patient_document2 = PatientDocument(type=DocumentType.NOTE,
                                            id="doc2",
                                            content=DocumentContent(source_type=DocumentContentSourceType.INLINE,
                                                                    value=doc_content2),
                                            clinical_type=ClinicalDocumentType.PATHOLOGY,
                                            language="en",
                                            created_date_time=datetime.datetime(2021, 10, 20))

        doc_content3 = "PATHOLOGY REPORT" \
                       + "                          Clinical Information" \
                       + "Ultrasound-guided biopsy; A. 18 mm mass; most likely diagnosis based on imaging:  IDC" \
                       + "                               Diagnosis" \
                       + " A.  BREAST, LEFT AT 2:00 4 CM FN; ULTRASOUND-GUIDED NEEDLE CORE BIOPSIES:" \
                       + " - Invasive carcinoma of no special type (invasive ductal carcinoma), grade 1" \
                       + " Nottingham histologic grade:  1/3 (tubules 2; nuclear grade 2; mitotic rate 1; " \
                       + " total score; 5/9)" \
                       + " Fragments involved by invasive carcinoma:  2" \
                       + " Largest measurement of invasive carcinoma on a single fragment:  7 mm" \
                       + " Ductal carcinoma in situ (DCIS):  Present" \
                       + " Architectural pattern:  Cribriform" \
                       + " Nuclear grade:  2-" \
                       + "                  -intermediate" \
                       + " Necrosis:  Not identified" \
                       + " Fragments involved by DCIS:  1" \
                       + " Largest measurement of DCIS on a single fragment:  Span 2 mm" \
                       + " Microcalcifications:  Present in benign breast tissue and invasive carcinoma" \
                       + " Blocks with invasive carcinoma:  A1" \
                       + " Special studies: Pending"

        patient_document3 = PatientDocument(type=DocumentType.NOTE,
                                            id="doc3",
                                            content=DocumentContent(source_type=DocumentContentSourceType.INLINE,
                                                                    value=doc_content3),
                                            clinical_type=ClinicalDocumentType.PATHOLOGY,
                                            language="en",
                                            created_date_time=datetime.datetime(2022, 1, 1))

        patient_doc_list = [patient_document1, patient_document2, patient_document3]
        patient1.data = patient_doc_list
        # <\DocumentList>

        # Set configuration to include evidence for the cancer staging inferences
        configuration = OncoPhenotypeModelConfiguration(include_evidence=True)

        # Construct the request with the patient and configuration
        cancer_profiling_data = OncoPhenotypeData(patients=[patient1], configuration=configuration)

        # Health Insights Infer Oncology Phenotyping
        try:
            poller = await cancer_profiling_client.begin_infer_cancer_profile(cancer_profiling_data)
            cancer_profiling_result = await poller.result()
            self.print_inferences(cancer_profiling_result)
        except Exception as ex:
            print(str(ex))
            return

    # print the inferences
    def print_inferences(self, cancer_profiling_result):
        if cancer_profiling_result.status == JobStatus.SUCCEEDED:
            results = cancer_profiling_result.results
            for patient_result in results.patients:
                print(f"\n==== Inferences of Patient {patient_result.id} ====")
                for inference in patient_result.inferences:
                    print(
                        f"\n=== Clinical Type: {str(inference.type)} Value: {inference.value}\
                            ConfidenceScore: {inference.confidence_score} ===")
                    for evidence in inference.evidence:
                        data_evidence = evidence.patient_data_evidence
                        print(
                            f"Evidence {data_evidence.id} {data_evidence.offset} {data_evidence.length}\
                                {data_evidence.text}")
        else:
            errors = cancer_profiling_result.errors
            if errors is not None:
                for error in errors:
                    print(f"{error.code} : {error.message}")


async def main():
    sample = HealthInsightsSamples()
    await sample.infer_cancer_profiling()


if __name__ == "__main__":
    asyncio.run(main())
