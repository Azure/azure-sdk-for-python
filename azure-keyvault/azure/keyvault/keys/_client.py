# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import Any, Dict, Generator, Mapping, Optional, List
from datetime import datetime
import uuid

from azure.core.configuration import Configuration
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RetryPolicy,
    RedirectPolicy,)
from azure.core.pipeline.transport import RequestsTransport, HttpRequest, HttpResponse
from azure.core.pipeline import Pipeline
from azure.core.exceptions import ClientRequestError
from azure.keyvault._internal import _BearerTokenCredentialPolicy

from .._generated import DESERIALIZE, SERIALIZE
from ._models import (
    Key,
    DeletedKey,
    KeyAttributes,
)
from .._generated.v7_0.models import (
    BackupKeyResult,
    DeletedKeyBundle,
    DeletedKeyItem,
    DeletedKeyItemPaged,
    KeyCreateParameters,
    KeyItemPaged,
    KeyRestoreParameters,
    KeyUpdateParameters,
)
from .._generated.v7_0.models import KeyAttributes as _KeyAttributes


class KeyClient:
    _api_version = "7.0"

    @staticmethod
    def create_config(**kwargs):
        # type: (Any) -> Configuration
        config = Configuration(**kwargs)
        config.user_agent = UserAgentPolicy('KeyClient', **kwargs)
        config.headers = None
        config.retry = RetryPolicy(**kwargs)
        config.redirect = RedirectPolicy(**kwargs)

        return config

    def __init__(self, vault_url, credentials, config=None, transport=None, **kwargs):
        # type: (str, Any, Configuration, HttpTransport) -> None

        if not credentials:
            raise ValueError('credentials')

        if not vault_url:
            raise ValueError('vault_url')

        self.vault_url = vault_url.strip('/')   # do we need to strip these
        config = config or KeyClient.create_config(**kwargs)
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

    def create_key(
        self,
        name,
        key_type,
        size=None,
        key_ops=None,
        enabled=None,
        expires=None,
        not_before=None,
        tags=None,
        curve=None,
        **kwargs
    ):
        # type: (str, str, Optional[int], Optional[List[str]], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Optional[str], Mapping[str, Any]) -> Key
        """Creates a new key, stores it, then returns key attributes to the client.

        The create key operation can be used to create any key type in Azure
        Key Vault. If the named key already exists, Azure Key Vault creates a
        new version of the key. It requires the keys/create permission.

        :param name: The name for the new key. The system will generate
         the version name for the new key.
        :type name
        :param key_type: The type of key to create. For valid values, see
         JsonWebKeyType. Possible values include: 'EC', 'EC-HSM', 'RSA',
         'RSA-HSM', 'oct'
        :type key_type: str or ~azure.keyvault._generated.v7_0.models.JsonWebKeyType
        :param size: The key size in bits. For example: 2048, 3072, or
         4096 for RSA.
        :type size: int
        :param key_ops: Supported key operations.
        :type key_ops: list[str or
         ~~azure.keyvault._generated.v7_0.models.JsonWebKeyOperation]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key  in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :param curve: Elliptic curve name. For valid values, see
         JsonWebKeyCurveName. Possible values include: 'P-256', 'P-384',
         'P-521', 'SECP256K1'
        :type curve: str or
         ~~azure.keyvault._generated.v7_0.models.JsonWebKeyCurveName
        :returns: The created key
        :rtype: ~azure.keyvault.keys._models.Key
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to create the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START create_key]
                :end-before: [END create_key]
                :language: python
                :dedent: 4
                :caption: Creates a key in the key vault
        """
        url = '/'.join([self.vault_url, 'keys', name, 'create'])
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1()),
        }
        attributes = _KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)

        key = KeyCreateParameters(
            kty=key_type,
            key_size=size,
            key_ops=key_ops,
            key_attributes=attributes,
            tags=tags,
            curve=curve,
            **kwargs
        )
        query_parameters = {'api-version': self._api_version}
        request_body = SERIALIZE.body(key, 'KeyCreateParameters')
        request = HttpRequest('POST', url, headers, data=request_body)
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('KeyBundle', response)

        return Key._from_key_bundle(bundle)

    def delete_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedKey
        """Deletes a key of any type from storage in Azure Key Vault.

        The delete key operation cannot be used to remove individual versions
        of a key. This operation removes the cryptographic material associated
        with the key, which means the key is not usable for Sign/Verify,
        Wrap/Unwrap or Encrypt/Decrypt operations. This operation requires the
        keys/delete permission.

        :param name: The name of the key to delete.
        :type name
        :returns: The deleted key
        :rtype: ~azure.keyvault.keys._models.DeletedKey
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to delete the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START delete_key]
                :end-before: [END delete_key]
                :language: python
                :dedent: 4
                :caption: Deletes a key in the key vault
        """
        url = '/'.join([self.vault_url, 'keys', name])

        request = HttpRequest('DELETE', url)
        query_parameters = {'api-version': self._api_version}
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('DeletedKeyBundle', response)

        return DeletedKey._from_deleted_key_bundle(bundle)

    def get_key(self, name, version, **kwargs) -> Key:
        # type: (str, str, Mapping[str, Any]) -> Key

        """Gets the public part of a stored key.

        The get key operation is applicable to all key types. If the requested
        key is symmetric, then no key material is released in the response.
        This operation requires the keys/get permission.

        :param name: The name of the key to get.
        :type name
        :param version: Retrieves a specific version of a key. If the version is None or an empty string, the latest version of
            the key is returned
        :type version
        :returns: Key
        :rtype: ~azure.keyvault.keys._models.Key
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START get_key]
                :end-before: [END get_key]
                :language: python
                :dedent: 4
                :caption: Retrieves a key from the key vault
        """
        if version is None:
            version = ""

        url = '/'.join([self.vault_url, 'keys', name, version])
        request = HttpRequest('GET', url)

        query_parameters = {'api-version': self._api_version}
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('KeyBundle', response)

        return Key._from_key_bundle(bundle)

    def get_deleted_key(self, name, **kwargs) -> DeletedKey:
        # type: (str, Mapping[str, Any]) -> DeletedKey

        """Gets the public part of a deleted key.

        The Get Deleted Key operation is applicable for soft-delete enabled
        vaults. While the operation can be invoked on any vault, it will return
        an error if invoked on a non soft-delete enabled vault. This operation
        requires the keys/get permission.

        :param name: The name of the key.
        :type name
        :returns: The deleted key
        :rtype: ~azure.keyvault.keys._models.DeletedKey
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START get_deleted_key]
                :end-before: [END get_deleted_key]
                :language: python
                :dedent: 4
                :caption: Retrieves a deleted key from the key vault
        """
        url = '/'.join([self.vault_url, 'deletedkeys', name])

        request = HttpRequest('GET', url)
        query_parameters = {'api-version': self._api_version}
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('DeletedKeyBundle', response)

        return DeletedKey._from_deleted_key_bundle(bundle)      # Ques: Deleted key requires key, but DeletedkeyItem deosn't return?

    def list_deleted_keys(self, **kwargs):
        # type: (str, Mapping[str, Any]) -> Generator[DeletedKey]

        """Lists the deleted keys in the specified vault.

        Retrieves a list of the keys in the Key Vault as JSON Web Key
        structures that contain the public part of a deleted key. This
        operation includes deletion-specific information. The Get Deleted Keys
        operation is applicable for vaults enabled for soft-delete. While the
        operation can be invoked on any vault, it will return an error if
        invoked on a non soft-delete enabled vault. This operation requires the
        keys/list permission.

        :returns: An iterator like instance of DeletedKey
        :rtype:
         typing.Generator[~azure.keyvault.keys._models.DeletedKey]
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START list_deleted_keys]
                :end-before: [END list_deleted_keys]
                :language: python
                :dedent: 4
                :caption: List all the deleted keys in the vault
        """
        url = '{}/deletedkeys'.format(self.vault_url)
        max_page_size = kwargs.get("max_page_size", None)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = DeletedKeyItemPaged(paging, DESERIALIZE.dependencies)
        return (DeletedKey._from_deleted_key_item(item) for item in pages)

    def list_keys(self, **kwargs):
        # type: (str, Mapping[str, Any]) -> Generator[Key]

        """List keys in the specified vault.

        Retrieves a list of the keys in the Key Vault as JSON Web Key
        structures that contain the public part of a stored key. The LIST
        operation is applicable to all key types, however only the base key
        identifier, attributes, and tags are provided in the response.
        Individual versions of a key are not listed in the response. This
        operation requires the keys/list permission.

        :returns: An iterator like instance of Key
        :rtype:
         typing.Generator[~azure.keyvault.keys._models.Key]
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START list_keys]
                :end-before: [END list_keys]
                :language: python
                :dedent: 4
                :caption: List all keys in the vault
        """
        url = '{}/keys'.format(self.vault_url)
        max_page_size = kwargs.get("max_page_size", None)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = KeyItemPaged(paging, DESERIALIZE.dependencies)
        return (KeyAttributes._from_key_item(item) for item in pages)

    def list_key_versions(self, name, **kwargs):
        # type: (str, str, Mapping[str, Any]) -> Generator[KeyAttributes]

        """Retrieves a list of individual key versions with the same key name.

        The full key identifier, attributes, and tags are provided in the
        response. This operation requires the keys/list permission.

        :param name: The name of the key.
        :type name
        :returns: An iterator like instance of Key
        :rtype:
         typing.Generator[~azure.keyvault.keys._models.Key]
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START list_key_versions]
                :end-before: [END list_key_versions]
                :language: python
                :dedent: 4
                :caption: List all versions of the specified key
        """
        url = '{}/keys/{}/versions'.format(self.vault_url, name)
        max_page_size = kwargs.get("max_page_size", None)
        paging = functools.partial(self._internal_paging, url, max_page_size)
        pages = KeyItemPaged(paging, DESERIALIZE.dependencies)
        return (KeyAttributes._from_key_item(item) for item in pages)

    def purge_deleted_key(self, name, **kwargs) -> None:
        """Permanently deletes the specified key.

        The Purge Deleted Key operation is applicable for soft-delete enabled
        vaults. While the operation can be invoked on any vault, it will return
        an error if invoked on a non soft-delete enabled vault. This operation
        requires the keys/purge permission.

        :param name: The name of the key
        :type name
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START purge_deleted_key]
                :end-before: [END purge_deleted_key]
                :language: python
                :dedent: 4
                :caption: Permanently deletes the specified key
        """
        url = '/'.join([self.vault_url, 'deletedkeys', name])
        query_parameters = {'api-version': self._api_version}

        request = HttpRequest('DELETE', url)
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 204:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        return

    def recover_deleted_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedKey
        """Recovers the deleted key to its latest version.

        The Recover Deleted Key operation is applicable for deleted keys in
        soft-delete enabled vaults. It recovers the deleted key back to its
        latest version under /keys. An attempt to recover an non-deleted key
        will return an error. Consider this the inverse of the delete operation
        on soft-delete enabled vaults. This operation requires the keys/recover
        permission.

        :param name: The name of the deleted key.
        :type name: str
        :returns: The recovered deleted key
        :rtype: ~azure.keyvault.keys._models.Key
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START recover_deleted_key]
                :end-before: [END recover_deleted_key]
                :language: python
                :dedent: 4
                :caption: Recovers the specified soft-deleted key
        """
        url = '/'.join([self.vault_url, 'deletedkeys', name, 'recover'])
        query_parameters = {'api-version': self._api_version}

        request = HttpRequest('POST', url)
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('KeyBundle', response)

        return Key._from_key_bundle(bundle)

    def update_key(
        self, name, version, key_ops=None, enabled=None, expires=None, not_before=None, tags=None, **kwargs
    ):
        # type: (str, str, Optional[List[str]], Optional[bool], Optional[datetime], Optional[datetime], Optional[str], Mapping[str, Any]) -> Key

        """The update key operation changes specified attributes of a stored key
        and can be applied to any key type and key version stored in Azure Key
        Vault.

        In order to perform this operation, the key must already exist in the
        Key Vault. Note: The cryptographic material of a key itself cannot be
        changed. This operation requires the keys/update permission.

        :param name: The name of key to update.
        :type name
        :param version: The version of the key to update.
        :type version
        :param key_ops: Json web key operations. For more information on
         possible key operations, see JsonWebKeyOperation.
        :type key_ops: list[str or
         ~~azure.keyvault._generated.v7_0.models.JsonWebKeyOperation]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key  in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :returns: The updated key
        :rtype: ~azure.keyvault.v7_0.models.Key
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START update_key]
                :end-before: [END update_key]
                :language: python
                :dedent: 4
                :caption: Updates a key in the key vault
        """

        url = '/'.join([self.vault_url, 'keys', name, version])

        attributes = _KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        key = KeyUpdateParameters(key_ops=key_ops, key_attributes=attributes, tags=tags)

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1()),
        }
        query_parameters = {'api-version': self._api_version}
        request_body = SERIALIZE.body(key, 'KeyUpdateParameters')

        request = HttpRequest('PATCH', url, headers=headers, data=request_body)
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))
        # should this return key attributes or key ?
        bundle = DESERIALIZE('KeyBundle', response)

        return Key._from_key_bundle(bundle)

    def backup_key(self, name, **kwargs)-> bytes:
        """Requests that a backup of the specified key be downloaded to the
        client.

        The Key Backup operation exports a key from Azure Key Vault in a
        protected form. Note that this operation does NOT return key material
        in a form that can be used outside the Azure Key Vault system, the
        returned key material is either protected to a Azure Key Vault HSM or
        to Azure Key Vault itself. The intent of this operation is to allow a
        client to GENERATE a key in one Azure Key Vault instance, BACKUP the
        key, and then RESTORE it into another Azure Key Vault instance. The
        BACKUP operation may be used to export, in protected form, any key type
        from Azure Key Vault. Individual versions of a key cannot be backed up.
        BACKUP / RESTORE can be performed within geographical boundaries only;
        meaning that a BACKUP from one geographical area cannot be restored to
        another geographical area. For example, a backup from the US
        geographical area cannot be restored in an EU geographical area. This
        operation requires the key/backup permission.

        :param name: The name of the key.
        :type name
        :return: The raw bytes of the key backup.
        :rtype: bytes
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START backup_key]
                :end-before: [END backup_key]
                :language: python
                :dedent: 4
                :caption: Backs up the specified key to the key vault
        """
        url = '/'.join([self.vault_url, 'keys', name, 'backup'])
        request = HttpRequest('POST', url)
        query_parameters = {'api-version': self._api_version}
        request.format_parameters(query_parameters)
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        result = DESERIALIZE('BackupKeyResult', response)
        return result.value

    def restore_key(self, backup, **kwargs):
        """Restores a backed up key to a vault.

        Imports a previously backed up key into Azure Key Vault, restoring the
        key, its key identifier, attributes and access control policies. The
        RESTORE operation may be used to import a previously backed up key.
        Individual versions of a key cannot be restored. The key is restored in
        its entirety with the same key name as it had when it was backed up. If
        the key name is not available in the target Key Vault, the RESTORE
        operation will be rejected. While the key name is retained during
        restore, the final key identifier will change if the key is restored to
        a different vault. Restore will restore all versions and preserve
        version identifiers. The RESTORE operation is subject to security
        constraints: The target Key Vault must be owned by the same Microsoft
        Azure Subscription as the source Key Vault The user must have RESTORE
        permission in the target Key Vault. This operation requires the
        keys/restore permission.

        :param backup: The raw bytes of the secret backup
        :type backup: bytes
        :returns: The restored key
        :rtype: ~azure.keyvault.keys._models.Key
        :raises: ~azure.core.exceptions.ClientRequestError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keyvault.py
                :start-after: [START restore_key]
                :end-before: [END restore_key]
                :language: python
                :dedent: 4
                :caption: Restores a backed up key to the vault
        """
        url = '/'.join([self.vault_url, 'keys', 'restore'])

        query_parameters = {'api-version': self._api_version}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ms-client-request-id': str(uuid.uuid1())
        }
        restore_parameters = KeyRestoreParameters(key_bundle_backup=backup)
        request_body = SERIALIZE.body(restore_parameters, 'KeyRestoreParameters')

        request = HttpRequest('POST', url, headers, data=request_body)
        request.format_parameters(query_parameters)
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError('Request failed status code {}.  {}'.format(response.status_code, response.text()))

        bundle = DESERIALIZE('KeyBundle', response)

        return Key._from_key_bundle(bundle)

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

    # def wrap_key(self, name, version, algorithm, value, **kwargs):
    #     pass

    # def unwrap_key(self, name, version, algorithm, value, **kwargs):
    #     pass

    # TODO:
    # def import_key(self, name, key, hsm=None, attributes=None, tags=None, **kwargs):
    #     pass
