import itertools
import time

from azure.keyvault.certificates._key_vault_id import KeyVaultId
from devtools_testutils import ResourceGroupPreparer
from certificates_preparer import VaultClientPreparer
from certificates_test_case import KeyVaultTestCase
from azure.keyvault.certificates._generated.v7_0.models import (
    SecretProperties, KeyProperties, CertificatePolicy, IssuerParameters, X509CertificateProperties,
    SubjectAlternativeNames, Contact, LifetimeAction, Trigger, Action, ActionType)

class CertificateClientTests(KeyVaultTestCase):
    def _import_common_certificate(self, client, cert_name):
        cert_content = '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'
        cert_password = '123'
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        secret_properties=SecretProperties(content_type='application/x-pkcs12'))
        return (
            client.import_certificate(
                name=cert_name,
                base64_encoded_certificate=cert_content,
                password=cert_password,
                policy=cert_policy
            ),
            cert_policy
        )

    def _validate_certificate_operation(self, pending_cert_operation, vault, cert_name, cert_policy):
        self.assertIsNotNone(pending_cert_operation)
        self.assertIsNotNone(pending_cert_operation.csr)
        self.assertEqual(cert_policy.issuer_parameters.name, pending_cert_operation.issuer_name)
        pending_id = KeyVaultId.parse_certificate_operation_id(id=pending_cert_operation.id)
        self.assertEqual(pending_id.vault.strip('/'), vault.strip('/'))
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate_bundle(self, cert, vault, cert_name, cert_policy):
        self.assertIsNotNone(cert)
        self.assertEqual(cert_name, cert.name)
        self.assertIsNotNone(cert.cer)
        self.assertIsNotNone(cert.policy)
        self.assertEqual(cert_policy.issuer_parameters.name, cert.policy.issuer_name)
        self.assertEqual(cert.policy.content_type, cert_policy.secret_properties.content_type)
        if cert_policy.x509_certificate_properties.ekus:
            self.assertEqual(cert_policy.x509_certificate_properties.ekus, cert.policy.key_properties.ekus)
        if cert_policy.x509_certificate_properties.key_usage:
            self.assertEqual(cert_policy.x509_certificate_properties.key_usage, cert.policy.key_properties.key_usage)
        if cert_policy.x509_certificate_properties:
            self._validate_x509_properties(cert_bundle_policy=cert.policy, cert_policy_x509_props=cert_policy.x509_certificate_properties)
        if cert_policy.key_properties:
            self._validate_key_properties(cert_bundle_key_props=cert.policy.key_properties, cert_policy_key_props=cert_policy.key_properties)
        if cert_policy.lifetime_actions:
            self._validate_lifetime_actions(cert_bundle_lifetime_actions=cert.policy.lifetime_actions, cert_policy_lifetime_actions=cert_policy.lifetime_actions)

    def _validate_x509_properties(self, cert_bundle_policy, cert_policy_x509_props):
        self.assertIsNotNone(cert_bundle_policy)
        self.assertEqual(cert_policy_x509_props.subject,
                         cert_bundle_policy.subject_name)
        if cert_policy_x509_props.subject_alternative_names.emails:
            for (sans_email, policy_email) in itertools.zip_longest(
                    cert_policy_x509_props.subject_alternative_names.emails, cert_bundle_policy.sans_emails):
                self.assertEqual(sans_email, policy_email)
        if cert_policy_x509_props.subject_alternative_names.upns:
            for (sans_upns, policy_upns) in itertools.zip_longest(cert_policy_x509_props.subject_alternative_names.upns,
                                                                  cert_bundle_policy.sans_upns):
                self.assertEqual(sans_upns, policy_upns)
        if cert_policy_x509_props.subject_alternative_names.dns_names:
            for (sans_dns_name, policy_dns_name) in itertools.zip_longest(
                    cert_policy_x509_props.subject_alternative_names.dns_names, cert_bundle_policy.sans_dns_names):
                self.assertEqual(sans_dns_name, policy_dns_name)

    def _validate_key_properties(self, cert_bundle_key_props, cert_policy_key_props):
        self.assertIsNotNone(cert_bundle_key_props)
        if cert_policy_key_props:
            self.assertEqual(cert_policy_key_props.exportable, cert_bundle_key_props.exportable)
            self.assertEqual(cert_policy_key_props.key_type, cert_bundle_key_props.key_type)
            self.assertEqual(cert_policy_key_props.key_size, cert_bundle_key_props.key_size)
            self.assertEqual(cert_policy_key_props.reuse_key, cert_bundle_key_props.reuse_key)
            self.assertEqual(cert_policy_key_props.curve, cert_bundle_key_props.curve)

    def _validate_lifetime_actions(self, cert_bundle_lifetime_actions, cert_policy_lifetime_actions):
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

    def _validate_certificate_list(self, certificates, expected):
        for cert in certificates:
            if cert.id in expected.keys():
                del expected[cert.id]
            else:
                self.assertTrue(False)
        self.assertEqual(len(expected), 0)

    def _validate_certificate_contacts(self, contacts, expected):
        self.assertEqual(len(list(contacts)), len(expected))
        for contact in contacts:
            exp_contact = next(x for x in expected if x.email_address == contact.email_address)
            self.assertEqual(contact, exp_contact)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_crud_operations(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = self.get_resource_name("cert")
        lifetime_actions = [LifetimeAction(
            trigger=Trigger(lifetime_percentage=2),
            action=Action(action_type=ActionType.email_contacts)
        )]
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        secret_properties=SecretProperties(content_type='application/x-pkcs12'),
                                        issuer_parameters=IssuerParameters(name='Self'),
                                        lifetime_actions=lifetime_actions,
                                        x509_certificate_properties=X509CertificateProperties(
                                            subject='CN=*.microsoft.com',
                                            subject_alternative_names=SubjectAlternativeNames(
                                                dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com']
                                            ),
                                            validity_in_months=24
                                        ))

        # create certificate
        interval_time = 5 if not self.is_playback() else 0
        cert_operation = client.create_certificate(name=cert_name, policy=cert_policy)
        while True:
            pending_cert = client.get_certificate_operation(cert_name)
            self._validate_certificate_operation(pending_cert, client.vault_url, cert_name, cert_policy)
            if pending_cert.status.lower() == 'completed':
                cert_id = KeyVaultId.parse_certificate_operation_id(id=pending_cert.target)
                break
            elif pending_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
            time.sleep(interval_time)

        # get certificate
        cert = client.get_certificate(name=cert_id.name)
        self._validate_certificate_bundle(
            cert=cert, vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        # get certificate as secret
        secret_id = KeyVaultId.parse_secret_id(id=cert.sid)
        secret_bundle = vault_client.secrets.get_secret(secret_id.name)

        # update certificate
        tags = {'tag1': 'updated_value1'}
        cert_bundle = client.update_certificate(name=cert_name, tags=tags)
        self._validate_certificate_bundle(
            cert=cert_bundle,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )
        self.assertEqual(tags, cert_bundle.tags)
        self.assertEqual(cert.id, cert_bundle.id)
        self.assertNotEqual(cert.updated, cert_bundle.updated)

        # delete certificate
        deleted_cert_bundle = client.delete_certificate(name=cert_name)
        self._validate_certificate_bundle(
            cert=deleted_cert_bundle,
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
    @VaultClientPreparer()
    def test_list(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        max_certificates = self.list_test_size
        expected = {}

        # import some certificates
        for x in range(max_certificates):
            cert_name = self.get_resource_name('cert{}'.format(x))
            error_count = 0
            try:
                cert_bundle = self._import_common_certificate(client=client, cert_name=cert_name)[0]
                cid = KeyVaultId.parse_certificate_id(cert_bundle.id).base_id.strip('/')
                expected[cid] = cert_bundle
            except Exception as ex:
                if hasattr(ex, 'message') and 'Throttled' in ex.message:
                    error_count += 1
                    time.sleep(2.5 * error_count)
                    continue
                else:
                    raise ex

        # list certificates
        result = client.list_certificates()
        self._validate_certificate_list(certificates=result, expected=expected)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_list_versions(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = self.get_resource_name('certver')

        max_certificates = self.list_test_size
        expected = {}

        # import same certificates as different versions
        for x in range(max_certificates):
            error_count = 0
            try:
                cert_bundle = self._import_common_certificate(client=client, cert_name=cert_name)[0]
                cid = KeyVaultId.parse_certificate_id(id=cert_bundle.id).id.strip('/')
                expected[cid] = cert_bundle
            except Exception as ex:
                if hasattr(ex, 'message') and 'Throttled' in ex.message:
                    error_count += 1
                    time.sleep(2.5 * error_count)
                    continue
                else:
                    raise ex

        # list certificate versions
        self._validate_certificate_list(certificates=(client.list_versions(cert_name)), expected=expected)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_crud_contacts(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        contact_list = [
            Contact(email_address='admin@contoso.com',
                    name='John Doe',
                    phone='1111111111'),
            Contact(email_address='admin2@contoso.com',
                    name='John Doe2',
                    phone='2222222222')
        ]

        # create certificate contacts
        contacts = client.create_contacts(contacts=contact_list)
        self._validate_certificate_contacts(contacts=contacts, expected=contact_list)

        # get certificate contacts
        contacts = client.list_contacts()
        self._validate_certificate_contacts(contacts=contacts, expected=contact_list)

        # delete certificate contacts
        contacts = client.delete_contacts()
        self._validate_certificate_contacts(contacts=contacts, expected=contact_list)

        # get certificate contacts returns not found
        try:
            contacts = client.list_contacts()
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_recover_and_purge(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        certs = {}
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
        # create certificates to recover
        for i in range(self.list_test_size):
            cert_name = self.get_resource_name('certrec{}'.format(str(i)))
            certs[cert_name] = self._import_common_certificate(client=client, cert_name=cert_name)

        # create certificates to purge
        for i in range(self.list_test_size):
            cert_name = self.get_resource_name('certprg{}'.format(str(i)))
            certs[cert_name] = self._import_common_certificate(client=client, cert_name=cert_name)

        # delete all certificates
        for cert_name in certs.keys():
            delcert = client.delete_certificate(name=cert_name)
            print(delcert)

        if not self.is_playback():
            time.sleep(30)

        # validate all our deleted certificates are returned by list_deleted_certificates
        deleted = [KeyVaultId.parse_certificate_id(id=c.id).name for c in client.list_deleted_certificates()]
        # self.assertTrue(all(s in deleted for s in certs.keys()))

        # recover select certificates
        for certificate_name in [c for c in certs.keys() if c.startswith('certrec')]:
            client.recover_deleted_certificate(name=certificate_name)

        # purge select certificates
        for certificate_name in [c for c in certs.keys() if c.startswith('certprg')]:
            client.purge_deleted_certificate(name=certificate_name)

        if not self.is_playback():
            time.sleep(30)

        # validate none of our deleted certificates are returned by list_deleted_certificates
        deleted = [KeyVaultId.parse_secret_id(id=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(not any(c in deleted for c in certs.keys()))

        # validate the recovered certificates
        expected = {k: v for k, v in certs.items() if k.startswith('certrec')}
        actual = {k: client.get_certificate(k, KeyVaultId.version_none) for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_async_request_cancellation_and_deletion(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        cert_name = 'asyncCanceledDeletedCert'
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
        client.create_certificate(name=cert_name, policy=cert_policy)

        # cancel certificate operation
        cancel_operation = client.cancel_certificate_operation(name=cert_name, cancellation_requested=True)
        self.assertTrue(hasattr(cancel_operation, 'cancellation_requested'))
        self.assertTrue(cancel_operation.cancellation_requested)
        self._validate_certificate_operation(
            pending_cert_operation=cancel_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        retrieved_operation = client.get_certificate_operation(name=cert_name)
        self.assertTrue(hasattr(retrieved_operation, 'cancellation_requested'))
        self.assertTrue(retrieved_operation.cancellation_requested)
        self._validate_certificate_operation(
            pending_cert_operation=retrieved_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        # delete certificate operation
        deleted_operation = client.delete_certificate_operation(name=cert_name)
        self.assertIsNotNone(deleted_operation)
        self._validate_certificate_operation(
            pending_cert_operation=deleted_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            cert_policy=cert_policy
        )

        try:
            client.get_certificate_operation(name=cert_name)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

        # delete cancelled certificate
        client.delete_certificate(cert_name)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_policy(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        cert_name = 'policyCertificate'

        # get certificate policy
        (cert_bundle, cert_policy) = self._import_common_certificate(client=client, cert_name=cert_name)
        retrieved_policy = client.get_policy(name=cert_name)
        self.assertIsNotNone(retrieved_policy)

        # update certificate policy
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        secret_properties=SecretProperties(content_type='application/x-pkcs12'),
                                        issuer_parameters=IssuerParameters(name='Self')
                                        )

        client.update_policy(name=cert_name, policy=cert_policy)
        updated_cert_policy = client.get_policy(name=cert_name)
        self.assertIsNotNone(updated_cert_policy)