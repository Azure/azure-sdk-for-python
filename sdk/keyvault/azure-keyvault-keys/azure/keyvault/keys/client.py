# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Mapping, Optional
    from azure.core.paging import ItemPaged
    from .models import JsonWebKey

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace

from ._shared import KeyVaultClientBase
from .crypto import CryptographyClient
from .models import Key, KeyBase, DeletedKey, KeyOperationResult


class KeyClient(KeyVaultClientBase):
    """A high-level interface for managing a vault's keys.

    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :param str vault_url: URL of the vault the client will access

    Example:
        .. literalinclude:: ../tests/test_samples_keys.py
            :start-after: [START create_key_client]
            :end-before: [END create_key_client]
            :language: python
            :caption: Create a new ``KeyClient``
            :dedent: 4
    """

    # pylint:disable=protected-access

    def get_cryptography_client(self, key, **kwargs):
        # type: (Union[Key, str], Any) -> CryptographyClient

        # the initializer requires a credential but won't actually use it in this case because we pass in this
        # KeyClient's generated client, whose pipeline (and auth policy) is fully configured
        credential = object()
        return CryptographyClient(key, credential, generated_client=self._client, **kwargs)

    @distributed_trace
    def create_key(
        self,
        name,
        key_type,
        size=None,
        key_operations=None,
        enabled=None,
        expires=None,
        not_before=None,
        tags=None,
        curve=None,
        **kwargs
    ):
        # type: (str, str, Optional[int], Optional[List[str]], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Optional[str], Mapping[str, Any]) -> Key
        """Create a key. If ``name`` is already in use, create a new version of the key. Requires the keys/create
        permission.

        :param str name: The name of the new key. Key Vault will generate the key's version.
        :param key_type: The type of key to create
        :type key_type: str or ~azure.keyvault.keys.enums.JsonWebKeyType
        :param int size: (optional) RSA key size in bits, for example 2048, 3072, or 4096.
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(str or ~azure.keyvault.keys.enums.JsonWebKeyOperation)
        :param bool enabled: (optional) Whether the key is enabled for use
        :param expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :param dict tags: (optional) Application specific metadata in the form of key-value pairs
        :param curve: (optional) Elliptic curve name. Defaults to the NIST P-256 elliptic curve.
        :type curve: ~azure.keyvault.keys.enums.JsonWebKeyCurveName or str
        :returns: The created key
        :rtype: ~azure.keyvault.keys.models.Key

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_key]
                :end-before: [END create_key]
                :language: python
                :caption: Create a key
                :dedent: 8
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None

        bundle = self._client.create_key(
            self.vault_url,
            name,
            key_type,
            size,
            key_attributes=attributes,
            key_ops=key_operations,
            tags=tags,
            curve=curve,
            **kwargs
        )
        return Key._from_key_bundle(bundle)

    @distributed_trace
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
        """Create a new RSA key. If ``name`` is already in use, create a new version of the key. Requires the
        keys/create permission.

        :param str name: The name for the new key. Key Vault will generate the key's version.
        :param bool hsm: Whether to create a hardware key (HSM) or software key
        :param int size: (optional) Key size in bits, for example 2048, 3072, or 4096
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(str or ~azure.keyvault.keys.enums.JsonWebKeyOperation)
        :param bool enabled: (optional) Whether the key is enabled for use
        :param expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :param dict tags: (optional) Application specific metadata in the form of key-value pairs
        :returns: The created key
        :rtype: ~azure.keyvault.keys.models.Key

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_rsa_key]
                :end-before: [END create_rsa_key]
                :language: python
                :caption: Create RSA key
                :dedent: 8
        """
        key_type = "RSA-HSM" if hsm else "RSA"

        return self.create_key(
            name,
            key_type=key_type,
            size=size,
            key_operations=key_operations,
            enabled=enabled,
            expires=expires,
            not_before=not_before,
            tags=tags,
            **kwargs
        )

    @distributed_trace
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
        """Create a new elliptic curve key. If ``name`` is already in use, create a new version of the key. Requires
        the keys/create permission.

        :param str name: The name for the new key. Key Vault will generate the key's version.
        :param bool hsm: Whether to create as a hardware key (HSM) or software key.
        :param curve: (optional) Elliptic curve name. Defaults to the NIST P-256 elliptic curve.
        :type curve: ~azure.keyvault.keys.enums.JsonWebKeyCurveName or str
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(~azure.keyvault.keys.enums.JsonWebKeyOperation)
        :param bool enabled: (optional) Whether the key is enabled for use
        :param datetime.datetime expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :param dict tags: (optional) Application specific metadata in the form of key-value pairs
        :returns: The created key
        :rtype: ~azure.keyvault.keys.models.Key

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_ec_key]
                :end-before: [END create_ec_key]
                :language: python
                :caption: Create an elliptic curve key
                :dedent: 8
        """

        key_type = "EC-HSM" if hsm else "EC"

        return self.create_key(
            name,
            key_type=key_type,
            curve=curve,
            key_operations=key_operations,
            enabled=enabled,
            expires=expires,
            not_before=not_before,
            tags=tags,
            **kwargs
        )

    @distributed_trace
    def delete_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedKey
        """Delete all versions of a key and its cryptographic material. Requires the keys/delete permission.

        :param str name: The name of the key to delete.
        :returns: The deleted key
        :rtype: ~azure.keyvault.keys.models.DeletedKey
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the key doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START delete_key]
                :end-before: [END delete_key]
                :language: python
                :caption: Delete a key
                :dedent: 8
        """
        bundle = self._client.delete_key(self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs)
        return DeletedKey._from_deleted_key_bundle(bundle)

    @distributed_trace
    def get_key(self, name, version=None, **kwargs):
        # type: (str, Optional[str], Mapping[str, Any]) -> Key
        """Get a key's attributes and, if it's an asymmetric key, its public material. Requires the keys/get permission.

        :param str name: The name of the key to get.
        :param str version: (optional) A specific version of the key to get. If not specified, gets the latest version
            of the key.
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the key doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START get_key]
                :end-before: [END get_key]
                :language: python
                :caption: Get a key
                :dedent: 8
        """
        bundle = self._client.get_key(
            self.vault_url, name, key_version=version or "", error_map={404: ResourceNotFoundError}, **kwargs
        )
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def get_deleted_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedKey
        """Get a deleted key. This is only possible in a vault with soft-delete enabled. Requires the keys/get
        permission.

        :param str name: The name of the key
        :returns: The deleted key
        :rtype: ~azure.keyvault.keys.models.DeletedKey

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START get_deleted_key]
                :end-before: [END get_deleted_key]
                :language: python
                :caption: Get a deleted key
                :dedent: 8
        """
        # TODO: which exception is raised when soft-delete is not enabled
        bundle = self._client.get_deleted_key(self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs)
        return DeletedKey._from_deleted_key_bundle(bundle)

    @distributed_trace
    def list_deleted_keys(self, **kwargs):
        # type: (Mapping[str, Any]) -> ItemPaged[DeletedKey]
        """List all deleted keys, including the public part of each. This is only possible in a vault with soft-delete
        enabled. Requires the keys/list permission.

        :returns: An iterator of deleted keys
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.models.DeletedKey]

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START list_deleted_keys]
                :end-before: [END list_deleted_keys]
                :language: python
                :caption: List all the deleted keys
                :dedent: 8
        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_deleted_keys(
            self._vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [DeletedKey._from_deleted_key_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_keys(self, **kwargs):
        # type: (Mapping[str, Any]) -> ItemPaged[KeyBase]
        """List identifiers, attributes, and tags of all keys in the vault. Requires the keys/list permission.

        :returns: An iterator of keys without their cryptographic material or version information
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.models.KeyBase]

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START list_keys]
                :end-before: [END list_keys]
                :language: python
                :caption: List all keys
                :dedent: 8
        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_keys(
            self._vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [KeyBase._from_key_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_key_versions(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> ItemPaged[KeyBase]
        """List the identifiers, attributes, and tags of a key's versions. Requires the keys/list permission.

        :param str name: The name of the key
        :returns: An iterator of keys without their cryptographic material
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.models.KeyBase]

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START list_key_versions]
                :end-before: [END list_key_versions]
                :language: python
                :caption: List all versions of a key
                :dedent: 8
        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_key_versions(
            self._vault_url,
            name,
            maxresults=max_page_size,
            cls=lambda objs: [KeyBase._from_key_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def purge_deleted_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
        """Permanently delete the specified key. This is only possible in vaults with soft-delete enabled. If a vault
        does not have soft-delete enabled, :func:`delete_key` is permanent, and this method will return an error.

        Requires the keys/purge permission.

        :param str name: The name of the key
        :returns: None

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes a deleted key
                # (with soft-delete disabled, delete_key is permanent)
                key_client.purge_deleted_key("key-name")

        """
        self._client.purge_deleted_key(self.vault_url, name, kwargs)

    @distributed_trace
    def recover_deleted_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Key
        """Recover a deleted key to its latest version. This is only possible in vaults with soft-delete enabled. If a
        vault does not have soft-delete enabled, :func:`delete_key` is permanent, and this method will return an error.
        Attempting to recover an non-deleted key will also return an error.

        Requires the keys/recover permission.

        :param str name: The name of the deleted key
        :returns: The recovered key
        :rtype: ~azure.keyvault.keys.models.Key

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START recover_deleted_key]
                :end-before: [END recover_deleted_key]
                :language: python
                :caption: Recover a deleted key
                :dedent: 8
        """
        bundle = self._client.recover_deleted_key(self.vault_url, name, kwargs)
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def update_key(
        self, name, version=None, key_operations=None, enabled=None, expires=None, not_before=None, tags=None, **kwargs
    ):
        # type: (str, Optional[str], Optional[List[str]], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Key
        """Change attributes of a key. Cannot change a key's cryptographic material. Requires the keys/update
        permission.

        :param str name: The name of key to update
        :param str version: (optional) The version of the key to update
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(str or ~azure.keyvault.keys.enums.JsonWebKeyOperation)
        :param bool enabled: (optional) Whether the key is enabled for use
        :param datetime.datetime expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :param dict tags: (optional) Application specific metadata in the form of key-value pairs
        :returns: The updated key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the key doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START update_key]
                :end-before: [END update_key]
                :language: python
                :caption: Update a key's attributes
                :dedent: 8
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.update_key(
            self.vault_url,
            name,
            key_version=version or "",
            key_ops=key_operations,
            tags=tags,
            key_attributes=attributes,
            error_map={404: ResourceNotFoundError},
            **kwargs
        )
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def backup_key(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> bytes
        """Back up a key in a protected form that can't be used outside Azure Key Vault. This is intended to allow
        copying a key from one vault to another. Requires the key/backup permission.

        Backup / restore cannot be performed across geopolitical boundaries. For example, a backup from a vault in a
        USA region cannot be restored to a vault in an EU region.

        :param str name: The name of the key
        :returns: The raw bytes of the key backup
        :rtype: bytes
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the key doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START backup_key]
                :end-before: [END backup_key]
                :language: python
                :caption: Get a key backup
                :dedent: 8
        """
        backup_result = self._client.backup_key(self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs)
        return backup_result.value

    @distributed_trace
    def restore_key(self, backup, **kwargs):
        # type: (bytes, Mapping[str, Any]) -> Key
        """Restore a key backup to the vault. This imports all versions of the key, with its name, attributes, and
        access control policies. Requires the keys/restore permission.

        If the backed up key's name is already in use in the target vault, restoring it will fail. Also, the target
        vault must be owned by the same Microsoft Azure subscription as the source vault.

        :param bytes backup: The raw bytes of the key backup
        :returns: The restored key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: ~azure.core.exceptions.ResourceExistsError if the backed up key's name is already in use

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START restore_key]
                :end-before: [END restore_key]
                :language: python
                :caption: Restore a key backup
                :dedent: 8
        """
        bundle = self._client.restore_key(self.vault_url, backup, error_map={409: ResourceExistsError}, **kwargs)
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def import_key(self, name, key, hsm=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, List[str], Optional[bool], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Key
        """Import an externally created key. If ``name`` is already in use, import the key as a new version. Requires
        the keys/import permission.

        :param str name: Name for the imported key
        :param key: The JSON web key to import
        :type key: ~azure.keyvault.keys.models.JsonWebKey
        :param bool hsm: (optional) Whether to import as a hardware key (HSM) or software key
        :param bool enabled: (optional) Whether the key is enabled for use
        :param expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :param dict tags: (optional) Application specific metadata in the form of key-value pairs
        :returns: The imported key
        :rtype: ~azure.keyvault.keys.models.Key

        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.import_key(
            self.vault_url, name, key=key, hsm=hsm, key_attributes=attributes, tags=tags, **kwargs
        )
        return Key._from_key_bundle(bundle)
