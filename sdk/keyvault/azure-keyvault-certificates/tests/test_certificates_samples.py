# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import print_function
import functools
import itertools
import time
import datetime

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import ResourceGroupPreparer
from certificates_preparer import VaultClientPreparer
from certificates_test_case import KeyVaultTestCase

from azure.keyvault.certificates._key_vault_id import KeyVaultId
from azure.keyvault.certificates._shared._generated.v7_0.models import (ActionType, CertificateAttributes)
from azure.keyvault.certificates.models import (CertificatePolicy, KeyProperties, LifetimeAction)


def print(*args):
    assert all(arg is not None for arg in args)

def test_create_certificate_client():
    vault_url = "vault_url"
    # pylint:disable=unused-variable
    # [START create_key_client]

    from azure.identity import DefaultAzureCredential
    from azure.keyvault.certificates import CertificateClient

    # Create a KeyClient using default Azure credentials
    credential = DefaultAzureCredential()
    certificate_client = CertificateClient(vault_url, credential)

    # [END create_key_client]

class TestSamplesKeyVault(KeyVaultTestCase):

    def _validate_key_properties(self, cert_policy_key_props, cert_bundle_key_props):
        self.assertIsNotNone(cert_bundle_key_props)
        self.assertEqual(cert_policy_key_props.ekus, cert_bundle_key_props.ekus)
        self.assertEqual(cert_policy_key_props.key_usage, cert_bundle_key_props.key_usage)
        self.assertEqual(cert_policy_key_props.exportable, cert_bundle_key_props.exportable)
        self.assertEqual(cert_policy_key_props.key_type, cert_bundle_key_props.key_type)
        self.assertEqual(cert_policy_key_props.key_size, cert_bundle_key_props.key_size)
        self.assertEqual(cert_policy_key_props.reuse_key, cert_bundle_key_props.reuse_key)
        self.assertEqual(cert_policy_key_props.curve, cert_bundle_key_props.curve)

    def _validate_lifetime_actions(self, cert_policy_lifetime_actions, cert_bundle_lifetime_actions):
        self.assertIsNotNone(cert_bundle_lifetime_actions)
        if cert_policy_lifetime_actions:
            for (bundle_lifetime_action, policy_lifetime_action) in itertools.zip_longest(cert_bundle_lifetime_actions,
                                                                                          cert_bundle_lifetime_actions):
                self.assertEqual(bundle_lifetime_action.action_type, policy_lifetime_action.action_type)
                if policy_lifetime_action.lifetime_percentage:
                    self.assertEqual(bundle_lifetime_action.lifetime_percentage,
                                     policy_lifetime_action.lifetime_percentage)
                if policy_lifetime_action.days_before_expiry:
                    self.assertEqual(bundle_lifetime_action.days_before_expiry,
                                     policy_lifetime_action.days_before_expiry)

    def _validate_certificate_operation(self, pending_cert_operation, vault, cert_name, cert_policy):
        self.assertIsNotNone(pending_cert_operation)
        self.assertIsNotNone(pending_cert_operation.csr)
        self.assertEqual(cert_policy.issuer_name, pending_cert_operation.issuer_name)
        pending_id = KeyVaultId.parse_certificate_operation_id(id=pending_cert_operation.id)
        self.assertEqual(pending_id.vault.strip('/'), vault.strip('/'))
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate(self, cert, vault, cert_name, cert_policy):
        self.assertIsNotNone(cert)
        self.assertEqual(cert_name, cert.name)
        self.assertIsNotNone(cert.cer)
        self.assertIsNotNone(cert.policy)
        self.assertEqual(cert_policy.issuer_name, cert.policy.issuer_name)
        self.assertEqual(cert_policy.content_type, cert.policy.content_type)
        self.assertEqual(cert_policy.subject_name, cert.policy.subject_name)
        print(cert.policy.key_properties)
        # if cert_policy.key_properties:
        #     self._validate_key_properties(cert_policy_key_props=cert_policy.key_properties, cert_bundle_key_props=cert.policy.key_properites)
        if cert_policy.lifetime_actions:
            self._validate_lifetime_actions(cert_policy_lifetime_actions=cert_policy.lifetime_actions, cert_bundle_lifetime_actions=cert.policy.lifetime_actions)
        if cert_policy.san_emails:
            for (san_email, policy_email) in itertools.zip_longest(
                    cert_policy.san_emails, cert.policy.san_emails):
                self.assertEqual(san_email, policy_email)
        if cert_policy.san_upns:
            for (san_upn, policy_upn) in itertools.zip_longest(
                    cert_policy.san_upns, cert.policy.san_upns):
                self.assertEqual(san_upn, policy_upn)
        if cert_policy.san_dns_names:
            for (san_dns_name, policy_dns_name) in itertools.zip_longest(
                    cert_policy.san_dns_names, cert.policy.san_dns_names):
                self.assertEqual(san_dns_name, policy_dns_name)

    def _validate_certificate_list(self, certificates, expected):
        for cert in certificates:
            if cert.id in expected.keys():
                del expected[cert.id]
            else:
                self.assertTrue(False)
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_backup_restore_operations_sample(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = "BackupRestoreCertificate"
        lifetime_actions = [LifetimeAction(
            lifetime_percentage=2,
            action_type=ActionType.email_contacts
        )]
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        content_type='application/x-pkcs12',
                                        issuer_name='Self',
                                        subject_name='CN=*.microsoft.com',
                                        san_dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com'],
                                        validity_in_months=24,
                                        lifetime_actions=lifetime_actions,
                                        attributes=CertificateAttributes(recovery_level="Purgeable")
                                        )

        # create certificate
        certificate_operation = client.create_certificate(name=cert_name, policy=cert_policy)
        create_interval_time = 5 if not self.is_playback() else 0

        while True:
            pending_cert = client.get_certificate_operation(cert_name)
            self._validate_certificate_operation(pending_cert, client.vault_url, cert_name, cert_policy)
            if pending_cert.status.lower() == 'completed':
                cert_id = KeyVaultId.parse_certificate_operation_id(id=pending_cert.target)
                break
            elif pending_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
            time.sleep(create_interval_time)

        # create a backup
        certificate_backup = client.backup_certificate(name=certificate_operation.name)

        # delete the certificate
        deleted_certificate = client.delete_certificate(name=certificate_operation.name)
        self._validate_certificate(
            cert=deleted_certificate,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        # to ensure certificate is deleted on the server side.
        delete_interval_time = 20 if not self.is_playback() else 0
        time.sleep(delete_interval_time)

        # purging certificate
        client.purge_deleted_certificate(name=certificate_operation.name)

        # to ensure certificate is purged on the server side.
        purge_interval_time = 30 if not self.is_playback() else 0
        time.sleep(purge_interval_time)

        # validate the purged certificate is not returned by list_deleted_certificates
        deleted = [KeyVaultId.parse_secret_id(id=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(deleted_certificate.name not in deleted)

        # restore certificate
        restored_certificate = client.restore_certificate(backup=certificate_backup)
        self._validate_certificate(
            cert=restored_certificate,
            vault=client.vault_url,
            cert_name=certificate_operation.name,
            cert_policy=cert_policy
        )

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_hello_word_sample(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        # create certificate
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        content_type='application/x-pkcs12',
                                        issuer_name='Self',
                                        subject_name='CN=*.microsoft.com',
                                        san_dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com'],
                                        validity_in_months=24
                                        )
        cert_name = "HelloWorldCertificate"
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        certificate_operation = client.create_certificate(name=cert_name, policy=cert_policy, expires=expires)
        create_interval_time = 5 if not self.is_playback() else 0

        while True:
            pending_cert = client.get_certificate_operation(cert_name)
            self._validate_certificate_operation(pending_cert, client.vault_url, cert_name, cert_policy)
            if pending_cert.status.lower() == 'completed':
                cert_id = KeyVaultId.parse_certificate_operation_id(id=pending_cert.target)
                break
            elif pending_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
            time.sleep(create_interval_time)

        # get certificate
        bank_certificate = client.get_certificate(name=certificate_operation.name)
        self._validate_certificate(
            cert=bank_certificate,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        # update certificate
        expires = bank_certificate.expires + datetime.timedelta(days=365)
        updated_certificate = client.update_certificate(name=bank_certificate.name, expires=expires)
        self._validate_certificate(
            cert=updated_certificate,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        # delete certificate
        deleted_certificate = client.delete_certificate(name=bank_certificate.name)
        self._validate_certificate(
            cert=deleted_certificate,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        # get certificate returns not found
        try:
            client.get_certificate(name=cert_name)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_list_operations_sample(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        # create certificate
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        content_type='application/x-pkcs12',
                                        issuer_name='Self',
                                        subject_name='CN=*.microsoft.com',
                                        san_dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com'],
                                        validity_in_months=24
                                        )
        bank_cert_name = "BankListCertificate"
        storage_cert_name = "StorageListCertificate"
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        bank_certificate_operation = client.create_certificate(name=bank_cert_name, policy=cert_policy, expires=expires)
        storage_certificate_operation = client.create_certificate(name=storage_cert_name, policy=cert_policy)

        create_interval_time = 5 if not self.is_playback() else 0
        while True:
            pending_bank_cert = client.get_certificate_operation(name=bank_certificate_operation.name)
            pending_storage_cert = client.get_certificate_operation(name=storage_certificate_operation.name)
            self._validate_certificate_operation(pending_bank_cert, client.vault_url, bank_cert_name, cert_policy)
            self._validate_certificate_operation(pending_storage_cert, client.vault_url, storage_cert_name, cert_policy)
            if pending_bank_cert.status.lower() == 'completed' and pending_storage_cert.status.lower() == 'completed':
                break
            elif pending_bank_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_bank_cert))
            elif pending_storage_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_storage_cert))
            time.sleep(create_interval_time)

        # list certificates
        certificates = client.list_certificates()
        expected = {}

        bank_certificate_expected = client.get_certificate(name=bank_cert_name)
        storage_certificate_expected = client.get_certificate(name=storage_cert_name)

        expected[KeyVaultId.parse_certificate_id(bank_certificate_expected.id).base_id.strip('/')] = bank_certificate_expected
        expected[KeyVaultId.parse_certificate_id(storage_certificate_expected.id).base_id.strip('/')] = storage_certificate_expected
        self._validate_certificate_list(certificates=certificates, expected=expected)

        # update bank certificate
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)

        updated_bank_certificate_operation = client.create_certificate(name=bank_certificate_operation.name,
                                                                       policy=cert_policy,
                                                                       expires=expires)

        # list versions
        certificate_versions = client.list_certificate_versions(bank_certificate_operation.name)
        expected = {}

        bank_certificate_1 = client.get_certificate(name=bank_cert_name, version=bank_certificate_expected.version)
        bank_certificate_2 = client.get_certificate(name=bank_cert_name, version=updated_bank_certificate_operation.version)

        expected[KeyVaultId.parse_certificate_id(bank_certificate_1.id).base_id.strip('/')] = bank_certificate_1
        expected[KeyVaultId.parse_certificate_id(bank_certificate_2.id).base_id.strip('/')] = bank_certificate_2
        self._validate_certificate_list(certificates=certificate_versions, expected=expected)


        # delete certificates
        client.delete_certificate(name=bank_certificate_operation.name)
        client.delete_certificate(name=storage_certificate_operation.name)
        deleted = [KeyVaultId.parse_certificate_id(id=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(all(c in deleted for c in [bank_certificate_operation.name, storage_certificate_operation.name]))

        # to ensure certificate is deleted on the server side.
        delete_interval_time = 30 if not self.is_playback() else 0
        time.sleep(delete_interval_time)

        # list deleted certificates
        deleted = [KeyVaultId.parse_certificate_id(id=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(all(c in deleted for c in [bank_certificate_operation.name, storage_certificate_operation.name]))