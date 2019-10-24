# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from functools import partial
from azure.core.tracing.decorator import distributed_trace

from ._models import KeyVaultSecret, DeletedSecret, SecretProperties
from ._shared import KeyVaultClientBase
from ._shared.exceptions import error_map as _error_map
from ._shared._polling import DeletePollingMethod, RecoverDeletedPollingMethod, KeyVaultOperationPoller

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

    :param str vault_url: URL of the vault the client will access
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`

    Keyword arguments
        - **api_version**: version of the Key Vault API to use. Defaults to the most recent.
        - **transport**: :class:`~azure.core.pipeline.transport.HttpTransport` to use. Defaults to
          :class:`~azure.core.pipeline.transport.RequestsTransport`.

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
        # type: (str, str, **Any) -> KeyVaultSecret
        """Get a secret. Requires the secrets/get permission.

        :param str name: The name of the secret
        :param str version: (optional) Version of the secret to get. If unspecified, gets the latest version.
        :rtype: ~azure.keyvault.secrets.KeyVaultSecret
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
            vault_base_url=self._vault_url,
            secret_name=name,
            secret_version=version or "",
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace
    def set_secret(self, name, value, **kwargs):
        # type: (str, str, **Any) -> KeyVaultSecret
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
            .. literalinclude:: ../tests/test_samples_secrets.py
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
        bundle = self._client.set_secret(
            vault_base_url=self.vault_url, secret_name=name, value=value, secret_attributes=attributes, **kwargs
        )
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace
    def update_secret_properties(self, name, version=None, **kwargs):
        # type: (str, Optional[str], **Any) -> SecretProperties
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
            - **content_type** (str): A descriptive string indicating the type of the secret, e.g. 'password'
            - **not_before** (:class:`~datetime.datetime`): Not before date of the secret in UTC
            - **expires_on** (:class:`~datetime.datetime`): Expiry date of the secret in UTC

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START update_secret]
                :end-before: [END update_secret]
                :language: python
                :caption: Update a secret's attributes
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
        bundle = self._client.update_secret(
            self.vault_url,
            name,
            secret_version=version or "",
            secret_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return SecretProperties._from_secret_bundle(bundle)  # pylint: disable=protected-access

    @distributed_trace
    def list_properties_of_secrets(self, **kwargs):
        # type: (**Any) -> ItemPaged[SecretProperties]
        """List the latest identifier and attributes of all secrets in the vault, not including their values. Requires
        the secrets/list permission.

        :returns: An iterator of secrets
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_secrets]
                :end-before: [END list_secrets]
                :language: python
                :caption: List all secrets
                :dedent: 8

        """
        return self._client.get_secrets(
            self._vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_properties_of_secret_versions(self, name, **kwargs):
        # type: (str, **Any) -> ItemPaged[SecretProperties]
        """List all versions of a secret, including their identifiers and attributes but not their values. Requires the
        secrets/list permission.

        :param str name: Name of the secret
        :returns: An iterator of secrets
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_properties_of_secret_versions]
                :end-before: [END list_properties_of_secret_versions]
                :language: python
                :caption: List all versions of a secret
                :dedent: 8

        """
        return self._client.get_secret_versions(
            self._vault_url,
            name,
            maxresults=kwargs.pop("max_page_size", None),
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
        backup_result = self._client.backup_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        return backup_result.value

    @distributed_trace
    def restore_secret_backup(self, backup, **kwargs):
        # type: (bytes, **Any) -> SecretProperties
        """Restore a backed up secret. Requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
        :returns: The restored secret
        :rtype: ~azure.keyvault.secrets.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceExistsError` if the secret's name is already in use,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START restore_secret_backup]
                :end-before: [END restore_secret_backup]
                :language: python
                :caption: Restore a backed up secret
                :dedent: 8

        """
        bundle = self._client.restore_secret(self.vault_url, backup, error_map=_error_map, **kwargs)
        return SecretProperties._from_secret_bundle(bundle)

    @distributed_trace
    def begin_delete_secret(self, name, **kwargs):
        # type: (str, **Any) -> DeletedSecret
        """Delete all versions of a secret.

        Requires the secrets/delete permission. The poller requires the secrets/get permission to function properly.

        :returns: A poller for the delete secret operation. Calling `result` returns the
         :class:`~azure.keyvault.secrets.DeletedSecret` without waiting for the operation to complete.
         If you are planning to immediately purge the deleted secret, call `wait` on the poller,
         which blocks until deletion is complete.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.secrets.DeletedSecret]
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
        polling_interval = kwargs.pop("_polling_interval", 2)
        deleted_secret = DeletedSecret._from_deleted_secret_bundle(
            self._client.delete_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        )
        sd_disabled = deleted_secret.recovery_id is None
        command = partial(self.get_deleted_secret, name=name, **kwargs)
        delete_secret_polling_method = DeletePollingMethod(
            command=command,
            final_resource=deleted_secret,
            initial_status="deleting",
            finished_status="deleted",
            sd_disabled=sd_disabled,
            interval=polling_interval
        )
        return KeyVaultOperationPoller(delete_secret_polling_method)

    @distributed_trace
    def get_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> DeletedSecret
        """Get a deleted secret. This is only possible in vaults with soft-delete enabled. Requires the secrets/get
        permission.

        :param str name: Name of the secret
        :rtype: ~azure.keyvault.secrets.DeletedSecret
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
        bundle = self._client.get_deleted_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def list_deleted_secrets(self, **kwargs):
        # type: (**Any) -> ItemPaged[DeletedSecret]
        """Lists all deleted secrets. This is only possible in vaults with soft-delete enabled. Requires the
        secrets/list permission.

        :returns: An iterator of deleted secrets
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.DeletedSecret]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_deleted_secrets]
                :end-before: [END list_deleted_secrets]
                :language: python
                :caption: List deleted secrets
                :dedent: 8

        """
        return self._client.get_deleted_secrets(
            self._vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [DeletedSecret._from_deleted_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def purge_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Permanently delete a secret. This is only possible in vaults with soft-delete enabled. If a vault
        doesn't have soft-delete enabled, :func:`begin_delete_secret` is permanent, and this method will return
        an error.

        Requires the secrets/purge permission.

        :param str name: Name of the secret
        :returns: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes the secret
                # (with soft-delete disabled, begin_delete_secret is permanent)
                secret_client.purge_deleted_secret("secret-name")

        """
        self._client.purge_deleted_secret(self.vault_url, name, **kwargs)

    @distributed_trace
    def begin_recover_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> SecretProperties
        """Recover a deleted secret to its latest version. This is only possible in vaults with soft-delete enabled. If
        a vault does not have soft-delete enabled, :func:`begin_delete_secret` is permanent, and this method will return
        an error. Attempting to recover an non-deleted secret will also return an error.

        Requires the secrets/recover permission. The poller requires the secrets/get permission to function properly.

        :param str name: Name of the secret
        :returns: A poller for the recover secret operation. Calling `result` on the poller returns the recovered
         :class:`~azure.keyvault.secrets.SecretProperties`. If you are planning to immediately use the recovered
         secret, call `wait` on the poller, which blocks until the secret is ready to use.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.secrets.SecretProperties]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START recover_deleted_secret]
                :end-before: [END recover_deleted_secret]
                :language: python
                :caption: Recover a deleted secret
                :dedent: 8

        """
        polling_interval = kwargs.pop("_polling_interval", 2)
        recovered_secret = SecretProperties._from_secret_bundle(
            self._client.recover_deleted_secret(self.vault_url, name, **kwargs)
        )
        command = partial(self.get_secret, name=name, **kwargs)
        recover_secret_polling_method = RecoverDeletedPollingMethod(
            command=command,
            final_resource=recovered_secret,
            initial_status="recovering",
            finished_status="recovered",
            interval=polling_interval
        )
        return KeyVaultOperationPoller(recover_secret_polling_method)
