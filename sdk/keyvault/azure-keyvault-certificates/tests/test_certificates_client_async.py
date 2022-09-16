# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
import logging
import json

from azure.core.exceptions import ResourceExistsError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure_devtools.scenario_tests import RecordingProcessor
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from azure.keyvault.certificates import (
    AdministratorContact,
    ApiVersion,
    CertificateContact,
    CertificatePolicyAction,
    CertificatePolicy,
    KeyType,
    KeyCurveName,
    KeyUsageType,
    KeyVaultCertificateIdentifier,
    CertificateContentType,
    LifetimeAction,
    CertificateIssuer,
    IssuerProperties,
    WellKnownIssuerNames
)
from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.certificates._client import NO_SAN_OR_SUBJECT
import pytest

from _shared.test_case_async import KeyVaultTestCase
from _async_test_case import get_decorator, AsyncCertificatesClientPreparer
from certs import CERT_CONTENT_PASSWORD_ENCODED, CERT_CONTENT_NOT_PASSWORD_ENCODED


all_api_versions = get_decorator(is_async=True)
logging_enabled = get_decorator(is_async=True, logging_enable=True)
logging_disabled = get_decorator(is_async=True, logging_enable=False)
exclude_2016_10_01 = get_decorator(is_async=True, api_versions=[v for v in ApiVersion if v != ApiVersion.V2016_10_01])
only_2016_10_01 = get_decorator(is_async=True, api_versions=[ApiVersion.V2016_10_01])
LIST_TEST_SIZE = 7


class RetryAfterReplacer(RecordingProcessor):
    """Replace the retry after wait time in the replay process to 0."""

    def process_response(self, response):
        if "retry-after" in response["headers"]:
            response["headers"]["retry-after"] = "0"
        return response


# used for logging tests
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class TestCertificateClient(KeyVaultTestCase):

    async def _import_common_certificate(self, client, cert_name):
        cert_password = "1234"
        cert_policy = CertificatePolicy(
            issuer_name="Self",
            subject="CN=DefaultPolicy",
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type="application/x-pkcs12",
            validity_in_months=12,
            key_usage=["digitalSignature", "keyEncipherment"],
        )
        return await client.import_certificate(
            cert_name, CERT_CONTENT_PASSWORD_ENCODED, policy=cert_policy, password=cert_password
        )

    def _validate_certificate_operation(self, pending_cert_operation, vault, cert_name, original_cert_policy):
        assert pending_cert_operation is not None
        assert pending_cert_operation.csr is not None
        assert original_cert_policy.issuer_name == pending_cert_operation.issuer_name
        pending_id = KeyVaultCertificateIdentifier(pending_cert_operation.id)
        assert pending_id.vault_url.strip("/") == vault.strip("/")
        assert pending_id.name, cert_name

    def _validate_certificate_bundle(self, cert, cert_name, cert_policy):
        assert cert is not None
        assert cert_name == cert.name
        assert cert.cer is not None
        assert cert.policy is not None
        self._validate_certificate_policy(cert_policy, cert_policy)

    def _validate_certificate_policy(self, a, b):
        assert a.issuer_name == b.issuer_name
        assert a.subject == b.subject
        assert a.exportable == b.exportable
        assert a.key_type == b.key_type
        assert a.key_size == b.key_size
        assert a.reuse_key == b.reuse_key
        assert a.key_curve_name == b.key_curve_name
        if a.enhanced_key_usage:
            assert set(a.enhanced_key_usage) == set(b.enhanced_key_usage)
        if a.key_usage:
            assert  set(a.key_usage) == set(b.key_usage)
        assert a.content_type == b.content_type
        assert a.validity_in_months == b.validity_in_months
        assert a.certificate_type == b.certificate_type
        assert a.certificate_transparency == b.certificate_transparency
        self._validate_sans(a, b)
        if a.lifetime_actions:
            self._validate_lifetime_actions(a.lifetime_actions, b.lifetime_actions)

    def _validate_sans(self, a, b):
        if a.san_dns_names:
            assert set(a.san_dns_names) == set(b.san_dns_names)
        if a.san_emails:
            assert set(a.san_emails) == set(b.san_emails)
        if a.san_user_principal_names:
            assert set(a.san_user_principal_names), set(b.san_user_principal_names)

    def _validate_lifetime_actions(self, a, b):
        assert len(a) == len(b)
        for a_entry in a:
            b_entry = next(x for x in b if x.action == a_entry.action)
            assert a_entry.lifetime_percentage == b_entry.lifetime_percentage
            assert a_entry.days_before_expiry == b_entry.days_before_expiry

    async def _validate_certificate_list(self, a, b):
        # verify that all certificates in a exist in b
        async for cert in b:
            if cert.id in a.keys():
                del a[cert.id]
        assert len(a) == 0

    def _validate_certificate_contacts(self, a, b):
        assert len(a) == len(b)
        for a_entry in a:
            b_entry = next(x for x in b if x.email == a_entry.email)
            assert a_entry.name == b_entry.name
            assert a_entry.phone == b_entry.phone

    def _admin_contact_equal(self, a, b):
        return a.first_name == b.first_name and a.last_name == b.last_name and a.email == b.email and a.phone == b.phone

    def _validate_certificate_issuer(self, a, b):
        assert a.provider == b.provider
        assert a.account_id == b.account_id
        assert len(a.admin_contacts) == len(b.admin_contacts)
        for a_admin_contact in a.admin_contacts:
            b_admin_contact = next(
                (ad for ad in b.admin_contacts if self._admin_contact_equal(a_admin_contact, ad)), None
            )
            assert b_admin_contact is not None
        assert a.password == b.password
        assert a.organization_id == b.organization_id

    def _validate_certificate_issuer_properties(self, a, b):
        assert a.id == b.id
        assert a.name == b.name
        assert a.provider == b.provider

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_crud_operations(self, client, **kwargs):
        cert_name = self.get_resource_name("cert")
        lifetime_actions = [LifetimeAction(lifetime_percentage=80, action=CertificatePolicyAction.auto_renew)]
        cert_policy = CertificatePolicy(
            issuer_name="Self",
            subject="CN=DefaultPolicy",
            exportable=True,
            key_type=KeyType.rsa,
            key_size=2048,
            reuse_key=False,
            content_type=CertificateContentType.pkcs12,
            lifetime_actions=lifetime_actions,
            validity_in_months=12,
            key_usage=[KeyUsageType.digital_signature, KeyUsageType.key_encipherment],
        )

        # create certificate
        cert = await client.create_certificate(certificate_name=cert_name, policy=CertificatePolicy.get_default())

        self._validate_certificate_bundle(cert=cert, cert_name=cert_name, cert_policy=cert_policy)

        assert (await client.get_certificate_operation(certificate_name=cert_name)).status.lower() == "completed"
        

        # get certificate
        cert = await client.get_certificate(certificate_name=cert_name)
        self._validate_certificate_bundle(cert=cert, cert_name=cert_name, cert_policy=cert_policy)

        # update certificate, ensuring the new updated_on value is at least one second later than the original
        if self.is_live:
            await asyncio.sleep(1)
        tags = {"tag1": "updated_value1"}
        updated_cert = await client.update_certificate_properties(cert_name, tags=tags)
        self._validate_certificate_bundle(cert=updated_cert, cert_name=cert_name, cert_policy=cert_policy)
        assert tags == updated_cert.properties.tags
        assert cert.id == updated_cert.id
        assert cert.properties.updated_on != updated_cert.properties.updated_on

        # delete certificate
        deleted_cert_bundle = await client.delete_certificate(certificate_name=cert_name)
        self._validate_certificate_bundle(cert=deleted_cert_bundle, cert_name=cert_name, cert_policy=cert_policy)

        # get certificate returns not found
        try:
            await client.get_certificate_version(cert_name, deleted_cert_bundle.properties.version)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_import_certificate_not_password_encoded_no_policy(self, client, **kwargs):
        # If a certificate is not password encoded, we can import the certificate
        # without passing in 'password'
        certificate = await client.import_certificate(
            certificate_name=self.get_resource_name("importNotPasswordEncodedCertificate"),
            certificate_bytes=CERT_CONTENT_NOT_PASSWORD_ENCODED,
        )
        assert certificate.policy is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_import_certificate_password_encoded_no_policy(self, client, **kwargs):
        # If a certificate is password encoded, we have to pass in 'password'
        # when importing the certificate
        certificate = await client.import_certificate(
            certificate_name=self.get_resource_name("importPasswordEncodedCertificate"),
            certificate_bytes=CERT_CONTENT_PASSWORD_ENCODED,
            password="1234",
        )
        assert certificate.policy is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_list(self, client, **kwargs):
        max_certificates = LIST_TEST_SIZE
        expected = {}

        # import some certificates
        for x in range(max_certificates):
            cert_name = self.get_resource_name("cert{}".format(x))
            error_count = 0
            try:
                cert_bundle = await self._import_common_certificate(client=client, cert_name=cert_name)
                # Going to remove the ID from the last '/' onwards. This is because list_properties_of_certificates
                # doesn't return the version in the ID
                cid = "/".join(cert_bundle.id.split("/")[:-1])
                expected[cid] = cert_bundle
            except Exception as ex:
                if hasattr(ex, "message") and "Throttled" in ex.message:
                    error_count += 1
                    await asyncio.sleep(2.5 * error_count)
                    continue
                else:
                    raise ex

        # list certificates
        returned_certificates = client.list_properties_of_certificates(max_page_size=max_certificates - 1)
        await self._validate_certificate_list(expected, returned_certificates)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_list_certificate_versions(self, client, **kwargs):
        cert_name = self.get_resource_name("certver")

        max_certificates = LIST_TEST_SIZE
        expected = {}

        # import same certificates as different versions
        for x in range(max_certificates):
            error_count = 0
            try:
                cert_bundle = await self._import_common_certificate(client=client, cert_name=cert_name)
                expected[cert_bundle.id.strip("/")] = cert_bundle
            except Exception as ex:
                if hasattr(ex, "message") and "Throttled" in ex.message:
                    error_count += 1
                    await asyncio.sleep(2.5 * error_count)
                    continue
                else:
                    raise ex

        # list certificate versions
        await self._validate_certificate_list(
            expected,
            (
                client.list_properties_of_certificate_versions(
                    certificate_name=cert_name, max_page_size=max_certificates - 1
                )
            ),
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_crud_contacts(self, client, **kwargs):
        contact_list = [
            CertificateContact(email="admin@contoso.com", name="John Doe", phone="1111111111"),
            CertificateContact(email="admin2@contoso.com", name="John Doe2", phone="2222222222"),
        ]

        # create certificate contacts
        contacts = await client.set_contacts(contacts=contact_list)
        self._validate_certificate_contacts(contact_list, contacts)

        # get certificate contacts
        contacts = await client.get_contacts()
        self._validate_certificate_contacts(contact_list, contacts)

        # delete certificate contacts
        contacts = await client.delete_contacts()
        self._validate_certificate_contacts(contact_list, contacts)

        # get certificate contacts returns not found
        try:
            await client.get_contacts()
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_recover_and_purge(self, client, **kwargs):
        set_bodiless_matcher()
        certs = {}
        # create certificates to recover
        for i in range(LIST_TEST_SIZE):
            cert_name = self.get_resource_name("certrec{}".format(str(i)))
            certs[cert_name] = await self._import_common_certificate(client=client, cert_name=cert_name)

        # create certificates to purge
        for i in range(LIST_TEST_SIZE):
            cert_name = self.get_resource_name("certprg{}".format(str(i)))
            certs[cert_name] = await self._import_common_certificate(client=client, cert_name=cert_name)

        # delete all certificates
        for cert_name in certs.keys():
            await client.delete_certificate(certificate_name=cert_name)

        # validate all our deleted certificates are returned by list_deleted_certificates
        deleted_certificates = client.list_deleted_certificates()
        deleted = []
        async for c in deleted_certificates:
            deleted.append(KeyVaultCertificateIdentifier(source_id=c.id).name)
        assert all(c in deleted for c in certs.keys())

        # recover select certificates (test resources have a "livekvtest" prefix)
        for certificate_name in [c for c in certs.keys() if c.startswith("livekvtestcertrec")]:
            await client.recover_deleted_certificate(certificate_name=certificate_name)

        # purge select certificates
        for certificate_name in [c for c in certs.keys() if c.startswith("livekvtestcertprg")]:
            await client.purge_deleted_certificate(certificate_name)

        if not self.is_playback():
            await asyncio.sleep(50)

        # validate none of our deleted certificates are returned by list_deleted_certificates
        deleted_certificates = client.list_deleted_certificates()
        deleted = []
        async for c in deleted_certificates:
            deleted.append(KeyVaultCertificateIdentifier(source_id=c.id).name)
        assert not any(c in deleted for c in certs.keys())

        # validate the recovered certificates
        expected = {k: v for k, v in certs.items() if k.startswith("livekvtestcertrec")}
        actual = {}
        for k in expected.keys():
            actual[k] = await client.get_certificate_version(certificate_name=k, version="")
        assert len(set(expected.keys()) & set(actual.keys())) == len(expected)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @pytest.mark.skip("Skipping because service doesn't allow cancellation of certificates with issuer 'Unknown'")
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_async_request_cancellation_and_deletion(self, client, **kwargs):
        cert_name = self.get_resource_name("asyncCanceledDeletedCert")
        cert_policy = CertificatePolicy.get_default()

        # create certificate
        await client.create_certificate(certificate_name=cert_name, policy=cert_policy)

        # cancel certificate operation
        cancel_operation = await client.cancel_certificate_operation(cert_name)
        assert hasattr(cancel_operation, "cancellation_requested")
        assert cancel_operation.cancellation_requested
        self._validate_certificate_operation(
            pending_cert_operation=cancel_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            original_cert_policy=cert_policy,
        )

        cancelled = False
        for _ in range(10):
            if (await client.get_certificate_operation(cert_name)).status.lower() == "cancelled":
                cancelled = True
                break
            await asyncio.sleep(10)
        assert cancelled

        retrieved_operation = await client.get_certificate_operation(certificate_name=cert_name)
        assert hasattr(retrieved_operation, "cancellation_requested")
        assert retrieved_operation.cancellation_requested
        self._validate_certificate_operation(
            pending_cert_operation=retrieved_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            original_cert_policy=cert_policy,
        )

        # delete certificate operation
        deleted_operation = await client.delete_certificate_operation(cert_name)
        assert deleted_operation is not None
        self._validate_certificate_operation(
            pending_cert_operation=deleted_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            original_cert_policy=cert_policy,
        )

        try:
            await client.get_certificate_operation(certificate_name=cert_name)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

        # delete cancelled certificate
        await client.delete_certificate(cert_name)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", exclude_2016_10_01)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_policy(self, client, **kwargs):
        cert_name = self.get_resource_name("policyCertificate")
        cert_policy = CertificatePolicy(
            issuer_name="Self",
            subject="CN=DefaultPolicy",
            exportable=True,
            key_type=KeyType.rsa,
            key_size=2048,
            reuse_key=True,
            enhanced_key_usage=["1.3.6.1.5.5.7.3.1", "1.3.6.1.5.5.7.3.2"],
            key_usage=[KeyUsageType.decipher_only],
            content_type=CertificateContentType.pkcs12,
            validity_in_months=12,
            lifetime_actions=[LifetimeAction(action=CertificatePolicyAction.email_contacts, lifetime_percentage=98)],
            certificate_transparency=False,
            san_dns_names=["sdk.azure-int.net"],
        )

        # get certificate policy
        await client.create_certificate(cert_name, cert_policy)

        returned_policy = await client.get_certificate_policy(certificate_name=cert_name)

        self._validate_certificate_policy(cert_policy, returned_policy)

        cert_policy._key_type = KeyType.ec
        cert_policy._key_size = 256
        cert_policy._key_curve_name = KeyCurveName.p_256

        returned_policy = await client.update_certificate_policy(certificate_name=cert_name, policy=cert_policy)

        self._validate_certificate_policy(cert_policy, returned_policy)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_get_pending_certificate_signing_request(self, client, **kwargs):
        cert_name = self.get_resource_name("unknownIssuerCert")

        # get pending certificate signing request
        await client.create_certificate(certificate_name=cert_name, policy=CertificatePolicy.get_default())
        operation = await client.get_certificate_operation(certificate_name=cert_name)
        pending_version_csr = operation.csr
        assert (await client.get_certificate_operation(certificate_name=cert_name)).csr == pending_version_csr

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", exclude_2016_10_01)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_backup_restore(self, client, **kwargs):
        cert_name = self.get_resource_name("cert")
        policy = CertificatePolicy.get_default()
        policy._san_user_principal_names = ["john.doe@domain.com"]

        # create certificate
        await client.create_certificate(certificate_name=cert_name, policy=policy)

        # create a backup
        certificate_backup = await client.backup_certificate(certificate_name=cert_name)

        # delete the certificate
        await client.delete_certificate(certificate_name=cert_name)

        # purge the certificate
        await client.purge_deleted_certificate(certificate_name=cert_name)

        # restore certificate
        restore_function = functools.partial(client.restore_certificate_backup, certificate_backup)
        restored_certificate = await self._poll_until_no_exception(
            restore_function, expected_exception=ResourceExistsError
        )
        self._validate_certificate_bundle(cert=restored_certificate, cert_name=cert_name, cert_policy=policy)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer()
    @recorded_by_proxy_async
    async def test_crud_issuer(self, client, **kwargs):
        issuer_name = self.get_resource_name("issuer")
        admin_contacts = [
            AdministratorContact(first_name="John", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        # create certificate issuer
        issuer = await client.create_issuer(
            issuer_name, "Test", account_id="keyvaultuser", admin_contacts=admin_contacts, enabled=True
        )

        expected = CertificateIssuer(
            provider="Test",
            account_id="keyvaultuser",
            admin_contacts=admin_contacts,
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer_name,
        )

        self._validate_certificate_issuer(expected, issuer)

        # get certificate issuer
        issuer = await client.get_issuer(issuer_name=issuer_name)
        self._validate_certificate_issuer(expected, issuer)

        # list certificate issuers
        issuer2_name = self.get_resource_name("issuer2")

        await client.create_issuer(
            issuer_name=issuer2_name,
            provider="Test",
            account_id="keyvaultuser2",
            admin_contacts=admin_contacts,
            enabled=True,
        )

        expected_base_1 = IssuerProperties(
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer_name, provider="Test"
        )

        expected_base_2 = IssuerProperties(
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer2_name, provider="Test"
        )
        expected_issuers = [expected_base_1, expected_base_2]

        issuers = client.list_properties_of_issuers()
        async for issuer in issuers:
            exp_issuer = next((i for i in expected_issuers if i.name == issuer.name), None)
            if exp_issuer:
                self._validate_certificate_issuer_properties(exp_issuer, issuer)
                expected_issuers.remove(exp_issuer)
        assert len(expected_issuers) == 0

        # update certificate issuer
        admin_contacts = [
            AdministratorContact(first_name="Jane", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        expected = CertificateIssuer(
            provider="Test",
            account_id="keyvaultuser",
            admin_contacts=admin_contacts,
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer_name,
        )
        issuer = await client.update_issuer(issuer_name, admin_contacts=admin_contacts)
        self._validate_certificate_issuer(expected, issuer)

        # delete certificate issuer
        await client.delete_issuer(issuer_name=issuer_name)

        # get certificate issuer returns not found
        try:
            await client.get_issuer(issuer_name=issuer_name)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer(logging_enable = True)
    @recorded_by_proxy_async
    async def test_logging_enabled(self, client, **kwargs):
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        issuer_name = self.get_resource_name("issuer")
        await client.create_issuer(issuer_name=issuer_name, provider="Test")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                # parts of the request are logged on new lines in a single message
                if "'/n" in message.message:
                    request_sections = message.message.split("/n")
                else:
                    request_sections = message.message.split("\n")
                for section in request_sections:
                    try:
                        # the body of the request should be JSON
                        body = json.loads(section)
                        if body["provider"] == "Test":
                            mock_handler.close()
                            return
                    except (ValueError, KeyError):
                        # this means the request section is not JSON
                        pass

        mock_handler.close()
        assert False, "Expected request body wasn't logged"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer(logging_enable = False)
    @recorded_by_proxy_async
    async def test_logging_disabled(self, client, **kwargs):
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        issuer_name = self.get_resource_name("issuer")
        await client.create_issuer(issuer_name=issuer_name, provider="Test")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                # parts of the request are logged on new lines in a single message
                if "'/n" in message.message:
                    request_sections = message.message.split("/n")
                else:
                    request_sections = message.message.split("\n")
                for section in request_sections:
                    try:
                        # the body of the request should be JSON
                        body = json.loads(section)
                        if body["provider"] == "Test":
                            mock_handler.close()
                            assert False, "Client request body was logged"
                    except (ValueError, KeyError):
                        # this means the request section is not JSON
                        pass

        mock_handler.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @AsyncCertificatesClientPreparer(logging_enable = True)
    @recorded_by_proxy_async
    async def test_get_certificate_version(self, client, **kwargs):
        cert_name = self.get_resource_name("cert")
        policy = CertificatePolicy.get_default()
        for _ in range(LIST_TEST_SIZE):
            await client.create_certificate(cert_name, policy)

        async for version_properties in client.list_properties_of_certificate_versions(cert_name):
            cert = await client.get_certificate_version(version_properties.name, version_properties.version)

            # This isn't factored out into a helper method because the properties are not exactly equal.
            # get_certificate_version sets "recovery_days" and "recovery_level" but the list method does not.
            # (This is Key Vault's behavior, not an SDK limitation.)
            assert version_properties.created_on == cert.properties.created_on
            assert version_properties.enabled == cert.properties.enabled
            assert version_properties.expires_on == cert.properties.expires_on
            assert version_properties.id == cert.properties.id
            assert version_properties.name == cert.properties.name
            assert version_properties.not_before == cert.properties.not_before
            assert version_properties.tags == cert.properties.tags
            assert version_properties.updated_on == cert.properties.updated_on
            assert version_properties.vault_url == cert.properties.vault_url
            assert version_properties.version == cert.properties.version
            assert version_properties.x509_thumbprint == cert.properties.x509_thumbprint

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_2016_10_01)
    @AsyncCertificatesClientPreparer(logging_enable = True)
    @recorded_by_proxy_async
    async def test_list_properties_of_certificates(self, client, **kwargs):
        """Tests API version v2016_10_01"""

        certs = client.list_properties_of_certificates()
        async for cert in certs:
            pass

        with pytest.raises(NotImplementedError) as excinfo:
            certs = client.list_properties_of_certificates(include_pending=True)
            async for cert in certs:
                pass

        assert "The 'include_pending' parameter to `list_properties_of_certificates` is only available for API versions v7.0 and up" in str(excinfo.value)

    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_2016_10_01)
    @AsyncCertificatesClientPreparer(logging_enable = True)
    @recorded_by_proxy_async
    async def test_list_deleted_certificates_2016_10_01(self, client, **kwargs):
        """Tests API version v2016_10_01"""

        certs = client.list_deleted_certificates()
        async for cert in certs:
            pass

        with pytest.raises(NotImplementedError) as excinfo:
            certs = client.list_deleted_certificates(include_pending=True)
            async for cert in certs:
                pass

        assert "The 'include_pending' parameter to `list_deleted_certificates` is only available for API versions v7.0 and up" in str(excinfo.value)


@pytest.mark.asyncio
async def test_policy_expected_errors_for_create_cert():
    """Either a subject or subject alternative name property are required for creating a certificate"""
    client = CertificateClient("...", object())

    with pytest.raises(ValueError, match=NO_SAN_OR_SUBJECT):
        policy = CertificatePolicy()
        await client.create_certificate("...", policy=policy)

    with pytest.raises(ValueError, match=NO_SAN_OR_SUBJECT):
        policy = CertificatePolicy(issuer_name=WellKnownIssuerNames.self)
        await client.create_certificate("...", policy=policy)


def test_service_headers_allowed_in_logs():
    service_headers = {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
    client = CertificateClient("...", object())
    assert service_headers.issubset(client._client._config.http_logging_policy.allowed_header_names)


def test_custom_hook_policy():
    class CustomHookPolicy(SansIOHTTPPolicy):
        pass

    client = CertificateClient("...", object(), custom_hook_policy=CustomHookPolicy())
    assert isinstance(client._client._config.custom_hook_policy, CustomHookPolicy)
