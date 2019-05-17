# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import Any, Dict, Generator, Mapping, Optional
from datetime import datetime
import uuid

from azure.core.configuration import Configuration
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RetryPolicy,
    RedirectPolicy,
)
from azure.core.pipeline.transport import RequestsTransport, HttpRequest, HttpResponse
from azure.core.pipeline import Pipeline
from azure.core.exceptions import HttpResponseError
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
    """SecretClient defines a high level interface for
    managing secrets in the specified vault.

    :param credentials:  A credential or credential provider which can be used to authenticate to the vault,
        a ValueError will be raised if the entity is not provided
    :type credentials: azure.authentication.Credential or azure.authentication.CredentialProvider
    :param str vault_url: The url of the vault to which the client will connect,
        a ValueError will be raised if the entity is not provided
    :param ~azure.core.configuration.Configuration config:  The configuration for the SecretClient

    Example:
        .. literalinclude:: ../tests/test_examples_keyvault.py
            :start-after: [START create_secret_client]
            :end-before: [END create_secret_client]
            :language: python
            :dedent: 4
            :caption: Creates a new instance of the Secret client
    """
    _api_version = "7.0"

    @staticmethod
    def create_config(**kwargs):
        """Creates a default configuration for SecretClient.
        """
        config = Configuration(**kwargs)
        config.user_agent = UserAgentPolicy('SecretClient', **kwargs)
        config.headers = None
        config.retry = RetryPolicy(**kwargs)
        config.redirect = RedirectPolicy(**kwargs)
        return config

    def __init__(self, vault_url, credentials, config=None, **kwargs):
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
        # type: () -> str
        return self._vault_url

    def get_secret(self, name, version, **kwargs):
        # type: (str, str, Mapping[str, Any]) -> Secret
        """Get a specified secret from the vault.

        The GET operation is applicable to any secret stored in Azure Key
        Vault. This operation requires the secrets/get permission.

        :param str name: The name of the secret.
        :param str version: The version of the secret. If version is None or the empty string, the latest version of
            the secret is returned
        :returns: An instance of Secret
        :rtype: ~azure.keyvault.secrets._models.Secret
        :raises: ~azure.core.exceptions.HttpResponseError if the client failed to get the secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START get_secret]
                :end-before: [END get_secret]
                :language: python
                :dedent: 4
                :caption: Get secret from the key vault

        """
        if version is None:
            version = ""
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
            raise HttpResponseError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return Secret._from_secret_bundle(bundle)

    def set_secret(
            self, name, value, content_type=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: (str, str, Optional[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Secret
        """Sets a secret in the vault.

        The SET operation adds a secret to the Azure Key Vault. If the named
        secret already exists, Azure Key Vault creates a new version of that
        secret. This operation requires the secrets/set permission.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :param str content_type: Type of the secret value such as a password
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date of the secret  in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict(str, str)
        :returns: The created secret
        :rtype: ~azure.keyvault.secrets._models.Secret
        :raises: ~azure.core.exceptions.HttpResponseError if the client failed to create the secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START set_secret]
                :end-before: [END set_secret]
                :language: python
                :dedent: 4
                :caption: Set a secret in the key vault

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
            raise HttpResponseError('Request failed status code {}.  {}'.format(
                response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return Secret._from_secret_bundle(bundle)

    def update_secret_attributes(
            self, name, version, content_type=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: (str, str, Optional[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> SecretAttributes
        """Updates the attributes associated with a specified secret in the key vault.

        The UPDATE operation changes specified attributes of an existing stored secret.
        Attributes that are not specified in the request are left unchanged. The value
        of a secret itself cannot be changed. This operation requires the secrets/set permission.

        :param str name: The name of the secret
        :param str version: The version of the secret.
        :param str content_type: Type of the secret value such as a password
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret  in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date  of the secret in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict(str, str)
        :returns: The created secret
        :rtype: ~azure.keyvault.secrets._models.SecretAttributes
        :raises: ~azure.core.exceptions.HttpResponseError if the client failed to create the secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START update_secret_attributes]
                :end-before: [END update_secret_attributes]
                :language: python
                :dedent: 4
                :caption: Updates the attributes associated with a specified secret in the key vault

        """
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
            raise HttpResponseError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return SecretAttributes._from_secret_bundle(bundle)

    def list_secrets(self, **kwargs):
        # type: (Mapping[str, Any]) -> Generator[SecretAttributes]
        """List secrets in the vault.

        The Get Secrets operation is applicable to the entire vault. However,
        only the latest secret identifier and its attributes are provided in the
        response. No secret values are returned and individual secret versions are
        not listed in the response.  This operation requires the secrets/list permission.

        :returns: An iterator like instance of Secrets
        :rtype:
         ~azure.keyvault.secrets._models.SecretAttributesPaged[~azure.keyvault.secrets._models.SecretAttributes]

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START list_secrets]
                :end-before: [END list_secrets]
                :language: python
                :dedent: 4
                :caption: Lists all the secrets in the vault

        """
        url = '{}/secrets'.format(self._vault_url)
        max_page_size = kwargs.get("max_page_size", None)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = SecretItemPaged(paging, DESERIALIZE.dependencies)
        return (SecretAttributes._from_secret_item(item) for item in pages)

    def list_secret_versions(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Generator[SecretAttributes]
        """List all versions of the specified secret.

        The full secret identifier and attributes are provided in the response.
        No values are returned for the secrets. This operations requires the
        secrets/list permission.

        :param str name: The name of the secret.
        :returns: An iterator like instance of Secret
        :rtype:
         ~azure.keyvault.secrets._models.SecretAttributesPaged[~azure.keyvault.secrets._models.SecretAttributes]

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START list_secret_versions]
                :end-before: [END list_secret_versions]
                :language: python
                :dedent: 4
                :caption: List all versions of the specified secret

        """

        url = '{}/secrets/{}/versions'.format(self._vault_url, name)
        max_page_size = kwargs.get("max_page_size", None)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = SecretItemPaged(paging, DESERIALIZE.dependencies)
        return (SecretAttributes._from_secret_item(item) for item in pages)

    def backup_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> bytes
        """Backs up the specified secret.

        Requests that a backup of the specified secret be downloaded to the
        client. All versions of the secret will be downloaded. This operation
        requires the secrets/backup permission.

        :param str name: The name of the secret.
        :returns: The raw bytes of the secret backup.
        :rtype: bytes
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to back up the secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START backup_secret]
                :end-before: [END backup_secret]
                :language: python
                :dedent: 4
                :caption: Backs up the specified secret

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
            raise HttpResponseError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        result = DESERIALIZE('BackupSecretResult', response)

        return result.value

    def restore_secret(self, backup, **kwargs):
        # type: (bytes, Mapping[str, Any]) -> SecretAttributes
        """Restore a backed up secret to the vault.

        Restores a backed up secret, and all its versions, to a vault. This
        operation requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
        :returns: The restored secret
        :rtype: ~azure.keyvault.secrets._models.SecretAttributes
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to restore the secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START restore_secret]
                :end-before: [END restore_secret]
                :language: python
                :dedent: 4
                :caption: Restores a backed up secret to the vault

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
            raise HttpResponseError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return SecretAttributes._from_secret_bundle(bundle)

    def delete_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        """Deletes a secret from the vault.

        The DELETE operation applies to any secret stored in Azure Key Vault.
        DELETE cannot be applied to an individual version of a secret. This
        operation requires the secrets/delete permission.

        :param str name: The name of the secret
        :return: The deleted secret.
        :rtype: ~azure.keyvault.secrets._models.DeletedSecret
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to delete the secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START delete_secret]
                :end-before: [END delete_secret]
                :language: python
                :dedent: 4
                :caption: Deletes a secret

        """
        url = '/'.join([self._vault_url, 'secrets', name])

        request = HttpRequest('DELETE', url)
        request.format_parameters({'api-version': self._api_version})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise HttpResponseError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        bundle = DESERIALIZE('DeletedSecretBundle', response)

        return DeletedSecret._from_deleted_secret_bundle(bundle)

    def get_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        """Gets the specified deleted secret.

        The Get Deleted Secret operation returns the specified deleted secret
        along with its attributes. This operation requires the secrets/get permission.

        :param str name: The name of the secret
        :return: The deleted secret.
        :rtype: ~azure.keyvault.secrets._models.DeletedSecret
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to get the deleted secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START get_deleted_secret]
                :end-before: [END get_deleted_secret]
                :language: python
                :dedent: 4
                :caption: Gets the deleted secret

        """
        url = "/".join([self.vault_url, "deletedsecrets", name])

        request = HttpRequest('GET', url)
        request.format_parameters({'api-version': self._api_version})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise HttpResponseError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        bundle = DESERIALIZE('DeletedSecretBundle', response)

        return DeletedSecret._from_deleted_secret_bundle(bundle)

    def list_deleted_secrets(self, **kwargs):
        # type: (Mapping[str, Any]) -> Generator[DeletedSecret]
        """Lists deleted secrets of the vault.

        The Get Deleted Secrets operation returns the secrets that have
        been deleted for a vault enabled for soft-delete. This
        operation requires the secrets/list permission.

        :returns: An iterator like instance of DeletedSecrets
        :rtype:
         ~azure.keyvault.secrets._models.DeletedSecretPaged[~azure.keyvault.secrets._models.DeletedSecret]

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START list_deleted_secrets]
                :end-before: [END list_deleted_secrets]
                :language: python
                :dedent: 4
                :caption: Lists the deleted secrets of the vault

        """
        url = '{}/deletedsecrets'.format(self._vault_url)
        max_page_size = kwargs.get("max_page_size", None)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = DeletedSecretItemPaged(paging, DESERIALIZE.dependencies)
        return (DeletedSecret._from_deleted_secret_item(item) for item in pages)

    def purge_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
        """Permanently deletes the specified secret.

        The purge deleted secret operation removes the secret permanently, without the
        possibility of recovery. This operation can only be enabled on a soft-delete enabled
        vault. This operation requires the secrets/purge permission.

        :param str name: The name of the secret
        :returns: None
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to return the purged secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START purge_deleted_secret]
                :end-before: [END purge_deleted_secret]
                :language: python
                :dedent: 4
                :caption: Restores a backed up secret to the vault

        """
        url = "/".join([self.vault_url, "deletedsecrets", name])

        request = HttpRequest('DELETE', url)
        request.format_parameters({'api-version': self._api_version})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 204:
            raise HttpResponseError("Request failed with code {}: '{}'".format(response.status_code, response.text()))
        return

    def recover_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> SecretAttributes
        """Recovers the deleted secret to the latest version.

        Recovers the deleted secret in the specified vault.
        This operation can only be performed on a soft-delete enabled
        vault. This operation requires the secrets/recover permission.

        :param str name: The name of the secret
        :returns: The recovered deleted secret
        :rtype: ~azure.keyvault.secrets._models.SecretAttributes
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to recover the deleted secret

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START recover_deleted_secret]
                :end-before: [END recover_deleted_secret]
                :language: python
                :dedent: 4
                :caption: Restores a backed up secret to the vault

        """
        url = "/".join([self.vault_url, "deletedsecrets", name, "recover"])

        request = HttpRequest('POST', url)
        request.format_parameters({'api-version': self._api_version})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise HttpResponseError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        bundle = DESERIALIZE('SecretBundle', response)

        return SecretAttributes._from_secret_bundle(bundle)

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
            raise HttpResponseError("Request failed with code {}: '{}'".format(response.status_code, response.text()))

        return response
