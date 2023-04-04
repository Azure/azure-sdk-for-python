# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: dps_service_sample_device_registration_async.py
DESCRIPTION:
    This sample demos basic device registration state operations
PREREQUISITES:
    This sample requires a few prerequisites in order to successfully register a device:
    1) An existing DPS instance that is linked to at least one existing IoT Hub:
        https://learn.microsoft.com/azure/iot-dps/how-to-manage-linked-iot-hubs
    2) In order to register the device, you will need to install the IoT Device SDK:
        `pip install azure-iot-device`
USAGE: python dps_service_sample_device_registration.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_DPS_CONNECTION_STRING - the connection string to your DPS instance.
    2) AZURE_DPS_ID_SCOPE - the ID Scope property of your DPS instance (for registering a device)
"""

import asyncio
import os

# Global Provisioning Endpoint
GLOBAL_PROVISIONING_HOST = "global.azure-devices-provisioning.net"


class DeviceRegistrationSamples(object):
    connection_string = os.getenv("AZURE_DPS_CONNECTION_STRING")
    id_scope = os.getenv("AZURE_DPS_ID_SCOPE")
    enrollment_group_id = "sample_symmetric_enrollment_group"
    device_id = "test-device"

    async def create_enrollment_group_and_register_device_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice.aio import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Create enrollment group object
        enrollment_group = {
            "enrollmentGroupId": self.enrollment_group_id,
            "attestation": {
                "type": "symmetricKey",
            },
        }

        # Create Enrollment on DPS
        await dps_service_client.enrollment_group.create_or_update(
            id=self.enrollment_group_id, enrollment_group=enrollment_group
        )

        # Get Enrollment Attestation with Symmetric Key
        attestation = (
            await dps_service_client.enrollment_group.get_attestation_mechanism(
                id=self.enrollment_group_id
            )
        )

        # Get Primary Key of Enrollment Attestation
        enrollment_group_key = attestation["symmetricKey"]["primaryKey"]

        # Register device using Device SDK
        _register_device_with_symmetric_key(
            enrollment_group_key=enrollment_group_key,
            device_id=self.device_id,
            id_scope=self.id_scope,
        )

    async def query_registration_state_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice.aio import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Query all device registrations for enrollment_group_id
        await dps_service_client.device_registration_state.query(
            id=self.enrollment_group_id
        )

    async def get_device_registration_state_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice.aio import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Get Device Registration State by Device ID
        await dps_service_client.device_registration_state.get(id=self.device_id)

    async def delete_device_registration_state_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice.aio import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Get Device Registration State by Device ID
        registration_response = await dps_service_client.device_registration_state.get(
            id=self.device_id
        )

        # Parse Registration ID
        registration_id = registration_response["registrationId"]

        # Delete Registration
        await dps_service_client.device_registration_state.delete(id=registration_id)

    async def cleanup_enrollment_group(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice.aio import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Delete our created enrollment group
        await dps_service_client.enrollment_group.delete(id=self.enrollment_group_id)


def _register_device_with_symmetric_key(
    id_scope: str, enrollment_group_key: str, device_id: str
):
    """
    Helper method to register a device using the IoT Device SDK
    Args:
        id_scope: DPS ID Scope property
        enrollment_group_key: Enrollment group primary or secondary key
        device_id: Device ID to register as
    """

    # Register device using Provisioning Device Client from Device SDK
    from azure.iot.device import ProvisioningDeviceClient  # type: ignore

    symmetric_key = _compute_device_symmetric_key(
        key=enrollment_group_key, string_to_sign=device_id
    )

    device_sdk = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=GLOBAL_PROVISIONING_HOST,
        registration_id=device_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )

    device_sdk.register()


def _compute_device_symmetric_key(key, string_to_sign, key_is_base64=True):
    """
    Helper method to compute device SAS key
    Args:
        key: Enrollment key used to sign `device_id`
        device_id: ID of the device, signed with `key`
    Returns:
        Signed Device Symmetric key bytes
    """
    import hashlib
    import hmac
    from base64 import b64decode, b64encode

    if key_is_base64:
        key = b64decode(key)
    else:
        if isinstance(key, str):
            key = key.encode("utf-8")
    if isinstance(string_to_sign, str):
        string_to_sign = string_to_sign.encode("utf-8")
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = b64encode(digest)
    return encoded_digest


async def main():
    sample = DeviceRegistrationSamples()
    # This sample must be run before the other samples in order to create the enrollment group
    await sample.create_enrollment_group_and_register_device_async()
    await sample.query_registration_state_sample_async()
    await sample.get_device_registration_state_sample_async()
    await sample.delete_device_registration_state_sample_async()
    await sample.cleanup_enrollment_group()


if __name__ == "__main__":
    asyncio.run(main())
