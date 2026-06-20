# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
End-to-end scenario test for Credential Management Service (CMS) flow.

Ports the .NET DeviceRegistryCredentialsAndPoliciesFlowTest to Python.

PREREQUISITES
=============
Create RG, UAMI, ADR Namespace, IoT Hub, and DPS BEFORE running in Record/Live mode.
Use the helper scripts from the .NET SDK repo:
  Setup:    .\\tests\\Scripts\\Setup-CmsTestPrerequisites.ps1 -Suffix both -Iteration <N> -NoPrompt
  Teardown: .\\tests\\Scripts\\Teardown-CmsTestPrerequisites.ps1 -Suffix both -Iteration <N> -Force

The scripts create these resources for each suffix (sync/async):
  Resource Group:    adr-sdk-test-cms-{suffix}{iteration}
  Managed Identity:  cms-test-uami-{suffix}{iteration}
  ADR Namespace:     cms-test-namespace-{suffix}{iteration}
  IoT Hub (GEN2):    adr-sdk-cms-test-hub-{suffix}{iteration}
  DPS:               adr-sdk-cms-test-dps-{suffix}{iteration}

The test itself creates and deletes Credential, Policy, and Device resources during execution.

Run:
  $env:AZURE_TEST_RUN_LIVE = "true"
  pytest tests/test_device_registry_mgmt_credentials_and_policies_flow.py -v -s
