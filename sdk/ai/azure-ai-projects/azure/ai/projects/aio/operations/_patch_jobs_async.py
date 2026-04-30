# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async customized training/jobs operations — flat CommandJob UX, no envelope required."""

import logging
from datetime import datetime, timezone
from os import PathLike
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from azure.core.async_paging import AsyncItemPaged

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from azure.storage.blob.aio import ContainerClient

from ._operations import BetaTrainingJobsOperations as _GeneratedTrainingJobsOps
from ._patch_datasets_async import DatasetsOperations
from ...models._models import BlobReference
from ...models._models import Job as _RestJob
from ...models._models import Input as _Input
from ...models._models import Output as _Output
from ...models._patch_jobs import CommandJob
from ...models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _has_header_case_insensitive
from ...models._enums import FoundryFeaturesOptInKeys
from ...operations._job_helper import (
    _TERMINAL_JOB_STATUSES,
    _MAX_CONCURRENCY,
    _NAMED_OUTPUTS_DIR,
    _DEFAULT_OUTPUT_NOT_SUPPORTED_MSG,
    _blob_uri_to_prefix,
    _is_folder_marker,
    _ensure_dir,
    _validate_output_for_download,
)

_logger = logging.getLogger(__name__)


class TrainingJobsOperations(_GeneratedTrainingJobsOps):
    """Async patched Jobs operations that expose a flat :class:`~azure.ai.projects.models.CommandJob`
    interface — no ``Job`` envelope wrapping required by callers.

    Also automatically injects the ``Foundry-Features: Jobs=V1Preview`` preview opt-in header
    into every request so callers do not need to supply it manually.

    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, access it via ``client.beta.training.jobs``.
    """

    _JOBS_PREVIEW_HEADER: str = FoundryFeaturesOptInKeys.JOBS_V1_PREVIEW.value

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._datasets = DatasetsOperations(self._client, self._config, self._serialize, self._deserialize)

    def _validate(self, name: str, body: CommandJob) -> None:
        """Validate required fields before sending to the service.

        :param name: The job name.
        :type name: str
        :param body: The command job body.
        :type body: ~azure.ai.projects.models.CommandJob
        :raises ValueError: If any required field is missing or empty.
        """
        if not name or not name.strip():
            raise ValueError("'name' is required and cannot be empty.")
        if not body.command or not body.command.strip():
            raise ValueError("'command' is required and cannot be empty for a CommandJob.")
        if not body.environment_image_reference or not body.environment_image_reference.strip():
            raise ValueError("'environment_image_reference' is required and cannot be empty for a CommandJob.")
        if not body.compute or not body.compute.strip():
            raise ValueError("'compute' is required and cannot be empty for a CommandJob.")
        if isinstance(body.code, str) and not body.code.strip():
            raise ValueError(
                "'code' cannot be an empty string. Omit it or provide a valid local path or datastore URI."
            )

    async def _resolve_asset_uri(self, uri: str, dataset_name: str) -> str:
        """Resolve a single URI to a dataset asset URI (async).

        :param uri: The URI string to resolve.
        :type uri: str
        :param dataset_name: Dataset name to use when uploading a new local asset.
        :type dataset_name: str
        :return: A datastore URI.
        :rtype: str
        """
        local_path = Path(uri)
        if local_path.exists():
            version = "1"
            if local_path.is_dir():
                _logger.debug(
                    "[TrainingJobsOperations] Uploading folder '%s' as dataset '%s' v%s.", uri, dataset_name, version
                )
                result = await self._datasets.upload_folder(name=dataset_name, version=version, folder=uri)
            else:
                _logger.debug(
                    "[TrainingJobsOperations] Uploading file '%s' as dataset '%s' v%s.", uri, dataset_name, version
                )
                result = await self._datasets.upload_file(name=dataset_name, version=version, file_path=uri)
            if not result.data_uri:
                raise ValueError(f"Dataset upload succeeded but the service did not return a URI for '{uri}'.")
            _logger.debug("[TrainingJobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
            return result.data_uri

        if ":" in uri and "://" not in uri:
            raw = uri[len("azureai:") :] if uri.startswith("azureai:") else uri
            ds_name, ds_version = raw.split(":", 1)
            _logger.debug("[TrainingJobsOperations] Resolving name:version '%s' to dataset URI.", uri)
            result = await self._datasets.get(name=ds_name, version=ds_version)
            if not result.data_uri:
                raise ValueError(f"Dataset '{uri}' was fetched but the service did not return a URI.")
            _logger.debug("[TrainingJobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
            return result.data_uri

        return uri

    async def _resolve_code(self, name: str, body: CommandJob) -> None:
        """Resolve ``code`` on the job body to a datastore URI if it is a local path.

        :param name: The job name.
        :type name: str
        :param body: The command job body to mutate in-place.
        :type body: ~azure.ai.projects.models.CommandJob
        """
        if not isinstance(body.code, str):
            return
        dataset_name = f"{name}-code-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        body.code = await self._resolve_asset_uri(body.code, dataset_name)

    async def _resolve_input_paths(self, name: str, body: CommandJob) -> None:
        """Resolve local paths in ``inputs`` to datastore URIs.

        :param name: The job name.
        :type name: str
        :param body: The command job body to mutate in-place.
        :type body: ~azure.ai.projects.models.CommandJob
        """
        if not body.inputs:
            return
        for input_key, job_input in body.inputs.items():
            if not isinstance(job_input, _Input):
                continue
            if not isinstance(job_input.path, str):
                continue
            dataset_name = f"{name}-input-{input_key}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
            job_input.path = await self._resolve_asset_uri(job_input.path, dataset_name)

    async def _resolve_local_paths(self, name: str, body: CommandJob) -> None:
        """Resolve all local paths in the job body to datastore URIs.

        :param name: The job name.
        :type name: str
        :param body: The command job body to mutate in-place.
        :type body: ~azure.ai.projects.models.CommandJob
        """
        await self._resolve_code(name, body)
        await self._resolve_input_paths(name, body)

    def _inject_preview_header(self, kwargs: dict) -> None:
        """Add the Jobs preview feature header if not already present."""
        headers = kwargs.get("headers", {}) or {}
        if not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
            kwargs["headers"] = dict(headers)
            kwargs["headers"][_FOUNDRY_FEATURES_HEADER_NAME] = self._JOBS_PREVIEW_HEADER

    @distributed_trace
    def list(  # type: ignore[override]
        self,
        *,
        job_type: Optional[Union[str, Any]] = None,
        tag: Optional[str] = None,
        list_view_type: Optional[Union[str, Any]] = None,
        properties: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[CommandJob]:
        """List all training jobs as flat :class:`~azure.ai.projects.models.CommandJob`.

        :keyword job_type: Filter by job type. Default value is None.
        :paramtype job_type: str or ~azure.ai.projects.models.JobType
        :keyword tag: Filter by tag in the format ``'key=value'``. Default value is None.
        :paramtype tag: str
        :keyword list_view_type: Which view type to apply. Default value is None.
        :paramtype list_view_type: str or ~azure.ai.projects.models.ListViewType
        :keyword properties: Comma-separated user properties filter. Default value is None.
        :paramtype properties: str
        :return: An async iterator like instance of :class:`~azure.ai.projects.models.CommandJob`.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.projects.models.CommandJob]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)

        def _convert_page(page: List) -> List[CommandJob]:
            return [CommandJob._from_rest_object(item) for item in page]

        return super().list(
            job_type=job_type,
            tag=tag,
            list_view_type=list_view_type,
            properties=properties,
            cls=_convert_page,
            **kwargs,
        )  # type: ignore[return-value]

    @distributed_trace_async
    async def get(self, name: str, **kwargs: Any) -> CommandJob:  # type: ignore[override]
        """Async get a training job by name.

        :param name: The name of the job. Required.
        :type name: str
        :return: The job as a flat :class:`~azure.ai.projects.models.CommandJob`.
        :rtype: ~azure.ai.projects.models.CommandJob
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        rest_result = await super().get(name=name, **kwargs)
        return CommandJob._from_rest_object(rest_result)

    @distributed_trace_async
    async def create_or_update(self, name: str, job: CommandJob, **kwargs: Any) -> CommandJob:  # type: ignore[override]
        """Async create or update a training job.

        :param name: The name of the job. Required.
        :type name: str
        :param job: The command job to create or update. Required.
        :type job: ~azure.ai.projects.models.CommandJob
        :return: The created/updated job.
        :rtype: ~azure.ai.projects.models.CommandJob
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ValueError: If required fields are missing or empty.
        """
        self._validate(name, job)
        await self._resolve_local_paths(name, job)
        self._inject_preview_header(kwargs)
        rest_body = _RestJob(properties=job)
        rest_result = await super().create_or_update(name=name, job=rest_body, **kwargs)
        return CommandJob._from_rest_object(rest_result)

    @distributed_trace_async
    async def begin_delete(self, name: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Async delete a training job by name.

        :param name: The name of the job. Required.
        :type name: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        return await super().begin_delete(name=name, **kwargs)

    @distributed_trace_async
    async def begin_cancel(self, name: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Async cancel a training job by name.

        :param name: The name of the job. Required.
        :type name: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        return await super().begin_cancel(name=name, **kwargs)

    async def _resolve_output_to_blob_ref(self, output_name: str, output: _Output) -> BlobReference:
        """Resolve a job ``Output`` to a :class:`~azure.ai.projects.models.BlobReference`.

        :param output_name: The output name.
        :type output_name: str
        :param output: The job output object from the Get Job response.
        :type output: ~azure.ai.projects.models.Output
        :return: A blob reference describing the storage location and SAS credential.
        :rtype: ~azure.ai.projects.models.BlobReference
        :raises ValueError: If ``asset_name`` / ``asset_version`` are missing or
            the output type is not supported for download.
        :raises NotImplementedError: If the output type requires Models operations
            not yet generated in this SDK build.
        """
        _validate_output_for_download(output_name, output)
        assert output.asset_name is not None and output.asset_version is not None
        credential = await self._datasets.get_credentials(name=output.asset_name, version=output.asset_version)
        return credential.blob_reference

    async def _download_blob_reference(self, blob_ref: BlobReference, destination: Path) -> Tuple[int, int]:
        """Download every blob under ``blob_ref`` into ``destination``.

        :param blob_ref: The blob reference to download.
        :type blob_ref: ~azure.ai.projects.models.BlobReference
        :param destination: Local directory to write files to. Created if missing.
        :type destination: ~pathlib.Path
        :return: A tuple of ``(file_count, total_bytes_downloaded)``.
        :rtype: Tuple[int, int]
        :raises ValueError: If the SAS URI or blob URI is missing.
        """
        if not blob_ref or not blob_ref.credential or not blob_ref.credential.sas_uri:
            raise ValueError("Blob reference is missing a SAS URI credential.")
        if not blob_ref.blob_uri:
            raise ValueError("Blob reference is missing the blob URI.")

        prefix = _blob_uri_to_prefix(blob_ref.blob_uri)
        sas_uri = blob_ref.credential.sas_uri

        destination.mkdir(parents=True, exist_ok=True)

        async with ContainerClient.from_container_url(container_url=sas_uri) as container_client:
            list_prefix = (prefix + "/") if prefix else ""
            blobs = []
            async for b in container_client.list_blobs(name_starts_with=list_prefix or None, include=["metadata"]):
                blobs.append(b)
            all_names = {b.name for b in blobs}

            file_count = 0
            total_bytes = 0
            for blob in blobs:
                blob_name = blob.name
                if list_prefix and blob_name.startswith(list_prefix):
                    relative = blob_name[len(list_prefix) :]
                else:
                    relative = blob_name
                if not relative:
                    continue
                local_path = destination / relative
                if _is_folder_marker(blob, all_names):
                    _ensure_dir(local_path)
                    continue
                _ensure_dir(local_path.parent)
                _logger.debug("[TrainingJobsOperations] Downloading blob '%s' \u2192 '%s'.", blob_name, local_path)
                downloader = await container_client.download_blob(blob=blob_name, max_concurrency=_MAX_CONCURRENCY)
                with open(local_path, "wb") as fh:
                    await downloader.readinto(fh)
                file_count += 1
                total_bytes += blob.size or 0
            return file_count, total_bytes

    @distributed_trace_async
    async def download(
        self,
        name: str,
        *,
        download_path: Union[PathLike, str] = ".",
        output_name: Optional[str] = None,
        all: bool = False,  # pylint: disable=redefined-builtin
        **kwargs: Any,
    ) -> None:
        """Download outputs of a completed training job to a local directory.

        :param name: The name of the job. Required.
        :type name: str
        :keyword download_path: The local path to be used as the download destination.
            Defaults to ``"."`` (the current working directory). Created if it does not exist.
        :paramtype download_path: Union[PathLike, str]
        :keyword output_name: Name of a single named output to download.
            Mutually exclusive with ``all``.
        :paramtype output_name: str
        :keyword all: If True, download every named output, each into its own
            ``<download_path>/named-outputs/<output_name>/`` subfolder. Mutually
            exclusive with ``output_name``.
        :paramtype all: bool
        :raises ValueError: If both ``output_name`` and ``all`` are provided,
            if the job has no outputs, or if ``output_name`` does not exist.
        :raises NotImplementedError: If the user requests the default-output
            download (no ``output_name`` and ``all`` is False).
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if output_name is not None and all:
            raise ValueError("Specify either 'output_name' or 'all=True', not both.")

        self._inject_preview_header(kwargs)
        job = await self.get(name=name, **kwargs)

        job_status = (job.status or "").lower()
        if job_status not in _TERMINAL_JOB_STATUSES:
            raise ValueError(
                f"Job '{name}' is in state '{job.status}'. Download is allowed only when the job is in "
                f"a terminal state: {sorted(_TERMINAL_JOB_STATUSES)}."
            )

        outputs: dict = job.outputs or {}
        if not outputs:
            raise ValueError(f"Job '{name}' has no outputs to download.")

        dest_root = Path(download_path)

        if output_name is not None:
            if output_name not in outputs:
                raise ValueError(
                    f"Job '{name}' has no output named '{output_name}'. "
                    f"Available outputs: {sorted(outputs.keys())}."
                )
            blob_ref = await self._resolve_output_to_blob_ref(output_name, outputs[output_name])
            destination = dest_root / _NAMED_OUTPUTS_DIR / output_name
            _logger.info(
                "[TrainingJobsOperations] Downloading output '%s' from '%s' to '%s'.",
                output_name,
                blob_ref.blob_uri,
                destination,
            )
            file_count, total_bytes = await self._download_blob_reference(blob_ref, destination)
            _logger.info(
                "[TrainingJobsOperations] Downloaded %d file(s) (%.2f MB) for output '%s'.",
                file_count,
                total_bytes / (1024 * 1024),
                output_name,
            )
            return

        if all:
            for out_name, out in outputs.items():
                try:
                    blob_ref = await self._resolve_output_to_blob_ref(out_name, out)
                except ValueError as exc:
                    _logger.warning(
                        "[TrainingJobsOperations] Skipping output '%s' for job '%s': %s",
                        out_name,
                        name,
                        exc,
                    )
                    continue
                destination = dest_root / _NAMED_OUTPUTS_DIR / out_name
                _logger.info(
                    "[TrainingJobsOperations] Downloading output '%s' from '%s' to '%s'.",
                    out_name,
                    blob_ref.blob_uri,
                    destination,
                )
                file_count, total_bytes = await self._download_blob_reference(blob_ref, destination)
                _logger.info(
                    "[TrainingJobsOperations] Downloaded %d file(s) (%.2f MB) for output '%s'.",
                    file_count,
                    total_bytes / (1024 * 1024),
                    out_name,
                )
            return

        raise NotImplementedError(_DEFAULT_OUTPUT_NOT_SUPPORTED_MSG)
