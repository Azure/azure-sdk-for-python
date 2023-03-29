# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import os
import datetime

from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.clinicalmatching.models import *  # type: ignore  # pylint: disable=ungrouped-imports
from azure.healthinsights.clinicalmatching.aio import ClinicalMatchingClient

"""
FILE: sample_match_trials_fhir.py

DESCRIPTION:
    Trial Eligibility Assessment for a Custom Trial.

    Trial Matcher can be used to understand the gaps of eligibility criteria for a specific patient for a given clinical
    trial. In this case, the trial is not taken from clinicaltrials.gov, however the trial is a custom trial that might 
    be not published clinicaltrials.gov yet.  The custom trial eligibility criteria section is provided as an input to 
    the Trial Matcher. 

    In this use case, the patient clinical information is provided to the Trial Matcher as a FHIR bundle. 
    Note that the Trial Matcher configuration include reference to the FHIR Server where the patient FHIR bundle is located.


USAGE:
    python sample_match_trials_fhir.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHINSIGHTS_KEY - your source from Health Insights API key.
    2) HEALTHINSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
"""


class HealthInsightsSamples:
    async def match_trials(self):
        KEY = os.getenv("HEALTHINSIGHTS_KEY") or "0"
        ENDPOINT = os.getenv("HEALTHINSIGHTS_ENDPOINT") or "0"

        # Create an Trial Matcher client
        # <client>
        trial_matcher_client = ClinicalMatchingClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
        # </client>

        # Create clinical info list
        # <clinicalInfo>
        clinical_info_list = [
            ClinicalCodedElement(
                system="http://www.nlm.nih.gov/research/umls",
                code="C0006826",
                name="Malignant Neoplasms",
                value="true",
            ),
            ClinicalCodedElement(
                system="http://www.nlm.nih.gov/research/umls",
                code="C1522449",
                name="Therapeutic radiology procedure",
                value="true",
            ),
            ClinicalCodedElement(
                system="http://www.nlm.nih.gov/research/umls",
                code="C1512162",
                name="Eastern Cooperative Oncology Group",
                value="1",
            ),
            ClinicalCodedElement(
                system="http://www.nlm.nih.gov/research/umls",
                code="C0019693",
                name="HIV Infections",
                value="false",
            ),
            ClinicalCodedElement(
                system="http://www.nlm.nih.gov/research/umls",
                code="C1300072",
                name="Tumor stage",
                value="2",
            ),
        ]

        # </clinicalInfo>

        # Construct Patient
        # <PatientConstructor>
        patient1 = self.get_patient_from_fhir_patient()
        # </PatientConstructor>

        # Create registry filter
        registry_filters = ClinicalTrialRegistryFilter()
        # Limit the trial to a specific patient condition ("Non-small cell lung cancer")
        registry_filters.conditions = ["Non-small cell lung cancer"]
        # Limit the clinical trial to a certain phase, phase 1
        registry_filters.phases = [ClinicalTrialPhase.PHASE1]
        # Specify the clinical trial registry source as ClinicalTrials.Gov
        registry_filters.sources = [ClinicalTrialSource.CLINICALTRIALS_GOV]
        # Limit the clinical trial to a certain location, in this case California, USA
        registry_filters.facility_locations = [
            GeographicLocation(country_or_region="United States", city="Gilbert", state="Arizona")
        ]
        # Limit the trial to a specific study type, interventional
        registry_filters.study_types = [ClinicalTrialStudyType.INTERVENTIONAL]

        # Construct ClinicalTrial instance and attach the registry filter to it.
        clinical_trials = ClinicalTrials(registry_filters=[registry_filters])

        # Create TrialMatcherRequest
        configuration = TrialMatcherModelConfiguration(clinical_trials=clinical_trials)
        trial_matcher_data = TrialMatcherData(patients=[patient1], configuration=configuration)

        # Health Health Insights Trial match trials
        try:
            poller = await trial_matcher_client.begin_match_trials(trial_matcher_data)
            trial_matcher_result = await poller.result()
            self.print_results(trial_matcher_result)
        except Exception as ex:
            print(str(ex))
            return

    # print match trials (eligible/ineligible)
    def print_results(self, trial_matcher_result):
        if trial_matcher_result.status == JobStatus.SUCCEEDED:
            tm_results = trial_matcher_result.results
            for patient_result in tm_results.patients:
                print(f"Inferences of Patient {patient_result.id}")
                for tm_inferences in patient_result.inferences:
                    print(f"Trial Id {tm_inferences.id}")
                    print(f"Type: {str(tm_inferences.type)}  Value: {tm_inferences.value}")
                    print(f"Description {tm_inferences.description}")
        else:
            tm_errors = trial_matcher_result.errors
            if tm_errors is not None:
                for error in tm_errors:
                    print(f"{error.code} : {error.message}")

    def get_patient_from_fhir_patient(self) -> PatientRecord:
        patient_info = PatientInfo(sex=PatientInfoSex.MALE, birth_date=datetime.date(1965, 12, 26))
        patient_data = PatientDocument(
            type=DocumentType.FHIR_BUNDLE,
            id="Consultation-14-Demo",
            content=DocumentContent(
                source_type=DocumentContentSourceType.INLINE,
                value=self.get_patient_doc_content(),
            ),
            clinical_type=ClinicalDocumentType.CONSULTATION,
        )
        return PatientRecord(id="patient_id", info=patient_info, data=[patient_data])

    def get_patient_doc_content(self) -> str:
        with open("match_trial_fhir_data.txt", "r", encoding="utf-8-sig") as f:
            content = f.read()
        return content


async def main():
    sample = HealthInsightsSamples()
    await sample.match_trials()


if __name__ == "__main__":
    asyncio.run(main())
