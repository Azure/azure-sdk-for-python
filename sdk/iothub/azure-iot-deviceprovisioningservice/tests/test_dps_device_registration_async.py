import pytest
from azure.iot.deviceprovisioningservice.aio import ProvisioningServiceClient
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from tests.conftest import GLOBAL_PROVISIONING_HOST, ProvisioningServicePreparer
from tests.utility.common import generate_enrollment_group, sign_string


class TestDeviceRegistration(AzureRecordedTestCase):
    def create_provisioning_service_client(self, endpoint):
        credential = self.get_credential(ProvisioningServiceClient, is_async=True)
        client = ProvisioningServiceClient(endpoint=endpoint, credential=credential)
        return client

    async def create_symmetric_device_registration(
        self, endpoint, id_scope, group_id, device_id
    ):
        from azure.iot.device import ProvisioningDeviceClient

        client = self.create_provisioning_service_client(endpoint)

        # get enrollment key
        enrollment_group_attestation = (
            await client.enrollment_group.get_attestation_mechanism(id=group_id)
        )
        primary_key = enrollment_group_attestation["symmetricKey"]["primaryKey"]
        symmetric_key = sign_string(primary_key, device_id)

        sdk = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host=GLOBAL_PROVISIONING_HOST,
            registration_id=device_id,
            id_scope=id_scope,
            symmetric_key=symmetric_key,
        )
        return sdk.register()

    @pytest.mark.asyncio
    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_dps_device_registration_lifecycle(
        self, iothub_dps_endpoint, iothub_dps_idscope
    ):
        client = self.create_provisioning_service_client(iothub_dps_endpoint)
        # create new enrollment group
        enrollment_group_id = self.create_random_name("reg_enroll_grp_")
        device_id = self.create_random_name("device-")
        enrollment_group = generate_enrollment_group(
            id=enrollment_group_id,
            allocation_policy="static",
            attestation_type="symmetricKey",
        )
        enrollment_group = await client.enrollment_group.create_or_update(
            id=enrollment_group_id, enrollment_group=enrollment_group
        )

        # query - should have zero registrations
        device_registrations = await client.device_registration_state.query(
            id=enrollment_group_id
        )
        assert len(device_registrations) == 0

        # create device registration
        if self.is_live:
            registration = await self.create_symmetric_device_registration(
                endpoint=iothub_dps_endpoint,
                id_scope=iothub_dps_idscope,
                group_id=enrollment_group_id,
                device_id=device_id,
            )
            assert device_id == registration.registration_state.device_id

        # get registration
        registration_response = await client.device_registration_state.get(id=device_id)
        assert registration_response["status"] == "assigned"
        registration_id = registration_response["registrationId"]

        # query registration
        registration_query_response: list = (
            await client.device_registration_state.query(id=enrollment_group_id)
        )
        assert len(registration_query_response) == 1
        assert registration_query_response[0]["registrationId"] == registration_id

        # delete registration
        await client.device_registration_state.delete(id=registration_id)

        # confirm delete
        registration_query_response: list = (
            await client.device_registration_state.query(id=enrollment_group_id)
        )
        assert len(registration_query_response) == 0

        # delete enrollment group
        await client.enrollment_group.delete(id=enrollment_group_id)
