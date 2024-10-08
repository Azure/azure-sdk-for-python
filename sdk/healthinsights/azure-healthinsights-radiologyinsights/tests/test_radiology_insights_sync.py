import functools
import datetime

from azure.healthinsights.radiologyinsights import RadiologyInsightsClient
from azure.healthinsights.radiologyinsights import models

from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
    recorded_by_proxy,
    get_credential,
)

HealthInsightsEnvPreparer = functools.partial(
    EnvironmentVariableLoader,
    "healthinsights",
    healthinsights_endpoint="https://fake_ad_resource.cognitiveservices.azure.com",
)


class TestRadiologyInsightsClient(AzureRecordedTestCase):
    @HealthInsightsEnvPreparer()
    @recorded_by_proxy
    def test_sync(self, healthinsights_endpoint):

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
        encounter = models.PatientEncounter(
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
            created_at=create_date_time,
            specialty_type=models.SpecialtyType.RADIOLOGY,
            administrative_metadata=models.DocumentAdministrativeMetadata(
                ordered_procedures=[ordered_procedure], encounter_id="encounter2"
            ),
            authors=[author],
            language="en",
        )

        patient1 = models.PatientRecord(
            id="patient_id2",
            details=patient_info,
            encounters=[encounter],
            patient_documents=[patient_document1],
        )

        configuration = models.RadiologyInsightsModelConfiguration(verbose=False, include_evidence=True, locale="en-US")

        data = models.RadiologyInsightsData(patients=[patient1], configuration=configuration)
        jobdata = models.RadiologyInsightsJob(job_data=data)

        radiology_insights_client = RadiologyInsightsClient(healthinsights_endpoint, get_credential())

        poller = radiology_insights_client.begin_infer_radiology_insights(
            id="SyncJobID",
            resource=jobdata,
        )
        radiology_insights_result = poller.result()

        for patient_result in radiology_insights_result.patient_results:
            assert patient_result.inferences is not None
            for inference in patient_result.inferences:
                assert inference.kind is not None
