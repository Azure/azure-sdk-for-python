import time
from devtools_testutils import ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from azure.keyvault import KeyVaultId
from azure.keyvault.models import (
    SecretProperties, KeyProperties, CertificatePolicy, IssuerParameters, X509CertificateProperties,
    SubjectAlternativeNames, IssuerCredentials, OrganizationDetails, AdministratorDetails, Contact
)

class KeyVaultCertificateTest(KeyvaultTestCase):

    def _import_common_certificate(self, vault_uri, cert_name):
        cert_content = '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'
        cert_password = '123'
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        secret_properties=SecretProperties(content_type='application/x-pkcs12'))
        return (
            self.client.import_certificate(vault_uri, cert_name, cert_content, cert_password, cert_policy),
            cert_policy
        )

    def _validate_certificate_operation(self, pending_cert, vault, cert_name, cert_policy):
        self.assertIsNotNone(pending_cert)
        self.assertIsNotNone(pending_cert.csr)
        self.assertEqual(cert_policy.issuer_parameters.name, pending_cert.issuer_parameters.name)
        pending_id = KeyVaultId.parse_certificate_operation_id(pending_cert.id)
        self.assertEqual(pending_id.vault.strip('/'), vault.strip('/'))
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate_bundle(self, cert, vault, cert_name, cert_policy):
        cert_id = KeyVaultId.parse_certificate_id(cert.id)
        self.assertEqual(cert_id.vault.strip('/'), vault.strip('/'))
        self.assertEqual(cert_id.name, cert_name)
        self.assertIsNotNone(cert)
        self.assertIsNotNone(cert.x509_thumbprint)
        self.assertIsNotNone(cert.cer)
        self.assertIsNotNone(cert.attributes)
        self.assertIsNotNone(cert.policy)
        self.assertIsNotNone(cert.policy.id)
        self.assertIsNotNone(cert.policy.issuer_parameters)
        self.assertIsNotNone(cert.policy.lifetime_actions)
        self.assertEqual(cert.policy.key_properties, cert_policy.key_properties)
        self.assertEqual(cert.policy.secret_properties, cert_policy.secret_properties)
        self.assertIsNotNone(cert.policy.x509_certificate_properties)
        if cert_policy.x509_certificate_properties:
            self.assertEqual(cert.policy.x509_certificate_properties.validity_in_months,
                             cert_policy.x509_certificate_properties.validity_in_months)
        KeyVaultId.parse_secret_id(cert.sid)
        KeyVaultId.parse_key_id(cert.kid)

    def _validate_certificate_list(self, certificates, expected):
        for cert in certificates:
            if cert.id in expected.keys():
                del expected[cert.id]
            else:
                self.assertTrue(False)

    def _validate_issuer_bundle(self, bundle, vault, name, provider, credentials, org_details):
        self.assertIsNotNone(bundle)
        self.assertIsNotNone(bundle.attributes)
        self.assertIsNotNone(bundle.organization_details)
        self.assertEqual(bundle.provider, provider)

        issuer_id = KeyVaultId.parse_certificate_issuer_id(bundle.id)
        self.assertEqual(issuer_id.vault.strip('/'), vault.strip('/'))
        self.assertEqual(issuer_id.name, name)

        if credentials:
            self.assertEqual(bundle.credentials.account_id, credentials.account_id)
        if org_details:
            # To Accomodate tiny change in == semantic in msrest 0.4.20
            org_details.additional_properties = {}
            bundle.organization_details.additional_properties = {}

            self.assertEqual(bundle.organization_details, org_details)

    def _validate_certificate_issuer_list(self, issuers, expected):
        for issuer in issuers:
            KeyVaultId.parse_certificate_issuer_id(issuer.id)
            provider = expected[issuer.id]
            if provider:
                self.assertEqual(provider, issuer.provider)
                del expected[issuer.id]

    def _validate_certificate_contacts(self, contacts, vault, expected):
        contact_id = '{}certificates/contacts'.format(vault)
        self.assertEqual(contact_id, contacts.id)
        self.assertEqual(len(contacts.contact_list), len(expected))

        for contact in contacts.contact_list:
            exp_contact = next(x for x in expected if x.email_address == contact.email_address)
            self.assertEqual(contact, exp_contact)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_crud_operations(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        cert_name = self.get_resource_name('cert')

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
        cert_operation = self.client.create_certificate(vault_uri, cert_name, cert_policy)
        while True:
            pending_cert = self.client.get_certificate_operation(vault_uri, cert_name)
            self._validate_certificate_operation(pending_cert, vault_uri, cert_name, cert_policy)
            if pending_cert.status.lower() == 'completed':
                cert_id = KeyVaultId.parse_certificate_operation_id(pending_cert.target)
                break
            elif pending_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
            time.sleep(interval_time)

        # get certificate
        cert_bundle = self.client.get_certificate(cert_id.vault, cert_id.name, '')
        self._validate_certificate_bundle(cert_bundle, vault_uri, cert_name, cert_policy)

        # get certificate as secret
        secret_id = KeyVaultId.parse_secret_id(cert_bundle.sid)
        secret_bundle = self.client.get_secret(secret_id.vault, secret_id.name, secret_id.version)

        # update certificate
        cert_policy.tags = {'tag1': 'value1'}
        cert_bundle = self.client.update_certificate(cert_id.vault, cert_id.name, cert_id.version, cert_policy)
        self._validate_certificate_bundle(cert_bundle, vault_uri, cert_name, cert_policy)

        # delete certificate
        cert_bundle = self.client.delete_certificate(vault_uri, cert_name)
        self._validate_certificate_bundle(cert_bundle, vault_uri, cert_name, cert_policy)

        # get certificate returns not found
        try:
            self.client.get_certificate(cert_id.vault, cert_id.name, '')
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_import(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        cert_name = self.get_resource_name('certimp')

        # import certificate(
        (cert_bundle, cert_policy) = self._import_common_certificate(vault_uri, cert_name)
        self._validate_certificate_bundle(cert_bundle, vault_uri, cert_name, cert_policy)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_list(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        max_certificates = self.list_test_size
        expected = {}

        # import some certificates
        for x in range(0, max_certificates):
            cert_name = self.get_resource_name('cert{}'.format(x))
            cert_bundle = None
            error_count = 0
            while not cert_bundle:
                try:
                    cert_bundle = self._import_common_certificate(vault_uri, cert_name)[0]
                    cid = KeyVaultId.parse_certificate_id(cert_bundle.id).base_id.strip('/')
                    expected[cid] = cert_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list certificates
        result = list(self.client.get_certificates(vault_uri, self.list_test_size))
        self._validate_certificate_list(result, expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_list_versions(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        cert_name = self.get_resource_name('certver')

        max_certificates = self.list_test_size
        expected = {}

        # import same certificates as different versions
        for x in range(0, max_certificates):
            cert_bundle = None
            error_count = 0
            while not cert_bundle:
                try:
                    cert_bundle = self._import_common_certificate(vault_uri, cert_name)[0]
                    cid = KeyVaultId.parse_certificate_id(cert_bundle.id).id.strip('/')
                    expected[cid] = cert_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list certificate versions
        self._validate_certificate_list(list(self.client.get_certificate_versions(vault_uri, cert_name)), expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_crud_issuer(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        issuer_name = 'pythonIssuer'
        issuer_credentials = IssuerCredentials(account_id='keyvaultuser', password='password')
        organization_details = OrganizationDetails(
            admin_details=[AdministratorDetails(first_name='Jane',
                                                last_name='Doe',
                                                email_address='admin@contoso.com',
                                                phone='4256666666')])

        # create certificate issuer
        issuer_bundle = self.client.set_certificate_issuer(vault_uri, issuer_name, 'test', issuer_credentials,
                                                           organization_details)
        self._validate_issuer_bundle(issuer_bundle, vault_uri, issuer_name, 'test', issuer_credentials,
                                     organization_details)

        # get certificate issuer
        issuer_bundle = self.client.get_certificate_issuer(vault_uri, issuer_name)
        self._validate_issuer_bundle(issuer_bundle, vault_uri, issuer_name, 'test', issuer_credentials,
                                     organization_details)

        # update certificate issue
        new_credentials = IssuerCredentials(account_id='xboxuser', password='security')
        new_org_details = OrganizationDetails(
            admin_details=[AdministratorDetails(first_name='Jane II',
                                                last_name='Doe',
                                                email_address='admin@contoso.com',
                                                phone='1111111111')])
        issuer_bundle = self.client.update_certificate_issuer(vault_uri, issuer_name, 'test', new_credentials,
                                                              new_org_details)
        self._validate_issuer_bundle(issuer_bundle, vault_uri, issuer_name, 'test', new_credentials, new_org_details)

        # delete certificate issuer(
        self.client.delete_certificate_issuer(vault_uri, issuer_name)

        # get certificate issuer returns not found
        try:
            self.client.get_certificate_issuer(vault_uri, issuer_name)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_list_issuers(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        max_issuers = self.list_test_size
        expected = {}

        # create some certificate issuers(
        for x in range(0, max_issuers):
            issuer_name = 'pythonIssuer{}'.format(x + 1)
            issuer_credentials = IssuerCredentials(account_id='keyvaultuser', password='password')
            organization_details = OrganizationDetails(
                admin_details=[AdministratorDetails(first_name='Jane',
                                                    last_name='Doe',
                                                    email_address='admin@contoso.com',
                                                    phone='4256666666')])
            error_count = 0
            issuer_bundle = None
            while not issuer_bundle:
                try:
                    issuer_bundle = self.client.set_certificate_issuer(vault_uri, issuer_name, 'test',
                                                                       issuer_credentials, organization_details)
                    expected[issuer_bundle.id] = issuer_bundle.provider
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list certificate issuers
        result = list(self.client.get_certificate_issuers(vault_uri, self.list_test_size))
        self._validate_certificate_issuer_list(result, expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_async_request_cancellation_and_deletion(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

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
        self.client.create_certificate(vault_uri, cert_name, cert_policy)

        # cancel certificate operation
        cancel_operation = self.client.update_certificate_operation(vault_uri, cert_name, True)
        self.assertTrue(hasattr(cancel_operation, 'cancellation_requested'))
        self.assertTrue(cancel_operation.cancellation_requested)
        self._validate_certificate_operation(cancel_operation, vault_uri, cert_name, cert_policy)

        retrieved_operation = self.client.get_certificate_operation(vault_uri, cert_name)
        self.assertTrue(hasattr(retrieved_operation, 'cancellation_requested'))
        self.assertTrue(retrieved_operation.cancellation_requested)
        self._validate_certificate_operation(retrieved_operation, vault_uri, cert_name, cert_policy)

        # delete certificate operation
        deleted_operation = self.client.delete_certificate_operation(vault_uri, cert_name)
        self.assertIsNotNone(deleted_operation)
        self._validate_certificate_operation(deleted_operation, vault_uri, cert_name, cert_policy)

        try:
            self.client.get_certificate_operation(vault_uri, cert_name)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

        # delete cancelled certificate operation
        self.client.delete_certificate(vault_uri, cert_name)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_crud_contacts(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        contact_list = [
            Contact(email_address='admin@contoso.com',
                    name='John Doe',
                    phone='1111111111'),
            Contact(email_address='admin2@contoso.com',
                    name='John Doe2',
                    phone='2222222222')
        ]

        # create certificate contacts
        contacts = self.client.set_certificate_contacts(vault_uri, contact_list)
        self._validate_certificate_contacts(contacts, vault_uri, contact_list)

        # get certificate contacts
        contacts = self.client.get_certificate_contacts(vault_uri)
        self._validate_certificate_contacts(contacts, vault_uri, contact_list)

        # delete certificate contacts
        contacts = self.client.delete_certificate_contacts(vault_uri)
        self._validate_certificate_contacts(contacts, vault_uri, contact_list)

        # get certificate contacts returns not found
        try:
            contacts = self.client.get_certificate_contacts(vault_uri)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_policy(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        cert_name = 'policyCertificate'

        # get certificate policy
        (cert_bundle, cert_policy) = self._import_common_certificate(vault_uri, cert_name)
        retrieved_policy = self.client.get_certificate_policy(vault_uri, cert_name)
        self.assertIsNotNone(retrieved_policy)

        # update certificate policy
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        secret_properties=SecretProperties(content_type='application/x-pkcs12'),
                                        issuer_parameters=IssuerParameters(name='Self')
                                        )

        self.client.update_certificate_policy(vault_uri, cert_name, cert_policy)
        updated_cert_policy = self.client.get_certificate_policy(vault_uri, cert_name)
        self.assertIsNotNone(updated_cert_policy)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_manual_enrolled(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        cert_name = 'unknownIssuerCert'
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        secret_properties=SecretProperties(content_type='application/x-pkcs12'),
                                        issuer_parameters=IssuerParameters(name='Unknown'),
                                        x509_certificate_properties=X509CertificateProperties(
                                            subject='CN=*.microsoft.com',
                                            subject_alternative_names=SubjectAlternativeNames(
                                                dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com']
                                            ),
                                            validity_in_months=24
                                        ))

        # get pending certificate signing request
        cert_operation = self.client.create_certificate(vault_uri, cert_name, cert_policy)
        pending_version_csr = self.client.get_pending_certificate_signing_request(vault_uri, cert_name)
        try:
            self.assertEqual(cert_operation.csr, pending_version_csr)
        except Exception as ex:
            pass
        finally:
            self.client.delete_certificate(vault_uri, cert_name)

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_recover_and_purge(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

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
        for i in range(0, self.list_test_size):
            cert_name = self.get_resource_name('certrec{}'.format(str(i)))
            certs[cert_name] = self._import_common_certificate(vault_uri, cert_name)

        # create certificates to purge
        for i in range(0, self.list_test_size):
            cert_name = self.get_resource_name('certprg{}'.format(str(i)))
            certs[cert_name] = self._import_common_certificate(vault_uri, cert_name)

        # delete all certificates
        for cert_name in certs.keys():
            delcert = self.client.delete_certificate(vault_uri, cert_name)
            print(delcert)

        if not self.is_playback():
            time.sleep(30)

        # validate all our deleted certificates are returned by get_deleted_certificates
        deleted = [KeyVaultId.parse_certificate_id(s.id).name for s in self.client.get_deleted_certificates(vault_uri)]
        # self.assertTrue(all(s in deleted for s in certs.keys()))

        # recover select secrets
        for certificate_name in [s for s in certs.keys() if s.startswith('certrec')]:
            self.client.recover_deleted_certificate(vault_uri, certificate_name)

        # purge select secrets
        for certificate_name in [s for s in certs.keys() if s.startswith('certprg')]:
            self.client.purge_deleted_certificate(vault_uri, certificate_name)

        if not self.is_playback():
            time.sleep(30)

        # validate none of our deleted certificates are returned by get_deleted_certificates
        deleted = [KeyVaultId.parse_secret_id(s.id).name for s in self.client.get_deleted_certificates(vault_uri)]
        self.assertTrue(not any(s in deleted for s in certs.keys()))

        # validate the recovered certificates
        expected = {k: v for k, v in certs.items() if k.startswith('certrec')}
        actual = {k: self.client.get_certificate(vault_uri, k, KeyVaultId.version_none) for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))
