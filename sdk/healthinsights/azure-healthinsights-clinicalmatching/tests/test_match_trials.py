import functools
import json

from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.clinicalmatching import ClinicalMatchingClient

from devtools_testutils import (
    AzureRecordedTestCase,
    PowerShellPreparer,
    recorded_by_proxy,
)

HealthInsightsEnvPreparer = functools.partial(
    PowerShellPreparer,
    "healthinsights",
    healthinsights_endpoint="https://fake_ad_resource.cognitiveservices.azure.com/",
    healthinsights_key="00000000000000000000000000000000",
)


class TestMatchTrials(AzureRecordedTestCase):

    @HealthInsightsEnvPreparer()
    @recorded_by_proxy
    def test_match_trials(self, healthinsights_endpoint, healthinsights_key):
        clinical_matching_client = ClinicalMatchingClient(healthinsights_endpoint,
                                                  AzureKeyCredential(healthinsights_key))

        assert clinical_matching_client is not None

        data = {
            "configuration": {
                "clinicalTrials": {
                    "registryFilters": [
                        {
                            "conditions": [
                                "non small cell lung cancer (nsclc)"
                            ],
                            "sources": [
                                "clinicaltrials_gov"
                            ],
                            "recruitmentStatuses": [
                                "recruiting"
                            ],
                            "facilityLocations": [
                                {
                                    "city": "gilbert",
                                    "state": "arizona",
                                    "country": "United States"
                                }
                            ]
                        }
                    ]
                },
                "includeEvidence": True
            },
            "patients": [
                {
                    "id": "patient1",
                    "info": {
                        "sex": "male",
                        "birthDate": "1961-04-25T09:54:29.5210127+00:00",
                        "clinicalInfo": [{
                            "system": "http://www.nlm.nih.gov/research/umls",
                            "code": "C0032181",
                            "name": "Platelet count",
                            "value": "250000"
                        },
                            {
                                "system": "http://www.nlm.nih.gov/research/umls",
                                "code": "C0002965",
                                "name": "Unstable Angina",
                                "value": "true"
                            },
                            {
                                "system": "http://www.nlm.nih.gov/research/umls",
                                "code": "C1522449",
                                "name": "Radiotherapy",
                                "value": "false"
                            },
                            {
                                "system": "http://www.nlm.nih.gov/research/umls",
                                "code": "C0242957",
                                "name": "GeneOrProtein-Expression",
                                "value": "Negative;EntityType:GENEORPROTEIN-EXPRESSION"
                            },
                            {
                                "system": "http://www.nlm.nih.gov/research/umls",
                                "code": "C1300072",
                                "name": "cancer stage",
                                "value": "2"
                            }]
                    }
                }
            ]
        }

        poller = clinical_matching_client.begin_match_trials(data)
        result = poller.result()

        assert len(result.results.patients[0].inferences) is not 0
