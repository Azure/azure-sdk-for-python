# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import functools
import pickle
from typing import Any, Callable, Optional, overload

from typing_extensions import Literal

from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.models import PreBackupOperationParameters, PreRestoreOperationParameters, SASTokenParameter
from .._backup_client import _parse_status_url
from .._internal import AsyncKeyVaultClientBase, parse_folder_url
from .._internal.async_polling import KeyVaultAsyncBackupClientPollingMethod
from .._internal.polling import KeyVaultBackupClientPolling
from .._models import KeyVaultBackupOperation, KeyVaultBackupResult, KeyVaultRestoreOperation


class KeyVaultBackupClient(AsyncKeyVaultClientBase):
    """Performs Key Vault backup and restore operations.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
        You should validate that this URL references a valid Key Vault or Managed HSM resource.
        See https://aka.ms/azsdk/blog/vault-uri for details.
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential

    :keyword api_version: Version of the service API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.administration.ApiVersion or str
    :keyword bool verify_challenge_resource: Whether to verify the authentication challenge resource matches the Key
        Vault or Managed HSM domain. Defaults to True.
    """

    async def _use_continuation_token(self, continuation_token: str, status_method: Callable) -> str:
        status_url = base64.b64decode(continuation_token.encode()).decode("ascii")
        try:
            job_id = _parse_status_url(status_url)
        except Exception as ex:  # pylint: disable=broad-except
            raise ValueError(
                "The provided continuation_token is malformed. A valid token can be obtained from the operation "
                + "poller's continuation_token() method"
            ) from ex

        pipeline_response = await status_method(
            job_id=job_id, cls=lambda pipeline_response, _, __: pipeline_response
        )
        if "azure-asyncoperation" not in pipeline_response.http_response.headers:
            pipeline_response.http_response.headers["azure-asyncoperation"] = status_url
        return base64.b64encode(pickle.dumps(pipeline_response)).decode("ascii")

    @overload
    async def begin_backup(
        self,
        blob_storage_url: str,
        *,
        use_managed_identity: Literal[True],
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[KeyVaultBackupResult]:
        ...

    @overload
    async def begin_backup(
        self,
        blob_storage_url: str,
        *,
        sas_token: str,
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[KeyVaultBackupResult]:
        ...

    # Disabling pylint checks because they don't correctly handle overloads
    @distributed_trace_async
    async def begin_backup(  # pylint: disable=docstring-missing-param,docstring-keyword-should-match-keyword-only
        self, blob_storage_url: str, *args: str, **kwargs: Any
    ) -> AsyncLROPoller[KeyVaultBackupResult]:
        """Begin a full backup of the Key Vault.

        :param str blob_storage_url: URL of the blob storage container in which the backup will be stored, for example
            https://<account>.blob.core.windows.net/backup.

        :keyword str sas_token: Optional Shared Access Signature (SAS) token to authorize access to the blob. Required
            unless `use_managed_identity` is set to True.
        :keyword use_managed_identity: Indicates which authentication method should be used. If set to True, Managed HSM
            will use the configured user-assigned managed identity to authenticate with Azure Storage. Otherwise, a SAS
            token has to be specified.
        :paramtype use_managed_identity: bool
        :keyword str continuation_token: A continuation token to restart polling from a saved state.

        :returns: An AsyncLROPoller. Call `result()` on this object to get a :class:`KeyVaultBackupResult`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.keyvault.administration.KeyVaultBackupResult]

        Example:
            .. literalinclude:: ../tests/test_examples_administration_async.py
                :start-after: [START begin_backup]
                :end-before: [END begin_backup]
                :language: python
                :caption: Create a vault backup
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        continuation_token = kwargs.pop("continuation_token", None)
        use_managed_identity = kwargs.pop("use_managed_identity", False)
        # `sas_token` was formerly a required positional parameter
        try:
            sas_token: Optional[str] = args[0]
        except IndexError:
            sas_token = kwargs.pop("sas_token", None)
        sas_parameter = self._models.SASTokenParameter(
            storage_resource_uri=blob_storage_url, token=sas_token, use_managed_identity=use_managed_identity
        )

        status_response = None
        if continuation_token:
            status_response = await self._use_continuation_token(continuation_token, self._client.full_backup_status)

        return await self._client.begin_full_backup(
            azure_storage_blob_container_uri=sas_parameter,
            cls=KeyVaultBackupResult._from_generated,  # pylint: disable=protected-access
            continuation_token=status_response,
            polling=KeyVaultAsyncBackupClientPollingMethod(
                lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs
            ),
            **kwargs,
        )

    @overload
    async def begin_restore(
        self,
        folder_url: str,
        *,
        use_managed_identity: Literal[True],
        key_name: Optional[str] = None,
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[None]:
        ...

    @overload
    async def begin_restore(
        self,
        folder_url: str,
        *,
        sas_token: str,
        key_name: Optional[str] = None,
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[None]:
        ...

    # Disabling pylint checks because they don't correctly handle overloads
    @distributed_trace_async
    async def begin_restore(  # pylint: disable=docstring-missing-param,docstring-keyword-should-match-keyword-only
        self, folder_url: str, *args: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Restore a Key Vault backup.

        This method restores either a complete Key Vault backup or when ``key_name`` has a value, a single key.

        :param str folder_url: URL for the blob storage resource, including the path to the blob holding the
            backup. This would be the `folder_url` of a :class:`KeyVaultBackupResult` returned by
            :func:`begin_backup`, for example
            https://<account>.blob.core.windows.net/backup/mhsm-account-2020090117323313

        :keyword str sas_token: Optional Shared Access Signature (SAS) token to authorize access to the blob. Required
            unless `use_managed_identity` is set to True.
        :keyword use_managed_identity: Indicates which authentication method should be used. If set to True, Managed HSM
            will use the configured user-assigned managed identity to authenticate with Azure Storage. Otherwise, a SAS
            token has to be specified.
        :paramtype use_managed_identity: bool
        :keyword str key_name: Name of a single key in the backup. When set, only this key will be restored.
        :keyword str continuation_token: A continuation token to restart polling from a saved state.

        :returns: An AsyncLROPoller. Call `wait()` or `result()` on this object to wait for the operation to complete
            (the return value is None in either case).
        :rtype: ~azure.core.polling.AsyncLROPoller

        Examples:
            .. literalinclude:: ../tests/test_examples_administration_async.py
                :start-after: [START begin_restore]
                :end-before: [END begin_restore]
                :language: python
                :caption: Restore a vault backup
                :dedent: 8

            .. literalinclude:: ../tests/test_examples_administration_async.py
                :start-after: [START begin_selective_restore]
                :end-before: [END begin_selective_restore]
                :language: python
                :caption: Restore a single key
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", 5)
        continuation_token = kwargs.pop("continuation_token", None)
        key_name = kwargs.pop("key_name", None)
        use_managed_identity = kwargs.pop("use_managed_identity", False)
        # `sas_token` was formerly a required positional parameter
        try:
            sas_token: Optional[str] = args[0]
        except IndexError:
            sas_token = kwargs.pop("sas_token", None)

        status_response = None
        if continuation_token:
            status_response = await self._use_continuation_token(continuation_token, self._client.restore_status)

        container_url, folder_name = parse_folder_url(folder_url)
        sas_parameter = self._models.SASTokenParameter(
            storage_resource_uri=container_url, token=sas_token, use_managed_identity=use_managed_identity
        )
        polling = KeyVaultAsyncBackupClientPollingMethod(
            lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs
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

        return await client_method(
            restore_blob_details=restore_details,
            cls=lambda *_: None,  # poller.result() returns None
            continuation_token=status_response,
            polling=polling,
            **kwargs,
        )

    @overload
    async def begin_pre_backup(
        self,
        blob_storage_url: str,
        *,
        use_managed_identity: Literal[True],
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[KeyVaultBackupOperation]:
        ...

    @overload
    async def begin_pre_backup(
        self,
        blob_storage_url: str,
        *,
        sas_token: str,
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[KeyVaultBackupOperation]:
        ...

    @distributed_trace_async
    async def begin_pre_backup(  # pylint: disable=docstring-keyword-should-match-keyword-only
        self, blob_storage_url: str, **kwargs: Any
    ) -> AsyncLROPoller[KeyVaultBackupOperation]:
        """Initiates a pre-backup check of whether a full Key Vault backup can be performed.

        A :class:`KeyVaultBackupOperation` instance will be returned by the poller's `result()` method. If the
        pre-backup check is successful, the object will have a string `folder_url` attribute, pointing to the blob
        storage container where the backup will be stored. If the check fails, the object will have a string `error`
        attribute.

        :param str blob_storage_url: URL of the blob storage container in which the backup will be stored, for example
            https://<account>.blob.core.windows.net/backup.

        :keyword str sas_token: Optional Shared Access Signature (SAS) token to authorize access to the blob. Required
            unless `use_managed_identity` is set to True.
        :keyword use_managed_identity: Indicates which authentication method should be used. If set to True, Managed HSM
            will use the configured user-assigned managed identity to authenticate with Azure Storage. Otherwise, a SAS
            token has to be specified.
        :paramtype use_managed_identity: bool
        :keyword str continuation_token: A continuation token to restart polling from a saved state.

        :returns: An AsyncLROPoller. Call `result()` on this object to wait for the operation to complete and get a
            :class:`KeyVaultBackupOperation`. If the pre-backup check is successful, the object will have a string
            `folder_url` attribute, pointing to the blob storage container where the backup will be stored. If the check
            fails, the object will have a string `error` attribute.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.keyvault.administration.KeyVaultBackupOperation]
        """
        polling_interval: int = kwargs.pop("_polling_interval", 5)
        continuation_token: Optional[str] = kwargs.pop("continuation_token", None)
        use_managed_identity: bool = kwargs.pop("use_managed_identity", False)
        sas_token: Optional[str] = kwargs.pop("sas_token", None)

        parameters: PreBackupOperationParameters = PreBackupOperationParameters(
            storage_resource_uri=blob_storage_url, token=sas_token, use_managed_identity=use_managed_identity
        )
        status_response: Optional[str] = None
        if continuation_token:
            status_response = await self._use_continuation_token(continuation_token, self._client.full_backup_status)

        return await self._client.begin_pre_full_backup(
            pre_backup_operation_parameters=parameters,
            cls=KeyVaultBackupOperation._from_generated,  # pylint: disable=protected-access
            polling=KeyVaultAsyncBackupClientPollingMethod(
                lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs
            ),
            continuation_token=status_response,
            **kwargs,
        )

    @overload
    async def begin_pre_restore(
        self,
        folder_url: str,
        *,
        use_managed_identity: Literal[True],
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[KeyVaultRestoreOperation]:
        ...

    @overload
    async def begin_pre_restore(
        self,
        folder_url: str,
        *,
        sas_token: str,
        continuation_token: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[KeyVaultRestoreOperation]:
        ...

    @distributed_trace_async
    async def begin_pre_restore(  # pylint: disable=docstring-keyword-should-match-keyword-only
        self, folder_url: str, **kwargs: Any
    ) -> AsyncLROPoller[KeyVaultRestoreOperation]:
        """Initiates a pre-restore check of whether a full Key Vault restore can be performed.

        A :class:`KeyVaultRestoreOperation` instance will be returned by the poller's `result()` method. If the
        pre-restore check fails, the object will have a string `error` attribute.

        :param str folder_url: URL of the blob holding the backup. This would be the `folder_url` of a
            :class:`KeyVaultBackupResult` returned by :func:`begin_backup`, for example
            https://<account>.blob.core.windows.net/backup/mhsm-account-2020090117323313

        :keyword str sas_token: Optional Shared Access Signature (SAS) token to authorize access to the blob. Required
            unless `use_managed_identity` is set to True.
        :keyword use_managed_identity: Indicates which authentication method should be used. If set to True, Managed HSM
            will use the configured user-assigned managed identity to authenticate with Azure Storage. Otherwise, a SAS
            token has to be specified.
        :paramtype use_managed_identity: bool
        :keyword str continuation_token: A continuation token to restart polling from a saved state.

        :returns: An AsyncLROPoller. Call `result()` on this object to wait for the operation to complete and get a
            :class:`KeyVaultRestoreOperation`. If the pre-restore check fails, the object will have a string `error`
            attribute.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.keyvault.administration.KeyVaultRestoreOperation]
        """
        polling_interval: int = kwargs.pop("_polling_interval", 5)
        continuation_token: Optional[str] = kwargs.pop("continuation_token", None)
        use_managed_identity: bool = kwargs.pop("use_managed_identity", False)
        sas_token: Optional[str] = kwargs.pop("sas_token", None)

        container_url, folder_name = parse_folder_url(folder_url)
        sas_parameter: SASTokenParameter = SASTokenParameter(
            storage_resource_uri=container_url, token=sas_token, use_managed_identity=use_managed_identity
        )
        parameters: PreRestoreOperationParameters = PreRestoreOperationParameters(
            folder_to_restore=folder_name, sas_token_parameters=sas_parameter
        )
        status_response: Optional[str] = None
        if continuation_token:
            status_response = await self._use_continuation_token(continuation_token, self._client.restore_status)

        return await self._client.begin_pre_full_restore_operation(
            pre_restore_operation_parameters=parameters,
            cls=KeyVaultRestoreOperation._from_generated,  # pylint: disable=protected-access
            polling=KeyVaultAsyncBackupClientPollingMethod(
                lro_algorithms=[KeyVaultBackupClientPolling()], timeout=polling_interval, **kwargs
            ),
            continuation_token=status_response,
            **kwargs,
        )

    async def __aenter__(self) -> "KeyVaultBackupClient":
        await self._client.__aenter__()
        return self
