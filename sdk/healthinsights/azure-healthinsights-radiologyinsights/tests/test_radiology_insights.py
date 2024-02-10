import functools

from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.radiologyinsights import RadiologyInsightsClient

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


class TestRadiologyInsights(AzureRecordedTestCase):

    @HealthInsightsEnvPreparer()
    @recorded_by_proxy
    def test_radiology_insights(self, healthinsights_endpoint, healthinsights_key):
        radiology_insights_client = RadiologyInsightsClient(
            healthinsights_endpoint, AzureKeyCredential(healthinsights_key)
        )

        assert radiology_insights_client is not None

        data = {
            {
                "_data": {
                    "patients": [
                        {
                            "_data": {
                                "id": "patient_id2",
                                "info": {
                                    "_data": {
                                        "sex": "female",
                                        "birthDate": "1959-11-11",
                                    }
                                },
                                "encounters": [
                                    {
                                        "_data": {
                                            "id": "encounter2",
                                            "class": "inpatient",
                                            "period": {
                                                "_data": {
                                                    "start": "2021-08-28T00:00:00Z",
                                                    "end": "2021-08-28T00:00:00Z",
                                                }
                                            },
                                        }
                                    }
                                ],
                                "patientDocuments": [
                                    {
                                        "_data": {
                                            "type": "note",
                                            "clinicalType": "radiologyReport",
                                            "id": "doc2",
                                            "content": {
                                                "_data": {
                                                    "sourceType": "inline",
                                                    "value": "CLINICAL HISTORY:   \n        20-year-old female presenting with abdominal pain. Surgical history significant for appendectomy.\n        COMPARISON:   \n        Right upper quadrant sonographic performed 1 day prior.\n        TECHNIQUE:   \n        Transabdominal grayscale pelvic sonography with duplex color Doppler and spectral waveform analysis of the ovaries.\n        FINDINGS:   \n        The uterus is unremarkable given the transabdominal technique with endometrial echo complex within physiologic normal limits. The ovaries are symmetric in size, measuring 2.5 x 1.2 x 3.0 cm and the left measuring 2.8 x 1.5 x 1.9 cm.\n On duplex imaging, Doppler signal is symmetric.\n        IMPRESSION:   \n        1. Normal pelvic sonography. Findings of testicular torsion.\n        A new US pelvis within the next 6 months is recommended.\n        These results have been discussed with Dr. Jones at 3 PM on November 5 2020.",
                                                }
                                            },
                                            "createdDateTime": "2024-01-24T23:03:01.554701Z",
                                            "specialtyType": "radiology",
                                            "administrativeMetadata": {
                                                "_data": {
                                                    "orderedProcedures": [
                                                        {
                                                            "_data": {
                                                                "description": "US PELVIS COMPLETE",
                                                                "code": {
                                                                    "_data": {
                                                                        "coding": [
                                                                            {
                                                                                "_data": {
                                                                                    "system": "Http://hl7.org/fhir/ValueSet/cpt-all",
                                                                                    "code": "USPELVIS",
                                                                                    "display": "US PELVIS COMPLETE",
                                                                                }
                                                                            }
                                                                        ]
                                                                    }
                                                                },
                                                            }
                                                        }
                                                    ],
                                                    "encounterId": "encounter2",
                                                }
                                            },
                                            "authors": [
                                                {
                                                    "_data": {
                                                        "id": "author2",
                                                        "fullName": "authorName2",
                                                    }
                                                }
                                            ],
                                            "language": "en",
                                        }
                                    }
                                ],
                            }
                        }
                    ],
                    "configuration": {
                        "_data": {
                            "verbose": False,
                            "includeEvidence": True,
                            "locale": "en-US",
                        }
                    },
                }
            }
        }

        poller = radiology_insights_client.begin_infer_radiology_insights(data)
        result = poller.result()

        assert len(result.patient_results) is not None
        assert len(result.patient_results[0].inferences) is not None
