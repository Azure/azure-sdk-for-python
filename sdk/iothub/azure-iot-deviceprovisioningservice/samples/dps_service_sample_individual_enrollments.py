# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: dps_service_sample_individual_enrollments.py
DESCRIPTION:
    This sample demos basic DPS individual enrollment operations
PREREQUISITE:
    In order to create an x509 enrollment, you'll need to have created at least
    one primary certificate. Any valid self-signed certificate should work.
    You can create a self-signed cert with openssl by running the following command:
        `openssl req -nodes -new -x509 -out enrollment-cert.pem --subj="/CN=Provisioning Service SDK Test Cert"`
USAGE: python dps_service_sample_individual_enrollments.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_DPS_CONNECTION_STRING - the connection string to your DPS instance.
    2) AZURE_DPS_ENROLLMENT_CERT_PATH - Path to your certificate
"""

import os


class EnrollmentSamples(object):
    connection_string = os.getenv("AZURE_DPS_CONNECTION_STRING")
    x509_cert_path = os.getenv("AZURE_DPS_ENROLLMENT_CERT_PATH")

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

    def create_symmetric_key_enrollment_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Create an individual enrollment object with "SymmetricKey" attestation mechanism
        enrollment = {
            "registrationId": self.symmetric_enrollment_id,
            "attestation": {
                "type": "symmetricKey",
            },
        }

        dps_service_client.individual_enrollment.create_or_update(
            id=self.symmetric_enrollment_id, enrollment=enrollment
        )

    def create_x590_enrollment_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Load certificate contents from file
        cert_contents = open_certificate(self.x509_cert_path)

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

        dps_service_client.individual_enrollment.create_or_update(
            id=self.x509_enrollment_id, enrollment=enrollment
        )

    def create_tpm_enrollment_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
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

        dps_service_client.individual_enrollment.create_or_update(
            id=self.tpm_enrollment_id, enrollment=enrollment
        )

    def get_enrollment_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Get individual enrollments
        dps_service_client.individual_enrollment.get(id=self.symmetric_enrollment_id)

        dps_service_client.individual_enrollment.get(id=self.x509_enrollment_id)

        dps_service_client.individual_enrollment.get(id=self.tpm_enrollment_id)

    def get_enrollment_attestation_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Get attestations for individual enrollments
        dps_service_client.individual_enrollment.get_attestation_mechanism(
            id=self.x509_enrollment_id
        )

        dps_service_client.individual_enrollment.get_attestation_mechanism(
            id=self.symmetric_enrollment_id
        )

        dps_service_client.individual_enrollment.get_attestation_mechanism(
            id=self.tpm_enrollment_id
        )

    def update_enrollment_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Get individual enrollment
        sym_enrollment = dps_service_client.individual_enrollment.get(
            id=self.symmetric_enrollment_id
        )

        # Parse eTag to ensure update
        eTag = sym_enrollment["etag"]

        # Update individual enrollment properties
        sym_enrollment["provisioningStatus"] = "disabled"
        sym_enrollment["allocationPolicy"] = "geoLatency"

        # Send update
        dps_service_client.individual_enrollment.create_or_update(
            id=self.symmetric_enrollment_id,
            enrollment=sym_enrollment,
            if_match=eTag,
        )

    def bulk_enrollment_operations_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
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
        dps_service_client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_operation
        )

        # Modify bulk operation properties
        bulk_operation["mode"] = "delete"

        # Send delete operation
        dps_service_client.individual_enrollment.run_bulk_operation(
            bulk_operation=bulk_operation
        )

    def delete_enrollments_sample(self):
        # Instantiate a DPS Service Client using a connection string
        from azure.iot.deviceprovisioningservice import ProvisioningServiceClient

        dps_service_client = ProvisioningServiceClient.from_connection_string(
            self.connection_string
        )

        # Delete individual enrollments
        dps_service_client.individual_enrollment.delete(id=self.x509_enrollment_id)
        dps_service_client.individual_enrollment.delete(id=self.symmetric_enrollment_id)
        dps_service_client.individual_enrollment.delete(id=self.tpm_enrollment_id)


def open_certificate(certificate_path: str) -> str:
    from base64 import b64encode

    """
    Helper method to read certificate file contents.
    Opens certificate file (as read binary) from the file system and
    returns the value read.

    Args:
        certificate_path (str): the path the the certificate file.

    Returns:
        certificate (str): returns utf-8 encoded value from certificate file.
    """

    certificate = ""
    if not certificate_path:
        return certificate

    with open(certificate_path, "rb") as cert_file:
        certificate = cert_file.read()
        try:
            certificate = certificate.decode("utf-8")
        except UnicodeError:
            certificate = b64encode(certificate).decode("utf-8")
    # Remove trailing white space from the certificate content
    return certificate.rstrip()


if __name__ == "__main__":
    sample = EnrollmentSamples()
    sample.create_symmetric_key_enrollment_sample()
    sample.create_x590_enrollment_sample()
    sample.create_tpm_enrollment_sample()
    sample.get_enrollment_sample()
    sample.get_enrollment_attestation_sample()
    sample.update_enrollment_sample()
    sample.bulk_enrollment_operations_sample()
    sample.delete_enrollments_sample()
