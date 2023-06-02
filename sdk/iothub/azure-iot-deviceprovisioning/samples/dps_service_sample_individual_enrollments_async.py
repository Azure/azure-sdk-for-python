# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: dps_service_sample_individual_enrollments_async.py
DESCRIPTION:
    This sample demos basic DPS individual enrollment operations
PREREQUISITE:
    In order to create an x509 enrollment, you'll need to have created at least
    one primary certificate. Any valid self-signed certificate should work.
    You can create a self-signed cert with openssl by running the following command:
        `openssl req -nodes -new -x509 -out enrollment-cert.pem --subj="/CN=Provisioning Service SDK Test Cert"`
USAGE: python dps_service_sample_individual_enrollments_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_DPS_CONNECTION_STRING - the connection string to your DPS instance.
    2) AZURE_DPS_ENROLLMENT_CERT_PATH - Path to your certificate
"""

import asyncio
from os import environ


class EnrollmentSamples(object):
    connection_string = environ["AZURE_DPS_CONNECTION_STRING"]
    x509_cert_path = environ["AZURE_DPS_ENROLLMENT_CERT_PATH"]

    symmetric_enrollment_id = "sample_symmetric_enrollment"
    x509_enrollment_id = "sample_x509_enrollment"
    tpm_enrollment_id = "sample_tpm_enrollment"

    # This is a sample TPM endorsement key
    TEST_ENDORSEMENT_KEY = (
        "AToAAQALAAMAsgAgg3GXZ0SEs/gakMyNRqXXJP1S124GUgtk8qHaGzMUaaoABgCAAEMAEAgAAAAAAAEAibym9HQP9vxCGF5dVc1Q"
        "QsAGe021aUGJzNol1/gycBx3jFsTpwmWbISRwnFvflWd0w2Mc44FAAZNaJOAAxwZvG8GvyLlHh6fGKdh+mSBL4iLH2bZ4Ry22cB3"
        "CJVjXmdGoz9Y/j3/NwLndBxQC+baNvzvyVQZ4/A2YL7vzIIj2ik4y+ve9ir7U0GbNdnxskqK1KFIITVVtkTIYyyFTIR0BySjPrRI"
        "Dj7r7Mh5uF9HBppGKQCBoVSVV8dI91lNazmSdpGWyqCkO7iM4VvUMv2HT/ym53aYlUrau+Qq87Tu+uQipWYgRdF11KDfcpMHqqzB"
        "QQ1NpOJVhrsTrhyJzO7KNw=="
    )

    async def create_symmetric_key_enrollment_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Set initial twin properties
        initial_twin = {
            "properties": {
                "desired": {
                    "property": "value"
                }
            }
        }

        # Create an individual enrollment object with "SymmetricKey" attestation mechanism
        enrollment = {
            "registrationId": self.symmetric_enrollment_id,
            "attestation": {
                "type": "symmetricKey",
            },
            "initialTwin": initial_twin
        }

        await dps_service_client.enrollment.create_or_update(
            id=self.symmetric_enrollment_id, enrollment=enrollment
        )

    async def create_x590_enrollment_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Load certificate contents from file
        certificate = open(self.x509_cert_path, "rt", encoding="utf-8")
        cert_contents = certificate.read()

        # Create an individual enrollment object with "x509" attestation mechanism
        enrollment = {
            "registrationId": self.x509_enrollment_id,
            "attestation": {
                "type": "x509",
                "x509": {
                    "clientCertificates": {
                        "primary": {"certificate": f"{cert_contents}"},
                        "secondary": {"certificate": f"{cert_contents}"},
                    }
                },
            },
        }

        await dps_service_client.enrollment.create_or_update(
            id=self.x509_enrollment_id, enrollment=enrollment
        )

    async def create_tpm_enrollment_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Create an individual enrollment object with "TPM" attestation mechanism
        enrollment = {
            "registrationId": self.tpm_enrollment_id,
            "attestation": {
                "type": "tpm",
                "tpm": {"endorsementKey": self.TEST_ENDORSEMENT_KEY},
            },
        }

        await dps_service_client.enrollment.create_or_update(
            id=self.tpm_enrollment_id, enrollment=enrollment
        )

    async def get_enrollment_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Get individual enrollments
        await dps_service_client.enrollment.get(
            id=self.symmetric_enrollment_id
        )

        await dps_service_client.enrollment.get(id=self.x509_enrollment_id)

        await dps_service_client.enrollment.get(id=self.tpm_enrollment_id)

    async def get_enrollment_attestation_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Get attestations for individual enrollments
        await dps_service_client.enrollment.get_attestation_mechanism(
            id=self.x509_enrollment_id
        )

        await dps_service_client.enrollment.get_attestation_mechanism(
            id=self.symmetric_enrollment_id
        )

        await dps_service_client.enrollment.get_attestation_mechanism(
            id=self.tpm_enrollment_id
        )

    async def update_enrollment_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Get individual enrollment
        sym_enrollment = await dps_service_client.enrollment.get(
            id=self.symmetric_enrollment_id
        )

        # Parse eTag to ensure update
        eTag = sym_enrollment["etag"]

        # Update individual enrollment properties
        sym_enrollment["provisioningStatus"] = "disabled"
        sym_enrollment["allocationPolicy"] = "geoLatency"

        # Send update
        await dps_service_client.enrollment.create_or_update(
            id=self.symmetric_enrollment_id,
            enrollment=sym_enrollment,
            if_match=eTag,
        )

    async def update_enrollment_reprovisioning_policy_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Get individual enrollment
        sym_enrollment = await dps_service_client.enrollment.get(
            id=self.symmetric_enrollment_id
        )

        # Parse eTag to ensure update
        eTag = sym_enrollment["etag"]

        # Create a new reprovisioning policy
        sym_enrollment['reprovisionPolicy'] = {
            # update device's hub assignment
            "updateHubAssignment": True,
            # don't migrate device data to a new hub
            "migrateDeviceData": False,
        }

        # Update enrollment with custom reprovisioning policy
        await dps_service_client.enrollment.create_or_update(
            id=self.symmetric_enrollment_id,
            enrollment=sym_enrollment,
            if_match=eTag,
        )

    async def bulk_enrollment_operations_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Create a few more individual enrollments in bulk
        enrollment_id = "bulk_enrollment_1"
        enrollment2_id = "bulk_enrollment_2"
        enrollments = [
            # Create first enrollment
            {
                "registrationId": enrollment_id,
                "attestation": {
                    "type": "symmetricKey",
                },
            },
            {
                "registrationId": enrollment2_id,
                "attestation": {
                    "type": "symmetricKey",
                },
            },
        ]

        # Create a bulk operation object
        bulk_operation = {"mode": "create", "enrollments": enrollments}

        # Send create operation
        await dps_service_client.enrollment.run_bulk_operation(
            bulk_operation=bulk_operation
        )

        # Modify bulk operation properties
        bulk_operation["mode"] = "delete"

        # Send delete operation
        await dps_service_client.enrollment.run_bulk_operation(
            bulk_operation=bulk_operation
        )

    async def delete_enrollments_sample_async(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

        dps_service_client = DeviceProvisioningClient.from_connection_string(
            self.connection_string
        )

        # Delete individual enrollments
        await dps_service_client.enrollment.delete(
            id=self.x509_enrollment_id
        )
        await dps_service_client.enrollment.delete(
            id=self.symmetric_enrollment_id
        )
        await dps_service_client.enrollment.delete(id=self.tpm_enrollment_id)


async def main():
    sample = EnrollmentSamples()
    await sample.create_symmetric_key_enrollment_sample_async()
    await sample.create_x590_enrollment_sample_async()
    await sample.create_tpm_enrollment_sample_async()
    await sample.get_enrollment_sample_async()
    await sample.get_enrollment_attestation_sample_async()
    await sample.update_enrollment_sample_async()
    await sample.update_enrollment_reprovisioning_policy_sample()
    await sample.bulk_enrollment_operations_sample_async()
    await sample.delete_enrollments_sample_async()


if __name__ == "__main__":
    asyncio.run(main())
