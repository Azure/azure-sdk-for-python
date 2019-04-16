# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
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

from msrest import Serializer, Deserializer

from ._models import (
    DeletedSecret,
    DeletedSecretPaged,
    Secret,
    SecretAttributesPaged,
    SecretAttributes,
    _SecretManagementAttributes,
)

from .._internal import _BackupResult


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

        self.vault_url = vault_url
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
        client_models = {
            'DeletedSecret': DeletedSecret,
            'DeletedSecretPaged': DeletedSecretPaged,
            'Secret': Secret,
            'SecretAttributes': SecretAttributes,
            '_SecretManagementAttributes': _SecretManagementAttributes,
            '_BackupResult': _BackupResult,
        }
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._pipeline = Pipeline(transport, policies=policies)

    def get_secret(self, name, version=None, **kwargs):
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
        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name, version or '')])

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

        return self._deserialize('Secret', response)

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
        if all(attribute is None for attribute in (enabled, not_before, expires)):
            management_attributes = None
        else:
            management_attributes = _SecretManagementAttributes(enabled=enabled, not_before=not_before, expires=expires)
        secret = Secret(value=value, content_type=content_type, _management_attributes=management_attributes, tags=tags)

        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name)])

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request_body = self._serialize.body(secret, 'Secret')

        request = HttpRequest('PUT', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('Secret', response)

    def update_secret_attributes(
        self, name, version, content_type=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: () -> SecretAttributes
        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name, version)])

        if all(attribute is None for attribute in (enabled, not_before, expires)):
            management_attributes = None
        else:
            management_attributes = _SecretManagementAttributes(enabled=enabled, not_before=not_before, expires=expires)
        secret = Secret(content_type=content_type, _management_attributes=management_attributes, tags=tags)

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request_body = self._serialize.body(secret, 'Secret')

        request = HttpRequest('PATCH', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('SecretAttributes', response)

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
        url = '{}/secrets'.format(self.vault_url)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        return SecretAttributesPaged(paging, self._deserialize.dependencies)

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

        url = '{}/secrets/{}/versions'.format(self.vault_url, name)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        return SecretAttributesPaged(paging, self._deserialize.dependencies)

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
        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', name, 'backup')])

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

        return self._deserialize('_BackupResult', response).value

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
        backup = _BackupResult(value=backup)

        url = '/'.join([s.strip('/') for s in (self.vault_url, 'secrets', 'restore')])

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }

        request_body = self._serialize.body(backup, '_BackupResult')

        request = HttpRequest('POST', url, headers, data=request_body)

        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return self._deserialize('SecretAttributes', response)

    def delete_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        url = '/'.join([self.vault_url, 'secrets', name])

        request = HttpRequest('DELETE', url)
        request.format_parameters({'api-version': self._api_version})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))
        deleted_secret = self._deserialize('DeletedSecret', response)

        return deleted_secret

    def get_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        url = '/'.join([self.vault_url, 'deletedsecrets', name])

        request = HttpRequest('GET', url)
        request.format_parameters({'api-version': self._api_version})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))
        deleted_secret = self._deserialize('DeletedSecret', response)

        return deleted_secret

    def list_deleted_secrets(self, max_page_size=None, **kwargs):
        # type: (Optional[int], Mapping[str, Any]) -> DeletedSecretPaged
        url = '{}/deletedsecrets'.format(self.vault_url)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        return DeletedSecretPaged(paging, self._deserialize.dependencies)

    def purge_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
        url = '/'.join([self.vault_url, 'deletedsecrets', name])

        request = HttpRequest('DELETE', url)
        request.format_parameters({'api-version': self._api_version})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 204:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        return

    def recover_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> SecretAttributes
        url = '/'.join([self.vault_url, 'deletedsecrets', name, 'recover'])

        request = HttpRequest('POST', url)
        request.format_parameters({'api-version': self._api_version})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        secret_attributes = self._deserialize('SecretAttributes', response)

        return secret_attributes

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
