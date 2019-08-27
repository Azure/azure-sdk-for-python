# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from typing import Any, AsyncIterable, Optional, Dict

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from azure.keyvault.secrets.models import Secret, DeletedSecret, SecretAttributes
from .._shared import AsyncKeyVaultClientBase


class SecretClient(AsyncKeyVaultClientBase):
    """A high-level asynchronous interface for managing a vault's secrets.

    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :param str vault_url: URL of the vault the client will access

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
    async def get_secret(self, name: str, version: Optional[str] = None, **kwargs: "**Any") -> Secret:
        """Get a secret. Requires the secrets/get permission.

        :param str name: The name of the secret
        :param str version: (optional) Version of the secret to get. If unspecified, gets the latest version.
        :rtype: ~azure.keyvault.secrets.models.Secret
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the secret doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START get_secret]
                :end-before: [END get_secret]
                :language: python
                :caption: Get a secret
                :dedent: 8
        """
        bundle = await self._client.get_secret(
            self.vault_url, name, version or "", error_map={404: ResourceNotFoundError}, **kwargs
        )
        return Secret._from_secret_bundle(bundle)

    @distributed_trace_async
    async def set_secret(
        self,
        name: str,
        value: str,
        content_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: "**Any"
    ) -> Secret:
        """Set a secret value. Create a new secret if ``name`` is not in use. If it is, create a new version of the
        secret.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :param str content_type: (optional) An arbitrary string indicating the type of the secret, e.g. 'password'
        :param bool enabled: (optional) Whether the secret is enabled for use
        :param datetime.datetime not_before: (optional) Not before date of the secret in UTC
        :param datetime.datetime expires: (optional) Expiry date of the secret in UTC
        :param dict tags: (optional) Application specific metadata in the form of key-value pairs
        :rtype: ~azure.keyvault.secrets.models.Secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START set_secret]
                :end-before: [END set_secret]
                :language: python
                :caption: Set a secret's value
                :dedent: 8
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = await self._client.set_secret(
            self.vault_url, name, value, secret_attributes=attributes, content_type=content_type, tags=tags, **kwargs
        )
        return Secret._from_secret_bundle(bundle)

    @distributed_trace_async
    async def update_secret(
        self,
        name: str,
        version: Optional[str] = None,
        content_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: "**Any"
    ) -> SecretAttributes:
        """Update a secret's attributes, such as its tags or whether it's enabled. Requires the secrets/set permission.

        **This method can't change a secret's value.** Use :func:`set_secret` to change values.

        :param str name: Name of the secret
        :param str version: (optional) Version of the secret to update. If unspecified, the latest version is updated.
        :param str content_type: (optional) An arbitrary string indicating the type of the secret, e.g. 'password'
        :param bool enabled: (optional) Whether the secret is enabled for use
        :param datetime.datetime not_before: (optional) Not before date of the secret in UTC
        :param datetime.datetime expires: (optional) Expiry date  of the secret in UTC.
        :param dict(str, str) tags: (optional) Application specific metadata in the form of key-value pairs.
        :rtype: ~azure.keyvault.secrets.models.SecretAttributes
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the secret doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START update_secret]
                :end-before: [END update_secret]
                :language: python
                :caption: Updates a secret's attributes
                :dedent: 8
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = await self._client.update_secret(
            self.vault_url,
            name,
            secret_version=version or "",
            content_type=content_type,
            tags=tags,
            secret_attributes=attributes,
            error_map={404: ResourceNotFoundError},
            **kwargs
        )
        return SecretAttributes._from_secret_bundle(bundle)  # pylint: disable=protected-access

    @distributed_trace
    def list_secrets(self, **kwargs: "**Any") -> AsyncIterable[SecretAttributes]:
        """List the latest identifier and attributes of all secrets in the vault, not including their values. Requires
        the secrets/list permission.

        :returns: An iterator of secrets
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.models.SecretAttributes]

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
            self.vault_url,
            maxresults=max_results,
            cls=lambda objs: [SecretAttributes._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_secret_versions(self, name: str, **kwargs: "**Any") -> AsyncIterable[SecretAttributes]:
        """List all versions of a secret, including their identifiers and attributes but not their values. Requires the
        secrets/list permission.

        :param str name: Name of the secret
        :returns: An iterator of secrets
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.models.SecretAttributes]

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
            self.vault_url,
            name,
            maxresults=max_results,
            cls=lambda objs: [SecretAttributes._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace_async
    async def backup_secret(self, name: str, **kwargs: "**Any") -> bytes:
        """Get a backup of all versions of a secret. Requires the secrets/backup permission.

        :param str name: Name of the secret
        :returns: The raw bytes of the secret backup
        :rtype: bytes
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the secret doesn't exist

         Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START backup_secret]
                :end-before: [END backup_secret]
                :language: python
                :caption: Back up a secret
                :dedent: 8
        """
        backup_result = await self._client.backup_secret(
            self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs
        )
        return backup_result.value

    @distributed_trace_async
    async def restore_secret(self, backup: bytes, **kwargs: "**Any") -> SecretAttributes:
        """Restore a backed up secret. Requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
        :returns: The restored secret
        :rtype: ~azure.keyvault.secrets.models.SecretAttributes
        :raises: ~azure.core.exceptions.ResourceExistsError if the secret's name is already in use

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START restore_secret]
                :end-before: [END restore_secret]
                :language: python
                :caption: Restore a backed up secret
                :dedent: 8
        """
        bundle = await self._client.restore_secret(
            self.vault_url, backup, error_map={409: ResourceExistsError}, **kwargs
        )
        return SecretAttributes._from_secret_bundle(bundle)

    @distributed_trace_async
    async def delete_secret(self, name: str, **kwargs: "**Any") -> DeletedSecret:
        """Delete all versions of a secret. Requires the secrets/delete permission.

        :param str name: Name of the secret
        :rtype: ~azure.keyvault.secrets.models.DeletedSecret
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the secret doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START delete_secret]
                :end-before: [END delete_secret]
                :language: python
                :caption: Delete a secret
                :dedent: 8
        """
        bundle = await self._client.delete_secret(
            self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs
        )
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace_async
    async def get_deleted_secret(self, name: str, **kwargs: "**Any") -> DeletedSecret:
        """Get a deleted secret. This is only possible in vaults with soft-delete enabled. Requires the secrets/get
        permission.

        :param str name: Name of the secret
        :rtype: ~azure.keyvault.secrets.models.DeletedSecret
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the deleted secret doesn't exist

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START get_deleted_secret]
                :end-before: [END get_deleted_secret]
                :language: python
                :caption: Get a deleted secret
                :dedent: 8
        """
        bundle = await self._client.get_deleted_secret(
            self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs
        )
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def list_deleted_secrets(self, **kwargs: "**Any") -> AsyncIterable[DeletedSecret]:
        """Lists all deleted secrets. This is only possible in vaults with soft-delete enabled. Requires the
        secrets/list permission.

        :returns: An iterator of deleted secrets
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.keyvault.secrets.models.DeletedSecret]

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
            self.vault_url,
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

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes the secret
                # (with soft-delete disabled, delete_secret is permanent)
                await secret_client.purge_deleted_secret("secret-name")

        """
        await self._client.purge_deleted_secret(self.vault_url, name, **kwargs)

    @distributed_trace_async
    async def recover_deleted_secret(self, name: str, **kwargs: "**Any") -> SecretAttributes:
        """Recover a deleted secret to its latest version. This is only possible in vaults with soft-delete enabled.
        Requires the secrets/recover permission.

        :param str name: Name of the secret
        :returns: The recovered secret
        :rtype: ~azure.keyvault.secrets.models.SecretAttributes

        Example:
            .. literalinclude:: ../tests/test_samples_secrets_async.py
                :start-after: [START recover_deleted_secret]
                :end-before: [END recover_deleted_secret]
                :language: python
                :caption: Recover a deleted secret
                :dedent: 8
        """
        bundle = await self._client.recover_deleted_secret(self.vault_url, name, **kwargs)
        return SecretAttributes._from_secret_bundle(bundle)
