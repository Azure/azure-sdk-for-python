# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.polling.async_base_polling import AsyncLROBasePolling

from .._internal import AsyncKeyVaultClientBase
from .._internal.polling import KeyVaultBackupClientPolling
from .._models import BackupOperation, RestoreOperation, SelectiveKeyRestoreOperation

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any
    from azure.core.polling import AsyncLROPoller


class KeyVaultBackupClient(AsyncKeyVaultClientBase):
    """Performs Key Vault backup and restore operations.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
    :param credential: an object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    """

    # pylint:disable=protected-access
    async def begin_full_backup(
        self, blob_storage_uri: str, sas_token: str, **kwargs: "Any"
    ) -> "AsyncLROPoller[BackupOperation]":
        """Begin a full backup of the Key Vault.

        :param str blob_storage_uri: URI of the blob storage resource in which the backup will be stored
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :keyword str continuation_token: a continuation token to restart polling from a saved state
        :returns: An AsyncLROPoller. Call `result()` on this object to get a :class:`BackupOperation`.
        :rtype: ~azure.core.polling.AsyncLROPoller[BackupOperation]
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=blob_storage_uri, token=sas_token)
        return await self._client.begin_full_backup(
            vault_base_url=self._vault_url,
            azure_storage_blob_container_uri=sas_parameter,
            cls=BackupOperation._wrap_generated,
            continuation_token=kwargs.pop("continuation_token", None),
            polling=AsyncLROBasePolling(
                lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs
            ),
            **kwargs
        )

    async def begin_full_restore(
        self, blob_storage_uri: str, sas_token: str, folder_name: str, **kwargs: "Any"
    ) -> "AsyncLROPoller[RestoreOperation]":
        """Restore a full backup of a Key Vault.

        :param str blob_storage_uri: URI of the blob storage resource in which the backup is stored
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :param str folder_name: name of the blob container which contains the backup
        :rtype: ~azure.core.polling.AsyncLROPoller[RestoreOperation]
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=blob_storage_uri, token=sas_token)
        restore_details = self._models.RestoreOperationParameters(
            sas_token_parameters=sas_parameter, folder_to_restore=folder_name,
        )
        return await self._client.begin_full_restore_operation(
            vault_base_url=self._vault_url,
            restore_blob_details=restore_details,
            cls=RestoreOperation._wrap_generated,
            continuation_token=kwargs.pop("continuation_token", None),
            polling=AsyncLROBasePolling(
                lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs
            ),
            **kwargs
        )

    async def begin_selective_restore(
        self, blob_storage_uri: str, sas_token: str, folder_name: str, key_name: str, **kwargs: "Any"
    ) -> "AsyncLROPoller[SelectiveKeyRestoreOperation]":
        """Restore a single key from a full Key Vault backup.

        :param str blob_storage_uri: URI of the blob storage resource in which the backup is stored
        :param str sas_token: a Shared Access Signature (SAS) token authorizing access to the blob storage resource
        :param str folder_name: name of the blob container which contains the backup
        :param str key_name: name of the key to restore from the backup
        :rtype: ~azure.core.polling.AsyncLROPoller[RestoreOperation]
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        sas_parameter = self._models.SASTokenParameter(storage_resource_uri=blob_storage_uri, token=sas_token)
        restore_details = self._models.SelectiveKeyRestoreOperationParameters(
            sas_token_parameters=sas_parameter, folder=folder_name,
        )
        return await self._client.begin_selective_key_restore_operation(
            vault_base_url=self._vault_url,
            key_name=key_name,
            restore_blob_details=restore_details,
            cls=SelectiveKeyRestoreOperation._wrap_generated,
            continuation_token=kwargs.pop("continuation_token", None),
            polling=AsyncLROBasePolling(
                lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs
            ),
            **kwargs
        )

    async def get_backup_status(
        self, job_id: str, **kwargs: "Any"
    ) -> "BackupOperation":
        """Returns the status of a full backup operation.

        :param str job_id: The job ID returned as part of the backup request
        :returns: The full backup operation status as a :class:`BackupOperation`
        :rtype: BackupOperation
        """
        return await self._client.full_backup_status(
            vault_base_url=self._vault_url,
            job_id=job_id,
            cls=BackupOperation._wrap_generated,
            **kwargs
        )

    async def get_restore_status(
        self, job_id: str, **kwargs: "Any"
    ) -> "RestoreOperation":
        """Returns the status of a restore operation.

        :param str job_id: The ID returned as part of the restore request
        :returns: The restore operation status as a :class:`RestoreOperation`
        :rtype: RestoreOperation
        """
        return await self._client.restore_status(
            vault_base_url=self._vault_url,
            job_id=job_id,
            cls=RestoreOperation._wrap_generated,
            **kwargs
        )
