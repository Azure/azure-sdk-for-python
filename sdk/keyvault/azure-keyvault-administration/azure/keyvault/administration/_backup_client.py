# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from typing import TYPE_CHECKING

from azure.core.polling.base_polling import LROBasePolling

from ._models import KeyVaultBackupOperation
from ._internal import KeyVaultClientBase, parse_folder_url
from ._internal.polling import KeyVaultBackupClientPolling

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any
    from azure.core.polling import LROPoller


class KeyVaultBackupClient(KeyVaultClientBase):
    """Performs Key Vault backup and restore operations.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
    :param credential: an object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    """

    # pylint:disable=protected-access
    def begin_backup(self, blob_storage_url, sas_token, **kwargs):
        # type: (str, str, **Any) -> LROPoller[KeyVaultBackupOperation]
        """Begin a full backup of the Key Vault.

        :param str blob_storage_url: URL of the blob storage container in which the backup will be stored, for example
            https://<account>.blob.core.windows.net/backup
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :keyword str continuation_token: a continuation token to restart polling from a saved state
        :returns: An :class:`~azure.core.polling.LROPoller` instance. Call `result()` on this object to wait for the
            operation to complete and get a :class:`KeyVaultBackupOperation`.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.administration.KeyVaultBackupOperation]
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=blob_storage_url, token=sas_token)
        return self._client.begin_full_backup(
            vault_base_url=self._vault_url,
            azure_storage_blob_container_uri=sas_parameter,
            cls=KeyVaultBackupOperation._from_generated,
            continuation_token=kwargs.pop("continuation_token", None),
            polling=LROBasePolling(lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs),
            **kwargs
        )

    def begin_restore(self, folder_url, sas_token, **kwargs):
        # type: (str, str, **Any) -> LROPoller
        """Restore a Key Vault backup.

        This method restores either a complete Key Vault backup or when ``key_name`` has a value, a single key.

        :param str folder_url: URL of the blob holding the backup. This would be the `folder_url` of a
            :class:`KeyVaultBackupOperation` returned by :func:`begin_backup` or :func:`get_backup_status`, for example
            https://<account>.blob.core.windows.net/backup/mhsm-account-2020090117323313
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :keyword str continuation_token: a continuation token to restart polling from a saved state
        :keyword str key_name: name of a single key in the backup. When set, only this key will be restored.
        :rtype: ~azure.core.polling.LROPoller
        """
        # LROBasePolling passes its kwargs to pipeline.run(), so we remove unexpected args before constructing it
        continuation_token = kwargs.pop("continuation_token", None)
        key_name = kwargs.pop("key_name", None)

        container_url, folder_name = parse_folder_url(folder_url)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=container_url, token=sas_token)
        polling = LROBasePolling(
            lro_algorithms=[KeyVaultBackupClientPolling()], timeout=kwargs.pop("_polling_interval", 5), **kwargs
        )

        if key_name:
            client_method = functools.partial(self._client.begin_selective_key_restore_operation, key_name=key_name)
            restore_details = self._models.SelectiveKeyRestoreOperationParameters(
                sas_token_parameters=sas_parameter, folder=folder_name
            )
        else:
            client_method = self._client.begin_full_restore_operation
            restore_details = self._models.RestoreOperationParameters(
                sas_token_parameters=sas_parameter, folder_to_restore=folder_name
            )

        return client_method(
            vault_base_url=self._vault_url,
            restore_blob_details=restore_details,
            cls=lambda *_: None,  # poller.result() returns None
            continuation_token=continuation_token,
            polling=polling,
            **kwargs
        )

    def get_backup_status(self, job_id, **kwargs):
        # type: (str, **Any) -> KeyVaultBackupOperation
        """Returns the status of a full backup operation.

        :param job_id: The job ID returned as part of the backup request
        :type job_id: str
        :return: The full backup operation status as a :class:`KeyVaultBackupOperation`
        :rtype: ~azure.keyvault.administration.KeyVaultBackupOperation
        """
        return self._client.full_backup_status(
            vault_base_url=self._vault_url, job_id=job_id, cls=KeyVaultBackupOperation._wrap_generated, **kwargs
        )

    def get_restore_status(self, job_id, **kwargs):
        # type: (str, **Any) -> KeyVaultRestoreOperation
        """Returns the status of a restore operation.

        :param job_id: The job ID returned as part of the restore request
        :type job_id: str
        :return: The restore operation status as a :class:`KeyVaultRestoreOperation`
        :rtype: ~azure.keyvault.administration.KeyVaultRestoreOperation
        """
        return self._client.restore_status(
            vault_base_url=self.vault_url, job_id=job_id, cls=KeyVaultRestoreOperation._wrap_generated, **kwargs
        )
