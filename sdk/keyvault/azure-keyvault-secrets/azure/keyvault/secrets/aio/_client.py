# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from typing import Any, AsyncIterable, Optional, Dict

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._models import KeyVaultSecret, DeletedSecret, SecretProperties
from .._shared import AsyncKeyVaultClientBase
from .._shared.exceptions import error_map as _error_map


class SecretClient(AsyncKeyVaultClientBase):
    """A high-level asynchronous interface for managing a vault's secrets.

    :param str vault_endpoint: URL of the vault the client will access
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`

    Keyword arguments
        - **api_version**: version of the Key Vault API to use. Defaults to the most recent.
        - **transport**: :class:`~azure.core.pipeline.transport.AsyncHttpTransport` to use. Defaults to
          :class:`~azure.core.pipeline.transport.AioHttpTransport`.

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
        bundle = await self._client.get_secret(self.vault_endpoint, name, version or "", error_map=_error_map, **kwargs)
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace_async
    async def set_secret(self, name: str, value: str, **kwargs: "Any") -> KeyVaultSecret:
        """Set a secret value. Create a new secret if ``name`` is not in use. If it is, create a new version of the
        secret.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :rtype: ~azure.keyvault.secrets.KeyVaultSecret
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - **enabled** (bool): Whether the secret is enabled for use.
            - **tags** (dict[str, str]): Application specific metadata in the form of key-value pairs.
            - **content_type** (str): An arbitrary string indicating the type of the secret, e.g. 'password'
            - **not_before** (:class:`~datetime.datetime`): Not before date of the secret in UTC
            - **expires_on** (:class:`~datetime.datetime`): Expiry date of the secret in UTC

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
            attributes = self._client.models.SecretAttributes(
                enabled=enabled, not_before=not_before, expires=expires_on
            )
        else:
            attributes = None
        bundle = await self._client.set_secret(self.vault_endpoint, name, value, secret_attributes=attributes, **kwargs)
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace_async
    async def update_secret_properties(
        self, name: str, version: "Optional[str]" = None, **kwargs: "Any"
    ) -> SecretProperties:
        """Update a secret's attributes, such as its tags or whether it's enabled. Requires the secrets/set permission.

        **This method can't change a secret's value.** Use :func:`set_secret` to change values.

        :param str name: Name of the secret
        :param str version: (optional) Version of the secret to update. If unspecified, the latest version is updated.
        :rtype: ~azure.keyvault.secrets.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Keyword arguments
            - **enabled** (bool): Whether the secret is enabled for use.
            - **tags** (dict[str, str]): Application specific metadata in the form of key-value pairs.
            - **content_type** (str): An arbitrary string indicating the type of the secret, e.g. 'password'
            - **not_before** (:class:`~datetime.datetime`): Not before date of the secret in UTC
            - **expires_on** (:class:`~datetime.datetime`): Expiry date of the secret in UTC

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
            attributes = self._client.models.SecretAttributes(
                enabled=enabled, not_before=not_before, expires=expires_on
            )
        else:
            attributes = None
        bundle = await self._client.update_secret(
            self.vault_endpoint,
            name,
            secret_version=version or "",
            secret_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return SecretProperties._from_secret_bundle(bundle)  # pylint: disable=protected-access

    @distributed_trace
    def list_properties_of_secrets(self, **kwargs: "Any") -> AsyncIterable[SecretProperties]:
        """List the latest identifier and attributes of all secrets in the vault, not including their values. Requires
        the secrets/list permission.

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
        max_results = kwargs.get("max_page_size")
        return self._client.get_secrets(
            self.vault_endpoint,
            maxresults=max_results,
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_secret_versions(self, name: str, **kwargs: "**Any") -> AsyncIterable[SecretProperties]:
        """List all versions of a secret, including their identifiers and attributes but not their values. Requires the
        secrets/list permission.

        :param str name: Name of the secret
        :returns: An iterator of secrets
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START list_secret_versions]
                :end-before: [END list_secret_versions]
                :language: python
                :caption: List all versions of a secret
                :dedent: 8
        """
        max_results = kwargs.get("max_page_size")
        return self._client.get_secret_versions(
            self.vault_endpoint,
            name,
            maxresults=max_results,
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace_async
    async def backup_secret(self, name: str, **kwargs: "**Any") -> bytes:
        """Get a backup of all versions of a secret. Requires the secrets/backup permission.

        :param str name: Name of the secret
        :returns: The raw bytes of the secret backup
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
        backup_result = await self._client.backup_secret(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return backup_result.value

    @distributed_trace_async
    async def restore_secret_backup(self, backup: bytes, **kwargs: "Any") -> SecretProperties:
        """Restore a backed up secret. Requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
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
        bundle = await self._client.restore_secret(self.vault_endpoint, backup, error_map=_error_map, **kwargs)
        return SecretProperties._from_secret_bundle(bundle)

    @distributed_trace_async
    async def delete_secret(self, name: str, **kwargs: "**Any") -> DeletedSecret:
        """Delete all versions of a secret. Requires the secrets/delete permission.

        :param str name: Name of the secret
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
        bundle = await self._client.delete_secret(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace_async
    async def get_deleted_secret(self, name: str, **kwargs: "**Any") -> DeletedSecret:
        """Get a deleted secret. This is only possible in vaults with soft-delete enabled. Requires the secrets/get
        permission.

        :param str name: Name of the secret
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
        bundle = await self._client.get_deleted_secret(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def list_deleted_secrets(self, **kwargs: "**Any") -> AsyncIterable[DeletedSecret]:
        """Lists all deleted secrets. This is only possible in vaults with soft-delete enabled. Requires the
        secrets/list permission.

        :returns: An iterator of deleted secrets
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.DeletedSecret]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START list_deleted_secrets]
                :end-before: [END list_deleted_secrets]
                :language: python
                :caption: Lists deleted secrets
                :dedent: 8
        """
        max_results = kwargs.get("max_page_size")
        return self._client.get_deleted_secrets(
            self.vault_endpoint,
            maxresults=max_results,
            cls=lambda objs: [DeletedSecret._from_deleted_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace_async
    async def purge_deleted_secret(self, name: str, **kwargs: "**Any") -> None:
        """Permanently delete a secret. This is only possible in vaults with soft-delete enabled. If a vault
        doesn't have soft-delete enabled, :func:`delete_secret` is permanent, and this method will return an error.

        Requires the secrets/purge permission.

        :param str name: Name of the secret
        :returns: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes the secret
                # (with soft-delete disabled, delete_secret is permanent)
                await secret_client.purge_deleted_secret("secret-name")

        """
        await self._client.purge_deleted_secret(self.vault_endpoint, name, **kwargs)

    @distributed_trace_async
    async def recover_deleted_secret(self, name: str, **kwargs: "**Any") -> SecretProperties:
        """Recover a deleted secret to its latest version. This is only possible in vaults with soft-delete enabled.
        Requires the secrets/recover permission.

        :param str name: Name of the secret
        :returns: The recovered secret
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
        bundle = await self._client.recover_deleted_secret(self.vault_endpoint, name, **kwargs)
        return SecretProperties._from_secret_bundle(bundle)
