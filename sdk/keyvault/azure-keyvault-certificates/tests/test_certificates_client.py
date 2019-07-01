from dateutil import parser as date_parse
import time

from azure.keyvault.certificates._key_vault_id import KeyVaultId
from azure.keyvault.certificates._generated.v7_0.models import (
    SecretProperties, KeyProperties, CertificatePolicy, IssuerParameters, X509CertificateProperties,
    SubjectAlternativeNames, IssuerCredentials, OrganizationDetails, AdministratorDetails, Contact
)

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import ResourceGroupPreparer
from certificates_preparer import VaultClientPreparer
from certificates_test_case import KeyVaultTestCase


from dateutil import parser as date_parse

class CertificatesClientTest(KeyVaultTestCase):

    def _validate_certificate_operation(self, pending_cert_operation, vault, cert_name, cert_policy):
        self.assertIsNotNone(pending_cert_operation)
        self.assertIsNotNone(pending_cert_operation.csr)
        self.assertEqual(cert_policy.issuer_parameters.name, pending_cert_operation.issuer_name)
        pending_id = KeyVaultId.parse_certificate_operation_id(pending_cert_operation.id)
        self.assertEqual(pending_id.vault.strip('/'), vault.strip('/'))
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate_bundle(self, cert, vault, cert_name, cert_policy):
        self.assertIsNotNone(cert)
        self.assertEqual(cert_name, cert.name)
        self.assertIsNotNone(cert.cer)
        self.assertIsNotNone(cert.policy)
        self.assertEqual(cert_policy.issuer_parameters.name, cert.policy.issuer_name)
        # self.assertIsNotNone(cert.policy.lifetime_actions)
        # self.assertEqual(cert.policy.key_properties, cert_policy.key_properties)
        self.assertEqual(cert.policy.content_type, cert_policy.secret_properties.content_type)
        if cert_policy.x509_certificate_properties.ekus:
            self.assertEqual(cert_policy.x509_certificate_properties.ekus, cert.policy.key_properties.ekus)
        if cert_policy.x509_certificate_properties.key_usage:
            self.assertEqual(cert_policy.x509_certificate_properties.key_usage, cert.policy.key_properties.key_usage)
        if cert_policy.x509_certificate_properties:
            self._validate_x509_properties(cert.policy, cert_policy.x509_certificate_properties)
        if cert_policy.key_properties:
           self. _validate_key_properties(cert.policy.key_properties, cert_policy.key_properties)
        if cert_policy.lifetime_actions:
            self._validate_lifetime_actions(cert.policy.lifetime_actions, cert_policy.lifetime_actions)

    def _validate_x509_properties(self, cert_bundle_policy, cert_policy_x509_props):
        self.assertIsNotNone(cert_bundle_policy)
        self.assertEqual(cert_policy_x509_props.subject,
                        cert_bundle_policy.subject_name)
        # if cert_policy.x509_certificate_properties.subject_alternative_names.emails:
        #     for sans_email in cert_policy.x509_certificate_properties.subject_alternative_names.emails:
        #         cert_bundle_policy.sans_emails # has one
        # if cert_policy.x509_certificate_properties.subject_alternative_names.upns:
        #     for sans_upns in cert_policy.x509_certificate_properties.subject_alternative_names.upns:
        #         cert_bundle_policy.sans_upns # has one
        # if cert_policy.x509_certificate_properties.subject_alternative_names.sans_dns_names:
        #     for sans_dns_names in cert_policy.x509_certificate_properties.subject_alternative_names.dns_names:
        #         cert_bundle_policy.sans_emails # has one

    def _validate_key_properties(self, cert_bundle_key_props, cert_policy_key_props):
        self.assertIsNotNone(cert_bundle_key_props)
        if cert_policy_key_props:
            self.assertEqual(cert_policy_key_props.exportable, cert_bundle_key_props.exportable)
            self.assertEqual(cert_policy_key_props.key_type, cert_bundle_key_props.key_type)
            self.assertEqual(cert_policy_key_props.key_size, cert_bundle_key_props.key_size)
            self.assertEqual(cert_policy_key_props.reuse_key, cert_bundle_key_props.reuse_key)
            self.assertEqual(cert_policy_key_props.curve, cert_bundle_key_props.curve)
    
    def _validate_lifetime_actions(self, cert_bundle_liftime_actions, cert_policy_liftime_actions):
        self.assertIsNotNone(cert_bundle_lifetime_actions)
        # if cert_policy.x509_certificate_properties.subject_alternative_names.emails:
        #     for sans_email in cert_policy.x509_certificate_properties.subject_alternative_names.emails:
        #         cert_bundle_policy.sans_emails # has one
        # if cert_policy.x509_certificate_properties.subject_alternative_names.upns:
        #     for sans_upns in cert_policy.x509_certificate_properties.subject_alternative_names.upns:
        #         cert_bundle_policy.sans_upns # has one
        # if cert_policy.x509_certificate_properties.subject_alternative_names.sans_dns_names:
        #     for sans_dns_names in cert_policy.x509_certificate_properties.subject_alternative_names.dns_names:
        #         cert_bundle_policy.sans_emails # has one


    def _validate_certificate_list(self, certificates, expected):
        for cert in certificates:
            if cert.id in expected.keys():
                del expected[cert.id]
            else:
                self.assertTrue(False)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_crud_operations(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = self.get_resource_name("cert")

        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        secret_properties=SecretProperties(content_type='application/x-pkcs12'),
                                        issuer_parameters=IssuerParameters(name='Self'),
                                        x509_certificate_properties=X509CertificateProperties(
                                            subject='CN=*.microsoft.com',
                                            subject_alternative_names=SubjectAlternativeNames(
                                                dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com']
                                            ),
                                            validity_in_months=24
                                        ))

        # create certificate
        interval_time = 5 if not self.is_playback() else 0
        cert_operation = client.create_certificate(cert_name, cert_policy)
        while True:
            pending_cert = client.get_certificate_operation(cert_name)
            self._validate_certificate_operation(pending_cert, client.vault_url, cert_name, cert_policy)
            if pending_cert.status.lower() == 'completed':
                cert_id = KeyVaultId.parse_certificate_operation_id(pending_cert.target)
                break
            elif pending_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
            time.sleep(interval_time)

        # get certificate
        cert_bundle = client.get_certificate(cert_id.name)
        self._validate_certificate_bundle(cert_bundle, client.vault_url, cert_name, cert_policy)

        # get certificate as secret
        secret_id = KeyVaultId.parse_secret_id(cert_bundle.sid)
        secret_bundle = vault_client.secrets.get_secret(secret_id.name)

        # update certificate
        cert_policy.tags = {'tag1': 'value1'}
        cert_bundle = client.update_certificate(cert_id.name, cert_id.version, cert_policy)
        self._validate_certificate_bundle(cert_bundle, client.vault_url, cert_name, cert_policy)

        # delete certificate
        cert_bundle = client.delete_certificate(client.vault_url, cert_name)
        self._validate_certificate_bundle(cert_bundle, client.vault_url, cert_name, cert_policy)

        # get certificate returns not found
        try:
            client.get_certificate(cert_id.name)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex