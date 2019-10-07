# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import itertools
import time

from azure_devtools.scenario_tests import RecordingProcessor, RequestUrlNormalizer

from azure.keyvault.certificates import AdministratorDetails, Contact, CertificatePolicy
from azure.keyvault.certificates._shared import parse_vault_id
from devtools_testutils import ResourceGroupPreparer
from certificates_preparer import VaultClientPreparer
from certificates_test_case import KeyVaultTestCase
from azure.keyvault.certificates._shared._generated.v7_0.models import CertificatePolicy as CertificatePolicyGenerated
from azure.keyvault.certificates._shared._generated.v7_0.models import (
    SecretProperties,
    IssuerParameters,
    X509CertificateProperties,
    KeyProperties,
    SubjectAlternativeNames,
    LifetimeAction,
    Trigger,
    Action,
    ActionType,
    IssuerAttributes,
)
from azure.keyvault.certificates.models import Issuer, IssuerProperties


class RetryAfterReplacer(RecordingProcessor):
    """Replace the retry after wait time in the replay process to 0."""

    def process_response(self, response):
        if "retry-after" in response["headers"]:
            response["headers"]["retry-after"] = "0"
        return response


class CertificateClientTests(KeyVaultTestCase):
    FILTER_HEADERS = [
        "authorization",
        "client-request-id",
        "x-ms-client-request-id",
        "x-ms-correlation-request-id",
        "x-ms-ratelimit-remaining-subscription-reads",
        "x-ms-request-id",
        "x-ms-routing-request-id",
        "x-ms-gateway-service-instanceid",
        "x-ms-ratelimit-remaining-tenant-reads",
        "x-ms-served-by",
        "x-ms-authorization-auxiliary",
    ]

    def __init__(self, *args, **kwargs):
        super(CertificateClientTests, self).__init__(
            *args, replay_processors=[RetryAfterReplacer(), RequestUrlNormalizer()], **kwargs
        )

    def _import_common_certificate(self, client, cert_name):
        cert_content = b"0\x82\t;\x02\x01\x030\x82\x08\xf7\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\x08\xe8\x04\x82\x08\xe40\x82\x08\xe00\x82\x06\t\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\x05\xfa\x04\x82\x05\xf60\x82\x05\xf20\x82\x05\xee\x06\x0b*\x86H\x86\xf7\r\x01\x0c\n\x01\x02\xa0\x82\x04\xfe0\x82\x04\xfa0\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x030\x0e\x04\x08\xf5\xe5\x81\xfd\xa4\xe19\xf0\x02\x02\x07\xd0\x04\x82\x04\xd8.\xb2>H\n\xee\xd9\xd0YE\x04e%\x8e\xd7Cr\xde.F\xa1\xd8W\x11Gw@L;!ght \r\xa8\x06\xb9\x10!\xdb\x0b\xc8\x00\x16g}\xaaa\x1dj\x91lK\x1e\x7f@\xa9x.\xdb\xb0\x04l\xe97\xe7\xeaHM\x96\xa2\xcb\xad\xd8`\x19$\xa5\x1f\xa9\r\xd9\xe0f\xdd}gC\xd6\xacl\x07\x12\xaes\xe8\x11\xd2\xd8b\xf2\xc8\xdf\x12H\xe0\x9bw0\xb3\xed\xb9c\xdf\xee\xc8e\x8a\x0c\x8f\x85\x8e>\x03\xa6\xfe\xd4:S\x8e\x12\x15g\xa4\xe3\xa407l\xde\x03\x88\xbd\xee\xfe\xdf\xb4\xd3g\xb3n\xe6\xb3\x9d\xa3\xa9\xf8N\xbd0=s\xfc2}\x92\x80c\x86\x8a%\xf6\x18Rl\x9c*9\xe7F]5\xdaWR\xdaS\xa4\x01!m\xfa[\xb8@&\xbb\xd8\x86:x\xfbQ\xb9\xd3\xc2\xbel\xd1\xbfjd-\x84\xba\xcfw\x08\xee\x89\x93\xf2q\xcf\xdc<\xa64\xea\x8blZ\xab\xe4\xed\x8c\xd5\x96\x1a,.\xb7C|m\xdd\xe5om\xc3\xe1\xdc\xdd<\x0fXG\x92\x1c\xff(4\xef\x91\x10\x10\xa6\xfa\xd6\xf0\x84\x8a\x9a\x00\xdd\x9b3y\xe4\xf7\xb9\xe7\x11\xdfIa\x81\xee\x03\xf0\xf2\xc6^k\x9e\xc8\xc4\\\xd6\x1d2\xb6\xca\xf4\xec\x96\x8a\x16\xa2\x8b&\x1b\x16\xa7a\x8d\x88\x1b\xf9\xe8\xdcF\xcf9`\xca\x8c\xf6x\x8aV\t{\x92I\xda)\xa6\x97\x13\xf3\xfbg\xb6\x10\xe0\x8a\xa42>\xed\xfc\xd0q\x1c\xf7=7w\x04\xaf\x9b\xb9\xd6|iu\xfcio\xe5:\x02\x92\xf1i\xb1f\x82\xa78\x90MY\xe4\xcdY\x01n\x82i-]\xf7O\x1c\x07q2\x18\xd4^\xa7\x86A\xdf0N\xf6x\x134\r5\xa7\xe8\xbf\t\x08\xec\x85\x7fe\x8a\x1a\xfb\xe4F\xa1\xf5Q\xdd\x96\xd1J M\x17\xa4\xc3\x8f\xfa\x97\x16\xdd07\xf0\x90\x9e\xc1\x80\x99\x00\x066#~\x0f\x89\x98\xee-\xb9v\xd4\xee\xfc\x97;;\x12\xdd\x84\x05\x05\xa4|\x89\xa7*\xd8X\xb7\xef:$\xb9Y\x80^\x101\xe4\x88\xf5\x1a\xff\xc7\x99H\xf071u\x99GTb\xb8;\xee6\xa3#r\xddRK\x07W\x004\xed\x17\xaf%\xfdD\xb5\x92\xc5:\xe7\xbf\x97H/\xba\x97-@\xfe\xeas\xf9~\xf5\xf8.\x07\xa3\xa5\xb4\xef\x9dc\xe5\x93\x13\xeb\x12\xa3\x1a\x1eiy\xee\xccV\xe7n\xc4\x8c\xd7\x8db2\xdd\x84\x9d\xd1\xf2\x13\xddM\x00\xe4\xd2\xc4\xbc\x9fk~Lz&!\xe3D\xbczW[j\xb2\xbbS\xe8\x1b\x06\xb6`\x90GU\x02$\xf2\xea\xb0\xa5C\xbc\x02\r\xc7w\x0f\x03\xf0\x86\xaa\xbeN_`FfP\"\x84i\x8d\xea~\xe0\xbf\xcc8;I4,\xf4\xc0{\x96\x1e~\x05\xcd\xdeoi\x13\xce\xbb7}F\xb4uYh\x9f\xd4V\x00\xcda-\xa3\xba\xc7\x9d\xe2\xbc;\xe9\x95\x8d\xe3V\xa4\xc7d\r\xd0\x94\x9e0\x9a\x87^\xa5s\xe8\x02\x9f\xcf\xc2\x02K\xf7E\x9cA\xb2\x04\xdaW\x88\xc4q\xad\x8f\xd0<\xa8\xbf\xc0\xe3p\xaa\xc6\xc3\xc5\x15\xbb\xbd\x94U*\xce\xfc\xa4\x19\x04\xd2K\x1aJ\x19Y\x93\x91\xa4y\xac\x83X/\xfb\x1e/\xcd\xa9Am\"Z\n\xf5pw\xa5\xa2\xf1\xa3P\xc6\xbb\x9a\xaah]\xf8\x8d\x97d\xb79\x17\xa7K\x99\xaa\x9a~\x15\xf2\x99j*/2;|\x17\xbc\x87\x08\xf9>-\x8aQ\xb1M\x82\xc9\xcfCV\x80\xc0\xea\xb2 \x7f\xeb\x84?\x88\xe9\xa6\x07\xa1\xb3\x1c\x93\xd2RGk\x1d\xad\xf3\xafQ\xda6\x1d\xb1|\x18Qx\xe0\xc0r\x15\xd2\xfa#\xed\xb2X<ae\x165\xce\xa7\xa6V\xf3\xab\x1c\xb0s9\xc5\xfb\x06B\x82\xb6\x16\x9f7\xf1T\xf7\xe1!\xc4\xd5\x95\xd4\xfe\x9b\x8c\xee\xbb\xe2DA\xd8[\xbd\xa9~\x98\x06eB\x0b@\xca!\xb93\xe7w\xcbE\xb4\t\x1b\xaeh\xcb\x0e\x8f\xa4\xf7\x1c{\x1dK\xe0\xa0T\xe24\xd5\xae\xab\xf7\x11\x8e\xbe\xf4\x14\xa3`\xb8\xc3\x13\"\xb8\x9d\xf8|\x1f\x99\xb4hk\x11\rY\xd2\xdc93^j\xc7\x04Gf\xbe\xdf\xb5\x10\xa2R\x83\xe6K+<\x91\xbaE\xd3@\xec\xed\xa9\xce\x9d\xe6\x89\xc0\xd8F\xcf\xfe\xb3o\x1c\x08\x8cN\xff\xf2\x7fw\x89\xec\x80zzE;\x82\xbb\x8f\x89\x9b\xd94a<6^\x0e\xf9og\x16*\xbcF\x9c5 \xc8\x89o4\xf6\x99L\x1ePl\xc8\x9d\xe3\x1e8\xfeQ4,\xb8\xbd\x91\xc3\xd0\x85\x18++N\xce\x9ez\xcc\x81\x9b\xd5\x1a;u\x08\xb1\xa1)K\xfb(W7\xc5]k\xd6\xbc\n\x92\x8b1\x9e\x81\xbd\xf6\x80\xa8M\x0bkz\x07\x17\xe6\xb2\x0c\x8cx$sR\x1d~Q\x89\x91\x9c\xdaX\xc9\x18TS\x89\xe1g\xb2\x9f=4\xf2.\x1dvK${\x9b\xdam\x9b7\xec\xb6\xfc\x8a\x08\x14`\xd0Xg!\xb3jZ\xee\x06\t\xd0\xc8\xae\x1f\xcf\x7f\x05i\xee'Y\x88\xf2\x8aWU~\x0c\xa8\xfd\xf0\x9e=\x1d\xa8\xbc\xe7\xe9\x87\x1fN@\x98\xbe3\xd0h\x16c\xeb\x02\x0f\xbc\x01\x10\xd9\xf9\x1f\xb9\xcb6.\x11\xcfY\xa1U\xfb\x9eJ{-1\x81\xdc0\r\x06\t+\x06\x01\x04\x01\x827\x11\x021\x000\x13\x06\t*\x86H\x86\xf7\r\x01\t\x151\x06\x04\x04\x01\x00\x00\x000W\x06\t*\x86H\x86\xf7\r\x01\t\x141J\x1eH\x00a\x008\x000\x00d\x00f\x00f\x008\x006\x00-\x00e\x009\x006\x00e\x00-\x004\x002\x002\x004\x00-\x00a\x00a\x001\x001\x00-\x00b\x00d\x001\x009\x004\x00d\x005\x00a\x006\x00b\x007\x0070]\x06\t+\x06\x01\x04\x01\x827\x11\x011P\x1eN\x00M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00S\x00t\x00r\x00o\x00n\x00g\x00 \x00C\x00r\x00y\x00p\x00t\x00o\x00g\x00r\x00a\x00p\x00h\x00i\x00c\x00 \x00P\x00r\x00o\x00v\x00i\x00d\x00e\x00r0\x82\x02\xcf\x06\t*\x86H\x86\xf7\r\x01\x07\x06\xa0\x82\x02\xc00\x82\x02\xbc\x02\x01\x000\x82\x02\xb5\x06\t*\x86H\x86\xf7\r\x01\x07\x010\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x060\x0e\x04\x08\xd5\xfeT\xbd\x8c\xc7<\xd6\x02\x02\x07\xd0\x80\x82\x02\x88\xe6D\x13\xbe\x08\xf7\xd55C\xb4\xb3\xe0U\xbb\x08N\xce)\x00\x18\xd0f@sB\x86b\x7f\xa7,\xcfl\xc5\x1b\xc7\xbbN\xebw\x88U':\xee!\x11u\xad\x96\x08I\x95\xc0\xf8\xa0iT$=\xab\xa6\xb1\xfa|\xf8\xbe\xa2W\xf0L\x7f\x94J\x97$Ws\x08t\xbdGn\xd9\x06\xbb\xa9\xa7C\xfa\x01P\xdaI\xe0\x7f\x80\xe4\xea\xf6(\xdb\xfd\x87\xc5\xac\xae!\xfe\xa3\xa7\x07\xbc\xbe\xa9xq\xad\xd9\xb5e\xdf\xb9\x18\xb1\xd9\xfc \x96\xd34l\xcc\xf5\x83\x9f]\xef\x1f\xe0\x957\xcd\xab\x13e\xb2\xdc\xb4\x03\xfa\xd6\xac\xf2c5\xb3\x8fEM\x97\xcaB\xeesp-\x95;X\xb1\r\xf6f\xc9\xae\xeb\xb0;P\xd0p\xea\xd5m\x90E\xe5\x14:\xa1j\xf1!PC\xb7v\xf6*1\x8f\x90/\x1c\xe9f\x104\xab\x8e\x19g\xdf\xde\xc7E\xfa@\x01M+\x9c.[\x10\x9b\xba\x91\xd6\xb2\x0cQ\xc0\xa7\xed\xaf\x1c\xac\xcc\xc1\xec\x02\xf3h5\xc4\xe5\xa9\xc7-y\xef\x9ep\xdc\x13%\x06\xb5\xfc\xc0\xdb\x9e\x13\xba\xfe\xa1\xc0\xed\xc7\xc6\xd6\xa6\x03\xab\xc4\xe1\xeb~o\x18\xd3\x16\xd7\r\xecU.\xe5\xd2\xe1/u\xac\x80\xb0\x11\xd6M\xc3\x82\xda\xd9Lk\x96\xdf\x1e\xb8X\xf0\xe1\x08\xaa>[7\x91\xfdE\xd1r\xf0o\xd6\xdb\x7fm\x8c;\xb59\x88\xc1\x0f'b\x06\xac\xc1\x9f\xc1\xc6\xd44\xa3\xd4\xf8\xdc\xd2G\x7f\xf3gxeM7\xd3\xc2\x85L-\xf2\x19\xc4ZwA\xa7\x10}\x0e\x8bx\x84'\xd1\xdb\xae%\x1b}S\x1b\\\xd1\xce\x17\xe3$\xb5h\x83V\xac\xe7tc\n\x9a\xe2Ru\xf4\xc1*\xf1\x85\xbd\xe8\xc0YS\xb9\x13\x89\xa0.\xfa\x1a2f\xdc\x85\xcd\xc1;\xbb\x0bz\xb6\x87\x9c\x93y\x86\xf3\x01h\xb7\x10#\x7f\r\xf3\xa9\x94}4|\x00\xfe\x80'\xd76\x93\x9dx)\xa0\xcbrY\xb8\xcf\xa2|t\xcc\xfa\xd2u\x1e\xa3\x90\xf7`==\x1b\xa0Z\xbcQ\xf1J\xf2|0]\x0b\xbb\x9c\xce\x171\x1e<4E\x9b\xd9\x87\xf1m\r\xfe\xc1e!\xa6\x1f\x0f\xf1\x96S\xfc8\xe2d.r6\x81\x93\xdeX\xb6\xa3\x86D\x88\xf9\xf2\xd1\x83Z\xbf\"Q\xd1\xf0i\x82\x86\xa9M\xb8\xccg\x91i\xefC\x84U\xcf\xcd\x9b!WVF\xb0\x14\x05E\xaa\x18\x93\"\xc0\xc1\xd2V!t\xe2\xf9\xcd\xfba\xa0\xbc\x15\x14\x84\x9esfK\xbfC\xa2\xedJspo+\x81\x18(\x00\xf6+\x18\xedQ\xe6\xebW^\xf8\x80=\x10\xfb\xd6.'A\x979;)\x06\xf0\x85w\x95S\xd9\x1c9\xcc3k\x03\xf2w\x17\x97\xcc\nN0;0\x1f0\x07\x06\x05+\x0e\x03\x02\x1a\x04\x14\xb1\x82\x1d\xb1\xc8_\xbc\xf1^/\x01\xf7\xc1\x99\x95\xef\xf1<m\xe0\x04\x14\xe0\xef\xcd_\x83#\xc5*\x1dlN\xc0\xa4\xd0\x0c\"\xfa\xedDL\x02\x02\x07\xd0"
        cert_password = "123"
        cert_policy = CertificatePolicyGenerated(
            key_properties=KeyProperties(exportable=True, key_type="RSA", key_size=2048, reuse_key=False),
            secret_properties=SecretProperties(content_type="application/x-pkcs12"),
        )
        return (
            client.import_certificate(
                name=cert_name,
                certificate_bytes=cert_content,
                policy=CertificatePolicy._from_certificate_policy_bundle(cert_policy),
                password=cert_password,
            ),
            cert_policy,
        )

    def _validate_certificate_operation(self, pending_cert_operation, vault, cert_name, cert_policy):
        self.assertIsNotNone(pending_cert_operation)
        self.assertIsNotNone(pending_cert_operation.csr)
        self.assertEqual(cert_policy.issuer_parameters.name, pending_cert_operation.issuer_name)
        pending_id = parse_vault_id(pending_cert_operation.id)
        self.assertEqual(pending_id.vault_endpoint.strip("/"), vault.strip("/"))
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate_bundle(self, cert, cert_name, cert_policy):
        self.assertIsNotNone(cert)
        self.assertEqual(cert_name, cert.name)
        self.assertIsNotNone(cert.cer)
        self.assertIsNotNone(cert.policy)
        self.assertEqual(cert_policy.issuer_parameters.name, cert.policy.issuer_name)
        self.assertEqual(cert_policy.secret_properties.content_type, cert.policy.content_type)
        if cert_policy.x509_certificate_properties.ekus:
            self.assertEqual(cert_policy.x509_certificate_properties.ekus, cert.policy.ekus)
        if cert_policy.x509_certificate_properties.key_usage:
            self.assertEqual(cert_policy.x509_certificate_properties.key_usage, cert.policy.key_usage)
        if cert_policy.x509_certificate_properties:
            self._validate_x509_properties(
                policy=cert.policy, cert_policy_x509_props=cert_policy.x509_certificate_properties
            )
        self._validate_key_properties(policy=cert.policy, cert_policy_key_props=cert_policy.key_properties)
        if cert_policy.lifetime_actions:
            self._validate_lifetime_actions(
                cert_bundle_lifetime_actions=cert.policy.lifetime_actions,
                cert_policy_lifetime_actions=cert_policy.lifetime_actions,
            )

    def _validate_x509_properties(self, policy, cert_policy_x509_props):
        self.assertIsNotNone(policy)
        self.assertEqual(cert_policy_x509_props.subject, policy.subject_name)
        if not cert_policy_x509_props.subject_alternative_names:
            return
        if cert_policy_x509_props.subject_alternative_names.emails:
            policy_emails = policy.san_emails
            for san_email in cert_policy_x509_props.subject_alternative_names.emails:
                for policy_email in policy_emails:
                    if san_email == policy_email:
                        policy_emails.remove(policy_email)
                        break
            self.assertFalse(policy_emails)
        if cert_policy_x509_props.subject_alternative_names.upns:
            policy_upns_list = policy.san_upns
            for san_upns in cert_policy_x509_props.subject_alternative_names.upns:
                for policy_upns in policy_upns_list:
                    if san_upns == policy_upns:
                        policy_upns_list.remove(policy_upns)
                        break
            self.assertFalse(policy_upns_list)
        if cert_policy_x509_props.subject_alternative_names.dns_names:
            policy_dns_names = policy.san_dns_names
            for san_dns_name in cert_policy_x509_props.subject_alternative_names.dns_names:
                for policy_dns_name in policy_dns_names:
                    if san_dns_name == policy_dns_name:
                        policy_dns_names.remove(policy_dns_name)
                        break
            self.assertFalse(policy_dns_names)

    def _validate_key_properties(self, policy, cert_policy_key_props):
        self.assertIsNotNone(policy)
        if policy:
            self.assertEqual(policy.exportable, cert_policy_key_props.exportable)
            self.assertEqual(policy.key_type, cert_policy_key_props.key_type)
            self.assertEqual(policy.key_size, cert_policy_key_props.key_size)
            self.assertEqual(policy.reuse_key, cert_policy_key_props.reuse_key)
            self.assertEqual(policy.curve, cert_policy_key_props.curve)

    def _validate_lifetime_actions(self, cert_bundle_lifetime_actions, cert_policy_lifetime_actions):
        self.assertIsNotNone(cert_bundle_lifetime_actions)
        if cert_policy_lifetime_actions:
            policy_lifetime_actions = cert_bundle_lifetime_actions
            for bundle_lifetime_action in cert_bundle_lifetime_actions:
                for policy_lifetime_action in policy_lifetime_actions:
                    if bundle_lifetime_action == policy_lifetime_action:
                        if policy_lifetime_action.lifetime_percentage:
                            self.assertEqual(
                                bundle_lifetime_action.lifetime_percentage, policy_lifetime_action.lifetime_percentage
                            )
                        if policy_lifetime_action.days_before_expiry:
                            self.assertEqual(
                                bundle_lifetime_action.days_before_expiry, policy_lifetime_action.days_before_expiry
                            )
                        policy_lifetime_actions.remove(policy_lifetime_action)
                        break
            self.assertFalse(policy_lifetime_actions)

    def _validate_certificate_list(self, certificates, expected):
        for cert in certificates:
            if cert.id in expected.keys():
                del expected[cert.id]
            else:
                self.assertTrue(False)
        self.assertEqual(len(expected), 0)

    def _validate_certificate_contacts(self, contacts, expected):
        self.assertEqual(len(contacts), len(expected))
        for contact in contacts:
            exp_contact = next(x for x in expected if x.email == contact.email)
            self.assertEqual(contact.name, exp_contact.name)
            self.assertEqual(contact.phone, exp_contact.phone)

    def _admin_detail_equal(self, admin_detail, exp_admin_detail):
        return (
            admin_detail.first_name == exp_admin_detail.first_name
            and admin_detail.last_name == exp_admin_detail.last_name
            and admin_detail.email == exp_admin_detail.email
            and admin_detail.phone == exp_admin_detail.phone
        )

    def _validate_certificate_issuer(self, issuer, expected):
        self._validate_certificate_issuer_properties(issuer.properties, expected.properties)
        self.assertEqual(issuer.account_id, expected.account_id)
        self.assertEqual(len(issuer.admin_details), len(expected.admin_details))
        for admin_detail in issuer.admin_details:
            exp_admin_detail = next(
                (ad for ad in expected.admin_details if self._admin_detail_equal(admin_detail, ad)), None
            )
            self.assertIsNotNone(exp_admin_detail)
        self.assertEqual(issuer.password, expected.password)
        self.assertEqual(issuer.organization_id, expected.organization_id)

    def _validate_certificate_issuer_properties(self, issuer, expected):
        self.assertEqual(issuer.id, expected.id)
        self.assertEqual(issuer.name, expected.name)
        self.assertEqual(issuer.provider, expected.provider)
        self.assertEqual(issuer.vault_endpoint, expected.vault_endpoint)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_crud_operations(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = self.get_resource_name("cert")
        lifetime_actions = [
            LifetimeAction(trigger=Trigger(days_before_expiry=90), action=Action(action_type=ActionType.auto_renew))
        ]
        cert_policy = CertificatePolicyGenerated(
            key_properties=KeyProperties(exportable=True, key_type="RSA", key_size=2048, reuse_key=True),
            secret_properties=SecretProperties(content_type="application/x-pkcs12"),
            issuer_parameters=IssuerParameters(name="Self"),
            lifetime_actions=lifetime_actions,
            x509_certificate_properties=X509CertificateProperties(
                subject="CN=DefaultPolicy",
                validity_in_months=12,
                key_usage=[
                    "cRLSign",
                    "dataEncipherment",
                    "digitalSignature",
                    "keyAgreement",
                    "keyCertSign",
                    "keyEncipherment",
                ],
            ),
        )

        # create certificate
        certificate = client.create_certificate(name=cert_name).result()
        self._validate_certificate_bundle(cert=certificate, cert_name=cert_name, cert_policy=cert_policy)

        self.assertEqual(client.get_certificate_operation(name=cert_name).status.lower(), "completed")

        # get certificate
        cert = client.get_certificate_with_policy(name=cert_name)
        self._validate_certificate_bundle(cert=cert, cert_name=cert_name, cert_policy=cert_policy)

        # update certificate
        tags = {"tag1": "updated_value1"}
        cert_bundle = client.update_certificate_properties(name=cert_name, tags=tags)
        self._validate_certificate_bundle(cert=cert_bundle, cert_name=cert_name, cert_policy=cert_policy)
        self.assertEqual(tags, cert_bundle.properties.tags)
        self.assertEqual(cert.id, cert_bundle.id)
        self.assertNotEqual(cert.properties.updated, cert_bundle.properties.updated)

        # delete certificate
        deleted_cert_bundle = client.delete_certificate(name=cert_name)
        self._validate_certificate_bundle(cert=deleted_cert_bundle, cert_name=cert_name, cert_policy=cert_policy)

        # get certificate returns not found
        try:
            client.get_certificate(name=cert_name, version=deleted_cert_bundle.properties.version)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
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
            cert_name = self.get_resource_name("cert{}".format(x))
            error_count = 0
            try:
                cert_bundle = self._import_common_certificate(client=client, cert_name=cert_name)[0]
                parsed_id = parse_vault_id(url=cert_bundle.id)
                cid = parsed_id.vault_endpoint + "/" + parsed_id.collection + "/" + parsed_id.name
                expected[cid.strip("/")] = cert_bundle
            except Exception as ex:
                if hasattr(ex, "message") and "Throttled" in ex.message:
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
    def test_list_certificate_versions(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = self.get_resource_name("certver")

        max_certificates = self.list_test_size
        expected = {}

        # import same certificates as different versions
        for x in range(max_certificates):
            error_count = 0
            try:
                cert_bundle = self._import_common_certificate(client=client, cert_name=cert_name)[0]
                parsed_id = parse_vault_id(url=cert_bundle.id)
                cid = (
                    parsed_id.vault_endpoint
                    + "/"
                    + parsed_id.collection
                    + "/"
                    + parsed_id.name
                    + "/"
                    + parsed_id.version
                )
                expected[cid.strip("/")] = cert_bundle
            except Exception as ex:
                if hasattr(ex, "message") and "Throttled" in ex.message:
                    error_count += 1
                    time.sleep(2.5 * error_count)
                    continue
                else:
                    raise ex

        # list certificate versions
        self._validate_certificate_list(certificates=(client.list_certificate_versions(cert_name)), expected=expected)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_crud_contacts(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        contact_list = [
            Contact(email="admin@contoso.com", name="John Doe", phone="1111111111"),
            Contact(email="admin2@contoso.com", name="John Doe2", phone="2222222222"),
        ]

        # create certificate contacts
        contacts = client.create_contacts(contacts=contact_list)
        self._validate_certificate_contacts(contacts=contacts, expected=contact_list)

        # get certificate contacts
        contacts = client.get_contacts()
        self._validate_certificate_contacts(contacts=contacts, expected=contact_list)

        # delete certificate contacts
        contacts = client.delete_contacts()
        self._validate_certificate_contacts(contacts=contacts, expected=contact_list)

        # get certificate contacts returns not found
        try:
            client.get_contacts()
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_recover_and_purge(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        certs = {}
        # create certificates to recover
        for i in range(self.list_test_size):
            cert_name = self.get_resource_name("certrec{}".format(str(i)))
            certs[cert_name] = self._import_common_certificate(client=client, cert_name=cert_name)

        # create certificates to purge
        for i in range(self.list_test_size):
            cert_name = self.get_resource_name("certprg{}".format(str(i)))
            certs[cert_name] = self._import_common_certificate(client=client, cert_name=cert_name)

        # delete all certificates
        for cert_name in certs.keys():
            client.delete_certificate(name=cert_name)

        if not self.is_playback():
            time.sleep(30)

        # validate all our deleted certificates are returned by list_deleted_certificates
        deleted = [parse_vault_id(url=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(all(c in deleted for c in certs.keys()))

        # recover select certificates
        for certificate_name in [c for c in certs.keys() if c.startswith("certrec")]:
            client.recover_deleted_certificate(name=certificate_name)

        # purge select certificates
        for certificate_name in [c for c in certs.keys() if c.startswith("certprg")]:
            client.purge_deleted_certificate(name=certificate_name)

        if not self.is_playback():
            time.sleep(30)

        # validate none of our deleted certificates are returned by list_deleted_certificates
        deleted = [parse_vault_id(url=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(not any(c in deleted for c in certs.keys()))

        # validate the recovered certificates
        expected = {k: v for k, v in certs.items() if k.startswith("certrec")}
        actual = {k: client.get_certificate(name=k, version="") for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_async_request_cancellation_and_deletion(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        cert_name = "asyncCanceledDeletedCert"
        cert_policy = CertificatePolicyGenerated(
            key_properties=KeyProperties(exportable=True, key_type="RSA", key_size=2048, reuse_key=False),
            secret_properties=SecretProperties(content_type="application/x-pkcs12"),
            issuer_parameters=IssuerParameters(name="Self"),
            x509_certificate_properties=X509CertificateProperties(
                subject="CN=*.microsoft.com",
                subject_alternative_names=SubjectAlternativeNames(dns_names=["sdk.azure-int.net"]),
                validity_in_months=24,
            ),
        )

        # create certificate
        create_certificate_poller = client.create_certificate(
            name=cert_name, policy=CertificatePolicy._from_certificate_policy_bundle(cert_policy)
        )

        # cancel certificate operation
        cancel_operation = client.cancel_certificate_operation(name=cert_name)
        self.assertTrue(hasattr(cancel_operation, "cancellation_requested"))
        self.assertTrue(cancel_operation.cancellation_requested)
        self._validate_certificate_operation(
            pending_cert_operation=cancel_operation,
            vault=client.vault_endpoint,
            cert_name=cert_name,
            cert_policy=cert_policy,
        )

        self.assertEqual(create_certificate_poller.result().status.lower(), "cancelled")

        retrieved_operation = client.get_certificate_operation(name=cert_name)
        self.assertTrue(hasattr(retrieved_operation, "cancellation_requested"))
        self.assertTrue(retrieved_operation.cancellation_requested)
        self._validate_certificate_operation(
            pending_cert_operation=retrieved_operation,
            vault=client.vault_endpoint,
            cert_name=cert_name,
            cert_policy=cert_policy,
        )

        # delete certificate operation
        deleted_operation = client.delete_certificate_operation(name=cert_name)
        self.assertIsNotNone(deleted_operation)
        self._validate_certificate_operation(
            pending_cert_operation=deleted_operation,
            vault=client.vault_endpoint,
            cert_name=cert_name,
            cert_policy=cert_policy,
        )

        try:
            client.get_certificate_operation(name=cert_name)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

        # delete cancelled certificate
        client.delete_certificate(cert_name)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_policy(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates

        cert_name = "policyCertificate"

        # get certificate policy
        self._import_common_certificate(client=client, cert_name=cert_name)
        retrieved_policy = client.get_policy(certificate_name=cert_name)
        self.assertIsNotNone(retrieved_policy)

        # update certificate policy
        cert_policy = CertificatePolicyGenerated(
            key_properties=KeyProperties(exportable=True, key_type="RSA", key_size=2048, reuse_key=False),
            secret_properties=SecretProperties(content_type="application/x-pkcs12"),
            issuer_parameters=IssuerParameters(name="Self"),
        )

        client.update_policy(
            certificate_name=cert_name, policy=CertificatePolicy._from_certificate_policy_bundle(cert_policy)
        )
        updated_cert_policy = client.get_policy(certificate_name=cert_name)
        self.assertIsNotNone(updated_cert_policy)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_get_pending_certificate_signing_request(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = "unknownIssuerCert"
        cert_policy = CertificatePolicyGenerated(
            key_properties=KeyProperties(exportable=True, key_type="RSA", key_size=2048, reuse_key=False),
            secret_properties=SecretProperties(content_type="application/x-pkcs12"),
            issuer_parameters=IssuerParameters(name="Self"),
            x509_certificate_properties=X509CertificateProperties(
                subject="CN=*.microsoft.com",
                subject_alternative_names=SubjectAlternativeNames(dns_names=["sdk.azure-int.net"]),
                validity_in_months=24,
            ),
        )

        # get pending certiificate signing request
        certificate = client.create_certificate(
            name=cert_name, policy=CertificatePolicy._from_certificate_policy_bundle(cert_policy)
        ).wait()
        pending_version_csr = client.get_pending_certificate_signing_request(name=cert_name)
        try:
            self.assertEqual(client.get_certificate_operation(name=cert_name).csr, pending_version_csr)
        except Exception as ex:
            pass
        finally:
            client.delete_certificate(name=cert_name)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_backup_restore(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = self.get_resource_name("cert")
        lifetime_actions = [
            LifetimeAction(trigger=Trigger(lifetime_percentage=2), action=Action(action_type=ActionType.email_contacts))
        ]
        cert_policy = CertificatePolicyGenerated(
            key_properties=KeyProperties(exportable=True, key_type="RSA", key_size=2048, reuse_key=False),
            secret_properties=SecretProperties(content_type="application/x-pkcs12"),
            issuer_parameters=IssuerParameters(name="Self"),
            lifetime_actions=lifetime_actions,
            x509_certificate_properties=X509CertificateProperties(
                subject="CN=*.microsoft.com",
                # commented out for now because of server side bug not
                # restoring san dns names
                # subject_alternative_names=SubjectAlternativeNames(
                #     dns_names=['sdk.azure-int.net']
                # ),
                validity_in_months=24,
            ),
        )

        # create certificate
        create_certificate_poller = client.create_certificate(
            name=cert_name, policy=CertificatePolicy._from_certificate_policy_bundle(cert_policy)
        )
        create_certificate_poller.wait()

        # create a backup
        certificate_backup = client.backup_certificate(name=cert_name)

        # delete the certificate
        client.delete_certificate(name=cert_name)

        # restore certificate
        restored_certificate = client.restore_certificate(backup=certificate_backup)
        self._validate_certificate_bundle(cert=restored_certificate, cert_name=cert_name, cert_policy=cert_policy)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_merge_certificate(self, vault_client, **kwargs):
        import base64
        import os
        from OpenSSL import crypto

        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        cert_name = "mergeCertificate"
        issuer_name = "Unknown"
        cert_policy = CertificatePolicyGenerated(
            issuer_parameters=IssuerParameters(name=issuer_name, certificate_transparency=False),
            x509_certificate_properties=X509CertificateProperties(subject="CN=MyCert"),
        )
        dirname = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.abspath(os.path.join(dirname, "ca.key")), "rt") as f:
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
        with open(os.path.abspath(os.path.join(dirname, "ca.crt")), "rt") as f:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

        client.create_certificate(
            name=cert_name, policy=CertificatePolicy._from_certificate_policy_bundle(cert_policy)
        ).wait()

        csr = (
            "-----BEGIN CERTIFICATE REQUEST-----\n"
            + base64.b64encode(client.get_certificate_operation(name=cert_name).csr).decode()
            + "\n-----END CERTIFICATE REQUEST-----"
        )
        req = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr)

        cert = crypto.X509()
        cert.set_serial_number(1)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(60)  # Testing certificates need not be long lived
        cert.set_issuer(ca_cert.get_subject())
        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())
        cert.sign(pkey, "sha256")
        signed_certificate_bytes = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode().replace("\n", "")
        signed_certificate_bytes = signed_certificate_bytes.lstrip("-----BEGIN CERTIFICATE-----")
        signed_certificate_bytes = signed_certificate_bytes.rstrip("-----END CERTIFICATE-----")

        client.merge_certificate(name=cert_name, x509_certificates=[signed_certificate_bytes.encode()])

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_crud_issuer(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.certificates
        issuer_name = "issuer"
        admin_details = [
            AdministratorDetails(first_name="John", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        properties = IssuerProperties(
            issuer_id=client.vault_endpoint + "/certificates/issuers/" + issuer_name, provider="Test"
        )

        # create certificate issuer
        issuer = client.create_issuer(
            name=issuer_name, provider="Test", account_id="keyvaultuser", admin_details=admin_details, enabled=True
        )

        expected = Issuer(
            properties=properties,
            account_id="keyvaultuser",
            admin_details=admin_details,
            attributes=IssuerAttributes(enabled=True),
        )

        self._validate_certificate_issuer(issuer=issuer, expected=expected)

        # get certificate issuer
        issuer = client.get_issuer(name=issuer_name)
        self._validate_certificate_issuer(issuer=issuer, expected=expected)

        # list certificate issuers

        client.create_issuer(
            name=issuer_name + "2",
            provider="Test",
            account_id="keyvaultuser2",
            admin_details=admin_details,
            enabled=True,
        )

        expected_base_1 = IssuerProperties(
            issuer_id=client.vault_endpoint + "/certificates/issuers/" + issuer_name, provider="Test"
        )

        expected_base_2 = IssuerProperties(
            issuer_id=client.vault_endpoint + "/certificates/issuers/" + issuer_name + "2", provider="Test"
        )
        expected_issuers = [expected_base_1, expected_base_2]

        issuers = list(client.list_issuers())
        self.assertEqual(len(issuers), len(expected_issuers))
        for issuer in issuers:
            exp_issuer = next((i for i in expected_issuers if i.name == issuer.name), None)
            self.assertIsNotNone(exp_issuer)
            self._validate_certificate_issuer_properties(issuer=issuer, expected=exp_issuer)

        # update certificate issuer
        admin_details = [
            AdministratorDetails(first_name="Jane", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        expected = Issuer(
            properties=properties,
            account_id="keyvaultuser",
            admin_details=admin_details,
            attributes=IssuerAttributes(enabled=True),
        )
        issuer = client.update_issuer(name=issuer_name, admin_details=admin_details)
        self._validate_certificate_issuer(issuer=issuer, expected=expected)

        # delete certificate issuer
        client.delete_issuer(name=issuer_name)

        # get certificate issuer returns not found
        try:
            client.get_issuer(name=issuer_name)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex
