import functools
import datetime
import asyncio

from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.radiologyinsights.aio import RadiologyInsightsClient
from azure.healthinsights.radiologyinsights import models
from devtools_testutils.aio import recorded_by_proxy_async

from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)

HealthInsightsEnvPreparer = functools.partial(
    EnvironmentVariableLoader,
    "healthinsights",
    healthinsights_endpoint="https://fake_ad_resource.cognitiveservices.azure.com/",
    healthinsights_key="00000000000000000000000000000000",
)


class TestRadiologyInsightsClient(AzureRecordedTestCase):
    def create_request(self):

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

        procedure_coding = models.Coding(
            system="Http://hl7.org/fhir/ValueSet/cpt-all",
            code="USPELVIS",
            display="US PELVIS COMPLETE",
        )
        procedure_code = models.CodeableConcept(coding=[procedure_coding])
        ordered_procedure = models.OrderedProcedure(description="US PELVIS COMPLETE", code=procedure_code)

        start = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
        end = datetime.datetime(2021, 8, 28, 0, 0, 0, 0)
        encounter = models.Encounter(
            id="encounter2",
            class_property=models.EncounterClass.IN_PATIENT,
            period=models.TimePeriod(start=start, end=end),
        )

        birth_date = datetime.date(1959, 11, 11)
        patient_info = models.PatientDetails(sex=models.PatientSex.FEMALE, birth_date=birth_date)

        author = models.DocumentAuthor(id="author2", full_name="authorName2")

        create_date_time = datetime.datetime(2024, 2, 19, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        patient_document1 = models.PatientDocument(
            type=models.DocumentType.NOTE,
            clinical_type=models.ClinicalDocumentType.RADIOLOGY_REPORT,
            id="doc2",
            content=models.DocumentContent(source_type=models.DocumentContentSourceType.INLINE, value=doc_content1),
            created_date_time=create_date_time,
            specialty_type=models.SpecialtyType.RADIOLOGY,
            administrative_metadata=models.DocumentAdministrativeMetadata(
                ordered_procedures=[ordered_procedure], encounter_id="encounter2"
            ),
            authors=[author],
            language="en",
        )

        patient1 = models.PatientRecord(
            id="patient_id2",
            info=patient_info,
            encounters=[encounter],
            patient_documents=[patient_document1],
        )

        configuration = models.RadiologyInsightsModelConfiguration(verbose=False, include_evidence=True, locale="en-US")

        data = models.RadiologyInsightsData(patients=[patient1], configuration=configuration)
        return data

    @HealthInsightsEnvPreparer()
    @recorded_by_proxy_async
    async def test_critical_result(self, healthinsights_endpoint, healthinsights_key):
        radiology_insights_client = RadiologyInsightsClient(
            healthinsights_endpoint, AzureKeyCredential(healthinsights_key)
        )
        data = TestRadiologyInsightsClient.create_request(self)
        request_time = datetime.datetime(2024, 2, 26, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        poller = await radiology_insights_client.begin_infer_radiology_insights(
            data,
            headers={
                "Repeatability-First-Sent": request_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "Repeatability-Request-ID": "5189b7f2-a13a-4cac-bebf-407c4ffc3a7c",
            },
        )
        radiology_insights_result = await poller.result()

        for patient_result in radiology_insights_result.patient_results:
            assert patient_result.inferences is not None
            for inference in patient_result.inferences:
                assert inference.kind is not None
