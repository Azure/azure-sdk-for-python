# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.tracing.decorator import distributed_trace

from ._shared import KeyVaultClientBase
from ._shared.exceptions import error_map as _error_map
from .models import Secret, DeletedSecret, SecretProperties

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Optional
    from datetime import datetime
    from azure.core.paging import ItemPaged


class SecretClient(KeyVaultClientBase):
    """A high-level interface for managing a vault's secrets.

    :param str vault_endpoint: URL of the vault the client will access
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`

    Example:
        .. literalinclude:: ../tests/test_samples_secrets.py
            :start-after: [START create_secret_client]
            :end-before: [END create_secret_client]
            :language: python
            :caption: Create a new ``SecretClient``
            :dedent: 4
    """

    # pylint:disable=protected-access

    @distributed_trace
    def get_secret(self, name, version=None, **kwargs):
        # type: (str, str, **Any) -> Secret
        """Get a secret. Requires the secrets/get permission.

        :param str name: The name of the secret
        :param str version: (optional) Version of the secret to get. If unspecified, gets the latest version.
        :rtype: ~azure.keyvault.secrets.models.Secret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START get_secret]
                :end-before: [END get_secret]
                :language: python
                :caption: Get a secret
                :dedent: 8
        """
        bundle = self._client.get_secret(
            vault_base_url=self._vault_endpoint,
            secret_name=name,
            secret_version=version or "",
            error_map=_error_map,
            **kwargs
        )
        return Secret._from_secret_bundle(bundle)

    @distributed_trace
    def set_secret(
        self,
        name,  # type: str
        value,  # type: str
        content_type=None,  # type: Optional[str]
        not_before=None,  # type: Optional[datetime]
        expires=None,  # type: Optional[datetime]
        **kwargs  # type:  **Any
    ):
        # type: (...) -> Secret
        """Set a secret value. Create a new secret if ``name`` is not in use. If it is, create a new version of the
        secret.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :param str content_type: (optional) An arbitrary string indicating the type of the secret, e.g. 'password'
        :param datetime.datetime not_before: (optional) Not before date of the secret in UTC
        :param datetime.datetime expires: (optional) Expiry date of the secret in UTC
        :rtype: ~azure.keyvault.secrets.models.Secret
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Whether the secret is enabled for use.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START set_secret]
                :end-before: [END set_secret]
                :language: python
                :caption: Set a secret's value
                :dedent: 8

        """
        enabled = kwargs.pop('enabled', None)
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.set_secret(
            vault_base_url=self.vault_endpoint,
            secret_name=name,
            value=value,
            secret_attributes=attributes,
            content_type=content_type,
            **kwargs
        )
        return Secret._from_secret_bundle(bundle)

    @distributed_trace
    def update_secret_properties(
        self,
        name,  # type: str
        version=None,  # type: Optional[str]
        content_type=None,  # type: Optional[str]
        not_before=None,  # type: Optional[datetime]
        expires=None,  # type: Optional[datetime]
        **kwargs  # type: **Any
    ):
        # type: (...) -> SecretProperties
        """Update a secret's attributes, such as its tags or whether it's enabled. Requires the secrets/set permission.

        **This method can't change a secret's value.** Use :func:`set_secret` to change values.

        :param str name: Name of the secret
        :param str version: (optional) Version of the secret to update. If unspecified, the latest version is updated.
        :param str content_type: (optional) An arbitrary string indicating the type of the secret, e.g. 'password'
        :param datetime.datetime not_before: (optional) Not before date of the secret in UTC
        :param datetime.datetime expires: (optional) Expiry date  of the secret in UTC.
        :rtype: ~azure.keyvault.secrets.models.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Keyword arguments
            - *enabled (bool)* - Whether the secret is enabled for use.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START update_secret]
                :end-before: [END update_secret]
                :language: python
                :caption: Update a secret's attributes
                :dedent: 8

        """
        enabled = kwargs.pop('enabled', None)
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.update_secret(
            self.vault_endpoint,
            name,
            secret_version=version or "",
            content_type=content_type,
            secret_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return SecretProperties._from_secret_bundle(bundle)  # pylint: disable=protected-access

    @distributed_trace
    def list_secrets(self, **kwargs):
        # type: (**Any) -> ItemPaged[SecretProperties]
        """List the latest identifier and attributes of all secrets in the vault, not including their values. Requires
        the secrets/list permission.

        :returns: An iterator of secrets
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.models.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_secrets]
                :end-before: [END list_secrets]
                :language: python
                :caption: List all secrets
                :dedent: 8

        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_secrets(
            self._vault_endpoint,
            maxresults=max_page_size,
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_secret_versions(self, name, **kwargs):
        # type: (str, **Any) -> ItemPaged[SecretProperties]
        """List all versions of a secret, including their identifiers and attributes but not their values. Requires the
        secrets/list permission.

        :param str name: Name of the secret
        :returns: An iterator of secrets
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.models.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_secret_versions]
                :end-before: [END list_secret_versions]
                :language: python
                :caption: List all versions of a secret
                :dedent: 8

        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_secret_versions(
            self._vault_endpoint,
            name,
            maxresults=max_page_size,
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def backup_secret(self, name, **kwargs):
        # type: (str, **Any) -> bytes
        """Get a backup of all versions of a secret. Requires the secrets/backup permission.

        :param str name: Name of the secret
        :returns: The raw bytes of the secret backup
        :rtype: bytes
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START backup_secret]
                :end-before: [END backup_secret]
                :language: python
                :caption: Back up a secret
                :dedent: 8

        """
        backup_result = self._client.backup_secret(
            self.vault_endpoint, name, error_map=_error_map, **kwargs
        )
        return backup_result.value

    @distributed_trace
    def restore_secret(self, backup, **kwargs):
        # type: (bytes, **Any) -> SecretProperties
        """Restore a backed up secret. Requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
        :returns: The restored secret
        :rtype: ~azure.keyvault.secrets.models.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceExistsError` if the secret's name is already in use,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START restore_secret]
                :end-before: [END restore_secret]
                :language: python
                :caption: Restore a backed up secret
                :dedent: 8

        """
        bundle = self._client.restore_secret(
            self.vault_endpoint, backup, error_map=_error_map, **kwargs
        )
        return SecretProperties._from_secret_bundle(bundle)

    @distributed_trace
    def delete_secret(self, name, **kwargs):
        # type: (str, **Any) -> DeletedSecret
        """Delete all versions of a secret. Requires the secrets/delete permission.

        :param str name: Name of the secret
        :rtype: ~azure.keyvault.secrets.models.DeletedSecret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START delete_secret]
                :end-before: [END delete_secret]
                :language: python
                :caption: Delete a secret
                :dedent: 8

        """
        bundle = self._client.delete_secret(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def get_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> DeletedSecret
        """Get a deleted secret. This is only possible in vaults with soft-delete enabled. Requires the secrets/get
        permission.

        :param str name: Name of the secret
        :rtype: ~azure.keyvault.secrets.models.DeletedSecret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the deleted secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START get_deleted_secret]
                :end-before: [END get_deleted_secret]
                :language: python
                :caption: Get a deleted secret
                :dedent: 8

        """
        bundle = self._client.get_deleted_secret(self.vault_endpoint, name, error_map=_error_map, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def list_deleted_secrets(self, **kwargs):
        # type: (**Any) -> ItemPaged[DeletedSecret]
        """Lists all deleted secrets. This is only possible in vaults with soft-delete enabled. Requires the
        secrets/list permission.

        :returns: An iterator of deleted secrets
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.models.DeletedSecret]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_deleted_secrets]
                :end-before: [END list_deleted_secrets]
                :language: python
                :caption: List deleted secrets
                :dedent: 8

        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_deleted_secrets(
            self._vault_endpoint,
            maxresults=max_page_size,
            cls=lambda objs: [DeletedSecret._from_deleted_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def purge_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> None
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
                secret_client.purge_deleted_secret("secret-name")

        """
        self._client.purge_deleted_secret(self.vault_endpoint, name, **kwargs)

    @distributed_trace
    def recover_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> SecretProperties
        """Recover a deleted secret to its latest version. This is only possible in vaults with soft-delete enabled.
        Requires the secrets/recover permission.

        :param str name: Name of the secret
        :returns: The recovered secret
        :rtype: ~azure.keyvault.secrets.models.SecretProperties
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START recover_deleted_secret]
                :end-before: [END recover_deleted_secret]
                :language: python
                :caption: Recover a deleted secret
                :dedent: 8

        """
        bundle = self._client.recover_deleted_secret(self.vault_endpoint, name, **kwargs)
        return SecretProperties._from_secret_bundle(bundle)
