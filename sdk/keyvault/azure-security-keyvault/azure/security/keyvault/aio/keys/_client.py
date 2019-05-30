# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, AsyncIterable, Mapping, Optional, Dict, List
from datetime import datetime

from azure.core.configuration import Configuration
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.transport import AsyncioRequestsTransport
from azure.core.pipeline import AsyncPipeline

from azure.security.keyvault._internal import _BearerTokenCredentialPolicy
from azure.security.keyvault._generated import KeyVaultClient
from azure.security.keyvault.aio._internal import AsyncPagingAdapter

from ...keys._models import Key, DeletedKey, KeyBase, KeyOperationResult


class KeyClient:
    """The KeyClient class defines a high level interface for managing keys in the specified vault.
    
    :param credentials: A credential or credential provider which can be used to authenticate to the vault,
     a ValueError will be raised if the entity is not provided
    :type credentials: azure.authentication.Credential or azure.authentication.CredentialProvider
    :param str vault_url: The url of the vault to which the client will connect,
     a ValueError will be raised if the entity is not provided
    :param ~azure.core.configuration.Configuration config: The configuration for the KeyClient
    
    Example:
        .. literalinclude:: ../tests/test_examples_keys_async.py
            :start-after: [START create_key_client]
            :end-before: [END create_key_client]
            :language: python
            :dedent: 4
            :caption: Creates a new instance of the Key client
    """

    @staticmethod
    def create_config(**kwargs):
        pass  # TODO

    def __init__(self, vault_url, credentials, config=None, api_version=None, **kwargs):
        if not credentials:
            raise ValueError("credentials")
        if not vault_url:
            raise ValueError("vault_url")
        self._vault_url = vault_url
        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION
        # TODO: need config to get default policies, config requires credentials but doesn't do anything with them
        config = config or KeyVaultClient.get_configuration_class(api_version, aio=True)(credentials)
        # TODO generated default pipeline should be fine when token policy isn't necessary
        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            _BearerTokenCredentialPolicy(credentials),
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
        ]
        transport = AsyncioRequestsTransport(config)
        pipeline = AsyncPipeline(transport, policies=policies)
        self._client = KeyVaultClient(credentials, api_version=api_version, pipeline=pipeline, aio=True)

    @property
    def vault_url(self) -> str:
        return self._vault_url

    async def get_key(self, name: str, version: Optional[str] = None, **kwargs: Mapping[str, Any]) -> Key:
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
        :rtype: ~azure.security.keyvault.keys._models.Key
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START get_key]
                :end-before: [END get_key]
                :language: python
                :dedent: 4
                :caption: Retrieves a key from the key vault
        """
        if version is None:
            version = ""

        bundle = await self._client.get_key(self.vault_url, name, version, error_map={404: ResourceNotFoundError})
        return Key._from_key_bundle(bundle)

    async def create_key(
        self,
        name: str,
        key_type: str,
        size: Optional[int] = None,
        curve: Optional[str] = None,
        key_ops: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
        expires: Optional[datetime] = None,
        not_before: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> Key:
        """Creates a new key, stores it, then returns key attributes to the client.

        The create key operation can be used to create any key type in Azure
        Key Vault. If the named key already exists, Azure Key Vault creates a
        new version of the key. It requires the keys/create permission.

        :param name: The name for the new key. The system will generate
         the version name for the new key.
        :type name: str
        :param key_type: The type of key to create. For valid values, see
         JsonWebKeyType. Possible values include: 'EC', 'EC-HSM', 'RSA',
         'RSA-HSM', 'oct'
        :param size: The key size in bits. For example: 2048, 3072, or
         4096 for RSA.
        :type size: int
        :param curve: Elliptic curve name. If none then defaults to 'P-256'. For valid values, see
         JsonWebKeyCurveName. Possible values include: 'P-256', 'P-384',
         'P-521', 'SECP256K1'
        :type curve: str or
        :type key_type: str or ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyType
        :param key_ops: Supported key operations.
        :type key_ops: list[str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :returns: The created key
        :rtype: ~azure.security.keyvault.keys._models.Key
        
        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START create_key]
                :end-before: [END create_key]
                :language: python
                :dedent: 4
                :caption: Creates a key in the key vault
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None

        bundle = await self._client.create_key(
            self.vault_url, name, key_type, size, key_attributes=attributes, key_ops=key_ops, tags=tags, curve=curve
        )
        return Key._from_key_bundle(bundle)

    async def create_rsa_key(
        self,
        name: str,
        hsm: bool,
        size: Optional[int] = None,
        key_ops: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
        expires: Optional[datetime] = None,
        not_before: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> Key:
        """Creates a new RSA type key, stores it, then returns key attributes to the client.
        The create key operation can be used to create any key type in Azure
        Key Vault. If the named key already exists, Azure Key Vault creates a
        new version of the key. It requires the keys/create permission.

        :param name: The name for the new key. The system will generate
         the version name for the new key.
        :type name
        :param hsm: Whether to import as a hardware key (HSM) or software key.
        :type hsm: bool
        :param size: The key size in bits. For example: 2048, 3072, or
        4096 for RSA.
        :type size: int
        :param key_ops: Supported key operations.
        :type key_ops: list[str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :returns: The created key
        :rtype: ~azure.security.keyvault.keys._models.Key
        
        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START create_rsa_key]
                :end-before: [END create_rsa_key]
                :language: python
                :dedent: 4
                :caption: Creates an RSA key in the key vault
        """
        key_type = "RSA-HSM" if hsm else "RSA"

        return await self.create_key(
            name,
            key_type=key_type,
            size=size,
            key_ops=key_ops,
            enabled=enabled,
            expires=expires,
            not_before=not_before,
            tags=tags,
        )

    async def create_ec_key(
        self,
        name: str,
        hsm: bool,
        curve: Optional[str] = None,
        key_ops: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
        expires: Optional[datetime] = None,
        not_before: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> Key:
        """Creates a new Elliptic curve type key, stores it, then returns key attributes to the client.

        The create key operation can be used to create any key type in Azure
        Key Vault. If the named key already exists, Azure Key Vault creates a
        new version of the key. It requires the keys/create permission.
        :param name: The name for the new key. The system will generate
        the version name for the new key.

        :type name
        :param hsm: Whether to import as a hardware key (HSM) or software key.
        :type hsm: bool
        :param curve: Elliptic curve name. If none then defaults to 'P-256'. For valid values, see
         JsonWebKeyCurveName. Possible values include: 'P-256', 'P-384',
        'P-521', 'SECP256K1'
        :type curve: str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyCurveName
        :param key_ops: Supported key operations.
        :type key_ops: list[str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :returns: The created key
        :rtype: ~azure.security.keyvault.keys._models.Key

        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START create_ec_key]
                :end-before: [END create_ec_key]
                :language: python
                :dedent: 4
                :caption: Creates an EC key in the key vault
        """
        key_type = "EC-HSM" if hsm else "EC"

        return await self.create_key(
            name,
            key_type=key_type,
            curve=curve,
            key_ops=key_ops,
            enabled=enabled,
            expires=expires,
            not_before=not_before,
            tags=tags,
        )

    async def update_key(
        self,
        name: str,
        version: str,
        key_ops: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> Key:
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
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :returns: The updated key
        :rtype: ~azure.security.keyvault.v7_0.models.Key
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START update_key]
                :end-before: [END update_key]
                :language: python
                :dedent: 4
                :caption: Updates a key in the key vault
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None

        bundle = await self._client.update_key(
            self.vault_url,
            name,
            key_version=version,
            key_ops=key_ops,
            tags=tags,
            key_attributes=attributes,
            error_map={404: ResourceNotFoundError},
        )
        return Key._from_key_bundle(bundle)

    def list_keys(self, **kwargs: Mapping[str, Any]) -> AsyncIterable[KeyBase]:
        """List keys in the specified vault.
        
        Retrieves a list of the keys in the Key Vault as JSON Web Key
        structures that contain the public part of a stored key. The LIST
        operation is applicable to all key types, however only the base key
        identifier, attributes, and tags are provided in the response.
        Individual versions of a key are not listed in the response. This
        operation requires the keys/list permission.

        :returns: An iterator like instance of KeyBase
        :rtype:
         typing.AsyncIterable[~azure.security.keyvault.keys._models.KeyBase]
        
        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START list_keys]
                :end-before: [END list_keys]
                :language: python
                :dedent: 4
                :caption: List all keys in the vault
        """
        max_results = kwargs.get("max_page_size")
        pages = self._client.get_keys(self.vault_url, maxresults=max_results)
        iterable = AsyncPagingAdapter(pages, KeyBase._from_key_item)
        return iterable

    def list_key_versions(self, name: str, **kwargs: Mapping[str, Any]) -> AsyncIterable[KeyBase]:
        """Retrieves a list of individual key versions with the same key name.
        
        The full key identifier, attributes, and tags are provided in the
        response. This operation requires the keys/list permission.

        :param name: The name of the key.
        :type name
        :returns: An iterator like instance of KeyBase
        :rtype:
         typing.AsyncIterable[~azure.security.keyvault.keys._models.KeyBase]
        
        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START list_key_versions]
                :end-before: [END list_key_versions]
                :language: python
                :dedent: 4
                :caption: List all versions of the specified key
        """
        max_results = kwargs.get("max_page_size")
        pages = self._client.get_key_versions(self.vault_url, name, maxresults=max_results)
        iterable = AsyncPagingAdapter(pages, KeyBase._from_key_item)
        return iterable

    async def backup_key(self, name: str, **kwargs: Mapping[str, Any]) -> bytes:
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
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START backup_key]
                :end-before: [END backup_key]
                :language: python
                :dedent: 4
                :caption: Backs up the specified key to the key vault
        """
        backup_result = await self._client.backup_key(self.vault_url, name, error_map={404: ResourceNotFoundError})
        return backup_result.value

    async def restore_key(self, backup: bytes, **kwargs: Mapping[str, Any]) -> Key:
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

        :param backup: The raw bytes of the key backup
        :type backup: bytes
        :returns: The restored key
        :rtype: ~azure.security.keyvault.keys._models.Key
        :raises: ~azure.core.exceptions.ResourceExistsError if the client failed to retrieve the key
        
        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START restore_key]
                :end-before: [END restore_key]
                :language: python
                :dedent: 4
                :caption: Restores a backed up key to the vault
        """
        bundle = await self._client.restore_key(self.vault_url, backup, error_map={409: ResourceExistsError})
        return Key._from_key_bundle(bundle)

    async def delete_key(self, name: str, **kwargs: Mapping[str, Any]) -> DeletedKey:
        """Deletes a key of any type from storage in Azure Key Vault.

        The delete key operation cannot be used to remove individual versions
        of a key. This operation removes the cryptographic material associated
        with the key, which means the key is not usable for Sign/Verify,
        Wrap/Unwrap or Encrypt/Decrypt operations. This operation requires the
        keys/delete permission.

        :param name: The name of the key to delete.
        :type name
        :returns: The deleted key
        :rtype: ~azure.security.keyvault.keys._models.DeletedKey
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to delete the key

        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START delete_key]
                :end-before: [END delete_key]
                :language: python
                :dedent: 4
                :caption: Deletes a key in the key vault
        """
        bundle = await self._client.delete_key(self.vault_url, name, error_map={404: ResourceNotFoundError})
        return DeletedKey._from_deleted_key_bundle(bundle)

    async def get_deleted_key(self, name: str, **kwargs: Mapping[str, Any]) -> DeletedKey:
        """Gets the public part of a deleted key.
        The Get Deleted Key operation is applicable for soft-delete enabled
        vaults. While the operation can be invoked on any vault, it will return
        an error if invoked on a non soft-delete enabled vault. This operation
        requires the keys/get permission.

        :param name: The name of the key.
        :type name
        :returns: The deleted key
        :rtype: ~azure.security.keyvault.keys._models.DeletedKey
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START get_deleted_key]
                :end-before: [END get_deleted_key]
                :language: python
                :dedent: 4
                :caption: Retrieves a deleted key from the key vault
        """
        bundle = await self._client.get_deleted_key(self.vault_url, name, error_map={404: ResourceNotFoundError})
        return DeletedKey._from_deleted_key_bundle(bundle)

    def list_deleted_keys(self, **kwargs: Mapping[str, Any]) -> AsyncIterable[DeletedKey]:
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
         typing.AsyncIterable[~azure.security.keyvault.keys._models.DeletedKey]
        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START list_deleted_keys]
                :end-before: [END list_deleted_keys]
                :language: python
                :dedent: 4
                :caption: List all the deleted keys in the vault
        """
        max_results = kwargs.get("max_page_size")
        pages = self._client.get_deleted_keys(self.vault_url, maxresults=max_results)
        iterable = AsyncPagingAdapter(pages, DeletedKey._from_deleted_key_item)
        return iterable

    async def purge_deleted_key(self, name: str, **kwargs: Mapping[str, Any]) -> None:
        """Permanently deletes the specified key.
        
        The Purge Deleted Key operation is applicable for soft-delete enabled
        vaults. While the operation can be invoked on any vault, it will return
        an error if invoked on a non soft-delete enabled vault. This operation
        requires the keys/purge permission.
        
        :param name: The name of the key
        :type name
        :returns: None
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START purge_deleted_key]
                :end-before: [END purge_deleted_key]
                :language: python
                :dedent: 4
                :caption: Permanently deletes the specified key
        """
        await self._client.purge_deleted_key(self.vault_url, name)

    async def recover_deleted_key(self, name: str, **kwargs: Mapping[str, Any]) -> Key:
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
        :rtype: ~azure.security.keyvault.keys._models.Key
        
        Example:
            .. literalinclude:: ../tests/test_examples_keys_async.py
                :start-after: [START recover_deleted_key]
                :end-before: [END recover_deleted_key]
                :language: python
                :dedent: 4
                :caption: Recovers the specified soft-deleted key
        """
        bundle = await self._client.recover_deleted_key(self.vault_url, name)
        return Key._from_key_bundle(bundle)

    async def import_key(
        self,
        name: str,
        key: List[str],
        hsm: Optional[bool] = None,
        enabled: Optional[bool] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> Key:
        """Imports an externally created key, stores it, and returns key
        parameters and attributes to the client.

        The import key operation may be used to import any key type into an
        Azure Key Vault. If the named key already exists, Azure Key Vault
        creates a new version of the key. This operation requires the
        keys/import permission.

        :param name: Name for the imported key.
        :type name: str
        :param key: The Json web key
        :type key: ~azure.security.keyvault.v7_0.models.JsonWebKey
        :param hsm: Whether to import as a hardware key (HSM) or software key.
        :type hsm: bool
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key  in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :returns: The created key
        :rtype: ~azure.security.keyvault.keys._models.Key

        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = await self._client.import_key(
            self.vault_url, name, key=key, hsm=hsm, key_attributes=attributes, tags=tags
        )
        return Key._from_key_bundle(bundle)

    async def wrap_key(
        self, name: str, algorithm: str, value: bytes, version: Optional[str] = None, **kwargs: Mapping[str, Any]
    ) -> KeyOperationResult:
        """Wraps a symmetric key using a specified key.

        The WRAP operation supports encryption of a symmetric key using a key
        encryption key that has previously been stored in an Azure Key Vault.
        The WRAP operation is only strictly necessary for symmetric keys stored
        in Azure Key Vault since protection with an asymmetric key can be
        performed using the public portion of the key. This operation is
        supported for asymmetric keys as a convenience for callers that have a
        key-reference but do not have access to the public key material. This
        operation requires the keys/wrapKey permission.

        :param name: The name of the key.
        :type name: str
        :param version: The version of the key.
        :type version: str
        :param algorithm: algorithm identifier. Possible values include:
         'RSA-OAEP', 'RSA-OAEP-256', 'RSA1_5'
        :type algorithm: str or
         ~azure.security.keyvault.v7_0.models.JsonWebKeyEncryptionAlgorithm
        :param value:
        :type value: bytes
        :returns: The wrapped symmetric key.
        :rtype: ~azure.security.keyvault.keys._models.KeyOperationResult

        """
        if version is None:
            version = ""

        bundle = await self._client.wrap_key(
            self.vault_url, name, key_version=version, algorithm=algorithm, value=value
        )
        return KeyOperationResult(id=bundle.kid, value=bundle.result)

    async def unwrap_key(
        self, name: str, algorithm: str, value: bytes, version: Optional[str] = None, **kwargs: Mapping[str, Any]
    ) -> KeyOperationResult:
        """Unwraps a symmetric key using the specified key that was initially used
        for wrapping that key.

        The UNWRAP operation supports decryption of a symmetric key using the
        target key encryption key. This operation is the reverse of the WRAP
        operation. The UNWRAP operation applies to asymmetric and symmetric
        keys stored in Azure Key Vault since it uses the private portion of the
        key. This operation requires the keys/unwrapKey permission.

        :param name: The name of the key.
        :type name: str
        :param version: The version of the key.
        :type version: str
        :param algorithm: algorithm identifier. Possible values include:
         'RSA-OAEP', 'RSA-OAEP-256', 'RSA1_5'
        :type algorithm: str or
         ~azure.security.keyvault.v7_0.models.JsonWebKeyEncryptionAlgorithm
        :param value:
        :type value: bytes
        :returns: The unwrapped symmetric key.
        :rtype: ~azure.security.keyvault.keys._models.KeyOperationResult

        """
        if version is None:
            version = ""

        bundle = await self._client.unwrap_key(
            self.vault_url, name, key_version=version, algorithm=algorithm, value=value
        )
        return KeyOperationResult(id=bundle.kid, value=bundle.result)
