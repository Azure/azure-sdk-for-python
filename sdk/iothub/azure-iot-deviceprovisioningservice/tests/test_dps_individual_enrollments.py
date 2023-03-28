import os
from os import mkdir
from pathlib import PurePath
from shutil import rmtree

from azure.iot.deviceprovisioningservice import ProvisioningServiceClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from tests.conftest import (
    API_VERSION,
    CERT_FOLDER,
    CUSTOM_ALLOCATION,
    DEVICE_INFO,
    REPROVISION_MIGRATE,
    TEST_DICT,
    TEST_ENDORSEMENT_KEY,
    WEBHOOK_URL,
    ProvisioningServicePreparer,
)
from tests.utility.common import create_test_cert, generate_enrollment, generate_key


class TestIndividualEnrollments(AzureRecordedTestCase):
    def create_provisioning_service_client(self, endpoint):
        credential = self.get_credential(ProvisioningServiceClient)
        client = ProvisioningServiceClient(endpoint=endpoint, credential=credential)
        return client

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_dps_enrollment_tpm_lifecycle(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)

        attestation_type = "tpm"
        enrollment_id = self.create_random_name("ind_enroll_tpm_")
        device_id = self.create_random_name("device_")
        enrollment = generate_enrollment(
            id=enrollment_id,
            attestation_type=attestation_type,
            endorsement_key=TEST_ENDORSEMENT_KEY,
            provisioning_status="enabled",
            device_id=device_id,
            allocation_policy="static",
        )

        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id, enrollment=enrollment
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["attestation"]["tpm"]
        assert (
            enrollment_response["attestation"]["tpm"]["endorsementKey"]
            == TEST_ENDORSEMENT_KEY
        )
        assert enrollment_response["allocationPolicy"] == "static"
        assert enrollment_response["deviceId"] == device_id
        assert enrollment_response["provisioningStatus"] == "enabled"

        # check for enrollment in query response
        enrollment_list = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 1
        assert enrollment_list[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = client.individual_enrollment.get(id=enrollment_id)

        assert enrollment_response["registrationId"] == enrollment_id

        # check attestation
        attestation_response = client.individual_enrollment.get_attestation_mechanism(
            id=enrollment_id
        )

        assert attestation_response["tpm"]["endorsementKey"] == TEST_ENDORSEMENT_KEY

        # update enrollment
        enrollment["provisioningStatus"] = "disabled"
        enrollment["optionalDeviceInformation"] = DEVICE_INFO
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert enrollment_response["provisioningStatus"] == "disabled"

        assert (
            enrollment_response["optionalDeviceInformation"]["additionalProperties"]
            == TEST_DICT
        )

        # delete enrollment
        client.individual_enrollment.delete(id=enrollment_id)

        # ensure deletion
        enrollment_list = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 0

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_dps_enrollment_x509_lifecycle(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)
        enrollment_id = self.create_random_name("x509_enrollment_")
        device_id = self.create_random_name("x509_device_")
        attestation_type = "x509"

        if not os.path.exists(CERT_FOLDER):
            mkdir(CERT_FOLDER)
        cert_name = self.create_random_name("enroll_cert_")
        thumb = create_test_cert(output_dir=CERT_FOLDER, subject=cert_name)
        cert_path = PurePath(CERT_FOLDER, cert_name + "-cert.pem").as_posix()

        enrollment = generate_enrollment(
            id=enrollment_id,
            device_id=device_id,
            certificate_path=cert_path,
            secondary_certificate_path=cert_path,
            provisioning_status="enabled",
            allocation_policy="hashed",
            attestation_type=attestation_type,
            reprovision_policy=REPROVISION_MIGRATE,
        )
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
        )

        assert enrollment_response
        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["deviceId"] == device_id

        # check auth
        assert enrollment_response["attestation"]["x509"]
        assert enrollment_response["attestation"]["type"] == "x509"
        assert (
            enrollment_response["attestation"]["x509"]["clientCertificates"]["primary"][
                "info"
            ]["subjectName"]
            == f"CN={cert_name}"
        )
        if self.is_live:
            assert (
                enrollment_response["attestation"]["x509"]["clientCertificates"][
                    "primary"
                ]["info"]["sha256Thumbprint"]
                == thumb
            )

        assert enrollment_response["provisioningStatus"] == "enabled"
        assert enrollment_response["allocationPolicy"] == "hashed"
        assert enrollment_response["reprovisionPolicy"]["migrateDeviceData"]
        assert enrollment_response["reprovisionPolicy"]["updateHubAssignment"]

        # check for enrollment in query response
        enrollment_list = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 1
        assert enrollment_list[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = client.individual_enrollment.get(id=enrollment_id)

        assert enrollment_response["registrationId"] == enrollment_id

        # check enrollment update
        enrollment["provisioningStatus"] = "disabled"
        enrollment["allocationPolicy"] = "custom"
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["provisioningStatus"] == "disabled"
        assert (
            enrollment_response["customAllocationDefinition"]["webhookUrl"]
            == WEBHOOK_URL
        )
        assert (
            enrollment_response["customAllocationDefinition"]["apiVersion"]
            == API_VERSION
        )

        # delete enrollment
        client.individual_enrollment.delete(id=enrollment_id)

        # ensure deletion
        enrollment_list = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 0

        # delete certificates
        rmtree(CERT_FOLDER, ignore_errors=True)

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_dps_enrollment_symmetrickey_lifecycle(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)
        attestation_type = "symmetricKey"
        enrollment_id = self.create_random_name("sym_enrollment_")
        primary_key = generate_key()
        secondary_key = generate_key()
        device_id = self.create_random_name("sym_key_device_")
        allocation_policy = "geoLatency"
        reprovision_policy = REPROVISION_MIGRATE
        enrollment = generate_enrollment(
            id=enrollment_id,
            device_id=device_id,
            allocation_policy=allocation_policy,
            reprovision_policy=reprovision_policy,
            attestation_type=attestation_type,
            primary_key=primary_key,
            secondary_key=secondary_key,
        )

        enrollment_id2 = self.create_random_name("sym_enrollment2_")

        # Use provided keys
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id, enrollment=enrollment
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["deviceId"] == device_id
        assert enrollment_response["attestation"]["symmetricKey"]

        if self.is_live:
            assert (
                enrollment_response["attestation"]["symmetricKey"]["primaryKey"]
                == primary_key
            )
            assert (
                enrollment_response["attestation"]["symmetricKey"]["secondaryKey"]
                == secondary_key
            )
        # reprovision migrate true
        assert enrollment_response["reprovisionPolicy"]["migrateDeviceData"]
        # reprovision update true
        assert enrollment_response["reprovisionPolicy"]["updateHubAssignment"]

        # check for enrollment in query response
        enrollment_list = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 1
        assert enrollment_list[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = client.individual_enrollment.get(id=enrollment_id)
        assert enrollment_response["registrationId"] == enrollment_id

        # check attestation
        attestation_response = client.individual_enrollment.get_attestation_mechanism(
            id=enrollment_id
        )

        if self.is_live:
            assert attestation_response["symmetricKey"]["primaryKey"] == primary_key
            assert attestation_response["symmetricKey"]["secondaryKey"] == secondary_key

        # check enrollment update
        enrollment["provisioningStatus"] = "disabled"
        enrollment["allocationPolicy"] = "custom"
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["provisioningStatus"] == "disabled"

        assert (
            enrollment_response["customAllocationDefinition"]["webhookUrl"]
            == WEBHOOK_URL
        )
        assert (
            enrollment_response["customAllocationDefinition"]["apiVersion"]
            == API_VERSION
        )

        # reprovision migrate true
        assert enrollment_response["reprovisionPolicy"]["migrateDeviceData"]
        # reprovision update true
        assert enrollment_response["reprovisionPolicy"]["updateHubAssignment"]

        # second enrollment
        enrollment2 = generate_enrollment(
            id=enrollment_id2,
            attestation_type=attestation_type,
            allocation_policy="custom",
            webhook_url=WEBHOOK_URL,
            api_version=API_VERSION,
        )
        enrollment_2 = client.individual_enrollment.create_or_update(
            id=enrollment_id2, enrollment=enrollment2
        )

        assert enrollment_2

        # check both enrollments
        enrollment_list = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 2
        assert enrollment_id in [e["registrationId"] for e in enrollment_list]
        assert enrollment_id2 in [e["registrationId"] for e in enrollment_list]

        # delete both enrollments
        client.individual_enrollment.delete(id=enrollment_id)
        client.individual_enrollment.delete(id=enrollment_id2)

        # ensure deletion
        enrollment_list = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 0

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_individual_enrollment_bulk_operations(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)
        attestation_type = "tpm"
        enrollment_id = self.create_random_name("ind_enroll_tpm_")
        device_id = self.create_random_name("device_")
        enrollment = generate_enrollment(
            id=enrollment_id,
            attestation_type=attestation_type,
            endorsement_key=TEST_ENDORSEMENT_KEY,
            provisioning_status="enabled",
            device_id=device_id,
            allocation_policy="static",
        )

        attestation_type = "symmetricKey"
        enrollment_id2 = self.create_random_name("sym_key_enrollment_")
        primary_key = generate_key()
        secondary_key = generate_key()
        device_id = self.create_random_name("sym_key_device_")
        allocation_policy = "geoLatency"
        reprovision_policy = REPROVISION_MIGRATE
        enrollment2 = generate_enrollment(
            id=enrollment_id2,
            device_id=device_id,
            allocation_policy=allocation_policy,
            reprovision_policy=reprovision_policy,
            attestation_type=attestation_type,
            primary_key=primary_key,
            secondary_key=secondary_key,
        )

        bulk_enrollment_operation = {
            "enrollments": [enrollment, enrollment2],
            "mode": "create",
        }

        bulk_enrollment_response = client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["enrollments"][0]["provisioningStatus"] == "disabled"
        bulk_enrollment_operation["enrollments"][1]["provisioningStatus"] == "disabled"
        bulk_enrollment_operation["mode"] = "update"

        bulk_enrollment_response = client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["mode"] = "delete"
        bulk_enrollment_response = client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response
