from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient
from conftest import (
    API_VERSION,
    CUSTOM_ALLOCATION,
    DEVICE_INFO,
    INITIAL_TWIN_PROPERTIES,
    REPROVISION_MIGRATE,
    TEST_DICT,
    TEST_ENDORSEMENT_KEY,
    WEBHOOK_URL,
    ProvisioningServicePreparer,
)
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from utility.common import create_test_cert, generate_enrollment, generate_key


class TestIndividualEnrollments(AzureRecordedTestCase):
    def create_provisioning_service_client(self, endpoint):
        credential = self.get_credential(DeviceProvisioningClient, is_async=True)
        client = DeviceProvisioningClient(endpoint=endpoint, credential=credential)
        return client

    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_enrollment_tpm_lifecycle(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(
            iothub_dps_endpoint
        )

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

        enrollment_response = await client.enrollment.create_or_update(
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
        enrollment_list = await client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        enrollments = [e async for e in enrollment_list]
        assert len(enrollments) == 1
        assert enrollments[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = await client.enrollment.get(id=enrollment_id)

        assert enrollment_response["registrationId"] == enrollment_id

        # check attestation
        attestation_response = (
            await client.enrollment.get_attestation_mechanism(
                id=enrollment_id
            )
        )

        assert attestation_response["tpm"]["endorsementKey"] == TEST_ENDORSEMENT_KEY

        # update enrollment
        enrollment["provisioningStatus"] = "disabled"
        enrollment["optionalDeviceInformation"] = DEVICE_INFO
        enrollment_response = await client.enrollment.create_or_update(
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
        await client.enrollment.delete(id=enrollment_id)

        # ensure deletion
        enrollment_list = await client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len([e async for e in enrollment_list]) == 0

    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_enrollment_x509_lifecycle(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client(
            iothub_dps_endpoint
        )
        enrollment_id = self.create_random_name("x509_enrollment_")
        device_id = self.create_random_name("x509_device_")
        attestation_type = "x509"

        cert_name = self.create_random_name("enroll_cert_")
        cert = create_test_cert(subject=cert_name)
        cert_contents = cert["certificate"]
        thumb = cert["thumbprint"]

        enrollment = generate_enrollment(
            id=enrollment_id,
            device_id=device_id,
            primary_cert=cert_contents,
            secondary_cert=cert_contents,
            provisioning_status="enabled",
            allocation_policy="hashed",
            attestation_type=attestation_type,
            reprovision_policy=REPROVISION_MIGRATE,
        )
        enrollment_response = await client.enrollment.create_or_update(
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
        enrollment_list = await client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        enrollments = [e async for e in enrollment_list]
        assert len(enrollments) == 1
        assert enrollments[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = await client.enrollment.get(id=enrollment_id)

        assert enrollment_response["registrationId"] == enrollment_id

        # check enrollment update
        enrollment["provisioningStatus"] = "disabled"
        enrollment["allocationPolicy"] = "custom"
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = await client.enrollment.create_or_update(
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
        await client.enrollment.delete(id=enrollment_id)

        # ensure deletion
        enrollment_list = await client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len([e async for e in enrollment_list]) == 0

    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_enrollment_symmetrickey_lifecycle(
        self, iothub_dps_endpoint
    ):
        client = self.create_provisioning_service_client(
            iothub_dps_endpoint
        )
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
            initial_twin_properties=INITIAL_TWIN_PROPERTIES,
        )

        enrollment_id2 = self.create_random_name("sym_enrollment2_")

        # Use provided keys
        enrollment_response = await client.enrollment.create_or_update(
            id=enrollment_id, enrollment=enrollment
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["deviceId"] == device_id
        assert enrollment_response["attestation"]["symmetricKey"]
        assert enrollment_response["initialTwin"] == INITIAL_TWIN_PROPERTIES

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
        enrollment_list = await client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        enrollments = [e async for e in enrollment_list]
        assert len(enrollments) == 1
        assert enrollments[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = await client.enrollment.get(id=enrollment_id)
        assert enrollment_response["registrationId"] == enrollment_id

        # check attestation
        attestation_response = (
            await client.enrollment.get_attestation_mechanism(
                id=enrollment_id
            )
        )
        if self.is_live:
            assert attestation_response["symmetricKey"]["primaryKey"] == primary_key
            assert attestation_response["symmetricKey"]["secondaryKey"] == secondary_key

        # check enrollment update
        enrollment["provisioningStatus"] = "disabled"
        enrollment["allocationPolicy"] = "custom"
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = await client.enrollment.create_or_update(
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
        enrollment_2 = await client.enrollment.create_or_update(
            id=enrollment_id2, enrollment=enrollment2
        )

        assert enrollment_2

        # check both enrollments
        enrollment_list = await client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        enrollments = [e["registrationId"] async for e in enrollment_list]
        assert len(enrollments) == 2
        assert enrollment_id in enrollments
        assert enrollment_id2 in enrollments

        # delete both enrollments
        await client.enrollment.delete(id=enrollment_id)
        await client.enrollment.delete(id=enrollment_id2)

        # ensure deletion
        enrollment_list = await client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len([e async for e in enrollment_list]) == 0

    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_individual_enrollment_bulk_operations(
        self, iothub_dps_endpoint
    ):
        client = self.create_provisioning_service_client(
            iothub_dps_endpoint
        )
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

        bulk_enrollment_response = (
            await client.enrollment.run_bulk_operation(
                bulk_operation=bulk_enrollment_operation
            )
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["enrollments"][0]["provisioningStatus"] == "disabled"
        bulk_enrollment_operation["enrollments"][1]["provisioningStatus"] == "disabled"
        bulk_enrollment_operation["mode"] = "update"

        bulk_enrollment_response = (
            await client.enrollment.run_bulk_operation(
                bulk_operation=bulk_enrollment_operation
            )
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["mode"] = "delete"
        bulk_enrollment_response = (
            await client.enrollment.run_bulk_operation(
                bulk_operation=bulk_enrollment_operation
            )
        )
        assert bulk_enrollment_response
