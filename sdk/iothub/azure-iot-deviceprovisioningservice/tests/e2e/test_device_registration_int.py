from os import getenv

from azure.identity import EnvironmentCredential
from azure.mgmt.iothubprovisioningservices import IotDpsClient

from azure.iot.provisioningservice import ProvisioningServiceClient
from azure.iot.provisioningservice.aio import (
    ProvisioningServiceClient as AsyncProvisioningServiceClient,
)
from azure.iot.provisioningservice.enums import (
    AttestationMechanismType,
    DeviceRegistrationStateStatus,
    EnrollmentGroupAllocationPolicy,
)
from azure.iot.provisioningservice.util.connection_strings import (
    parse_iot_dps_connection_string,
)
from tests.conftest import IOTDPS_PROVISIONING_HOST
from tests.utility.common import (
    create_random_name,
    generate_enrollment_group,
    sign_string,
)

dps_cs = getenv("AZIOTDPSSDK_DPS_CS")
rg = getenv("AZIOTDPSSDK_RG")
subscription = getenv("AZIOTDPSSDK_SUBSCRIPTION")

cs_dict = parse_iot_dps_connection_string(dps_cs)
dps_name = cs_dict["HostName"].split(".")[0]  # env["AZIOTDPSSDK_DPS_NAME"]

client = ProvisioningServiceClient.from_connection_string(dps_cs)
async_client = AsyncProvisioningServiceClient.from_connection_string(dps_cs)
mgmt_client = IotDpsClient(
    credential=EnvironmentCredential(), subscription_id=subscription
)


class TestDeviceRegistrationState(object):
    def create_symmetric_device_registration(self, group_id, device_id):
        from azure.iot.device import ProvisioningDeviceClient

        dps = mgmt_client.iot_dps_resource.get(
            provisioning_service_name=dps_name, resource_group_name=rg
        )
        id_scope = dps.properties.id_scope

        # get enrollment key
        enrollment_group_attestation = (
            client.enrollment_group.get_attestation_mechanism(id=group_id)
        )
        primary_key = enrollment_group_attestation["symmetricKey"]["primaryKey"]
        symmetric_key = sign_string(primary_key, device_id)

        sdk = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host=IOTDPS_PROVISIONING_HOST,
            registration_id=device_id,
            id_scope=id_scope,
            symmetric_key=symmetric_key,
        )
        # sdk.provisioning_payload = payload
        return sdk.register()

    def test_dps_device_registration_lifecycle(self):
        # create new enrollment group
        enrollment_group_id = create_random_name("reg_enroll_grp_")
        device_id = create_random_name("device-")
        enrollment_group = generate_enrollment_group(
            id=enrollment_group_id,
            allocation_policy=EnrollmentGroupAllocationPolicy.STATIC.value,
            attestation_type=AttestationMechanismType.SYMMETRIC_KEY.value,
        )
        enrollment_group = client.enrollment_group.create_or_update(
            id=enrollment_group_id, enrollment_group=enrollment_group
        )

        # query - should have zero registrations
        device_registrations = client.device_registration_state.query(
            id=enrollment_group_id
        )
        assert len(device_registrations) == 0

        # create device registration
        registration = self.create_symmetric_device_registration(
            group_id=enrollment_group_id, device_id=device_id
        )
        assert device_id == registration.registration_state.device_id

        # get registration
        registration_response = client.device_registration_state.get(id=device_id)
        assert (
            registration_response["status"]
            == DeviceRegistrationStateStatus.ASSIGNED.value
        )
        registration_id = registration_response["registrationId"]

        # query registration
        registration_query_response: list = client.device_registration_state.query(
            id=enrollment_group_id
        )
        assert len(registration_query_response) == 1
        assert registration_query_response[0]["registrationId"] == registration_id

        # delete registration
        client.device_registration_state.delete(id=registration_id)

        # confirm delete
        registration_query_response: list = client.device_registration_state.query(
            id=enrollment_group_id
        )
        assert len(registration_query_response) == 0

        # delete enrollment group
        client.enrollment_group.delete(id=enrollment_group_id)

    async def test_dps_device_registration_lifecycle_async(self):
        # create new enrollment group
        enrollment_group_id = create_random_name("reg_enroll_grp_")
        device_id = create_random_name("device-")
        enrollment_group = generate_enrollment_group(
            id=enrollment_group_id,
            allocation_policy=EnrollmentGroupAllocationPolicy.STATIC.value,
            attestation_type=AttestationMechanismType.SYMMETRIC_KEY.value,
        )
        enrollment_group = await async_client.enrollment_group.create_or_update(
            id=enrollment_group_id, enrollment_group=enrollment_group
        )

        # query - should have zero registrations
        device_registrations = await async_client.device_registration_state.query(
            id=enrollment_group_id
        )
        assert len(device_registrations) == 0

        # create device registration
        registration = self.create_symmetric_device_registration(
            group_id=enrollment_group_id, device_id=device_id
        )
        assert device_id == registration.registration_state.device_id

        # get registration
        registration_response = await async_client.device_registration_state.get(
            id=device_id
        )
        assert (
            registration_response["status"]
            == DeviceRegistrationStateStatus.ASSIGNED.value
        )
        registration_id = registration_response["registrationId"]

        # query registration
        registration_query_response: list = (
            await async_client.device_registration_state.query(id=enrollment_group_id)
        )
        assert len(registration_query_response) == 1
        assert registration_query_response[0]["registrationId"] == registration_id

        # delete registration
        await async_client.device_registration_state.delete(id=registration_id)

        # confirm delete
        registration_query_response: list = (
            await async_client.device_registration_state.query(id=enrollment_group_id)
        )
        assert len(registration_query_response) == 0

        # delete enrollment group
        await async_client.enrollment_group.delete(id=enrollment_group_id)
