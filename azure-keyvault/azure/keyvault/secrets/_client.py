# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import Mapping, Any
import uuid

from azure.core.configuration import Configuration
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RetryPolicy,
    RedirectPolicy,
)
from azure.core.pipeline.transport import RequestsTransport, HttpRequest
from azure.core.pipeline import Pipeline
from azure.core.exceptions import ClientRequestError
from azure.keyvault._internal import _BearerTokenCredentialPolicy

from .._generated import DESERIALIZE, SERIALIZE
from .._generated.v7_0.models import (
    DeletedSecretItemPaged,
    SecretItemPaged,
    SecretRestoreParameters,
    SecretSetParameters,
    SecretUpdateParameters,
)
from .._generated.v7_0.models import SecretAttributes as _SecretAttributes

from ._models import (
    Secret,
    DeletedSecret,
    SecretAttributes,
)


class SecretClient:

    _api_version = '7.0'

    @staticmethod
    def create_config(**kwargs):
        config = Configuration(**kwargs)
        config.user_agent = UserAgentPolicy('SecretClient', **kwargs)
        config.headers = None
        config.retry = RetryPolicy(**kwargs)
        config.redirect = RedirectPolicy(**kwargs)
        return config

    def __init__(self, vault_url, credentials, config=None, **kwargs):
        """Creates a SecretClient with the for managing secrets in the specified vault.

        :param credentials:  A credential or credential provider which can be used to authenticate to the vault
        :type credentials: azure.authenctication.Credential or azure.authenctication.CredentialProvider
        :param str vault_url: The url of the vault
        :param azure.core.configuration.Configuration config:  The configuration for the SecretClient
        """
        if not credentials:
            raise ValueError('credentials')

        if not vault_url:
            raise ValueError('vault_url')

        self._vault_url = vault_url
        config = config or SecretClient.create_config(**kwargs)
        transport = RequestsTransport(config.connection)
        policies = [
            config.user_agent,
            config.headers,
            _BearerTokenCredentialPolicy(credentials),
            config.redirect,
            config.retry,
            config.logging,
        ]
        self._pipeline = Pipeline(transport, policies=policies)

    @property
    def vault_url(self):
        return self._vault_url

    def get_secret(self, name, version, **kwargs):
        """Get a specified from the vault.

        The GET operation is applicable to any secret stored in Azure Key
        Vault. This operation requires the secrets/get permission.

        :param str name: The name of the secret.
        :param str version: The version of the secret.  If not specified the latest version of
            the secret is returned
        :return: Secret
        :rtype: ~azure.keyvault.secrets.Secret
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.KeyVaultErrorException>`
        """
        url = '/'.join((self._vault_url, 'secrets', name, version))

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request = HttpRequest('GET', url, headers)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return Secret.from_secret_bundle(bundle)

    def set_secret(
        self, name, value, content_type=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs
    ):
        """Sets a secret in the vault.

        The SET operation adds a secret to the Azure Key Vault. If the named
        secret already exists, Azure Key Vault creates a new version of that
        secret. This operation requires the secrets/set permission.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :param str content_type: Type of the secret value such as a password
        :param attributes: The secret management attributes
        :type attributes: ~azure.keyvault.secrets.SecretAttributes
        :param dict[str, str] tags: Application specific metadata in the form of key-value
            deserialized response
        :param operation_config: :ref:`Operation configuration
            overrides<msrest:optionsforoperations>`.
        :return: The created secret
        :rtype: ~azure.keyvault.secret.Secret
        :raises:
        :class:`azure.core.ClientRequestError`
        """
        url = '/'.join((self._vault_url, 'secrets', name))

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        attributes = _SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        secret = SecretSetParameters(secret_attributes=attributes, value=value, tags=tags, content_type=content_type)
        request_body = SERIALIZE.body(secret, 'SecretSetParameters')

        request = HttpRequest('PUT', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return Secret.from_secret_bundle(bundle)

    def update_secret_attributes(
        self, name, version, content_type=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs
    ):
        url = '/'.join((self._vault_url, 'secrets', name, version))

        attributes = _SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        secret = SecretUpdateParameters(secret_attributes=attributes, tags=tags, content_type=content_type)

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request_body = SERIALIZE.body(secret, 'Secret')

        request = HttpRequest('PATCH', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return SecretAttributes.from_secret_bundle(bundle)

    def list_secrets(self, max_page_size=None, **kwargs):
        """List secrets in the vault.

        The Get Secrets operation is applicable to the entire vault. However,
        only the latest secret identifier and its attributes are provided in the
        response. No secret values are returned and individual secret versions are
        not listed in the response.  This operation requires the secrets/list permission.

        :param max_page_size: Maximum number of results to return in a page. If
         not max_page_size, the service will return up to 25 results.
        :type maxresults: int
        :return: An iterator like instance of Secrets
        :rtype:
         ~azure.keyvault.secrets.SecretAttributesPaged[~azure.keyvault.secret.Secret]
        :raises:
         :class:`ClientRequestError<azure.core.ClientRequestError>`
        """
        url = '{}/secrets'.format(self._vault_url)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = SecretItemPaged(paging, DESERIALIZE.dependencies)
        return (SecretAttributes.from_secret_item(item) for item in pages)

    def list_secret_versions(self, name, max_page_size=None, **kwargs):
        """List all versions of the specified secret.

        The full secret identifier and attributes are provided in the response.
        No values are returned for the secrets. This operations requires the
        secrets/list permission.

        :param name: The name of the secret.
        :type name: str
        :param max_page_size: Maximum number of results to return in a page. If
         not max_page_size, the service will return up to 25 results.
        :type maxresults: int
        :return: An iterator like instance of Secret
        :rtype:
         ~azure.keyvault.secrets.SecretAttributesPaged[~azure.keyvault.secret.Secret]
        :raises:
         :class:`ClientRequestError<azure.core.ClientRequestError>`
        """

        url = '{}/secrets/{}/versions'.format(self._vault_url, name)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = SecretItemPaged(paging, DESERIALIZE.dependencies)
        return (SecretAttributes.from_secret_item(item) for item in pages)

    def backup_secret(self, name, **kwargs):
        """Backs up the specified secret.

        Requests that a backup of the specified secret be downloaded to the
        client. All versions of the secret will be downloaded. This operation
        requires the secrets/backup permission.

        :param str name: The name of the secret.
        :return: The raw bytes of the secret backup.
        :rtype: bytes
        :raises:
         :class:azure.core.ClientRequestError
        """
        url = '/'.join((self._vault_url, 'secrets', name, 'backup'))

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request = HttpRequest('POST', url, headers)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        result = DESERIALIZE('BackupSecretResult', response)

        return result.value

    def restore_secret(self, backup, **kwargs):
        """Restores a backed up secret to a vault.

        Restores a backed up secret, and all its versions, to a vault. This
        operation requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
        :return: The restored secret
        :rtype: ~azure.keyvault.secrets.Secret
        :raises:
         :class:azure.core.ClientRequestError
        """
        url = '/'.join((self._vault_url, 'secrets', 'restore'))

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        restore_parameters = SecretRestoreParameters(secret_bundle_backup=backup)
        request_body = SERIALIZE.body(restore_parameters, 'SecretRestoreParameters')

        request = HttpRequest('POST', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return SecretAttributes.from_secret_bundle(bundle)

    def delete_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        url = '/'.join([self._vault_url, 'secrets', name])

        request = HttpRequest('DELETE', url)
        request.format_parameters({'api-version': self._api_version})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        bundle = DESERIALIZE('DeletedSecretBundle', response)

        return DeletedSecret.from_deleted_secret_bundle(bundle)

    def get_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        url = '/'.join([self._vault_url, 'deletedsecrets', name])

        request = HttpRequest('GET', url)
        request.format_parameters({'api-version': self._api_version})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        bundle = DESERIALIZE('DeletedSecretBundle', response)

        return DeletedSecret.from_deleted_secret_bundle(bundle)

    def list_deleted_secrets(self, max_page_size=None, **kwargs):
        # type: (Optional[int], Mapping[str, Any]) -> DeletedSecretPaged
        url = '{}/deletedsecrets'.format(self._vault_url)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = DeletedSecretItemPaged(paging, DESERIALIZE.dependencies)
        return (DeletedSecret.from_deleted_secret_item(item) for item in pages)

    def purge_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
        url = '/'.join([self._vault_url, 'deletedsecrets', name])

        request = HttpRequest('DELETE', url)
        request.format_parameters({'api-version': self._api_version})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 204:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))
        return

    def recover_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> SecretAttributes
        url = '/'.join([self._vault_url, 'deletedsecrets', name, 'recover'])

        request = HttpRequest('POST', url)
        request.format_parameters({'api-version': self._api_version})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return SecretAttributes.from_secret_bundle(bundle)

    def _internal_paging(self, url, max_page_size, next_link=None, raw=False, **kwargs):
        # type: (str, int, Optional[str], Optional[bool], Mapping[str, Any]) -> HttpResponse
        if next_link:
            url = next_link
            query_parameters = {}
        else:
            query_parameters = {'api-version': self._api_version}
            if max_page_size is not None:
                query_parameters['maxresults'] = str(max_page_size)

        headers = {'x-ms-client-request-id': str(uuid.uuid1())}

        request = HttpRequest('GET', url, headers)
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        return response
