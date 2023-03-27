import asyncio
from os import getenv, mkdir
from os.path import exists
from pathlib import PurePath
from shutil import rmtree

import pytest

from azure.iot.provisioningservice import ProvisioningServiceClient
from azure.iot.provisioningservice.aio import (
    ProvisioningServiceClient as AsyncProvisioningServiceClient,
)
from azure.iot.provisioningservice.enums import (
    AttestationMechanismType,
    BulkEnrollmentOperationMode,
    IndividualEnrollmentAllocationPolicy,
    IndividualEnrollmentProvisioningStatus,
)
from tests.conftest import (
    API_VERSION,
    CERT_FOLDER,
    CUSTOM_ALLOCATION,
    DEVICE_INFO,
    REPROVISION_MIGRATE,
    TEST_DICT,
    TEST_ENDORSEMENT_KEY,
    WEBHOOK_URL,
)
from tests.utility.common import (
    create_random_name,
    create_test_cert,
    generate_enrollment,
    generate_key,
)

cs = getenv("AZIOTDPSSDK_DPS_CS")
client = ProvisioningServiceClient.from_connection_string(cs)
async_client = AsyncProvisioningServiceClient.from_connection_string(cs)


# fix for pytest-asyncio closing event loops after first async test
@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestIndividualEnrollments(object):
    def test_dps_enrollment_tpm_lifecycle(self):
        attestation_type = AttestationMechanismType.TPM.value
        enrollment_id = create_random_name("ind_enroll_tpm_")
        device_id = create_random_name("device_")
        enrollment = generate_enrollment(
            id=enrollment_id,
            attestation_type=attestation_type,
            endorsement_key=TEST_ENDORSEMENT_KEY,
            provisioning_status=IndividualEnrollmentProvisioningStatus.ENABLED.value,
            device_id=device_id,
            allocation_policy=IndividualEnrollmentAllocationPolicy.STATIC.value,
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
        assert (
            enrollment_response["allocationPolicy"]
            == IndividualEnrollmentAllocationPolicy.STATIC.value
        )
        assert enrollment_response["deviceId"] == device_id
        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.ENABLED.value
        )

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
        enrollment[
            "provisioningStatus"
        ] = IndividualEnrollmentProvisioningStatus.DISABLED.value
        enrollment["optionalDeviceInformation"] = DEVICE_INFO
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.DISABLED.value
        )

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

    async def test_dps_enrollment_tpm_lifecycle_async(self):
        attestation_type = AttestationMechanismType.TPM.value
        enrollment_id = create_random_name("ind_enroll_tpm_")
        device_id = create_random_name("device_")
        enrollment = generate_enrollment(
            id=enrollment_id,
            attestation_type=attestation_type,
            endorsement_key=TEST_ENDORSEMENT_KEY,
            provisioning_status=IndividualEnrollmentProvisioningStatus.ENABLED.value,
            device_id=device_id,
            allocation_policy=IndividualEnrollmentAllocationPolicy.STATIC.value,
        )

        enrollment_response = await async_client.individual_enrollment.create_or_update(
            id=enrollment_id, enrollment=enrollment
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["attestation"]["tpm"]
        assert (
            enrollment_response["attestation"]["tpm"]["endorsementKey"]
            == TEST_ENDORSEMENT_KEY
        )
        assert (
            enrollment_response["allocationPolicy"]
            == IndividualEnrollmentAllocationPolicy.STATIC.value
        )
        assert enrollment_response["deviceId"] == device_id
        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.ENABLED.value
        )

        # check for enrollment in query response
        enrollment_list = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 1
        assert enrollment_list[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = await async_client.individual_enrollment.get(
            id=enrollment_id
        )

        assert enrollment_response["registrationId"] == enrollment_id

        # check attestation
        attestation_response = (
            await async_client.individual_enrollment.get_attestation_mechanism(
                id=enrollment_id
            )
        )

        assert attestation_response["tpm"]["endorsementKey"] == TEST_ENDORSEMENT_KEY

        # update enrollment
        enrollment[
            "provisioningStatus"
        ] = IndividualEnrollmentProvisioningStatus.DISABLED.value
        enrollment["optionalDeviceInformation"] = DEVICE_INFO
        enrollment_response = await async_client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.DISABLED.value
        )

        assert (
            enrollment_response["optionalDeviceInformation"]["additionalProperties"]
            == TEST_DICT
        )

        # delete enrollment
        await async_client.individual_enrollment.delete(id=enrollment_id)

        # ensure deletion
        enrollment_list = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 0

    def test_dps_enrollment_x509_lifecycle(self):
        enrollment_id = create_random_name("x509_enrollment_")
        device_id = create_random_name("x509_device_")
        attestation_type = AttestationMechanismType.X509.value

        if not exists(CERT_FOLDER):
            mkdir(CERT_FOLDER)
        cert_name = create_random_name("enroll_cert_")
        thumb = create_test_cert(output_dir=CERT_FOLDER, subject=cert_name)
        cert_path = PurePath(CERT_FOLDER, cert_name + "-cert.pem").as_posix()

        enrollment = generate_enrollment(
            id=enrollment_id,
            device_id=device_id,
            certificate_path=cert_path,
            secondary_certificate_path=cert_path,
            provisioning_status=IndividualEnrollmentProvisioningStatus.ENABLED.value,
            allocation_policy=IndividualEnrollmentAllocationPolicy.HASHED.value,
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
        assert (
            enrollment_response["attestation"]["type"]
            == AttestationMechanismType.X509.value
        )
        assert (
            enrollment_response["attestation"]["x509"]["clientCertificates"]["primary"][
                "info"
            ]["subjectName"]
            == f"CN={cert_name}"
        )
        assert (
            enrollment_response["attestation"]["x509"]["clientCertificates"]["primary"][
                "info"
            ]["sha256Thumbprint"]
            == thumb
        )

        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.ENABLED.value
        )
        assert (
            enrollment_response["allocationPolicy"]
            == IndividualEnrollmentAllocationPolicy.HASHED.value
        )
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
        enrollment[
            "provisioningStatus"
        ] = IndividualEnrollmentProvisioningStatus.DISABLED.value
        enrollment[
            "allocationPolicy"
        ] = IndividualEnrollmentAllocationPolicy.CUSTOM.value
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.DISABLED.value
        )
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

    async def test_dps_enrollment_x509_lifecycle_async(self):
        enrollment_id = create_random_name("x509_enrollment_")
        device_id = create_random_name("x509_device_")
        attestation_type = AttestationMechanismType.X509.value

        if not exists(CERT_FOLDER):
            mkdir(CERT_FOLDER)
        cert_name = create_random_name("enroll_cert_")
        thumb = create_test_cert(output_dir=CERT_FOLDER, subject=cert_name)
        cert_path = PurePath(CERT_FOLDER, cert_name + "-cert.pem").as_posix()

        enrollment = generate_enrollment(
            id=enrollment_id,
            device_id=device_id,
            certificate_path=cert_path,
            secondary_certificate_path=cert_path,
            provisioning_status=IndividualEnrollmentProvisioningStatus.ENABLED.value,
            allocation_policy=IndividualEnrollmentAllocationPolicy.HASHED.value,
            attestation_type=attestation_type,
            reprovision_policy=REPROVISION_MIGRATE,
        )
        enrollment_response = await async_client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
        )

        assert enrollment_response
        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["deviceId"] == device_id

        # check auth
        assert enrollment_response["attestation"]["x509"]
        assert (
            enrollment_response["attestation"]["type"]
            == AttestationMechanismType.X509.value
        )
        assert (
            enrollment_response["attestation"]["x509"]["clientCertificates"]["primary"][
                "info"
            ]["subjectName"]
            == f"CN={cert_name}"
        )
        assert (
            enrollment_response["attestation"]["x509"]["clientCertificates"]["primary"][
                "info"
            ]["sha256Thumbprint"]
            == thumb
        )

        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.ENABLED.value
        )
        assert (
            enrollment_response["allocationPolicy"]
            == IndividualEnrollmentAllocationPolicy.HASHED.value
        )
        assert enrollment_response["reprovisionPolicy"]["migrateDeviceData"]
        assert enrollment_response["reprovisionPolicy"]["updateHubAssignment"]

        # check for enrollment in query response
        enrollment_list = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 1
        assert enrollment_list[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = await async_client.individual_enrollment.get(
            id=enrollment_id
        )

        assert enrollment_response["registrationId"] == enrollment_id

        # check enrollment update
        enrollment[
            "provisioningStatus"
        ] = IndividualEnrollmentProvisioningStatus.DISABLED.value
        enrollment[
            "allocationPolicy"
        ] = IndividualEnrollmentAllocationPolicy.CUSTOM.value
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = await async_client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.DISABLED.value
        )
        assert (
            enrollment_response["customAllocationDefinition"]["webhookUrl"]
            == WEBHOOK_URL
        )
        assert (
            enrollment_response["customAllocationDefinition"]["apiVersion"]
            == API_VERSION
        )

        # delete enrollment
        await async_client.individual_enrollment.delete(id=enrollment_id)

        # ensure deletion
        enrollment_list = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 0

        # delete certificates
        rmtree(CERT_FOLDER, ignore_errors=True)

    def test_dps_enrollment_symmetrickey_lifecycle(self):
        attestation_type = AttestationMechanismType.SYMMETRIC_KEY.value
        enrollment_id = create_random_name("sym_key_enrollment_")
        primary_key = generate_key()
        secondary_key = generate_key()
        device_id = create_random_name("sym_key_device_")
        allocation_policy = IndividualEnrollmentAllocationPolicy.GEO_LATENCY.value
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

        enrollment_id2 = create_random_name("sym_key_enrollment_")

        # Use provided keys
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id, enrollment=enrollment
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["deviceId"] == device_id
        assert enrollment_response["attestation"]["symmetricKey"]

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

        assert attestation_response["symmetricKey"]["primaryKey"] == primary_key
        assert attestation_response["symmetricKey"]["secondaryKey"] == secondary_key

        # check enrollment update
        enrollment[
            "provisioningStatus"
        ] = IndividualEnrollmentProvisioningStatus.DISABLED.value
        enrollment[
            "allocationPolicy"
        ] = IndividualEnrollmentAllocationPolicy.CUSTOM.value
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.DISABLED.value
        )

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
            allocation_policy=IndividualEnrollmentAllocationPolicy.CUSTOM.value,
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

    async def test_dps_enrollment_symmetrickey_lifecycle_async(self):
        attestation_type = AttestationMechanismType.SYMMETRIC_KEY.value
        enrollment_id = create_random_name("sym_key_enrollment_")
        primary_key = generate_key()
        secondary_key = generate_key()
        device_id = create_random_name("sym_key_device_")
        allocation_policy = IndividualEnrollmentAllocationPolicy.GEO_LATENCY.value
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

        enrollment_id2 = create_random_name("sym_key_enrollment_")

        # Use provided keys
        enrollment_response = await async_client.individual_enrollment.create_or_update(
            id=enrollment_id, enrollment=enrollment
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert enrollment_response["deviceId"] == device_id
        assert enrollment_response["attestation"]["symmetricKey"]

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
        enrollment_list = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 1
        assert enrollment_list[0]["registrationId"] == enrollment_id

        # check enrollment get
        enrollment_response = await async_client.individual_enrollment.get(
            id=enrollment_id
        )
        assert enrollment_response["registrationId"] == enrollment_id

        # check attestation
        attestation_response = (
            await async_client.individual_enrollment.get_attestation_mechanism(
                id=enrollment_id
            )
        )

        assert attestation_response["symmetricKey"]["primaryKey"] == primary_key
        assert attestation_response["symmetricKey"]["secondaryKey"] == secondary_key

        # check enrollment update
        enrollment[
            "provisioningStatus"
        ] = IndividualEnrollmentProvisioningStatus.DISABLED.value
        enrollment[
            "allocationPolicy"
        ] = IndividualEnrollmentAllocationPolicy.CUSTOM.value
        enrollment["customAllocationDefinition"] = CUSTOM_ALLOCATION
        enrollment_response = await async_client.individual_enrollment.create_or_update(
            id=enrollment_id,
            enrollment=enrollment,
            if_match=enrollment_response["etag"],
        )

        assert enrollment_response["registrationId"] == enrollment_id
        assert (
            enrollment_response["provisioningStatus"]
            == IndividualEnrollmentProvisioningStatus.DISABLED.value
        )

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
            allocation_policy=IndividualEnrollmentAllocationPolicy.CUSTOM.value,
            webhook_url=WEBHOOK_URL,
            api_version=API_VERSION,
        )
        enrollment_2 = await async_client.individual_enrollment.create_or_update(
            id=enrollment_id2, enrollment=enrollment2
        )

        assert enrollment_2

        # check both enrollments
        enrollment_list = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 2
        assert enrollment_id in [e["registrationId"] for e in enrollment_list]
        assert enrollment_id2 in [e["registrationId"] for e in enrollment_list]

        # delete both enrollments
        await async_client.individual_enrollment.delete(id=enrollment_id)
        await async_client.individual_enrollment.delete(id=enrollment_id2)

        # ensure deletion
        enrollment_list = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert len(enrollment_list) == 0

    def test_individual_enrollment_bulk_operations(self):
        attestation_type = AttestationMechanismType.TPM.value
        enrollment_id = create_random_name("ind_enroll_tpm_")
        device_id = create_random_name("device_")
        enrollment = generate_enrollment(
            id=enrollment_id,
            attestation_type=attestation_type,
            endorsement_key=TEST_ENDORSEMENT_KEY,
            provisioning_status=IndividualEnrollmentProvisioningStatus.ENABLED.value,
            device_id=device_id,
            allocation_policy=IndividualEnrollmentAllocationPolicy.STATIC.value,
        )

        attestation_type = AttestationMechanismType.SYMMETRIC_KEY.value
        enrollment_id2 = create_random_name("sym_key_enrollment_")
        primary_key = generate_key()
        secondary_key = generate_key()
        device_id = create_random_name("sym_key_device_")
        allocation_policy = IndividualEnrollmentAllocationPolicy.GEO_LATENCY.value
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
            "mode": BulkEnrollmentOperationMode.CREATE.value,
        }

        bulk_enrollment_response = client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["enrollments"][0][
            "provisioningStatus"
        ] == IndividualEnrollmentProvisioningStatus.DISABLED.value
        bulk_enrollment_operation["enrollments"][1][
            "provisioningStatus"
        ] == IndividualEnrollmentProvisioningStatus.DISABLED.value
        bulk_enrollment_operation["mode"] = BulkEnrollmentOperationMode.UPDATE.value

        bulk_enrollment_response = client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["mode"] = BulkEnrollmentOperationMode.DELETE.value
        bulk_enrollment_response = client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_enrollment_operation
        )
        assert bulk_enrollment_response

    async def test_individual_enrollment_bulk_operations_async(self):
        attestation_type = AttestationMechanismType.TPM.value
        enrollment_id = create_random_name("ind_enroll_tpm_")
        device_id = create_random_name("device_")
        enrollment = generate_enrollment(
            id=enrollment_id,
            attestation_type=attestation_type,
            endorsement_key=TEST_ENDORSEMENT_KEY,
            provisioning_status=IndividualEnrollmentProvisioningStatus.ENABLED.value,
            device_id=device_id,
            allocation_policy=IndividualEnrollmentAllocationPolicy.STATIC.value,
        )

        attestation_type = AttestationMechanismType.SYMMETRIC_KEY.value
        enrollment_id2 = create_random_name("sym_key_enrollment_")
        primary_key = generate_key()
        secondary_key = generate_key()
        device_id = create_random_name("sym_key_device_")
        allocation_policy = IndividualEnrollmentAllocationPolicy.GEO_LATENCY.value
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
            "mode": BulkEnrollmentOperationMode.CREATE.value,
        }

        bulk_enrollment_response = (
            await async_client.individual_enrollment.run_bulk_operation(
                bulk_operation=bulk_enrollment_operation
            )
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["enrollments"][0][
            "provisioningStatus"
        ] == IndividualEnrollmentProvisioningStatus.DISABLED.value
        bulk_enrollment_operation["enrollments"][1][
            "provisioningStatus"
        ] == IndividualEnrollmentProvisioningStatus.DISABLED.value
        bulk_enrollment_operation["mode"] = BulkEnrollmentOperationMode.UPDATE.value

        bulk_enrollment_response = (
            await async_client.individual_enrollment.run_bulk_operation(
                bulk_operation=bulk_enrollment_operation
            )
        )
        assert bulk_enrollment_response

        bulk_enrollment_operation["mode"] = BulkEnrollmentOperationMode.DELETE.value
        bulk_enrollment_response = (
            await async_client.individual_enrollment.run_bulk_operation(
                bulk_operation=bulk_enrollment_operation
            )
        )
        assert bulk_enrollment_response
