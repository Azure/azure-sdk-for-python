#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import uuid
import re

from msrest.pipeline import ClientRawResponse

from azure.keyvault.generated import KeyVaultClient as _KeyVaultClient
from azure.keyvault.generated.models import KeyVaultErrorException
from .key_vault_id import *


# Pattern to detect vault/key/version parameters in generated code
_DOC_PATTERNS = {
    re.compile(r"( +):param vault_base_url:.+:param key_name:.+:type key_version:[^\n]+",
               re.MULTILINE+re.DOTALL):
        "\\1:param key_identifier: The key identifier\n\\1:type key_identifier: str",
    re.compile(r"( +):param vault_base_url:.+:param certificate_name:.+:type certificate_version:[^\n]+",
               re.MULTILINE + re.DOTALL):
        "\\1:param certificate_identifier: The certificate identifier\n\\1:type certificate_identifier: str",
    re.compile(r"( +):param vault_base_url:.+:param secret_name:.+:type secret_version:[^\n]+",
               re.MULTILINE + re.DOTALL):
        "\\1:param secret_identifier: The secret identifier\n\\1:type secret_identifier: str",
}


def _patch_docstring(docstring):
    """Patch the documentation to replace vault/name/version by KeyVaultId.

    :param str docstring: The Autorest generated DocString
    :rtype: str
    """
    for pattern, subs in _DOC_PATTERNS.items():
        replaced, count = pattern.subn(subs, docstring)
        if count:
            return replaced
    return docstring


class KeyVaultClient(object):

    def __init__(self, credentials):
        self.keyvault = _KeyVaultClient(credentials)

    def create_key(self, vault_base_url, key_name, kty, key_size=None, key_ops=None, key_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.create_key(vault_base_url, key_name, kty, key_size, key_ops, key_attributes, tags, custom_headers, raw, **operation_config)
    create_key.__doc__ = _KeyVaultClient.create_key.__doc__

    def import_key(self, vault_base_url, key_name, key, hsm=None, key_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.import_key(vault_base_url, key_name, key, hsm, key_attributes, tags, custom_headers, raw, **operation_config)
    import_key.__doc__ = _KeyVaultClient.import_key.__doc__

    def delete_key(self, vault_base_url, key_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.delete_key(vault_base_url, key_name, custom_headers, raw, **operation_config)
    delete_key.__doc__ = _KeyVaultClient.delete_key.__doc__

    def update_key(self, key_identifier, key_ops=None, key_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.update_key(kid.vault, kid.name, kid.version or '', key_ops, key_attributes, tags, custom_headers, raw, **operation_config)
    update_key.__doc__ = _patch_docstring(_KeyVaultClient.update_key.__doc__)

    def get_key(self, key_identifier, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.get_key(kid.vault, kid.name, kid.version or '', custom_headers, raw, **operation_config)
    get_key.__doc__ = _patch_docstring(_KeyVaultClient.get_key.__doc__)

    def get_key_versions(self, vault_base_url, key_name, maxresults=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_key_versions(vault_base_url, key_name, maxresults, custom_headers, raw, **operation_config)
    get_key_versions.__doc__ = _KeyVaultClient.get_key_versions.__doc__

    def get_keys(self, vault_base_url, maxresults=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_keys(vault_base_url, maxresults, custom_headers, raw, **operation_config)
    get_keys.__doc__ = _KeyVaultClient.get_keys.__doc__

    def backup_key(self, vault_base_url, key_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.backup_key(vault_base_url, key_name, custom_headers, raw, **operation_config)
    backup_key.__doc__ = _KeyVaultClient.backup_key.__doc__

    def restore_key(self, vault_base_url, key_bundle_backup, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.restore_key(vault_base_url, key_bundle_backup, custom_headers, raw, **operation_config)
    restore_key.__doc__ = _KeyVaultClient.restore_key.__doc__

    def encrypt(self, key_identifier, algorithm, value, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.encrypt(kid.vault, kid.name, kid.version or '', algorithm, value, custom_headers, raw, **operation_config)
    encrypt.__doc__ = _patch_docstring(_KeyVaultClient.encrypt.__doc__)

    def decrypt(self, key_identifier, algorithm, value, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.decrypt(kid.vault, kid.name, kid.version or '', algorithm, value, custom_headers, raw, **operation_config)
    decrypt.__doc__ = _patch_docstring(_KeyVaultClient.decrypt.__doc__)

    def sign(self, key_identifier, algorithm, value, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.sign(kid.vault, kid.name, kid.version or '', algorithm, value, custom_headers, raw, **operation_config)
    sign.__doc__ = _patch_docstring(_KeyVaultClient.sign.__doc__)

    def verify(self, key_identifier, algorithm, digest, signature, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.verify(kid.vault, kid.name, kid.version or '', algorithm, digest, signature, custom_headers, raw, **operation_config)
    verify.__doc__ = _patch_docstring(_KeyVaultClient.verify.__doc__)

    def wrap_key(self, key_identifier, algorithm, value, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.wrap_key(kid.vault, kid.name, kid.version or '', algorithm, value, custom_headers, raw, **operation_config)
    wrap_key.__doc__ = _patch_docstring(_KeyVaultClient.wrap_key.__doc__)

    def unwrap_key(self, key_identifier, algorithm, value, custom_headers=None, raw=False, **operation_config):
        kid = parse_key_id(key_identifier)
        return self.keyvault.unwrap_key(kid.vault, kid.name, kid.version or '', algorithm, value, custom_headers, raw, **operation_config)
    unwrap_key.__doc__ = _patch_docstring(_KeyVaultClient.unwrap_key.__doc__)

    def set_secret(self, vault_base_url, secret_name, value, tags=None, content_type=None, secret_attributes=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.set_secret(vault_base_url, secret_name, value, tags, content_type, secret_attributes, custom_headers, raw, **operation_config)
    set_secret.__doc__ = _KeyVaultClient.set_secret.__doc__

    def delete_secret(self, vault_base_url, secret_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.delete_secret(vault_base_url, secret_name, custom_headers, raw, **operation_config)
    delete_secret.__doc__ = _KeyVaultClient.delete_secret.__doc__

    def update_secret(self, secret_identifer, content_type=None, secret_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        sid = parse_secret_id(secret_identifer)
        return self.keyvault.update_secret(sid.vault, sid.name, sid.version or '', content_type, secret_attributes, tags, custom_headers, raw, **operation_config)
    update_secret.__doc__ = _patch_docstring(_KeyVaultClient.update_secret.__doc__)

    def get_secret(self, secret_identifer, custom_headers=None, raw=False, **operation_config):
        sid = parse_secret_id(secret_identifer)
        return self.keyvault.get_secret(sid.vault, sid.name, sid.version or '', custom_headers, raw, **operation_config)
    get_secret.__doc__ = _patch_docstring(_KeyVaultClient.get_secret.__doc__)

    def get_secrets(self, vault_base_url, maxresults=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_secrets(vault_base_url, maxresults, custom_headers, raw, **operation_config)
    get_secrets.__doc__ = _KeyVaultClient.get_secrets.__doc__

    def get_secret_versions(self, vault_base_url, secret_name, maxresults=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_secret_versions(vault_base_url, secret_name, maxresults, custom_headers, raw, **operation_config)
    get_secret_versions.__doc__ = _KeyVaultClient.get_secret_versions.__doc__

    def create_certificate(self, vault_base_url, certificate_name, certificate_policy=None, certificate_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.create_certificate(vault_base_url, certificate_name, certificate_policy, certificate_attributes, tags, custom_headers, raw, **operation_config)
    create_certificate.__doc__ = _KeyVaultClient.create_certificate.__doc__

    def update_certificate(self, certificate_identifier, certificate_policy=None, certificate_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        cid = parse_certificate_id(certificate_identifier)
        return self.keyvault.update_certificate(cid.vault, cid.name, cid.version or '', certificate_policy, certificate_attributes, tags, custom_headers, raw, **operation_config)
    update_certificate.__doc__ = _patch_docstring(_KeyVaultClient.update_certificate.__doc__)

    def delete_certificate(self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.delete_certificate(vault_base_url, certificate_name, custom_headers, raw, **operation_config)
    delete_certificate.__doc__ = _KeyVaultClient.delete_certificate.__doc__

    def get_certificate(self, certificate_identifier, custom_headers=None, raw=False, **operation_config):
        cid = parse_certificate_id(certificate_identifier)
        return self.keyvault.get_certificate(cid.vault, cid.name, cid.version or '', custom_headers, raw, **operation_config)
    get_certificate.__doc__ = _patch_docstring(_KeyVaultClient.get_certificate.__doc__)

    def get_certificates(self, vault_base_url, maxresults=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_certificates(vault_base_url, maxresults, custom_headers, raw, **operation_config)
    get_certificates.__doc__ = _KeyVaultClient.get_certificates.__doc__

    def merge_certificate(self, vault_base_url, certificate_name, x509_certificates, certificate_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.merge_certificate(vault_base_url, certificate_name, x509_certificates, certificate_attributes, tags, custom_headers, raw, **operation_config)
    merge_certificate.__doc__ = _KeyVaultClient.merge_certificate.__doc__

    def import_certificate(self, vault_base_url, certificate_name, base64_encoded_certificate, password=None, certificate_policy=None, certificate_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.import_certificate(vault_base_url, certificate_name, base64_encoded_certificate, password, certificate_policy, certificate_attributes, tags, custom_headers, raw, **operation_config)
    import_certificate.__doc__ = _KeyVaultClient.import_certificate.__doc__

    def get_certificate_versions(self, vault_base_url, certificate_name, maxresults=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_certificate_versions(vault_base_url, certificate_name, maxresults, custom_headers, raw, **operation_config)
    get_certificate_versions.__doc__ = _KeyVaultClient.get_certificate_versions.__doc__

    # pylint: disable=redefined-builtin
    def set_certificate_contacts(self, vault_base_url, contact_list=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.set_certificate_contacts(vault_base_url, contact_list, custom_headers, raw, **operation_config)
    set_certificate_contacts.__doc__ = _KeyVaultClient.set_certificate_contacts.__doc__

    def get_certificate_contacts(self, vault_base_url, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_certificate_contacts(vault_base_url, custom_headers, raw, **operation_config)
    get_certificate_contacts.__doc__ = _KeyVaultClient.get_certificate_contacts.__doc__

    def delete_certificate_contacts(self, vault_base_url, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.delete_certificate_contacts(vault_base_url, custom_headers, raw, **operation_config)
    delete_certificate_contacts.__doc__ = _KeyVaultClient.delete_certificate_contacts.__doc__

    def get_certificate_issuers(self, vault_base_url, maxresults=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_certificate_issuers(vault_base_url, maxresults, custom_headers, raw, **operation_config)
    get_certificate_issuers.__doc__ = _KeyVaultClient.get_certificate_issuers.__doc__

    def set_certificate_issuer(self, vault_base_url, issuer_name, provider, credentials=None, organization_details=None, attributes=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.set_certificate_issuer(vault_base_url, issuer_name, provider, credentials, organization_details, attributes, custom_headers, raw, **operation_config)
    set_certificate_issuer.__doc__ = _KeyVaultClient.set_certificate_issuer.__doc__

    def update_certificate_issuer(self, vault_base_url, issuer_name, provider=None, credentials=None, organization_details=None, attributes=None, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.update_certificate_issuer(vault_base_url, issuer_name, provider, credentials, organization_details, attributes, custom_headers, raw, **operation_config)
    update_certificate_issuer.__doc__ = _KeyVaultClient.update_certificate_issuer.__doc__

    def get_certificate_issuer(self, vault_base_url, issuer_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_certificate_issuer(vault_base_url, issuer_name, custom_headers, raw, **operation_config)
    get_certificate_issuer.__doc__ = _KeyVaultClient.get_certificate_issuer.__doc__

    def delete_certificate_issuer(self, vault_base_url, issuer_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.delete_certificate_issuer(vault_base_url, issuer_name, custom_headers, raw, **operation_config)
    delete_certificate_issuer.__doc__ = _KeyVaultClient.delete_certificate_issuer.__doc__

    def get_certificate_policy(self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_certificate_policy(vault_base_url, certificate_name, custom_headers, raw, **operation_config)
    get_certificate_policy.__doc__ = _KeyVaultClient.get_certificate_policy.__doc__

    def update_certificate_policy(self, vault_base_url, certificate_name, certificate_policy, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.update_certificate_policy(vault_base_url, certificate_name, certificate_policy, custom_headers, raw, **operation_config)
    update_certificate_policy.__doc__ = _KeyVaultClient.update_certificate_policy.__doc__

    def update_certificate_operation(self, vault_base_url, certificate_name, cancellation_requested, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.update_certificate_operation(vault_base_url, certificate_name, cancellation_requested, custom_headers, raw, **operation_config)
    update_certificate_operation.__doc__ = _KeyVaultClient.update_certificate_operation.__doc__

    def get_certificate_operation(self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.get_certificate_operation(vault_base_url, certificate_name, custom_headers, raw, **operation_config)
    get_certificate_operation.__doc__ = _KeyVaultClient.get_certificate_operation.__doc__

    def delete_certificate_operation(self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        return self.keyvault.delete_certificate_operation(vault_base_url, certificate_name, custom_headers, raw, **operation_config)
    delete_certificate_operation.__doc__ = _KeyVaultClient.delete_certificate_operation.__doc__

    def get_pending_certificate_signing_request(self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        """Gets the Base64 pending certificate signing request (PKCS-10).

        :param vault_base_url: The vault name, e.g.
         https://myvault.vault.azure.net
        :type vault_base_url: str
        :param certificate_name: The name of the certificate
        :type certificate_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Base64 encoded pending certificate signing request (PKCS-10).
        :rtype: str
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        """
        # Construct URL
        url = '/certificates/{certificate-name}/pending'
        path_format_arguments = {
            'vaultBaseUrl': self.keyvault._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'certificate-name': self.keyvault._serialize.url("certificate_name", certificate_name, 'str')
        }
        url = self.keyvault._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self.keyvault._serialize.query("self.keyvault.api_version", self.keyvault.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        header_parameters['Accept'] = 'application/pkcs10'
        if self.keyvault.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.keyvault.config.accept_language is not None:
            header_parameters['accept-language'] = self.keyvault._serialize.header("self.keyvault.config.accept_language", self.keyvault.config.accept_language, 'str')

        # Construct and send request
        request = self.keyvault._client.get(url, query_parameters)
        response = self.keyvault._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [200]:
            raise KeyVaultErrorException(self.keyvault._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = response.content

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

try:
    KeyVaultClient.__doc__ = _KeyVaultClient.__doc__
except (AttributeError, TypeError):
    pass
