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

<<<<<<< HEAD
try:
    KeyVaultClient.__doc__ = _KeyVaultClient.__doc__
except (AttributeError, TypeError):
    pass
=======
    def purge_deleted_certificate(
            self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        """Permanently deletes the specified deleted certificate.

        The PurgeDeletedCertificate operation performs an irreversible deletion
        of the specified certificate, without possibility for recovery. The
        operation is not available if the recovery level does not specify
        'Purgeable'. Requires the explicit granting of the 'purge' permission.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param certificate_name: The name of the certificate
        :type certificate_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: None
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        # Construct URL
        url = '/deletedcertificates/{certificate-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'certificate-name': self._serialize.url("certificate_name", certificate_name, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [204]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        if raw:
            client_raw_response = ClientRawResponse(None, response)
            return client_raw_response

    def recover_deleted_certificate(
            self, vault_base_url, certificate_name, custom_headers=None, raw=False, **operation_config):
        """Recovers the deleted certificate back to its current version under
        /certificates.

        The RecoverDeletedCertificate operation performs the reversal of the
        Delete operation. The operation is applicable in vaults enabled for
        soft-delete, and must be issued during the retention interval
        (available in the deleted certificate's attributes).

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param certificate_name: The name of the deleted certificate
        :type certificate_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`CertificateBundle
         <azure.keyvault.models.CertificateBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        # Construct URL
        url = '/deletedcertificates/{certificate-name}/recover'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'certificate-name': self._serialize.url("certificate_name", certificate_name, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('CertificateBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def get_storage_accounts(
            self, vault_base_url, maxresults=None, custom_headers=None, raw=False, **operation_config):
        """List storage accounts managed by specified key vault.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param maxresults: Maximum number of results to return in a page. If
         not specified the service will return up to 25 results.
        :type maxresults: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`StorageAccountItemPaged
         <azure.keyvault.models.StorageAccountItemPaged>`
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        def internal_paging(next_link=None, raw=False):

            if not next_link:
                # Construct URL
                url = '/storage'
                path_format_arguments = {
                    'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True)
                }
                url = self._client.format_url(url, **path_format_arguments)

                # Construct parameters
                query_parameters = {}
                if maxresults is not None:
                    query_parameters['maxresults'] = self._serialize.query("maxresults", maxresults, 'int', maximum=25, minimum=1)
                query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

            else:
                url = next_link
                query_parameters = {}

            # Construct headers
            header_parameters = {}
            header_parameters['Content-Type'] = 'application/json; charset=utf-8'
            if self.config.generate_client_request_id:
                header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
            if custom_headers:
                header_parameters.update(custom_headers)
            if self.config.accept_language is not None:
                header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

            # Construct and send request
            request = self._client.get(url, query_parameters)
            response = self._client.send(
                request, header_parameters, **operation_config)

            if response.status_code not in [200]:
                raise models.KeyVaultErrorException(self._deserialize, response)

            return response

        # Deserialize response
        deserialized = models.StorageAccountItemPaged(internal_paging, self._deserialize.dependencies)

        if raw:
            header_dict = {}
            client_raw_response = models.StorageAccountItemPaged(internal_paging, self._deserialize.dependencies, header_dict)
            return client_raw_response

        return deserialized

    def delete_storage_account(
            self, vault_base_url, storage_account_name, custom_headers=None, raw=False, **operation_config):
        """Deletes a storage account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`StorageBundle <azure.keyvault.models.StorageBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        # Construct URL
        url = '/storage/{storage-account-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('StorageBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def get_storage_account(
            self, vault_base_url, storage_account_name, custom_headers=None, raw=False, **operation_config):
        """Gets information about a specified storage account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`StorageBundle <azure.keyvault.models.StorageBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        # Construct URL
        url = '/storage/{storage-account-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('StorageBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def set_storage_account(
            self, vault_base_url, storage_account_name, resource_id, active_key_name, auto_regenerate_key, regeneration_period=None, storage_account_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        """Creates or updates a new storage account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param resource_id: Storage account resource id.
        :type resource_id: str
        :param active_key_name: Current active storage account key name.
        :type active_key_name: str
        :param auto_regenerate_key: whether keyvault should manage the storage
         account for the user.
        :type auto_regenerate_key: bool
        :param regeneration_period: The key regeneration time duration
         specified in ISO-8601 format.
        :type regeneration_period: str
        :param storage_account_attributes: The attributes of the storage
         account.
        :type storage_account_attributes: :class:`StorageAccountAttributes
         <azure.keyvault.models.StorageAccountAttributes>`
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: dict
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`StorageBundle <azure.keyvault.models.StorageBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        parameters = models.StorageAccountCreateParameters(resource_id=resource_id, active_key_name=active_key_name, auto_regenerate_key=auto_regenerate_key, regeneration_period=regeneration_period, storage_account_attributes=storage_account_attributes, tags=tags)

        # Construct URL
        url = '/storage/{storage-account-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct body
        body_content = self._serialize.body(parameters, 'StorageAccountCreateParameters')

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('StorageBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def update_storage_account(
            self, vault_base_url, storage_account_name, active_key_name=None, auto_regenerate_key=None, regeneration_period=None, storage_account_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        """Updates the specified attributes associated with the given storage
        account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param active_key_name: The current active storage account key name.
        :type active_key_name: str
        :param auto_regenerate_key: whether keyvault should manage the storage
         account for the user.
        :type auto_regenerate_key: bool
        :param regeneration_period: The key regeneration time duration
         specified in ISO-8601 format.
        :type regeneration_period: str
        :param storage_account_attributes: The attributes of the storage
         account.
        :type storage_account_attributes: :class:`StorageAccountAttributes
         <azure.keyvault.models.StorageAccountAttributes>`
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: dict
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`StorageBundle <azure.keyvault.models.StorageBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        parameters = models.StorageAccountUpdateParameters(active_key_name=active_key_name, auto_regenerate_key=auto_regenerate_key, regeneration_period=regeneration_period, storage_account_attributes=storage_account_attributes, tags=tags)

        # Construct URL
        url = '/storage/{storage-account-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct body
        body_content = self._serialize.body(parameters, 'StorageAccountUpdateParameters')

        # Construct and send request
        request = self._client.patch(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('StorageBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def regenerate_storage_account_key(
            self, vault_base_url, storage_account_name, key_name, custom_headers=None, raw=False, **operation_config):
        """Regenerates the specified key value for the given storage account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param key_name: The storage account key name.

        :type key_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`StorageBundle <azure.keyvault.models.StorageBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        parameters = models.StorageAccountRegenerteKeyParameters(key_name=key_name)

        # Construct URL
        url = '/storage/{storage-account-name}/regeneratekey'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct body
        body_content = self._serialize.body(parameters, 'StorageAccountRegenerteKeyParameters')

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('StorageBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def get_sas_definitions(
            self, vault_base_url, storage_account_name, maxresults=None, custom_headers=None, raw=False, **operation_config):
        """List storage SAS definitions for the given storage account.
        
        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param maxresults: Maximum number of results to return in a page. If
         not specified the service will return up to 25 results.
        :type maxresults: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`SasDefinitionItemPaged
         <azure.keyvault.models.SasDefinitionItemPaged>`
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        def internal_paging(next_link=None, raw=False):

            if not next_link:
                # Construct URL
                url = '/storage/{storage-account-name}/sas'
                path_format_arguments = {
                    'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
                    'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$')
                }
                url = self._client.format_url(url, **path_format_arguments)

                # Construct parameters
                query_parameters = {}
                if maxresults is not None:
                    query_parameters['maxresults'] = self._serialize.query("maxresults", maxresults, 'int', maximum=25, minimum=1)
                query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

            else:
                url = next_link
                query_parameters = {}

            # Construct headers
            header_parameters = {}
            header_parameters['Content-Type'] = 'application/json; charset=utf-8'
            if self.config.generate_client_request_id:
                header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
            if custom_headers:
                header_parameters.update(custom_headers)
            if self.config.accept_language is not None:
                header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

            # Construct and send request
            request = self._client.get(url, query_parameters)
            response = self._client.send(
                request, header_parameters, **operation_config)

            if response.status_code not in [200]:
                raise models.KeyVaultErrorException(self._deserialize, response)

            return response

        # Deserialize response
        deserialized = models.SasDefinitionItemPaged(internal_paging, self._deserialize.dependencies)

        if raw:
            header_dict = {}
            client_raw_response = models.SasDefinitionItemPaged(internal_paging, self._deserialize.dependencies, header_dict)
            return client_raw_response

        return deserialized

    def delete_sas_definition(
            self, vault_base_url, storage_account_name, sas_definition_name, custom_headers=None, raw=False, **operation_config):

        """Deletes a SAS definition from a specified storage account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param sas_definition_name: The name of the SAS definition.
        :type sas_definition_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`SasDefinitionBundle
         <azure.keyvault.models.SasDefinitionBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        # Construct URL
        url = '/storage/{storage-account-name}/sas/{sas-definition-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$'),
            'sas-definition-name': self._serialize.url("sas_definition_name", sas_definition_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('SasDefinitionBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def get_sas_definition(
            self, vault_base_url, storage_account_name, sas_definition_name, custom_headers=None, raw=False, **operation_config):

        """Gets information about a SAS definition for the specified storage
        account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param sas_definition_name: The name of the SAS definition.
        :type sas_definition_name: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`SasDefinitionBundle
         <azure.keyvault.models.SasDefinitionBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        # Construct URL
        url = '/storage/{storage-account-name}/sas/{sas-definition-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$'),
            'sas-definition-name': self._serialize.url("sas_definition_name", sas_definition_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('SasDefinitionBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def set_sas_definition(
            self, vault_base_url, storage_account_name, sas_definition_name, parameters, sas_definition_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        """Creates or updates a new SAS definition for the specified storage
        account.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param sas_definition_name: The name of the SAS definition.
        :type sas_definition_name: str
        :param parameters: Sas definition creation metadata in the form of
         key-value pairs.
        :type parameters: dict
        :param sas_definition_attributes: The attributes of the SAS
         definition.
        :type sas_definition_attributes: :class:`SasDefinitionAttributes
         <azure.keyvault.models.SasDefinitionAttributes>`
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: dict
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`SasDefinitionBundle
         <azure.keyvault.models.SasDefinitionBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        parameters1 = models.SasDefinitionCreateParameters(parameters=parameters, sas_definition_attributes=sas_definition_attributes, tags=tags)

        # Construct URL
        url = '/storage/{storage-account-name}/sas/{sas-definition-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$'),
            'sas-definition-name': self._serialize.url("sas_definition_name", sas_definition_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct body
        body_content = self._serialize.body(parameters1, 'SasDefinitionCreateParameters')

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('SasDefinitionBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized

    def update_sas_definition(
            self, vault_base_url, storage_account_name, sas_definition_name, parameters=None, sas_definition_attributes=None, tags=None, custom_headers=None, raw=False, **operation_config):
        """Updates the specified attributes associated with the given SAS
        definition.

        :param vault_base_url: The vault name, for example
         https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param storage_account_name: The name of the storage account.
        :type storage_account_name: str
        :param sas_definition_name: The name of the SAS definition.
        :type sas_definition_name: str
        :param parameters: Sas definition update metadata in the form of
         key-value pairs.
        :type parameters: dict
        :param sas_definition_attributes: The attributes of the SAS
         definition.
        :type sas_definition_attributes: :class:`SasDefinitionAttributes
         <azure.keyvault.models.SasDefinitionAttributes>`
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: dict
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :rtype: :class:`SasDefinitionBundle
         <azure.keyvault.models.SasDefinitionBundle>`
        :rtype: :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
         if raw=true
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.models.KeyVaultErrorException>`
        """
        parameters1 = models.SasDefinitionUpdateParameters(parameters=parameters, sas_definition_attributes=sas_definition_attributes, tags=tags)

        # Construct URL
        url = '/storage/{storage-account-name}/sas/{sas-definition-name}'
        path_format_arguments = {
            'vaultBaseUrl': self._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'storage-account-name': self._serialize.url("storage_account_name", storage_account_name, 'str', pattern='^[0-9a-zA-Z]+$'),
            'sas-definition-name': self._serialize.url("sas_definition_name", sas_definition_name, 'str', pattern='^[0-9a-zA-Z]+$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct body
        body_content = self._serialize.body(parameters1, 'SasDefinitionUpdateParameters')

        # Construct and send request
        request = self._client.patch(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, **operation_config)

        if response.status_code not in [200]:
            raise models.KeyVaultErrorException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('SasDefinitionBundle', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
>>>>>>> 91a4d87dcf30f501115b9dd2dea7aef7a6017cd3
