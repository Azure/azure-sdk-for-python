# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.polling.base_polling import LROBasePolling

from ._models import BackupOperation, RestoreOperation, SelectiveKeyRestoreOperation
from ._internal import KeyVaultClientBase
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
    def begin_full_backup(self, blob_storage_uri, sas_token, **kwargs):
        # type: (str, str, **Any) -> LROPoller[BackupOperation]
        """Begin a full backup of the Key Vault.

        :param str blob_storage_uri: URI of the blob storage resource in which the backup will be stored
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :keyword str continuation_token: a continuation token to restart polling from a saved state
        :returns: An instance of an LROPoller. Call `result()` on the poller object to get a :class:`BackupOperation`.
        :rtype: ~azure.core.polling.LROPoller[BackupOperation]
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=blob_storage_uri, token=sas_token)
        return self._client.begin_full_backup(
            vault_base_url=self._vault_url,
            azure_storage_blob_container_uri=sas_parameter,
            cls=BackupOperation._wrap_generated,
            continuation_token=kwargs.pop("continuation_token", None),
            polling=LROBasePolling(lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs),
            **kwargs
        )

    def begin_full_restore(self, blob_storage_uri, sas_token, folder_name, **kwargs):
        # type: (str, str, str, **Any) -> LROPoller[RestoreOperation]
        """Restore a full backup of a Key Vault.

        :param str blob_storage_uri: URI of the blob storage resource in which the backup is stored
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :param str folder_name: name of the blob container which contains the backup
        :rtype: ~azure.core.polling.LROPoller[RestoreOperation]
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=blob_storage_uri, token=sas_token)
        restore_details = self._models.RestoreOperationParameters(
            sas_token_parameters=sas_parameter, folder_to_restore=folder_name,
        )
        return self._client.begin_full_restore_operation(
            vault_base_url=self._vault_url,
            restore_blob_details=restore_details,
            cls=RestoreOperation._wrap_generated,
            continuation_token=kwargs.pop("continuation_token", None),
            polling=LROBasePolling(lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs),
            **kwargs
        )

    def begin_selective_restore(self, blob_storage_uri, sas_token, folder_name, key_name, **kwargs):
        # type: (str, str, str, str, **Any) -> LROPoller[SelectiveKeyRestoreOperation]
        """Restore a single key from a full Key Vault backup.

        :param str blob_storage_uri: URI of the blob storage resource in which the backup is stored
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :param str folder_name: name of the blob container which contains the backup
        :param str key_name: name of the key to restore from the backup
        :rtype: ~azure.core.polling.LROPoller[RestoreOperation]
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=blob_storage_uri, token=sas_token)
        restore_details = self._models.SelectiveKeyRestoreOperationParameters(
            sas_token_parameters=sas_parameter, folder=folder_name,
        )
        return self._client.begin_selective_key_restore_operation(
            vault_base_url=self._vault_url,
            key_name=key_name,
            restore_blob_details=restore_details,
            cls=SelectiveKeyRestoreOperation._wrap_generated,
            continuation_token=kwargs.pop("continuation_token", None),
            polling=LROBasePolling(lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs),
            **kwargs
        )

    def get_backup_status(self, job_id, **kwargs):
        # type: (str, **Any) -> BackupOperation
        """Returns the status of a full backup operation.

        :param job_id: The job ID returned as part of the backup request
        :type job_id: str
        :return: The full backup operation status as a :class:`BackupOperation`
        :rtype: BackupOperation
        """
        return self._client.full_backup_status(
            vault_base_url=self._vault_url,
            job_id=job_id,
            cls=BackupOperation._wrap_generated,
            **kwargs
        )

    def get_restore_status(self, job_id, **kwargs):
        # type: (str, **Any) -> RestoreOperation
        """Returns the status of a restore operation.

        :param job_id: The job ID returned as part of the restore request
        :type job_id: str
        :return: The restore operation status as a :class:`RestoreOperation`
        :rtype: RestoreOperation
        """
        return self._client.restore_status(
            vault_base_url=self.vault_url,
            job_id=job_id,
            cls=RestoreOperation._wrap_generated,
            **kwargs
        )
