# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.tracing.decorator import distributed_trace

from ._shared import KeyVaultClientBase
from ._shared.exceptions import error_map as _error_map
from .crypto import CryptographyClient
from .models import Key, KeyProperties, DeletedKey

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, List, Optional, Union
    from datetime import datetime
    from azure.core.paging import ItemPaged
    from .models import JsonWebKey


class KeyClient(KeyVaultClientBase):
    """A high-level interface for managing a vault's keys.

    :param str vault_endpoint: URL of the vault the client will access
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`

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
        # type: (Union[Key, str], **Any) -> CryptographyClient
        """
        Get a :class:`~azure.keyvault.keys.crypto.CryptographyClient` capable of performing cryptographic operations
        with a key.

        :param key:
            Either a :class:`~azure.keyvault.keys.Key` instance as returned by
            :func:`~azure.keyvault.keys.KeyClient.get_key`, or a string. If a string, the value must be the full
            identifier of an Azure Key Vault key with a version.
        :type key: str or :class:`~azure.keyvault.keys.Key`
        :rtype: :class:`~azure.keyvault.keys.crypto.CryptographyClient`
        """

        # the initializer requires a credential but won't actually use it in this case because we pass in this
        # KeyClient's generated client, whose pipeline (and auth policy) is fully configured
        credential = object()
        return CryptographyClient(key, credential, generated_client=self._client, **kwargs)

    @distributed_trace
    def create_key(
        self,
        name,  # type: str
        key_type,  # type: str
        size=None,  # type: Optional[int]
        key_operations=None,  # type: Optional[List[str]]
        expires=None,  # type: Optional[datetime]
        not_before=None,  # type: Optional[datetime]
        curve=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Key
        """Create a key. If ``name`` is already in use, create a new version of the key. Requires the keys/create
        permission.

        :param str name: The name of the new key. Key Vault will generate the key's version.
        :param key_type: The type of key to create
        :type key_type: str or ~azure.keyvault.keys.enums.KeyType
        :param int size: (optional) RSA key size in bits, for example 2048, 3072, or 4096.
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(str or ~azure.keyvault.keys.enums.KeyOperation)
        :param expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :param curve: (optional) Elliptic curve name. Defaults to the NIST P-256 elliptic curve.
        :type curve: ~azure.keyvault.keys.enums.KeyCurveName or str
        :returns: The created key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Whether the key is enabled for use.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_key]
                :end-before: [END create_key]
                :language: python
                :caption: Create a key
                :dedent: 8
        """
        enabled = kwargs.pop('enabled', None)

        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None

        bundle = self._client.create_key(
            vault_base_url=self.vault_endpoint,
            key_name=name,
            kty=key_type,
            key_size=size,
            key_attributes=attributes,
            key_ops=key_operations,
            curve=curve,
            **kwargs
        )
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def create_rsa_key(
        self,
        name,  # type: str
        hsm,  # type: bool
        size=None,  # type: Optional[int]
        key_operations=None,  # type: Optional[List[str]]
        expires=None,  # type: Optional[datetime]
        not_before=None,  # type: Optional[datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> Key
        """Create a new RSA key. If ``name`` is already in use, create a new version of the key. Requires the
        keys/create permission.

        :param str name: The name for the new key. Key Vault will generate the key's version.
        :param bool hsm: Whether to create a hardware key (HSM) or software key
        :param int size: (optional) Key size in bits, for example 2048, 3072, or 4096
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(str or ~azure.keyvault.keys.enums.KeyOperation)
        :param expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :returns: The created key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Whether the key is enabled for use.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

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
            expires=expires,
            not_before=not_before,
            **kwargs
        )

    @distributed_trace
    def create_ec_key(
        self,
        name,  # type: str
        hsm,  # type: bool
        curve=None,  # type: Optional[str]
        key_operations=None,  # type: Optional[List[str]]
        expires=None,  # type: Optional[datetime]
        not_before=None,  # type: Optional[datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> Key
        """Create a new elliptic curve key. If ``name`` is already in use, create a new version of the key. Requires
        the keys/create permission.

        :param str name: The name for the new key. Key Vault will generate the key's version.
        :param bool hsm: Whether to create as a hardware key (HSM) or software key.
        :param curve: (optional) Elliptic curve name. Defaults to the NIST P-256 elliptic curve.
        :type curve: ~azure.keyvault.keys.enums.KeyCurveName or str
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(~azure.keyvault.keys.enums.KeyOperation)
        :param datetime.datetime expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :returns: The created key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Whether the key is enabled for use.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

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
            expires=expires,
            not_before=not_before,
            **kwargs
        )

    @distributed_trace
    def delete_key(self, name, **kwargs):
        # type: (str, **Any) -> DeletedKey
        """Delete all versions of a key and its cryptographic material. Requires the keys/delete permission.

        :param str name: The name of the key to delete.
        :returns: The deleted key
        :rtype: ~azure.keyvault.keys.models.DeletedKey
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the key doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START delete_key]
                :end-before: [END delete_key]
                :language: python
                :caption: Delete a key
                :dedent: 8
        """
        bundle = self._client.delete_key(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return DeletedKey._from_deleted_key_bundle(bundle)

    @distributed_trace
    def get_key(self, name, version=None, **kwargs):
        # type: (str, Optional[str], **Any) -> Key
        """Get a key's attributes and, if it's an asymmetric key, its public material. Requires the keys/get permission.

        :param str name: The name of the key to get.
        :param str version: (optional) A specific version of the key to get. If not specified, gets the latest version
            of the key.
        :rtype: ~azure.keyvault.keys.models.Key
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the key doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START get_key]
                :end-before: [END get_key]
                :language: python
                :caption: Get a key
                :dedent: 8
        """
        bundle = self._client.get_key(
            self.vault_endpoint, name, key_version=version or "", error_map=_error_map, **kwargs
        )
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def get_deleted_key(self, name, **kwargs):
        # type: (str, **Any) -> DeletedKey
        """Get a deleted key. This is only possible in a vault with soft-delete enabled. Requires the keys/get
        permission.

        :param str name: The name of the key
        :returns: The deleted key
        :rtype: ~azure.keyvault.keys.models.DeletedKey
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the key doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START get_deleted_key]
                :end-before: [END get_deleted_key]
                :language: python
                :caption: Get a deleted key
                :dedent: 8
        """
        # TODO: which exception is raised when soft-delete is not enabled
        bundle = self._client.get_deleted_key(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return DeletedKey._from_deleted_key_bundle(bundle)

    @distributed_trace
    def list_deleted_keys(self, **kwargs):
        # type: (**Any) -> ItemPaged[DeletedKey]
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
            self._vault_endpoint,
            maxresults=max_page_size,
            cls=lambda objs: [DeletedKey._from_deleted_key_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_keys(self, **kwargs):
        # type: (**Any) -> ItemPaged[KeyProperties]
        """List identifiers, attributes, and tags of all keys in the vault. Requires the keys/list permission.

        :returns: An iterator of keys without their cryptographic material or version information
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.models.KeyProperties]

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
            self._vault_endpoint,
            maxresults=max_page_size,
            cls=lambda objs: [KeyProperties._from_key_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_key_versions(self, name, **kwargs):
        # type: (str, **Any) -> ItemPaged[KeyProperties]
        """List the identifiers, attributes, and tags of a key's versions. Requires the keys/list permission.

        :param str name: The name of the key
        :returns: An iterator of keys without their cryptographic material
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.models.KeyProperties]

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
            self._vault_endpoint,
            name,
            maxresults=max_page_size,
            cls=lambda objs: [KeyProperties._from_key_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def purge_deleted_key(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Permanently delete the specified key. This is only possible in vaults with soft-delete enabled. If a vault
        does not have soft-delete enabled, :func:`delete_key` is permanent, and this method will return an error.

        Requires the keys/purge permission.

        :param str name: The name of the key
        :returns: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes a deleted key
                # (with soft-delete disabled, delete_key is permanent)
                key_client.purge_deleted_key("key-name")

        """
        self._client.purge_deleted_key(vault_base_url=self.vault_endpoint, key_name=name, **kwargs)

    @distributed_trace
    def recover_deleted_key(self, name, **kwargs):
        # type: (str, **Any) -> Key
        """Recover a deleted key to its latest version. This is only possible in vaults with soft-delete enabled. If a
        vault does not have soft-delete enabled, :func:`delete_key` is permanent, and this method will return an error.
        Attempting to recover an non-deleted key will also return an error.

        Requires the keys/recover permission.

        :param str name: The name of the deleted key
        :returns: The recovered key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START recover_deleted_key]
                :end-before: [END recover_deleted_key]
                :language: python
                :caption: Recover a deleted key
                :dedent: 8
        """
        bundle = self._client.recover_deleted_key(vault_base_url=self.vault_endpoint, key_name=name, **kwargs)
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def update_key_properties(
        self,
        name,  # type: str
        version=None,  # type: Optional[str]
        key_operations=None,  # type: Optional[List[str]]
        expires=None,  # type: Optional[datetime]
        not_before=None,  # type: Optional[datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> Key
        """Change attributes of a key. Cannot change a key's cryptographic material. Requires the keys/update
        permission.

        :param str name: The name of key to update
        :param str version: (optional) The version of the key to update
        :param key_operations: (optional) Allowed key operations
        :type key_operations: list(str or ~azure.keyvault.keys.enums.KeyOperation)
        :param datetime.datetime expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :returns: The updated key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the key doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Keyword arguments
            - *enabled (bool)* - Whether the key is enabled for use.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START update_key]
                :end-before: [END update_key]
                :language: python
                :caption: Update a key's attributes
                :dedent: 8
        """
        enabled = kwargs.pop('enabled', None)
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.update_key(
            self.vault_endpoint,
            name,
            key_version=version or "",
            key_ops=key_operations,
            key_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def backup_key(self, name, **kwargs):
        # type: (str, **Any) -> bytes
        """Back up a key in a protected form that can't be used outside Azure Key Vault. This is intended to allow
        copying a key from one vault to another. Requires the key/backup permission.

        Backup / restore cannot be performed across geopolitical boundaries. For example, a backup from a vault in a
        USA region cannot be restored to a vault in an EU region.

        :param str name: The name of the key
        :returns: The raw bytes of the key backup
        :rtype: bytes
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the key doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START backup_key]
                :end-before: [END backup_key]
                :language: python
                :caption: Get a key backup
                :dedent: 8
        """
        backup_result = self._client.backup_key(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return backup_result.value

    @distributed_trace
    def restore_key(self, backup, **kwargs):
        # type: (bytes, **Any) -> Key
        """Restore a key backup to the vault. This imports all versions of the key, with its name, attributes, and
        access control policies. Requires the keys/restore permission.

        If the backed up key's name is already in use in the target vault, restoring it will fail. Also, the target
        vault must be owned by the same Microsoft Azure subscription as the source vault.

        :param bytes backup: The raw bytes of the key backup
        :returns: The restored key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises:
            :class:`~azure.core.exceptions.ResourceExistsError` if the backed up key's name is already in use,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START restore_key]
                :end-before: [END restore_key]
                :language: python
                :caption: Restore a key backup
                :dedent: 8
        """
        bundle = self._client.restore_key(self.vault_endpoint, backup, error_map=_error_map, **kwargs)
        return Key._from_key_bundle(bundle)

    @distributed_trace
    def import_key(
        self,
        name,  # type: str
        key,  # type: JsonWebKey
        hsm=None,  # type: Optional[bool]
        not_before=None,  # type: Optional[datetime]
        expires=None,  # type: Optional[datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> Key
        """Import an externally created key. If ``name`` is already in use, import the key as a new version. Requires
        the keys/import permission.

        :param str name: Name for the imported key
        :param key: The JSON web key to import
        :type key: ~azure.keyvault.keys.models.JsonWebKey
        :param bool hsm: (optional) Whether to import as a hardware key (HSM) or software key
        :param expires: (optional) Expiry date of the key in UTC
        :param datetime.datetime not_before: (optional) Not before date of the key in UTC
        :returns: The imported key
        :rtype: ~azure.keyvault.keys.models.Key
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Whether the key is enabled for use.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

        """
        enabled = kwargs.pop('enabled', None)
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.KeyAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.import_key(
            self.vault_endpoint,
            name,
            key=key._to_generated_model(),
            hsm=hsm,
            key_attributes=attributes,
            **kwargs
        )
        return Key._from_key_bundle(bundle)
