import functools
import json
import os
import pytest

from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.cancerprofiling import CancerProfilingClient

from devtools_testutils import (
    AzureRecordedTestCase,
    PowerShellPreparer,
    recorded_by_proxy,
)

HealthInsightsEnvPreparer = functools.partial(
    PowerShellPreparer,
    "healthinsights",
    healthinsights_endpoint="https://fake_ad_resource.cognitiveservices.azure.com",
    healthinsights_key="00000000000000000000000000000000",
)


class TestCancerProfiling(AzureRecordedTestCase):
    @pytest.mark.skip
    @HealthInsightsEnvPreparer()
    @recorded_by_proxy
    def test_cancer_profiling(self, healthinsights_endpoint, healthinsights_key):
        cancer_profiling_client = CancerProfilingClient(healthinsights_endpoint, AzureKeyCredential(healthinsights_key))

        assert cancer_profiling_client is not None

        data = {
          "configuration": {
            "checkForCancerCase": True,
            "verbose": False,
            "includeEvidence": True
          },
          "patients": [
            {
              "id": "patient1",
              "data": [
                {
                  "kind": "note",
                  "clinicalType": "pathology",
                  "id": "document1",
                  "language": "en",
                  "createdDateTime": "2022-01-01T00:00:00",
                  "content": {
                    "sourceType": "inline",
                    "value": "Laterality:  Left \n   Tumor type present:  Invasive duct carcinoma; duct carcinoma in situ \n   Tumor site:  Upper inner quadrant \n   Invasive carcinoma \n   Histologic type:  Ductal \n   Size of invasive component:  0.9 cm \n   Histologic Grade - Nottingham combined histologic score:  1 out of 3 \n   In situ carcinoma (DCIS) \n   Histologic type of DCIS:  Cribriform and solid \n   Necrosis in DCIS:  Yes \n   DCIS component of invasive carcinoma:  Extensive \n"
                  }
                }
              ]
            }
          ]
        }

        poller = cancer_profiling_client.begin_infer_cancer_profile(data)
        results = poller.result()

        assert len(results.results.patients[0].inferences) is not 0


