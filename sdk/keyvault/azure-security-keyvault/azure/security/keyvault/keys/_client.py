# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Generator, Mapping, Optional, List
from datetime import datetime

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

from .._internal import _KeyVaultClientBase
from ._models import Key, KeyBase, DeletedKey, KeyOperationResult


class KeyClient(_KeyVaultClientBase):
    """KeyClient is a high-level interface for managing a vault's keys.

    Example:
        .. literalinclude:: ../tests/test_examples_keys.py
            :start-after: [START create_key_client]
            :end-before: [END create_key_client]
            :language: python
            :caption: Creates a new instance of the Key client
    """

    # pylint:disable=protected-access

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
        :type name: str
        :param key_type: The type of key to create. For valid values, see
         JsonWebKeyType. Possible values include: 'EC', 'EC-HSM', 'RSA',
         'RSA-HSM', 'oct'
        :type key_type: str or ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyType
        :param size: The key size in bits. For example: 2048, 3072, or
         4096 for RSA.
        :type size: int
        :param key_operations: Supported key operations.
        :type key_operations: list[str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param expires: Expiry date of the key  in UTC.
        :type expires: datetime.datetime
        :param not_before: Not before date of the key in UTC
        :type not_before: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: Dict[str, str]
        :param curve: Elliptic curve name. If none then defaults to 'P-256'. For valid values, see
         JsonWebKeyCurveName. Possible values include: 'P-256', 'P-384',
         'P-521', 'SECP256K1'
        :type curve: str or
        :returns: The created key
        :rtype: ~azure.security.keyvault.keys._models.Key

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START create_key]
                :end-before: [END create_key]
                :language: python
                :caption: Creates a key in the key vault
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None

        bundle = self._client.create_key(
            self.vault_url, name, key_type, size, key_attributes=attributes, key_ops=key_ops, tags=tags, curve=curve
        )
        return Key._from_key_bundle(bundle)

    def create_rsa_key(
        self,
        name,
        hsm,
        size=None,
        key_operations=None,
        enabled=None,
        expires=None,
        not_before=None,
        tags=None,
        **kwargs
    ):
        # type: (str, bool, Optional[int], Optional[List[str]], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Key
        """Creates a new RSA type key, stores it, then returns key attributes to the client.

        The create key operation can be used to create any key type in Azure
        Key Vault. If the named key already exists, Azure Key Vault creates a
        new version of the key. It requires the keys/create permission.

        :param name: The name for the new key. The system will generate
         the version name for the new key.
        :type name
        :param hsm: Whether to create as a hardware key (HSM) or software key.
        :type hsm: bool
        :param size: The key size in bits. For example: 2048, 3072, or
         4096 for RSA.
        :type size: int
        :param key_operations: Supported key operations.
        :type key_operations: list[str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
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

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START create_rsa_key]
                :end-before: [END create_rsa_key]
                :language: python
                :caption: Creates a key in the key vault
        """
        key_type = "RSA-HSM" if hsm else "RSA"

        return self.create_key(
            name,
            key_type=key_type,
            size=size,
            key_ops=key_operations,
            enabled=enabled,
            expires=expires,
            not_before=not_before,
            tags=tags,
        )

    def create_ec_key(
        self,
        name,
        hsm,
        curve=None,
        key_operations=None,
        enabled=None,
        expires=None,
        not_before=None,
        tags=None,
        **kwargs
    ):
        # type: (str, bool, Optional[str],  Optional[List[str]], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Key
        """Creates a new Elliptic curve type key, stores it, then returns key attributes to the client.

        The create key operation can be used to create any key type in Azure
        Key Vault. If the named key already exists, Azure Key Vault creates a
        new version of the key. It requires the keys/create permission.

        :param name: The name for the new key. The system will generate
         the version name for the new key.
        :type name
        :param hsm: Whether to create as a hardware key (HSM) or software key.
        :type hsm: bool
        :param curve: Elliptic curve name. If none then defaults to 'P-256'. For valid values, see
         JsonWebKeyCurveName. Possible values include: 'P-256', 'P-384',
         'P-521', 'SECP256K1'
        :type curve: str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyCurveName
        :param key_operations: Supported key operations.
        :type key_operations: list[str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
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

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START create_ec_key]
                :end-before: [END create_ec_key]
                :language: python
                :caption: Creates a key in the key vault
        """

        key_type = "EC-HSM" if hsm else "EC"

        return self.create_key(
            name,
            key_type=key_type,
            curve=curve,
            key_ops=key_operations,
            enabled=enabled,
            expires=expires,
            not_before=not_before,
            tags=tags,
        )

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
        :rtype: ~azure.security.keyvault.keys._models.DeletedKey

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START delete_key]
                :end-before: [END delete_key]
                :language: python
                :caption: Deletes a key in the key vault
        """
        bundle = self._client.delete_key(self.vault_url, name, error_map={404: ResourceNotFoundError})
        return DeletedKey._from_deleted_key_bundle(bundle)

    def get_key(self, name, version=None, **kwargs):
        # type: (str, Optional[str], Mapping[str, Any]) -> Key
        """Gets the public part of a stored key.

        The get key operation is applicable to all key types. If the requested
        key is symmetric, then no key material is released in the response.
        This operation requires the keys/get permission.

        :param name: The name of the key to get.
        :type name
        :param version: Retrieves a specific version of a key. If the version is None or an empty string,
            the latest version of the key is returned
        :type version
        :returns: Key
        :rtype: ~azure.security.keyvault.keys._models.Key

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START get_key]
                :end-before: [END get_key]
                :language: python
                :caption: Retrieves a key from the key vault
        """
        if version is None:
            version = ""

        bundle = self._client.get_key(self.vault_url, name, version, error_map={404: ResourceNotFoundError})
        return Key._from_key_bundle(bundle)

    def get_deleted_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedKey
        """Gets the public part of a deleted key.

        The Get Deleted Key operation is applicable for soft-delete enabled
        vaults. While the operation can be invoked on any vault, it will return
        an error if invoked on a non soft-delete enabled vault. This operation
        requires the keys/get permission.

        :param name: The name of the key.
        :type name
        :returns: The deleted key
        :rtype: ~azure.security.keyvault.keys._models.DeletedKey

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START get_deleted_key]
                :end-before: [END get_deleted_key]
                :language: python
                :caption: Retrieves a deleted key from the key vault
        """
        bundle = self._client.get_deleted_key(self.vault_url, name, error_map={404: ResourceNotFoundError})
        return DeletedKey._from_deleted_key_bundle(bundle)

    def list_deleted_keys(self, **kwargs):
        # type: (Mapping[str, Any]) -> Generator[DeletedKey]
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
         typing.Generator[~azure.security.keyvault.keys._models.DeletedKey]

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START list_deleted_keys]
                :end-before: [END list_deleted_keys]
                :language: python
                :caption: List all the deleted keys in the vault
        """
        max_page_size = kwargs.get("max_page_size", None)
        pages = self._client.get_deleted_keys(self._vault_url, maxresults=max_page_size)
        return (DeletedKey._from_deleted_key_item(item) for item in pages)

    def list_keys(self, **kwargs):
        # type: (Mapping[str, Any]) -> Generator[KeyBase]
        """List keys in the specified vault.

        Retrieves a list of the keys in the Key Vault as JSON Web Key
        structures that contain the public part of a stored key. The LIST
        operation is applicable to all key types, however only the base key
        identifier, attributes, and tags are provided in the response.
        Individual versions of a key are not listed in the response. This
        operation requires the keys/list permission.

        :returns: An iterator like instance of KeyBase
        :rtype:
         typing.Generator[~azure.security.keyvault.keys._models.KeyBase]

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START list_keys]
                :end-before: [END list_keys]
                :language: python
                :caption: List all keys in the vault
        """
        max_page_size = kwargs.get("max_page_size", None)
        pages = self._client.get_keys(self._vault_url, maxresults=max_page_size)
        return (KeyBase._from_key_item(item) for item in pages)

    def list_key_versions(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Generator[KeyBase]
        """Retrieves a list of individual key versions with the same key name.
        The full key identifier, attributes, and tags are provided in the
        response. This operation requires the keys/list permission.

        :param name: The name of the key.
        :type name
        :returns: An iterator like instance of KeyBase
        :rtype:
         typing.Generator[~azure.security.keyvault.keys._models.KeyBase]

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START list_key_versions]
                :end-before: [END list_key_versions]
                :language: python
                :caption: List all versions of the specified key
        """
        max_page_size = kwargs.get("max_page_size", None)
        pages = self._client.get_key_versions(self._vault_url, name, maxresults=max_page_size)
        return (KeyBase._from_key_item(item) for item in pages)

    def purge_deleted_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
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
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes a deleted key
                # (with soft-delete disabled, delete itself is permanent)
                key_client.purge_deleted_key("key-name")

        """
        self._client.purge_deleted_key(self.vault_url, name)

    def recover_deleted_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Key
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
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START recover_deleted_key]
                :end-before: [END recover_deleted_key]
                :language: python
                :caption: Recovers the specified soft-deleted key
        """
        bundle = self._client.recover_deleted_key(self.vault_url, name)
        return Key._from_key_bundle(bundle)

    def update_key(
        self, name, version, key_operations=None, enabled=None, expires=None, not_before=None, tags=None, **kwargs
    ):
        # type: (str, str, Optional[List[str]], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Key
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
        :param key_operations: Json web key operations. For more information on
         possible key operations, see JsonWebKeyOperation.
        :type key_operations: list[str or
         ~azure.security.keyvault._generated.v7_0.models.JsonWebKeyOperation]
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
        :rtype: ~azure.security.keyvault.keys._models.Key
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START update_key]
                :end-before: [END update_key]
                :language: python
                :caption: Updates a key in the key vault
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.update_key(
            self.vault_url,
            name,
            key_version=version,
            key_ops=key_operations,
            tags=tags,
            key_attributes=attributes,
            error_map={404: ResourceNotFoundError},
        )
        return Key._from_key_bundle(bundle)  # pylint: disable=protected-access

    def backup_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> bytes
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
        :returns: The raw bytes of the key backup.
        :rtype: bytes
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to retrieve the key

        Example:
            .. literalinclude:: ../tests/test_examples_keys.py
                :start-after: [START backup_key]
                :end-before: [END backup_key]
                :language: python
                :caption: Backs up the specified key to the key vault
        """
        backup_result = self._client.backup_key(self.vault_url, name, error_map={404: ResourceNotFoundError})
        return backup_result.value

    def restore_key(self, backup, **kwargs):
        # type: (bytes, Mapping[str, Any]) -> Key
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
            .. literalinclude:: ../../../tests/test_examples_keys.py
                :start-after: [START restore_key]
                :end-before: [END restore_key]
                :language: python
                :caption: Restores a backed up key to the vault
        """
        bundle = self._client.restore_key(self.vault_url, backup, error_map={409: ResourceExistsError})
        return Key._from_key_bundle(bundle)

    def import_key(self, name, key, hsm=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, List[str], Optional[bool], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Key
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
        bundle = self._client.import_key(self.vault_url, name, key=key, hsm=hsm, key_attributes=attributes, tags=tags)
        return Key._from_key_bundle(bundle)

    def wrap_key(self, name, algorithm, value, version=None, **kwargs):
        # type: (str, str, Optional[str], bytes, Mapping[str, Any]) -> KeyOperationResult
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

        bundle = self._client.wrap_key(self.vault_url, name, key_version=version, algorithm=algorithm, value=value)
        return KeyOperationResult(id=bundle.kid, value=bundle.result)

    def unwrap_key(self, name, algorithm, value, version=None, **kwargs):
        # type: (str, str, Optional[str], bytes, Mapping[str, Any]) -> KeyOperationResult
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

        bundle = self._client.unwrap_key(self.vault_url, name, key_version=version, algorithm=algorithm, value=value)
        return KeyOperationResult(id=bundle.kid, value=bundle.result)
