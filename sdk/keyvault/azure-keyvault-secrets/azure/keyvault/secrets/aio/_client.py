# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, AsyncIterable, Optional, Dict
from functools import partial

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._models import KeyVaultSecret, DeletedSecret, SecretProperties
from .._shared import AsyncKeyVaultClientBase
from .._shared.exceptions import error_map as _error_map
from .._shared._polling_async import AsyncDeleteRecoverPollingMethod


class SecretClient(AsyncKeyVaultClientBase):
    """A high-level asynchronous interface for managing a vault's secrets.

    :param str vault_url: URL of the vault the client will access
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :keyword api_version: version of the Key Vault API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.secrets.ApiVersion
    :keyword transport: transport to use. Defaults to
     :class:`~azure.core.pipeline.transport.AioHttpTransport`.
    :paramtype transport: ~azure.core.pipeline.transport.AsyncHttpTransport

    Example:
        .. literalinclude:: ../tests/test_samples_secrets_async.py
            :start-after: [START create_secret_client]
            :end-before: [END create_secret_client]
            :language: python
            :caption: Create a new ``SecretClient``
            :dedent: 4
    """

    # pylint:disable=protected-access

    @distributed_trace_async
    async def get_secret(self, name: str, version: Optional[str] = None, **kwargs: "Any") -> KeyVaultSecret:
        """Get a secret. Requires the secrets/get permission.

        :param str name: The name of the secret
        :param str version: (optional) Version of the secret to get. If unspecified, gets the latest version.
        :rtype: ~azure.keyvault.secrets.KeyVaultSecret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START get_secret]
                :end-before: [END get_secret]
                :language: python
                :caption: Get a secret
                :dedent: 8
        """
        bundle = await self._client.get_secret(self.vault_url, name, version or "", error_map=_error_map, **kwargs)
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace_async
    async def set_secret(self, name: str, value: str, **kwargs: "Any") -> KeyVaultSecret:
        """Set a secret value. If `name` is in use, create a new version of the secret. If not, create a new secret.

        Requires secrets/set permission.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :keyword bool enabled: Whether the secret is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword str content_type: An arbitrary string indicating the type of the secret, e.g. 'password'
        :keyword ~datetime.datetime not_before: Not before date of the secret in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the secret in UTC
        :rtype: ~azure.keyvault.secrets.KeyVaultSecret
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START set_secret]
                :end-before: [END set_secret]
                :language: python
                :caption: Set a secret's value
                :dedent: 8
        """
        enabled = kwargs.pop("enabled", None)
        not_before = kwargs.pop("not_before", None)
        expires_on = kwargs.pop("expires_on", None)
        if enabled is not None or not_before is not None or expires_on is not None:
            attributes = self._models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires_on)
        else:
            attributes = None
        bundle = await self._client.set_secret(
            self.vault_url, name, value, secret_attributes=attributes, error_map=_error_map, **kwargs
        )
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace_async
    async def update_secret_properties(
        self, name: str, version: "Optional[str]" = None, **kwargs: "Any"
    ) -> SecretProperties:
        """Update properties of a secret other than its value. Requires secrets/set permission.

        This method updates properties of the secret, such as whether it's enabled, but can't change the secret's
        value. Use :func:`set_secret` to change the secret's value.

        :param str name: Name of the secret
        :param str version: (optional) Version of the secret to update. If unspecified, the latest version is updated.
        :keyword bool enabled: Whether the secret is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword str content_type: An arbitrary string indicating the type of the secret, e.g. 'password'
        :keyword ~datetime.datetime not_before: Not before date of the secret in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the secret in UTC
        :rtype: ~azure.keyvault.secrets.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START update_secret]
                :end-before: [END update_secret]
                :language: python
                :caption: Updates a secret's attributes
                :dedent: 8
        """
        enabled = kwargs.pop("enabled", None)
        not_before = kwargs.pop("not_before", None)
        expires_on = kwargs.pop("expires_on", None)
        if enabled is not None or not_before is not None or expires_on is not None:
            attributes = self._models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires_on)
        else:
            attributes = None
        bundle = await self._client.update_secret(
            self.vault_url,
            name,
            secret_version=version or "",
            secret_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return SecretProperties._from_secret_bundle(bundle)  # pylint: disable=protected-access

    @distributed_trace
    def list_properties_of_secrets(self, **kwargs: "Any") -> AsyncIterable[SecretProperties]:
        """List identifiers and attributes of all secrets in the vault. Requires secrets/list permission.

        List items don't include secret values. Use :func:`get_secret` to get a secret's value.

        :returns: An iterator of secrets
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START list_secrets]
                :end-before: [END list_secrets]
                :language: python
                :caption: Lists all secrets
                :dedent: 8
        """
        return self._client.get_secrets(
            self.vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_properties_of_secret_versions(self, name: str, **kwargs: "Any") -> AsyncIterable[SecretProperties]:
        """List properties of all versions of a secret, excluding their values. Requires secrets/list permission.

        List items don't include secret values. Use :func:`get_secret` to get a secret's value.

        :param str name: Name of the secret
        :returns: An iterator of secrets, excluding their values
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START list_properties_of_secret_versions]
                :end-before: [END list_properties_of_secret_versions]
                :language: python
                :caption: List all versions of a secret
                :dedent: 8
        """
        return self._client.get_secret_versions(
            self.vault_url,
            name,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace_async
    async def backup_secret(self, name: str, **kwargs: "Any") -> bytes:
        """Back up a secret in a protected form useable only by Azure Key Vault. Requires secrets/backup permission.

        :param str name: Name of the secret
        :rtype: bytes
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

         Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START backup_secret]
                :end-before: [END backup_secret]
                :language: python
                :caption: Back up a secret
                :dedent: 8
        """
        backup_result = await self._client.backup_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        return backup_result.value

    @distributed_trace_async
    async def restore_secret_backup(self, backup: bytes, **kwargs: "Any") -> SecretProperties:
        """Restore a backed up secret. Requires the secrets/restore permission.

        :param bytes backup: A secret backup as returned by :func:`backup_secret`
        :returns: The restored secret
        :rtype: ~azure.keyvault.secrets.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceExistsError` if the secret's name is already in use,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START restore_secret_backup]
                :end-before: [END restore_secret_backup]
                :language: python
                :caption: Restore a backed up secret
                :dedent: 8
        """
        bundle = await self._client.restore_secret(self.vault_url, backup, error_map=_error_map, **kwargs)
        return SecretProperties._from_secret_bundle(bundle)

    @distributed_trace_async
    async def delete_secret(self, name: str, **kwargs: "Any") -> DeletedSecret:
        """Delete all versions of a secret. Requires secrets/delete permission.

        If the vault has soft-delete enabled, deletion may take several seconds to complete.

        :rtype: ~azure.keyvault.secrets.DeletedSecret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START delete_secret]
                :end-before: [END delete_secret]
                :language: python
                :caption: Delete a secret
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        deleted_secret = DeletedSecret._from_deleted_secret_bundle(
            await self._client.delete_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        )

        polling_method = AsyncDeleteRecoverPollingMethod(
            # no recovery ID means soft-delete is disabled, in which case we initialize the poller as finished
            command=partial(self.get_deleted_secret, name=name, **kwargs),
            final_resource=deleted_secret,
            finished=deleted_secret.recovery_id is None,
            interval=polling_interval,
        )
        await polling_method.run()

        return polling_method.resource()

    @distributed_trace_async
    async def get_deleted_secret(self, name: str, **kwargs: "Any") -> DeletedSecret:
        """Get a deleted secret. Possible only in vaults with soft-delete enabled. Requires secrets/get permission.

        :param str name: Name of the deleted secret
        :rtype: ~azure.keyvault.secrets.DeletedSecret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the deleted secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START get_deleted_secret]
                :end-before: [END get_deleted_secret]
                :language: python
                :caption: Get a deleted secret
                :dedent: 8
        """
        bundle = await self._client.get_deleted_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def list_deleted_secrets(self, **kwargs: "Any") -> AsyncIterable[DeletedSecret]:
        """Lists all deleted secrets. Possible only in vaults with soft-delete enabled.

        Requires secrets/list permission.

        :returns: An iterator of deleted secrets, excluding their values
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.DeletedSecret]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START list_deleted_secrets]
                :end-before: [END list_deleted_secrets]
                :language: python
                :caption: Lists deleted secrets
                :dedent: 8
        """
        return self._client.get_deleted_secrets(
            self.vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [DeletedSecret._from_deleted_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace_async
    async def purge_deleted_secret(self, name: str, **kwargs: "Any") -> None:
        """Permanently delete a deleted secret. Possible only in vaults with soft-delete enabled.

        Performs an irreversible deletion of the specified secret, without
        possibility for recovery. The operation is not available if the
        :py:attr:`~azure.keyvault.secrets.SecretProperties.recovery_level` does not specify 'Purgeable'.
        This method is only necessary for purging a secret before its
        :py:attr:`~azure.keyvault.secrets.DeletedSecret.scheduled_purge_date`.

        Requires secrets/purge permission.

        :param str name: Name of the deleted secret to purge
        :returns: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes the secret
                # (with soft-delete disabled, delete_secret is permanent)
                await secret_client.purge_deleted_secret("secret-name")

        """
        await self._client.purge_deleted_secret(self.vault_url, name, error_map=_error_map, **kwargs)

    @distributed_trace_async
    async def recover_deleted_secret(self, name: str, **kwargs: "Any") -> SecretProperties:
        """Recover a deleted secret to its latest version. This is possible only in vaults with soft-delete enabled.

        If the vault does not have soft-delete enabled, :func:`delete_secret` is permanent, and this method will raise
        an error. Attempting to recover a non-deleted secret will also raise an error.

        Requires the secrets/recover permission.

        :param str name: Name of the deleted secret to recover
        :rtype: ~azure.keyvault.secrets.SecretProperties
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START recover_deleted_secret]
                :end-before: [END recover_deleted_secret]
                :language: python
                :caption: Recover a deleted secret
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        recovered_secret = SecretProperties._from_secret_bundle(
            await self._client.recover_deleted_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        )

        command = partial(self.get_secret, name=name, **kwargs)
        polling_method = AsyncDeleteRecoverPollingMethod(
            command=command, final_resource=recovered_secret, finished=False, interval=polling_interval
        )
        await polling_method.run()

        return polling_method.resource()
