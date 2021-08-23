# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from functools import partial
from azure.core.tracing.decorator import distributed_trace

from ._shared import KeyVaultClientBase
from ._shared.exceptions import error_map as _error_map
from ._shared._polling import DeleteRecoverPollingMethod, KeyVaultOperationPoller
from ._models import DeletedKey, KeyVaultKey, KeyProperties, RandomBytes, ReleaseKeyResult

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional, Union
    from azure.core.paging import ItemPaged
    from ._models import JsonWebKey


class KeyClient(KeyVaultClientBase):
    """A high-level interface for managing a vault's keys.

    :param str vault_url: URL of the vault the client will access. This is also called the vault's "DNS Name".
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`

    :keyword api_version: version of the Key Vault API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.keys.ApiVersion
    :keyword transport: transport to use. Defaults to :class:`~azure.core.pipeline.transport.RequestsTransport`.
    :paramtype transport: ~azure.core.pipeline.transport.HttpTransport

    Example:
        .. literalinclude:: ../tests/test_samples_keys.py
            :start-after: [START create_key_client]
            :end-before: [END create_key_client]
            :language: python
            :caption: Create a new ``KeyClient``
            :dedent: 4
    """

    # pylint:disable=protected-access

    def _get_attributes(self, enabled, not_before, expires_on, exportable=None):
        """Return a KeyAttributes object if none-None attributes are provided, or None otherwise"""
        if enabled is not None or not_before is not None or expires_on is not None or exportable is not None:
            return self._models.KeyAttributes(
                enabled=enabled, not_before=not_before, expires=expires_on, exportable=exportable
            )
        return None

    @distributed_trace
    def create_key(self, name, key_type, **kwargs):
        # type: (str, Union[str, azure.keyvault.keys.KeyType], **Any) -> KeyVaultKey
        """Create a key or, if ``name`` is already in use, create a new version of the key.

        Requires keys/create permission.

        :param str name: The name of the new key.
        :param key_type: The type of key to create
        :type key_type: ~azure.keyvault.keys.KeyType or str

        :keyword int size: Key size in bits. Applies only to RSA and symmetric keys. Consider using
         :func:`create_rsa_key` or :func:`create_oct_key` instead.
        :keyword curve: Elliptic curve name. Applies only to elliptic curve keys. Defaults to the NIST P-256
         elliptic curve. To create an elliptic curve key, consider using :func:`create_ec_key` instead.
        :paramtype curve: ~azure.keyvault.keys.KeyCurveName or str
        :keyword int public_exponent: The RSA public exponent to use. Applies only to RSA keys created in a Managed HSM.
        :keyword key_operations: Allowed key operations
        :paramtype key_operations: list[~azure.keyvault.keys.KeyOperation or str]
        :keyword bool enabled: Whether the key is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword ~datetime.datetime not_before: Not before date of the key in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the key in UTC
        :keyword bool exportable: Whether the private key can be exported.
        :keyword release_policy: The policy rules under which the key can be exported.
        :paramtype release_policy: ~azure.keyvault.keys.KeyReleasePolicy

        :returns: The created key
        :rtype: ~azure.keyvault.keys.KeyVaultKey
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_key]
                :end-before: [END create_key]
                :language: python
                :caption: Create a key
                :dedent: 8
        """
        enabled = kwargs.pop("enabled", None)
        not_before = kwargs.pop("not_before", None)
        expires_on = kwargs.pop("expires_on", None)
        exportable = kwargs.pop("exportable", None)
        attributes = self._get_attributes(
            enabled=enabled, not_before=not_before, expires_on=expires_on, exportable=exportable
        )

        policy = kwargs.pop("release_policy", None)
        if policy is not None:
            policy = self._models.KeyReleasePolicy(data=policy.data, content_type=policy.content_type)
        parameters = self._models.KeyCreateParameters(
            kty=key_type,
            key_size=kwargs.pop("size", None),
            key_attributes=attributes,
            key_ops=kwargs.pop("key_operations", None),
            tags=kwargs.pop("tags", None),
            curve=kwargs.pop("curve", None),
            public_exponent=kwargs.pop("public_exponent", None),
            release_policy=policy,
        )

        bundle = self._client.create_key(
            vault_base_url=self.vault_url,
            key_name=name,
            parameters=parameters,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultKey._from_key_bundle(bundle)

    @distributed_trace
    def create_rsa_key(self, name, **kwargs):
        # type: (str, **Any) -> KeyVaultKey
        """Create a new RSA key or, if ``name`` is already in use, create a new version of the key

        Requires the keys/create permission.

        :param str name: The name for the new key.

        :keyword int size: Key size in bits, for example 2048, 3072, or 4096.
        :keyword int public_exponent: The RSA public exponent to use. Applies only to RSA keys created in a Managed HSM.
        :keyword bool hardware_protected: Whether the key should be created in a hardware security module.
         Defaults to ``False``.
        :keyword key_operations: Allowed key operations
        :paramtype key_operations: list[~azure.keyvault.keys.KeyOperation or str]
        :keyword bool enabled: Whether the key is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword ~datetime.datetime not_before: Not before date of the key in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the key in UTC
        :keyword bool exportable: Whether the private key can be exported.
        :keyword release_policy: The policy rules under which the key can be exported.
        :paramtype release_policy: ~azure.keyvault.keys.KeyReleasePolicy

        :returns: The created key
        :rtype: ~azure.keyvault.keys.KeyVaultKey
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_rsa_key]
                :end-before: [END create_rsa_key]
                :language: python
                :caption: Create RSA key
                :dedent: 8
        """
        hsm = kwargs.pop("hardware_protected", False)
        return self.create_key(name, key_type="RSA-HSM" if hsm else "RSA", **kwargs)

    @distributed_trace
    def create_ec_key(self, name, **kwargs):
        # type: (str, **Any) -> KeyVaultKey
        """Create a new elliptic curve key or, if ``name`` is already in use, create a new version of the key.

        Requires the keys/create permission.

        :param str name: The name for the new key.

        :keyword curve: Elliptic curve name. Defaults to the NIST P-256 elliptic curve.
        :paramtype curve: ~azure.keyvault.keys.KeyCurveName or str
        :keyword key_operations: Allowed key operations
        :paramtype key_operations: list[~azure.keyvault.keys.KeyOperation or str]
        :keyword bool hardware_protected: Whether the key should be created in a hardware security module.
         Defaults to ``False``.
        :keyword bool enabled: Whether the key is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword ~datetime.datetime not_before: Not before date of the key in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the key in UTC
        :keyword bool exportable: Whether the private key can be exported.
        :keyword release_policy: The policy rules under which the key can be exported.
        :paramtype release_policy: ~azure.keyvault.keys.KeyReleasePolicy

        :returns: The created key
        :rtype: ~azure.keyvault.keys.KeyVaultKey
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_ec_key]
                :end-before: [END create_ec_key]
                :language: python
                :caption: Create an elliptic curve key
                :dedent: 8
        """
        hsm = kwargs.pop("hardware_protected", False)
        return self.create_key(name, key_type="EC-HSM" if hsm else "EC", **kwargs)

    @distributed_trace
    def create_oct_key(self, name, **kwargs):
        # type: (str, **Any) -> KeyVaultKey
        """Create a new octet sequence (symmetric) key or, if ``name`` is in use, create a new version of the key.

        Requires the keys/create permission.

        :param str name: The name for the new key.

        :keyword int size: Key size in bits, for example 128, 192, or 256.
        :keyword key_operations: Allowed key operations.
        :paramtype key_operations: list[~azure.keyvault.keys.KeyOperation or str]
        :keyword bool hardware_protected: Whether the key should be created in a hardware security module.
         Defaults to ``False``.
        :keyword bool enabled: Whether the key is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword ~datetime.datetime not_before: Not before date of the key in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the key in UTC
        :keyword bool exportable: Whether the key can be exported.
        :keyword release_policy: The policy rules under which the key can be exported.
        :paramtype release_policy: ~azure.keyvault.keys.KeyReleasePolicy

        :returns: The created key
        :rtype: ~azure.keyvault.keys.KeyVaultKey
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START create_oct_key]
                :end-before: [END create_oct_key]
                :language: python
                :caption: Create an octet sequence (symmetric) key
                :dedent: 8
        """
        hsm = kwargs.pop("hardware_protected", False)
        return self.create_key(name, key_type="oct-HSM" if hsm else "oct", **kwargs)

    @distributed_trace
    def begin_delete_key(self, name, **kwargs):
        # type: (str, **Any) -> DeletedKey
        """Delete all versions of a key and its cryptographic material.

        Requires keys/delete permission. When this method returns Key Vault has begun deleting the key. Deletion may
        take several seconds in a vault with soft-delete enabled. This method therefore returns a poller enabling you to
        wait for deletion to complete.

        :param str name: The name of the key to delete.

        :returns: A poller for the delete key operation. The poller's `result` method returns the
         :class:`~azure.keyvault.keys.DeletedKey` without waiting for deletion to complete. If the vault has
         soft-delete enabled and you want to permanently delete the key with :func:`purge_deleted_key`, call the
         poller's `wait` method first. It will block until the deletion is complete. The `wait` method requires
         keys/get permission.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.keys.DeletedKey]
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
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        deleted_key = DeletedKey._from_deleted_key_bundle(
            self._client.delete_key(self.vault_url, name, error_map=_error_map, **kwargs)
        )

        command = partial(self.get_deleted_key, name=name, **kwargs)
        polling_method = DeleteRecoverPollingMethod(
            # no recovery ID means soft-delete is disabled, in which case we initialize the poller as finished
            finished=deleted_key.recovery_id is None,
            command=command,
            final_resource=deleted_key,
            interval=polling_interval,
        )
        return KeyVaultOperationPoller(polling_method)

    @distributed_trace
    def get_key(self, name, version=None, **kwargs):
        # type: (str, Optional[str], **Any) -> KeyVaultKey
        """Get a key's attributes and, if it's an asymmetric key, its public material.

        Requires keys/get permission.

        :param str name: The name of the key to get.
        :param str version: (optional) A specific version of the key to get. If not specified, gets the latest version
            of the key.

        :rtype: ~azure.keyvault.keys.KeyVaultKey
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
        bundle = self._client.get_key(self.vault_url, name, key_version=version or "", error_map=_error_map, **kwargs)
        return KeyVaultKey._from_key_bundle(bundle)

    @distributed_trace
    def get_deleted_key(self, name, **kwargs):
        # type: (str, **Any) -> DeletedKey
        """Get a deleted key. Possible only in a vault with soft-delete enabled.

        Requires keys/get permission.

        :param str name: The name of the key

        :returns: The deleted key
        :rtype: ~azure.keyvault.keys.DeletedKey
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
        bundle = self._client.get_deleted_key(self.vault_url, name, error_map=_error_map, **kwargs)
        return DeletedKey._from_deleted_key_bundle(bundle)

    @distributed_trace
    def list_deleted_keys(self, **kwargs):
        # type: (**Any) -> ItemPaged[DeletedKey]
        """List all deleted keys, including the public part of each. Possible only in a vault with soft-delete enabled.

        Requires keys/list permission.

        :returns: An iterator of deleted keys
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.DeletedKey]

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START list_deleted_keys]
                :end-before: [END list_deleted_keys]
                :language: python
                :caption: List all the deleted keys
                :dedent: 8
        """
        return self._client.get_deleted_keys(
            self._vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [DeletedKey._from_deleted_key_item(x) for x in objs],
            error_map=_error_map,
            **kwargs
        )

    @distributed_trace
    def list_properties_of_keys(self, **kwargs):
        # type: (**Any) -> ItemPaged[KeyProperties]
        """List identifiers and properties of all keys in the vault.

        Requires keys/list permission.

        :returns: An iterator of keys without their cryptographic material or version information
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.KeyProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START list_keys]
                :end-before: [END list_keys]
                :language: python
                :caption: List all keys
                :dedent: 8
        """
        return self._client.get_keys(
            self._vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [KeyProperties._from_key_item(x) for x in objs],
            error_map=_error_map,
            **kwargs
        )

    @distributed_trace
    def list_properties_of_key_versions(self, name, **kwargs):
        # type: (str, **Any) -> ItemPaged[KeyProperties]
        """List the identifiers and properties of a key's versions.

        Requires keys/list permission.

        :param str name: The name of the key

        :returns: An iterator of keys without their cryptographic material
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.keys.KeyProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START list_properties_of_key_versions]
                :end-before: [END list_properties_of_key_versions]
                :language: python
                :caption: List all versions of a key
                :dedent: 8
        """
        return self._client.get_key_versions(
            self._vault_url,
            name,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [KeyProperties._from_key_item(x) for x in objs],
            error_map=_error_map,
            **kwargs
        )

    @distributed_trace
    def purge_deleted_key(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Permanently deletes a deleted key. Only possible in a vault with soft-delete enabled.

        Performs an irreversible deletion of the specified key, without
        possibility for recovery. The operation is not available if the
        :py:attr:`~azure.keyvault.keys.KeyProperties.recovery_level` does not specify 'Purgeable'.
        This method is only necessary for purging a key before its
        :py:attr:`~azure.keyvault.keys.DeletedKey.scheduled_purge_date`.

        Requires keys/purge permission.

        :param str name: The name of the deleted key to purge

        :returns: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes a deleted key
                # (with soft-delete disabled, begin_delete_key is permanent)
                key_client.purge_deleted_key("key-name")

        """
        self._client.purge_deleted_key(vault_base_url=self.vault_url, key_name=name, error_map=_error_map, **kwargs)

    @distributed_trace
    def begin_recover_deleted_key(self, name, **kwargs):
        # type: (str, **Any) -> KeyVaultKey
        """Recover a deleted key to its latest version. Possible only in a vault with soft-delete enabled.

        Requires keys/recover permission.

        When this method returns Key Vault has begun recovering the key. Recovery may take several seconds. This
        method therefore returns a poller enabling you to wait for recovery to complete. Waiting is only necessary when
        you want to use the recovered key in another operation immediately.

        :param str name: The name of the deleted key to recover

        :returns: A poller for the recovery operation. The poller's `result` method returns the recovered
         :class:`~azure.keyvault.keys.KeyVaultKey` without waiting for recovery to complete. If you want to use the
         recovered key immediately, call the poller's `wait` method, which blocks until the key is ready to use. The
         `wait` method requires keys/get permission.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.keys.KeyVaultKey]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START recover_deleted_key]
                :end-before: [END recover_deleted_key]
                :language: python
                :caption: Recover a deleted key
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        recovered_key = KeyVaultKey._from_key_bundle(
            self._client.recover_deleted_key(
                vault_base_url=self.vault_url, key_name=name, error_map=_error_map, **kwargs
            )
        )
        command = partial(self.get_key, name=name, **kwargs)
        polling_method = DeleteRecoverPollingMethod(
            finished=False, command=command, final_resource=recovered_key, interval=polling_interval,
        )

        return KeyVaultOperationPoller(polling_method)

    @distributed_trace
    def update_key_properties(self, name, version=None, **kwargs):
        # type: (str, Optional[str], **Any) -> KeyVaultKey
        """Change a key's properties (not its cryptographic material).

        Requires keys/update permission.

        :param str name: The name of key to update
        :param str version: (optional) The version of the key to update. If unspecified, the latest version is updated.

        :keyword key_operations: Allowed key operations
        :paramtype key_operations: list[~azure.keyvault.keys.KeyOperation or str]
        :keyword bool enabled: Whether the key is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword ~datetime.datetime not_before: Not before date of the key in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the key in UTC
        :keyword release_policy: The policy rules under which the key can be exported.
        :paramtype release_policy: ~azure.keyvault.keys.KeyReleasePolicy

        :returns: The updated key
        :rtype: ~azure.keyvault.keys.KeyVaultKey
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the key doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START update_key]
                :end-before: [END update_key]
                :language: python
                :caption: Update a key's attributes
                :dedent: 8
        """
        enabled = kwargs.pop("enabled", None)
        not_before = kwargs.pop("not_before", None)
        expires_on = kwargs.pop("expires_on", None)
        attributes = self._get_attributes(enabled=enabled, not_before=not_before, expires_on=expires_on)

        policy = kwargs.pop("release_policy", None)
        if policy is not None:
            policy = self._models.KeyReleasePolicy(content_type=policy.content_type, data=policy.data)
        parameters = self._models.KeyUpdateParameters(
            key_ops=kwargs.pop("key_operations", None),
            key_attributes=attributes,
            tags=kwargs.pop("tags", None),
            release_policy=policy,
        )

        bundle = self._client.update_key(
            self.vault_url,
            name,
            key_version=version or "",
            parameters=parameters,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultKey._from_key_bundle(bundle)

    @distributed_trace
    def backup_key(self, name, **kwargs):
        # type: (str, **Any) -> bytes
        """Back up a key in a protected form useable only by Azure Key Vault.

        Requires keys/backup permission.

        This is intended to allow copying a key from one vault to another. Both vaults must be owned by the same Azure
        subscription. Also, backup / restore cannot be performed across geopolitical boundaries. For example, a backup
        from a vault in a USA region cannot be restored to a vault in an EU region.

        :param str name: The name of the key to back up

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
        backup_result = self._client.backup_key(self.vault_url, name, error_map=_error_map, **kwargs)
        return backup_result.value

    @distributed_trace
    def restore_key_backup(self, backup, **kwargs):
        # type: (bytes, **Any) -> KeyVaultKey
        """Restore a key backup to the vault.

        Requires keys/restore permission.

        This imports all versions of the key, with its name, attributes, and access control policies. If the key's name
        is already in use, restoring it will fail. Also, the target vault must be owned by the same Microsoft Azure
        subscription as the source vault.

        :param bytes backup: A key backup as returned by :func:`backup_key`

        :returns: The restored key
        :rtype: ~azure.keyvault.keys.KeyVaultKey
        :raises:
            :class:`~azure.core.exceptions.ResourceExistsError` if the backed up key's name is already in use,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_keys.py
                :start-after: [START restore_key_backup]
                :end-before: [END restore_key_backup]
                :language: python
                :caption: Restore a key backup
                :dedent: 8
        """
        bundle = self._client.restore_key(
            self.vault_url,
            parameters=self._models.KeyRestoreParameters(key_bundle_backup=backup),
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultKey._from_key_bundle(bundle)

    @distributed_trace
    def import_key(self, name, key, **kwargs):
        # type: (str, JsonWebKey, **Any) -> KeyVaultKey
        """Import a key created externally.

        Requires keys/import permission. If ``name`` is already in use, the key will be imported as a new version.

        :param str name: Name for the imported key
        :param key: The JSON web key to import
        :type key: ~azure.keyvault.keys.JsonWebKey

        :keyword bool hardware_protected: Whether the key should be backed by a hardware security module
        :keyword bool enabled: Whether the key is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword ~datetime.datetime not_before: Not before date of the key in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the key in UTC
        :keyword bool exportable: Whether the private key can be exported.
        :keyword release_policy: The policy rules under which the key can be exported.
        :paramtype release_policy: ~azure.keyvault.keys.KeyReleasePolicy

        :returns: The imported key
        :rtype: ~azure.keyvault.keys.KeyVaultKey
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        enabled = kwargs.pop("enabled", None)
        not_before = kwargs.pop("not_before", None)
        expires_on = kwargs.pop("expires_on", None)
        exportable = kwargs.pop("exportable", None)
        attributes = self._get_attributes(
            enabled=enabled, not_before=not_before, expires_on=expires_on, exportable=exportable
        )

        policy = kwargs.pop("release_policy", None)
        if policy is not None:
            policy = self._models.KeyReleasePolicy(content_type=policy.content_type, data=policy.data)
        parameters = self._models.KeyImportParameters(
            key=key._to_generated_model(),
            key_attributes=attributes,
            hsm=kwargs.pop("hardware_protected", None),
            tags=kwargs.pop("tags", None),
            release_policy=policy,
        )

        bundle = self._client.import_key(
            self.vault_url,
            name,
            parameters=parameters,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultKey._from_key_bundle(bundle)

    @distributed_trace
    def release_key(self, name, target, version=None, **kwargs):
        # type: (str, str, Optional[str], **Any) -> ReleaseKeyResult
        """Releases a key.

        The release key operation is applicable to all key types. The target key must be marked
        exportable. This operation requires the keys/release permission.

        :param str name: The name of the key to get.
        :param str target: The attestation assertion for the target of the key release.
        :param str version: (optional) A specific version of the key to release. If unspecified, the latest version is
            released.

        :keyword algorithm: The encryption algorithm to use to protect the released key material.
        :paramtype algorithm: ~azure.keyvault.keys.KeyExportEncryptionAlgorithm
        :keyword str nonce: A client-provided nonce for freshness.

        :return: The result of the key release.
        :rtype: ~azure.keyvault.keys.ReleaseKeyResult
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        result = self._client.release(
            vault_base_url=self._vault_url,
            key_name=name,
            key_version=version or "",
            parameters=self._models.KeyReleaseParameters(
                target=target, nonce=kwargs.pop("nonce", None), enc=kwargs.pop("algorithm", None)
            ),
            **kwargs
        )
        return ReleaseKeyResult(result.value)

    @distributed_trace
    def get_random_bytes(self, count, **kwargs):
        # type: (int, **Any) -> RandomBytes
        """Get the requested number of random bytes from a managed HSM.

        :param int count: The requested number of random bytes.

        :return: The random bytes.
        :rtype: ~azure.keyvault.keys.RandomBytes
        :raises:
            :class:`ValueError` if less than one random byte is requested,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_key_client.py
                :start-after: [START get_random_bytes]
                :end-before: [END get_random_bytes]
                :language: python
                :caption: Get random bytes
                :dedent: 12
        """
        if count < 1:
            raise ValueError("At least one random byte must be requested")
        parameters = self._models.GetRandomBytesRequest(count=count)
        result = self._client.get_random_bytes(vault_base_url=self._vault_url, parameters=parameters, **kwargs)
        return RandomBytes(value=result.value)