"""
import time
import uuid

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.mgmt.deviceregistry import DeviceRegistryMgmtClient
from azure.mgmt.deviceregistry.models import (
    ActivateBringYourOwnRootRequest,
    CertificateAuthorityConfiguration,
    CertificateConfiguration,
    Credential,
    DeviceCredentialsRevokeRequest,
    LeafCertificateConfiguration,
    MessagingEndpoints,
    NamespaceDevice,
    NamespaceDeviceProperties,
    Policy,
    PolicyProperties,
    PolicyUpdate,
    PolicyUpdateProperties,
)

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

# ---------------------------------------------------------------------------
# Constants — must match what Setup-CmsTestPrerequisites.ps1 created.
# Change ITERATION here *and* in the setup script when you need fresh resources.
# ---------------------------------------------------------------------------
ITERATION = "1"
LOCATION = "eastus2euap"
SUFFIX = f"sync{ITERATION}"

RESOURCE_GROUP_NAME = f"adr-sdk-test-cms-{SUFFIX}"
NAMESPACE_NAME = f"cms-test-namespace-{SUFFIX}"
POLICY_NAME = f"cms-test-policy-{SUFFIX}"
BYOR_POLICY_NAME = f"cms-test-byor-policy-{SUFFIX}"
DEVICE_NAME = f"cms-test-device-{SUFFIX}"

# How long (seconds) to sleep between BYOR policy deletion and credential deletion
# in live/record mode to avoid RP 409 race condition.
PROPAGATION_DELAY_SECONDS = 10


def _delay_if_live(test_instance, seconds, reason=""):
    """Sleep only in Live or Record mode (not Playback)."""
    # In playback mode the test proxy replays instantly; no delay needed.
    # AzureMgmtRecordedTestCase does not expose mode directly, but
    # is_live is True for both Live and Record modes.
    if getattr(test_instance, "is_live", False):
        if reason:
            print(f"  [delay] {reason} ({seconds}s)")
        time.sleep(seconds)


@pytest.mark.live_test_only
class TestDeviceRegistryMgmtCredentialsAndPoliciesFlow(AzureMgmtRecordedTestCase):
    """
    Single end-to-end test covering:
      1. Namespace GET (prerequisite)
      2. Credential GET-or-CREATE
      3. Policy cleanup → CREATE (ECC, 90-day) → LIST → verify
      4. Credential Synchronize
      5. Policy UPDATE (PATCH validity 90→60)
      6. Device CREATE → GET → LIST
      7. Device Revoke (negative test — known RP LRO bug)
      8. Device DELETE
      9. Policy RevokeIssuer
     10. Policy DELETE (standard)
     11. BYOR Policy CREATE → verify PendingActivation/CSR
     12. BYOR ActivateBringYourOwnRoot with invalid cert (negative test)
     13. BYOR Policy UPDATE (validity 90→45)
     14. BYOR Policy DELETE
     15. Credential DELETE
    """

    def setup_method(self, method):
        self.client = self.create_mgmt_client(DeviceRegistryMgmtClient)

    @recorded_by_proxy
    def test_credential_and_policy_flow(self):
        # ==================================================================
        # Step 1: Get namespace (prerequisite — created via setup script)
        # ==================================================================
        namespace = self.client.namespaces.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
        )
        assert namespace is not None
        assert namespace.location.replace(" ", "").lower() == LOCATION.lower()
        assert namespace.name == NAMESPACE_NAME

        # ==================================================================
        # Step 2: Credential flow — GET or CREATE
        # ==================================================================
        try:
            credential = self.client.credentials.get(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
            )
        except (ResourceNotFoundError, HttpResponseError):
            credential = self.client.credentials.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
                resource=Credential(location=LOCATION),
            ).result()

        assert credential is not None
        assert credential.location.replace(" ", "").lower() == LOCATION.lower()

        # ==================================================================
        # Step 3: Delete all existing policies, then create a fresh one
        # ==================================================================
        existing_policies = list(
            self.client.policies.list_by_resource_group(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
            )
        )
        for p in existing_policies:
            self.client.policies.begin_delete(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
                policy_name=p.name,
            ).result()

        # Create policy with ECC key type and 90-day leaf certificate validity
        policy = self.client.policies.begin_create_or_update(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=POLICY_NAME,
            resource=Policy(
                properties=PolicyProperties(
                    certificate=CertificateConfiguration(
                        certificate_authority_configuration=CertificateAuthorityConfiguration(
                            key_type="ECC",
                        ),
                        leaf_certificate_configuration=LeafCertificateConfiguration(
                            validity_period_in_days=90,
                        ),
                    ),
                ),
            ),
        ).result()

        assert policy is not None
        assert policy.name == POLICY_NAME
        assert policy.properties is not None
        assert policy.properties.certificate is not None
        cert_config = policy.properties.certificate
        assert cert_config.certificate_authority_configuration.key_type == "ECC"
        assert cert_config.leaf_certificate_configuration.validity_period_in_days == 90
        assert policy.properties.provisioning_state == "Succeeded"

        # List policies — verify created policy appears
        all_policies = list(
            self.client.policies.list_by_resource_group(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
            )
        )
        assert any(p.name == POLICY_NAME for p in all_policies)

        # ==================================================================
        # Step 4: Synchronize credentials with IoT Hub
        # ==================================================================
        self.client.credentials.begin_synchronize(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
        ).result()

        # ==================================================================
        # Step 5: Policy UPDATE (PATCH) — change validity from 90 → 60 days
        #
        # IMPORTANT: Use raw dict to avoid sending immutable
        # certificateAuthorityConfiguration fields (keyType, bringYourOwnRoot)
        # which the 2026-03-01-preview API rejects on PATCH.
        # The Python SDK's CertificateConfiguration requires both fields,
        # unlike the .NET SDK which has a custom int-only constructor.
        # ==================================================================
        # GET fresh policy after sync
        policy = self.client.policies.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=POLICY_NAME,
        )
        assert policy.properties.certificate.leaf_certificate_configuration.validity_period_in_days == 90

        # PATCH with raw dict — only mutable fields
        self.client.policies.begin_update(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=POLICY_NAME,
            properties={
                "properties": {
                    "certificate": {
                        "leafCertificateConfiguration": {
                            "validityPeriodInDays": 60,
                        }
                    }
                }
            },
        ).result()

        # Verify update
        policy = self.client.policies.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=POLICY_NAME,
        )
        assert policy.properties.certificate.leaf_certificate_configuration.validity_period_in_days == 60

        # ==================================================================
        # Step 6: Device CRUD
        # ==================================================================
        device = self.client.namespace_devices.begin_create_or_replace(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            device_name=DEVICE_NAME,
            resource=NamespaceDevice(
                location=LOCATION,
                properties=NamespaceDeviceProperties(
                    manufacturer="Contoso",
                    model="CMS-TestModel-5000",
                    operating_system="Linux",
                    operating_system_version="22.04",
                    endpoints=MessagingEndpoints(),
                ),
            ),
        ).result()

        assert device is not None
        assert device.name == DEVICE_NAME
        assert device.properties is not None
        # UUID is assigned by the RP
        assert device.properties.uuid is not None
        try:
            uuid.UUID(device.properties.uuid)
        except ValueError:
            pytest.fail(f"Device UUID is not a valid UUID: {device.properties.uuid}")
        assert device.properties.manufacturer == "Contoso"
        assert device.properties.model == "CMS-TestModel-5000"

        # GET device and verify full properties
        device = self.client.namespace_devices.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            device_name=DEVICE_NAME,
        )
        assert device.properties.manufacturer == "Contoso"
        assert device.properties.model == "CMS-TestModel-5000"
        assert device.properties.operating_system == "Linux"
        assert device.properties.operating_system_version == "22.04"

        # List devices — verify created device appears
        all_devices = list(
            self.client.namespace_devices.list_by_resource_group(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
            )
        )
        assert any(d.name == DEVICE_NAME for d in all_devices)

        # ==================================================================
        # Step 7: Device Revoke (negative test)
        #
        # Known RP bug: RP returns HTTP 200 without LRO headers and missing
        # required "result" property. SDK LRO polling fails.
        # ARM-created devices have no CMS policy, so revoke also fails
        # from a business-logic perspective.
        # ==================================================================
        with pytest.raises(Exception):
            self.client.namespace_devices.begin_revoke(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
                device_name=DEVICE_NAME,
                body=DeviceCredentialsRevokeRequest(disable=False),
            ).result()

        # Verify device state unchanged after failed revoke
        device = self.client.namespace_devices.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            device_name=DEVICE_NAME,
        )
        assert device.properties is not None
        assert device.name == DEVICE_NAME

        # ==================================================================
        # Step 8: Delete device
        # ==================================================================
        # Known RP bug: DELETE returns HTTP 200 instead of 202/204,
        # which the SDK rejects. Swallow that specific error.
        # ==================================================================
        try:
            self.client.namespace_devices.begin_delete(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
                device_name=DEVICE_NAME,
            ).result()
        except HttpResponseError as e:
            if "OK" not in str(e):
                raise
        # ==================================================================
        # Step 9: RevokeIssuer on standard (non-BYOR) policy
        # ==================================================================
        self.client.policies.begin_revoke_issuer(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=POLICY_NAME,
        ).result()

        # Verify policy still healthy after revoke
        policy = self.client.policies.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=POLICY_NAME,
        )
        assert policy.properties.provisioning_state == "Succeeded"

        # ==================================================================
        # Step 10: Delete standard policy
        # ==================================================================
        self.client.policies.begin_delete(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=POLICY_NAME,
        ).result()

        # ==================================================================
        # Step 11: BYOR (Bring Your Own Root) Policy — CREATE
        # ==================================================================
        from azure.mgmt.deviceregistry.models import BringYourOwnRoot

        byor_policy = self.client.policies.begin_create_or_update(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=BYOR_POLICY_NAME,
            resource=Policy(
                properties=PolicyProperties(
                    certificate=CertificateConfiguration(
                        certificate_authority_configuration=CertificateAuthorityConfiguration(
                            key_type="ECC",
                            bring_your_own_root=BringYourOwnRoot(enabled=True),
                        ),
                        leaf_certificate_configuration=LeafCertificateConfiguration(
                            validity_period_in_days=90,
                        ),
                    ),
                ),
            ),
        ).result()

        assert byor_policy is not None
        assert byor_policy.name == BYOR_POLICY_NAME
        byor_ca = byor_policy.properties.certificate.certificate_authority_configuration
        assert byor_ca.bring_your_own_root is not None
        assert byor_ca.bring_your_own_root.enabled is True

        # Verify PendingActivation status and CSR
        assert byor_ca.bring_your_own_root.status == "PendingActivation"
        assert byor_ca.bring_your_own_root.certificate_signing_request is not None
        assert "-----BEGIN CERTIFICATE REQUEST-----" in byor_ca.bring_your_own_root.certificate_signing_request

        # ==================================================================
        # Step 12: ActivateBringYourOwnRoot with INVALID cert (negative test)
        #
        # Known RP bug: same LRO issue as Device.Revoke — RP returns HTTP 200
        # instead of proper 4xx. Even if the RP were fixed, the fake cert
        # would still fail validation.
        # ==================================================================
        fake_cert_chain = (
            "-----BEGIN CERTIFICATE-----\n"
            "MIIBkTCB+wIJALRiMLAhFake0DQYJKoZIhvcNAQELBQAwDzENMAsGA1UEAwwEdGVz\n"
            "dDAeFw0yNDAzMjAxMjAwMDBaFw0yNTAzMjAxMjAwMDBaMA8xDTALBgNVBAMMBHRl\n"
            "-----END CERTIFICATE-----"
        )
        with pytest.raises(Exception):
            self.client.policies.begin_activate_bring_your_own_root(
                resource_group_name=RESOURCE_GROUP_NAME,
                namespace_name=NAMESPACE_NAME,
                policy_name=BYOR_POLICY_NAME,
                body=ActivateBringYourOwnRootRequest(certificate_chain=fake_cert_chain),
            ).result()

        # Verify BYOR state unchanged after failed activation
        byor_policy = self.client.policies.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=BYOR_POLICY_NAME,
        )
        byor_ca = byor_policy.properties.certificate.certificate_authority_configuration
        assert byor_ca.bring_your_own_root.enabled is True
        assert byor_ca.bring_your_own_root.status == "PendingActivation"
        assert byor_ca.bring_your_own_root.certificate_signing_request is not None

        # ==================================================================
        # Step 13: BYOR Policy UPDATE — change validity from 90 → 45 days
        #    (raw dict PATCH, same approach as standard policy update)
        # ==================================================================
        self.client.policies.begin_update(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=BYOR_POLICY_NAME,
            properties={
                "properties": {
                    "certificate": {
                        "leafCertificateConfiguration": {
                            "validityPeriodInDays": 45,
                        }
                    }
                }
            },
        ).result()

        byor_policy = self.client.policies.get(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=BYOR_POLICY_NAME,
        )
        assert byor_policy.properties.certificate.leaf_certificate_configuration.validity_period_in_days == 45
        # BYOR should still be enabled after update
        assert (
            byor_policy.properties.certificate.certificate_authority_configuration.bring_your_own_root.enabled is True
        )

        # ==================================================================
        # Step 14: Delete BYOR policy
        # ==================================================================
        self.client.policies.begin_delete(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
            policy_name=BYOR_POLICY_NAME,
        ).result()

        # Delay to avoid RP 409 race condition between BYOR policy deletion
        # and credential deletion (RP may still be cleaning up child resources)
        _delay_if_live(self, PROPAGATION_DELAY_SECONDS, "Waiting for BYOR policy deletion to propagate")

        # ==================================================================
        # Step 15: Delete credential (final cleanup)
        # ==================================================================
        self.client.credentials.begin_delete(
            resource_group_name=RESOURCE_GROUP_NAME,
            namespace_name=NAMESPACE_NAME,
        ).result()
