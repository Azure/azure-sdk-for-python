# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import datetime

from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.clinicalmatching import ClinicalMatchingClient, models

"""
FILE: sample_match_trials_fhir.py

DESCRIPTION:
    Trial Eligibility Assessment for a Custom Trial.

    Trial Matcher can be used to understand the gaps of eligibility criteria for a specific patient for a given clinical
    trial. In this case, the trial is not taken from clinicaltrials.gov, however the trial is a custom trial that might 
    be not published clinicaltrials.gov yet.  The custom trial eligibility criteria section is provided as an input to 
    the Trial Matcher. 

    In this use case, the patient clinical information is provided to the Trial Matcher as a FHIR bundle. 
    Note that the Trial Matcher configuration include reference to the FHIR Server where the patient FHIR bundle is
    located.


USAGE:
    python sample_match_trials_fhir.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHINSIGHTS_KEY - your source from Health Insights API key.
    2) HEALTHINSIGHTS_ENDPOINT - the endpoint to your source Health Insights resource.
"""


class HealthInsightsSamples:
    def match_trials(self) -> None:
        KEY = os.environ["HEALTHINSIGHTS_KEY"]
        ENDPOINT = os.environ["HEALTHINSIGHTS_ENDPOINT"]

        # Create a Trial Matcher client
        # <client>
        trial_matcher_client = ClinicalMatchingClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
        # </client>

        # Construct Patient
        # <PatientConstructor>
        patient1 = self.get_patient_from_fhir_patient()
        # </PatientConstructor>

        # Create registry filter
        registry_filters = models.ClinicalTrialRegistryFilter()
        # Limit the trial to a specific patient condition ("Non-small cell lung cancer")
        registry_filters.conditions = ["Non-small cell lung cancer"]
        # Limit the clinical trial to a certain phase, phase 1
        registry_filters.phases = [models.ClinicalTrialPhase.PHASE1]
        # Specify the clinical trial registry source as ClinicalTrials.Gov
        registry_filters.sources = [models.ClinicalTrialSource.CLINICALTRIALS_GOV]
        # Limit the clinical trial to a certain location, in this case California, USA
        registry_filters.facility_locations = [
            models.GeographicLocation(country_or_region="United States", city="Gilbert", state="Arizona")]
        # Limit the trial to a specific study type, interventional
        registry_filters.study_types = [models.ClinicalTrialStudyType.INTERVENTIONAL]

        # Construct ClinicalTrial instance and attach the registry filter to it.
        clinical_trials = models.ClinicalTrials(registry_filters=[registry_filters])

        # Create TrialMatcherRequest
        configuration = models.TrialMatcherModelConfiguration(clinical_trials=clinical_trials)
        trial_matcher_data = models.TrialMatcherData(patients=[patient1], configuration=configuration)

        # Health Insights Trial match trials
        try:
            poller = trial_matcher_client.begin_match_trials(trial_matcher_data)
            trial_matcher_result = poller.result()
            self.print_results(trial_matcher_result)
        except Exception as ex:
            print(str(ex))
            return

    # print match trials (eligible/ineligible)
    @staticmethod
    def print_results(trial_matcher_result):
        if trial_matcher_result.status == models.JobStatus.SUCCEEDED:
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

    def get_patient_from_fhir_patient(self) -> models.PatientRecord:
        patient_info = models.PatientInfo(sex=models.PatientInfoSex.MALE, birth_date=datetime.date(1965, 12, 26))
        patient_data = models.PatientDocument(type=models.DocumentType.FHIR_BUNDLE,
                                              id="Consultation-14-Demo",
                                              content=models.DocumentContent(
                                                  source_type=models.DocumentContentSourceType.INLINE,
                                                  value=self.get_patient_doc_content()),
                                              clinical_type=models.ClinicalDocumentType.CONSULTATION)
        return models.PatientRecord(id="patient_id", info=patient_info, data=[patient_data])

    @staticmethod
    def get_patient_doc_content() -> str:
        samples_dir = os.path.dirname(os.path.realpath(__file__))
        data_location = os.path.join(samples_dir, "sample_data/match_trial_fhir_data.json")
        with open(data_location, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        return content


if __name__ == "__main__":
    sample = HealthInsightsSamples()
    sample.match_trials()
