from os import mkdir
from os.path import exists
from pathlib import PurePath
from shutil import rmtree

from azure.iot.deviceprovisioningservice import ProvisioningServiceClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from tests.conftest import (
    API_VERSION,
    CERT_FOLDER,
    CUSTOM_ALLOCATION,
    REPROVISION_MIGRATE,
    WEBHOOK_URL,
    ProvisioningServicePreparer,
)
from tests.utility.common import (
    create_test_cert,
    generate_enrollment_group,
    generate_key,
)


class TestEnrollmentGroups(AzureRecordedTestCase):
    def create_provisioning_service_client(self, endpoint):
        credential = self.get_credential(ProvisioningServiceClient)
        client = ProvisioningServiceClient(endpoint=endpoint, credential=credential)
        return client

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_dps_enrollment_group_x509_lifecycle(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)
        enrollment_group_id = self.create_random_name("x509_enroll_grp_")
        attestation_type = "x509"

        if not exists(CERT_FOLDER):
            mkdir(CERT_FOLDER)
        cert_name = self.create_random_name("enroll_cert_")
        thumb = create_test_cert(output_dir=CERT_FOLDER, subject=cert_name)
        cert_path = PurePath(CERT_FOLDER, cert_name + "-cert.pem").as_posix()

        enrollment_group = generate_enrollment_group(
            id=enrollment_group_id,
            certificate_path=cert_path,
            secondary_certificate_path=cert_path,
            provisioning_status="enabled",
            allocation_policy="hashed",
            attestation_type=attestation_type,
            reprovision_policy=REPROVISION_MIGRATE,
        )
        enrollment_group_response = client.enrollment_group.create_or_update(
            id=enrollment_group_id,
            enrollment_group=enrollment_group,
        )

        assert enrollment_group_response["enrollmentGroupId"] == enrollment_group_id

        # check auth
        assert enrollment_group_response["attestation"]["x509"]
        assert enrollment_group_response["attestation"]["type"] == "x509"
        assert (
            enrollment_group_response["attestation"]["x509"]["signingCertificates"][
                "primary"
            ]["info"]["subjectName"]
            == f"CN={cert_name}"
        )
        if self.is_live:
            assert (
                enrollment_group_response["attestation"]["x509"]["signingCertificates"][
                    "primary"
                ]["info"]["sha256Thumbprint"]
                == thumb
            )

        assert enrollment_group_response["provisioningStatus"] == "enabled"
        assert enrollment_group_response["allocationPolicy"] == "hashed"
        assert enrollment_group_response["reprovisionPolicy"]["migrateDeviceData"]
        assert enrollment_group_response["reprovisionPolicy"]["updateHubAssignment"]

        # check for enrollment in query response
        enrollment_group_list = client.enrollment_group.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_group_list) == 1
        assert enrollment_group_list[0]["enrollmentGroupId"] == enrollment_group_id

        # check enrollment get
        enrollment_group_response = client.enrollment_group.get(id=enrollment_group_id)

        assert enrollment_group_response["enrollmentGroupId"] == enrollment_group_id

        # check enrollment update
        enrollment_group["provisioningStatus"] = "disabled"
        enrollment_group["allocationPolicy"] = "custom"
        enrollment_group["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_group_response = client.enrollment_group.create_or_update(
            id=enrollment_group_id,
            enrollment_group=enrollment_group,
            if_match=enrollment_group_response["etag"],
        )

        assert enrollment_group_response["enrollmentGroupId"] == enrollment_group_id
        assert enrollment_group_response["provisioningStatus"] == "disabled"
        assert (
            enrollment_group_response["customAllocationDefinition"]["webhookUrl"]
            == WEBHOOK_URL
        )
        assert (
            enrollment_group_response["customAllocationDefinition"]["apiVersion"]
            == API_VERSION
        )

        # delete enrollment
        client.enrollment_group.delete(id=enrollment_group_id)

        # ensure deletion
        enrollment_group_list = client.enrollment_group.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_group_list) == 0

        # delete certificates
        rmtree(CERT_FOLDER, ignore_errors=True)

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_dps_enrollment_group_symmetrickey_lifecycle(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)
        attestation_type = "symmetricKey"
        enrollment_group_id = self.create_random_name("sym_enroll_grp_")
        primary_key = generate_key()
        secondary_key = generate_key()
        allocation_policy = "geoLatency"
        reprovision_policy = REPROVISION_MIGRATE
        enrollment_group = generate_enrollment_group(
            id=enrollment_group_id,
            allocation_policy=allocation_policy,
            reprovision_policy=reprovision_policy,
            attestation_type=attestation_type,
            primary_key=primary_key,
            secondary_key=secondary_key,
        )

        enrollment_group_id2 = self.create_random_name("sym_enroll_grp2_")

        # Use provided keys
        enrollment_group_response = client.enrollment_group.create_or_update(
            id=enrollment_group_id, enrollment_group=enrollment_group
        )

        assert enrollment_group_response["enrollmentGroupId"] == enrollment_group_id
        assert enrollment_group_response["attestation"]["symmetricKey"]
        if self.is_live:
            assert (
                enrollment_group_response["attestation"]["symmetricKey"]["primaryKey"]
                == primary_key
            )
            assert (
                enrollment_group_response["attestation"]["symmetricKey"]["secondaryKey"]
                == secondary_key
            )
        # reprovision migrate true
        assert enrollment_group_response["reprovisionPolicy"]["migrateDeviceData"]
        # reprovision update true
        assert enrollment_group_response["reprovisionPolicy"]["updateHubAssignment"]

        # check for enrollment in query response
        enrollment_group_list = client.enrollment_group.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_group_list) == 1
        assert enrollment_group_list[0]["enrollmentGroupId"] == enrollment_group_id

        # check enrollment get
        enrollment_group_response = client.enrollment_group.get(id=enrollment_group_id)

        assert enrollment_group_response["enrollmentGroupId"] == enrollment_group_id

        # check attestation
        attestation_response = client.enrollment_group.get_attestation_mechanism(
            id=enrollment_group_id
        )
        if self.is_live:
            assert attestation_response["symmetricKey"]["primaryKey"] == primary_key
            assert attestation_response["symmetricKey"]["secondaryKey"] == secondary_key

        # check enrollment update
        enrollment_group["provisioningStatus"] = "disabled"
        enrollment_group["allocationPolicy"] = "custom"
        enrollment_group["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_group_response = client.enrollment_group.create_or_update(
            id=enrollment_group_id,
            enrollment_group=enrollment_group,
            if_match=enrollment_group_response["etag"],
        )

        assert enrollment_group_response["enrollmentGroupId"] == enrollment_group_id
        assert enrollment_group_response["provisioningStatus"] == "disabled"
        assert (
            enrollment_group_response["customAllocationDefinition"]["webhookUrl"]
            == WEBHOOK_URL
        )
        assert (
            enrollment_group_response["customAllocationDefinition"]["apiVersion"]
            == API_VERSION
        )

        # reprovision migrate true
        assert enrollment_group_response["reprovisionPolicy"]["migrateDeviceData"]
        # reprovision update true
        assert enrollment_group_response["reprovisionPolicy"]["updateHubAssignment"]

        # second enrollment
        enrollment_group2 = generate_enrollment_group(
            id=enrollment_group_id2,
            attestation_type=attestation_type,
            allocation_policy="custom",
            webhook_url=WEBHOOK_URL,
            api_version=API_VERSION,
        )
        enrollment_group_2 = client.enrollment_group.create_or_update(
            id=enrollment_group_id2, enrollment_group=enrollment_group2
        )

        assert enrollment_group_2

        # check both enrollments
        enrollment_group_list = client.enrollment_group.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_group_list) == 2
        assert enrollment_group_id in [
            e["enrollmentGroupId"] for e in enrollment_group_list
        ]
        assert enrollment_group_id2 in [
            e["enrollmentGroupId"] for e in enrollment_group_list
        ]

        # delete both enrollments
        client.enrollment_group.delete(id=enrollment_group_id)
        client.enrollment_group.delete(id=enrollment_group_id2)

        # ensure deletion
        enrollment_group_list = client.enrollment_group.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_group_list) == 0

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_enrollment_group_bulk_operations(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)
        eg1_id = self.create_random_name("x509_enroll_grp_")
        attestation_type = "x509"

        if not exists(CERT_FOLDER):
            mkdir(CERT_FOLDER)
        cert_name = self.create_random_name("enroll_cert_")
        create_test_cert(output_dir=CERT_FOLDER, subject=cert_name)  # thumb =
        cert_path = PurePath(CERT_FOLDER, cert_name + "-cert.pem").as_posix()

        eg1 = generate_enrollment_group(
            id=eg1_id,
            certificate_path=cert_path,
            secondary_certificate_path=cert_path,
            provisioning_status="enabled",
            allocation_policy="hashed",
            attestation_type=attestation_type,
            reprovision_policy=REPROVISION_MIGRATE,
        )

        attestation_type = "symmetricKey"
        eg2_id = self.create_random_name("sym_key_enroll_grp_")
        primary_key = generate_key()
        secondary_key = generate_key()
        allocation_policy = "geoLatency"
        reprovision_policy = REPROVISION_MIGRATE
        eg2 = generate_enrollment_group(
            id=eg2_id,
            allocation_policy=allocation_policy,
            reprovision_policy=reprovision_policy,
            attestation_type=attestation_type,
            primary_key=primary_key,
            secondary_key=secondary_key,
        )

        bulk_enrollment_operation = {
            "enrollmentGroups": [eg1, eg2],
            "mode": "create",
        }

        bulk_enrollment_response = client.enrollment_group.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["enrollmentGroups"][0][
            "provisioningStatus"
        ] == "disabled"
        bulk_enrollment_operation["enrollmentGroups"][1][
            "provisioningStatus"
        ] == "disabled"
        bulk_enrollment_operation["mode"] = "update"

        bulk_enrollment_response = client.enrollment_group.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["mode"] = "delete"
        bulk_enrollment_response = client.enrollment_group.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response
