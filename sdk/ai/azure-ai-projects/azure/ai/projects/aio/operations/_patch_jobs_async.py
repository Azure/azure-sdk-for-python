# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async customized jobs operations — flat CommandJob UX, no envelope required."""

import asyncio
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from urllib.parse import urlparse

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import ResourceNotFoundError
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling.base_polling import BadStatus
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.storage.blob.aio import ContainerClient as AsyncContainerClient

from ._operations import BetaJobsOperations as _GeneratedJobsOps
from ._patch_datasets_async import DatasetsOperations
from ...operations._job_helper import (
    _TERMINAL_JOB_STATUSES,
    _IN_PROGRESS_JOB_STATUSES,
    _FINALIZING_JOB_STATUS,
    _FAILED_JOB_STATUS,
    _FINALIZING_RUN_MARKER,
    _MAX_CONCURRENCY,
    _NAMED_OUTPUTS_DIR,
    _ARTIFACTS_DIR,
    _DEFAULT_ARTIFACT_STORE_OUTPUT_NAME,
    _blob_uri_to_prefix,
    _is_folder_marker,
    _ensure_dir,
    _validate_output_for_download,
    _validate_command_job,
    _content_hash,
    _get_sorted_streamable_logs,
    _incremental_print,
    _wait_before_polling,
    _download_log_text,
    _safe_join,
    _sweep_tmp_files,
    _group_paths_by_prefix,
    _download_artifact_to_path,
)
from ...models._models import BlobReference
from ...models._models import Job as _RestJob
from ...models._models import Input as _Input
from ...models._models import Output as _Output
from ...models._patch_jobs import CommandJob, ServiceInstance, ValidationResult
from ...models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _has_header_case_insensitive
from ...models._enums import _FoundryFeaturesOptInKeys

_logger = logging.getLogger(__name__)


class JobsOperations(_GeneratedJobsOps):
    """Async patched Jobs operations that expose a flat :class:`~azure.ai.projects.models.CommandJob`
    interface — no ``Job`` envelope wrapping required by callers.

    Also automatically injects the ``Foundry-Features: Jobs=V1Preview`` preview opt-in header
    into every request so callers do not need to supply it manually.

    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, access it via ``client.beta.jobs``.
    """

    _JOBS_PREVIEW_HEADER: str = _FoundryFeaturesOptInKeys.JOBS_V1_PREVIEW.value

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._datasets = DatasetsOperations(self._client, self._config, self._serialize, self._deserialize)

    @distributed_trace_async
    async def validate(
        self,
        job: CommandJob,
        *,
        raise_on_failure: bool = False,
    ) -> ValidationResult:
        """Validates a CommandJob object before submitting to the service. Only command jobs are
        supported for validation currently.

        :param job: The job object to be validated.
        :type job: ~azure.ai.projects.models.CommandJob
        :keyword raise_on_failure: Specifies if an error should be raised if validation fails.
            Defaults to False.
        :paramtype raise_on_failure: bool
        :return: A ValidationResult object containing all found errors.
        :rtype: ~azure.ai.projects.models.ValidationResult
        """
        return _validate_command_job(job).try_raise(raise_on_failure=raise_on_failure)

    async def _resolve_asset_uri(
        self,
        uri: str,
        dataset_name: str,
        base_path: Optional[Union[str, PathLike[str]]] = None,
    ) -> str:
        """Resolve a single URI to a dataset asset URI.

        :param uri: The URI string to resolve.
        :type uri: str
        :param dataset_name: Dataset name to use when uploading a new local asset.
        :type dataset_name: str
        :param base_path: Base directory for resolving relative paths (e.g. the YAML file's parent
            directory). When supplied and ``uri`` is a relative path that does not exist relative to
            the current working directory, it is re-evaluated against this directory.
        :type base_path: str or os.PathLike or None
        :return: A datastore URI suitable for use in an :class:`~azure.ai.projects.models.Input`.
        :rtype: str
        """
        local_path = Path(uri)
        if not local_path.is_absolute() and base_path and not local_path.exists():
            resolved = (Path(base_path) / local_path).resolve()
            if resolved.exists():
                local_path = resolved
        if local_path.exists():
            version = _content_hash(local_path)

            try:
                existing = await self._datasets.get(name=dataset_name, version=version)
                if existing and existing.id:
                    _logger.debug("[JobsOperations] Reusing existing dataset '%s' v%s.", dataset_name, version)
                    return existing.id
            except ResourceNotFoundError:
                pass

            if local_path.is_dir():
                _logger.debug(
                    "[JobsOperations] Uploading folder '%s' as dataset '%s' v%s.",
                    local_path,
                    dataset_name,
                    version,
                )
                result = await self._datasets.upload_folder(name=dataset_name, version=version, folder=str(local_path))
            else:
                _logger.debug(
                    "[JobsOperations] Uploading file '%s' as dataset '%s' v%s.",
                    local_path,
                    dataset_name,
                    version,
                )
                result = await self._datasets.upload_file(name=dataset_name, version=version, file_path=str(local_path))
            if not result.id:
                raise ValueError(f"Dataset upload succeeded but the service did not return a URI for '{local_path}'.")
            _logger.debug("[JobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
            return result.id

        parsed = urlparse(uri)
        if parsed.scheme and not parsed.netloc:
            raw = uri[len("azureai:") :] if uri.startswith("azureai:") else uri
            ds_name, ds_version = raw.split(":", 1)
            _logger.debug("[JobsOperations] Resolving name:version '%s' to dataset URI.", uri)
            result = await self._datasets.get(name=ds_name, version=ds_version)
            if not result.id:
                raise ValueError(f"Dataset '{uri}' was fetched but the service did not return a URI.")
            _logger.debug("[JobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
            return result.id

        # Already a datastore / remote URI — pass through unchanged.
        return uri

    async def _resolve_code(self, name: str, job: CommandJob) -> None:
        """Resolve ``code`` on the job body to a datastore URI if it is a local path.

        :param name: The job name (used to derive a unique dataset name).
        :type name: str
        :param job: The command job body to mutate in-place.
        :type job: ~azure.ai.projects.models.CommandJob
        """
        if not isinstance(job.code, str):
            return
        dataset_name = f"{name}-code"
        job.code = await self._resolve_asset_uri(job.code, dataset_name, base_path=job._base_path)

    async def _resolve_input_paths(self, name: str, job: CommandJob) -> None:
        """Resolve local paths in ``inputs`` to datastore URIs.

        :param name: The job name (used to derive unique dataset names).
        :type name: str
        :param job: The command job body to mutate in-place.
        :type job: ~azure.ai.projects.models.CommandJob
        """
        if not job.inputs:
            return
        base_path = job._base_path
        for input_key, job_input in job.inputs.items():
            if not isinstance(job_input, _Input):
                continue
            if not isinstance(job_input.path, str):
                continue
            dataset_name = f"{name}-{input_key}"
            job_input.path = await self._resolve_asset_uri(job_input.path, dataset_name, base_path=base_path)

    async def _resolve_local_paths(self, name: str, job: CommandJob) -> None:
        """Resolve all local paths in the job body to datastore URIs.

        :param name: The job name.
        :type name: str
        :param job: The command job job to mutate in-place.
        :type job: ~azure.ai.projects.models.CommandJob
        """
        await self._resolve_code(name, job)
        await self._resolve_input_paths(name, job)

    def _inject_preview_header(self, kwargs: dict) -> None:
        """Add the Jobs preview feature header if not already present."""
        headers = kwargs.get("headers", {}) or {}
        if not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
            kwargs["headers"] = dict(headers)
            kwargs["headers"][_FOUNDRY_FEATURES_HEADER_NAME] = self._JOBS_PREVIEW_HEADER

    @staticmethod
    def _handle_not_found_as_deleted(polling_method: AsyncLROBasePolling) -> None:
        """Patch ``polling_method.update_status`` so that a 404 response on the polling
        URL is treated as success.

        :param polling_method: The ``AsyncLROBasePolling`` instance to patch.
        :type polling_method: ~azure.core.polling.async_base_polling.AsyncLROBasePolling
        """
        _base_update = polling_method.update_status

        async def _update_status(_base=_base_update, _pm=polling_method):
            try:
                await _base()
            except BadStatus:
                if _pm._pipeline_response and _pm._pipeline_response.http_response.status_code == 404:
                    _pm._status = "Succeeded"
                else:
                    raise

        polling_method.update_status = _update_status  # type: ignore[method-assign]

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
        """List all training jobs as flat :class:`~azure.ai.projects.models.CommandJob`
        objects with ``name`` and ``id`` promoted from the Job resource envelope.

        :keyword job_type: Filter by job type (e.g. ``'Command'``). Default value is None.
        :paramtype job_type: str or ~azure.ai.projects.models.JobType
        :keyword tag: Filter by tag in the format ``'key=value'``. Default value is None.
        :paramtype tag: str
        :keyword list_view_type: Which view type to apply. Default value is None.
        :paramtype list_view_type: str or ~azure.ai.projects.models.ListViewType
        :keyword properties: Comma-separated user properties filter. Default value is None.
        :paramtype properties: str
        :return: An iterator like instance of :class:`~azure.ai.projects.models.CommandJob`.
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
        """Get a training job by name.

        :param name: The name of the job. Required.
        :type name: str
        :return: The job as a flat :class:`~azure.ai.projects.models.CommandJob` with
            ``name`` and ``id`` promoted from the Job resource envelope.
        :rtype: ~azure.ai.projects.models.CommandJob
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        rest_result = await super().get(name=name, **kwargs)
        return CommandJob._from_rest_object(rest_result)

    @distributed_trace_async
    async def create_or_update(self, name: str, job: CommandJob, **kwargs: Any) -> CommandJob:  # type: ignore[override]
        """Create or update a training job.

        :param name: The name of the job. Required.
        :type name: str
        :param job: The command job to create or update. Required.
        :type job: ~azure.ai.projects.models.CommandJob
        :keyword skip_validation: If ``True``, skip the local validation step.
            Defaults to ``False``.
        :paramtype skip_validation: bool
        :return: The created/updated job.
        :rtype: ~azure.ai.projects.models.CommandJob
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ValueError: If required fields are missing or empty.
        """
        skip_validation = kwargs.pop("skip_validation", False)
        if not skip_validation:
            _validate_command_job(job).try_raise(raise_on_failure=True)
        await self._resolve_local_paths(name, job)
        self._inject_preview_header(kwargs)
        rest_body = _RestJob(properties=job)
        rest_result = await super().create_or_update(name=name, job=rest_body, **kwargs)
        return CommandJob._from_rest_object(rest_result)

    @distributed_trace_async
    async def begin_delete(self, name: str, **kwargs: Any) -> AsyncLROPoller[None]:  # type: ignore[override]
        """Delete a training job by name.

        Returns 202 Accepted with a Location header to poll for completion,
        or 204 if the job does not exist.

        :param name: The name of the job. Required.
        :type name: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        raw_result = await super().begin_delete(  # type: ignore[func-returns-value]
            name=name,
            cls=lambda x, y, z: x,
            **kwargs,
        )
        kwargs.pop("error_map", None)
        lro_headers = kwargs.pop("headers", {})
        lro_headers[_FOUNDRY_FEATURES_HEADER_NAME] = self._JOBS_PREVIEW_HEADER

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    headers=lro_headers,
                    **kwargs,
                ),
            )
            self._handle_not_found_as_deleted(polling_method)  # type: ignore[arg-type]
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        return AsyncLROPoller[None](self._client, raw_result, lambda _: None, polling_method)

    @distributed_trace_async
    async def begin_cancel(self, name: str, **kwargs: Any) -> AsyncLROPoller[None]:  # type: ignore[override]
        """Cancel a training job by name.

        Returns 200 if cancelled immediately, or 202 Accepted with a Location header
        to poll for completion.

        :param name: The name of the job. Required.
        :type name: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        raw_result = await super().begin_cancel(  # type: ignore[func-returns-value]
            name=name,
            cls=lambda x, y, z: x,
            **kwargs,
        )
        kwargs.pop("error_map", None)
        lro_headers = kwargs.pop("headers", {})
        lro_headers[_FOUNDRY_FEATURES_HEADER_NAME] = self._JOBS_PREVIEW_HEADER

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    headers=lro_headers,
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        return AsyncLROPoller[None](self._client, raw_result, lambda _: None, polling_method)

    @distributed_trace_async
    async def show_services(  # type: ignore[override]
        self, name: str, node_index: int = 0, **kwargs: Any
    ) -> Optional[Dict[str, ServiceInstance]]:
        """Get the runtime service instances associated with a job's compute node.

        Returns the interactive services (e.g. SSH, JupyterLab, VSCode, TensorBoard)
        currently running on the specified node. The ``<nodeIndex>`` placeholder
        in each service ``endpoint`` is substituted with the requested ``node_index``.

        :param name: The name of the job. Required.
        :type name: str
        :param node_index: Zero-based index of the compute node. Defaults to 0.
        :type node_index: int
        :return: A dict of service name to
            :class:`~azure.ai.projects.models.ServiceInstance`, or ``None`` if no
            services are running on the node.
        :rtype: Optional[dict[str, ~azure.ai.projects.models.ServiceInstance]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        result = await super().show_services(name=name, run_id=name, node_id=node_index, **kwargs)
        if not result or not result.instances:
            return None
        return {k: ServiceInstance._from_rest_object(v, node_index) for k, v in result.instances.items()}

    @distributed_trace_async
    async def stream(self, name: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Stream the logs of a running CommandJob to ``sys.stdout`` until the job reaches
        a terminal state.

        Polls the run details endpoint and incrementally prints any new content from the
        job's streamable log files. Raises an exception if the job ends in a failed state.

        :param name: The name of the job. Required.
        :type name: str
        :raises TypeError: If the job is not a CommandJob.
        :raises RuntimeError: If the job ends in a failed state.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        job = await self.get(name=name, **kwargs)
        studio_endpoint: Optional[str] = None
        if job.services:
            studio = job.services.get("Studio")
            if studio is not None:
                studio_endpoint = studio.endpoint

        fileout = sys.stdout
        fileout.write("RunId: {}\n".format(name))
        if studio_endpoint:
            fileout.write("Web View: {}\n".format(studio_endpoint))

        processed_logs: Dict[str, int] = {}
        poll_start_time = time.time()
        details = await super()._get_run_details(name=name, run_id=name, **kwargs)
        last_content = ""

        while True:
            status = (details.status or "").lower()
            in_progress = status in _IN_PROGRESS_JOB_STATUSES
            finalizing = status == _FINALIZING_JOB_STATUS
            if not in_progress and not finalizing:
                break

            fileout.flush()
            log_files: Dict[str, str] = details.log_files or {}
            available_logs = _get_sorted_streamable_logs(log_files.keys(), processed_logs)
            last_content = ""
            for current_log in available_logs:
                last_content = _download_log_text(log_files[current_log])
                _incremental_print(last_content, processed_logs, current_log, fileout)

            if finalizing and _FINALIZING_RUN_MARKER in last_content:
                break

            await asyncio.sleep(_wait_before_polling(time.time() - poll_start_time))
            details = await super()._get_run_details(name=name, run_id=name, **kwargs)

        # Final flush: capture any log lines written between the last poll and the
        # job reaching a terminal state (e.g. on cancel or quick completion).
        final_log_files: Dict[str, str] = details.log_files or {}
        for current_log in _get_sorted_streamable_logs(final_log_files.keys(), processed_logs):
            final_content = _download_log_text(final_log_files[current_log])
            _incremental_print(final_content, processed_logs, current_log, fileout)

        fileout.write("\n")
        fileout.write("Execution Summary\n")
        fileout.write("=================\n")
        fileout.write("RunId: {}\n".format(name))
        if studio_endpoint:
            fileout.write("Web View: {}\n".format(studio_endpoint))

        warnings = details.warnings
        if warnings:
            messages: List[str] = [w.message for w in warnings if w.message]
            if messages:
                fileout.write("\nWarnings:\n")
                for message in messages:
                    fileout.write(message + "\n")
                fileout.write("\n")

        if (details.status or "").lower() == _FAILED_JOB_STATUS:
            error_payload: Any = (
                details.error.as_dict()
                if details.error is not None
                else "Detailed error not set on the run. Please check the logs for details."
            )
            error_text = json.dumps(error_payload, indent=4) if isinstance(error_payload, dict) else error_payload
            raise RuntimeError("Exception : \n {} ".format(error_text))

    async def _resolve_output_to_blob_ref(self, output_name: str, output: _Output) -> BlobReference:
        """Resolve a job ``Output`` to a :class:`~azure.ai.projects.models.BlobReference`.

        :param output_name: The output name.
        :type output_name: str
        :param output: The job output object from the Get Job response.
        :type output: ~azure.ai.projects.models.Output
        :return: A blob reference describing the storage location and SAS credential.
        :rtype: ~azure.ai.projects.models.BlobReference
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

        async with AsyncContainerClient.from_container_url(container_url=sas_uri) as container_client:
            list_prefix = (prefix + "/") if prefix else ""
            blobs = []
            async for blob in container_client.list_blobs(name_starts_with=list_prefix or None, include=["metadata"]):
                blobs.append(blob)
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
                _logger.debug("[JobsOperations] Downloading blob '%s' → '%s'.", blob_name, local_path)
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
        """Download the logs and outputs of a job.

        :param name: The name of the job. Required.
        :type name: str
        :keyword download_path: The local path to be used as the download destination.
            Defaults to ``"."``.
        :paramtype download_path: Union[PathLike, str]
        :keyword output_name: The name of the output to download. Defaults to None.
        :paramtype output_name: Optional[str]
        :keyword all: Specifies if all logs and named outputs should be downloaded.
            Defaults to False.
        :paramtype all: bool
        :raises ValueError: If both ``output_name`` and ``all`` are provided, if
            ``output_name`` does not exist on the job, or if the job is not in a
            terminal state.
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

        dest_root = Path(download_path)
        outputs: dict = job.outputs or {}

        if output_name == _DEFAULT_ARTIFACT_STORE_OUTPUT_NAME:
            output_name = None

        if output_name is not None:
            if not outputs or output_name not in outputs:
                raise ValueError(
                    f"Job '{name}' has no output named '{output_name}'. "
                    f"Available outputs: {sorted(outputs.keys())}."
                )
            await self._download_named_output(name, output_name, outputs[output_name], dest_root)
            return

        if all:
            for out_name, out in outputs.items():
                if out_name == _DEFAULT_ARTIFACT_STORE_OUTPUT_NAME:
                    continue
                try:
                    await self._download_named_output(name, out_name, out, dest_root)
                except ValueError as exc:
                    _logger.warning(
                        "[JobsOperations] Skipping output '%s' for job '%s': %s",
                        out_name,
                        name,
                        exc,
                    )
            await self._download_default_artifacts(name, dest_root, **kwargs)
            return

        await self._download_default_artifacts(name, dest_root, **kwargs)

    async def _download_named_output(
        self,
        job_name: str,
        output_name: str,
        output: _Output,
        dest_root: Path,
    ) -> None:
        """Resolve and download a single named output into ``<dest_root>/named-outputs/<output_name>/``.

        :param job_name: The name of the job that owns the output.
        :type job_name: str
        :param output_name: The output name to download.
        :type output_name: str
        :param output: The job output object from the Get Job response.
        :type output: ~azure.ai.projects.models.Output
        :param dest_root: The base local directory; the output is written into
            ``<dest_root>/named-outputs/<output_name>/``.
        :type dest_root: ~pathlib.Path
        :raises ValueError: If the output cannot be resolved to a blob reference, or
            if the resolved blob reference is missing the SAS URI / blob URI.
        :raises NotImplementedError: If the output type requires Models operations
            not yet generated in this SDK build.
        """
        blob_ref = await self._resolve_output_to_blob_ref(output_name, output)
        destination = dest_root / _NAMED_OUTPUTS_DIR / output_name
        _logger.info(
            "[JobsOperations] Downloading output '%s' for job '%s' to '%s'.",
            output_name,
            job_name,
            destination,
        )
        file_count, total_bytes = await self._download_blob_reference(blob_ref, destination)
        _logger.info(
            "[JobsOperations] Downloaded %d file(s) (%.2f MB) for output '%s'.",
            file_count,
            total_bytes / (1024 * 1024),
            output_name,
        )

    async def _download_default_artifacts(
        self,
        name: str,
        dest_root: Path,
        **kwargs: Any,
    ) -> None:
        """Download the run's default artifacts to ``<dest_root>/artifacts/``.

        :param name: Job name (also used as the run id).
        :type name: str
        :param dest_root: Destination root directory; files are written under ``<dest_root>/artifacts/``.
        :type dest_root: ~pathlib.Path
        :raises ValueError: If the run has no ``experimentId``.
        """
        run = await super()._get_run(name=name, run_id=name, **kwargs)
        experiment_id = run.experiment_id
        if not experiment_id:
            raise ValueError(f"Job '{name}' run is missing 'experimentId'; cannot list artifacts.")

        # Async pagination: collect artifact paths
        paths: List[str] = []
        continuation: Optional[str] = None
        while True:
            page = await super()._list_artifacts(
                name,
                experiment_id,
                name,
                continuation_token_parameter=continuation,
            )
            for artifact in page.value or []:
                if artifact.path:
                    paths.append(artifact.path)
            continuation = page.continuation_token
            if not continuation:
                break

        if not paths:
            _logger.info("[JobsOperations] Job '%s' has no default artifacts to download.", name)
            return

        prefixes = _group_paths_by_prefix(paths)

        # Async pagination: resolve artifact URIs
        uri_map: Dict[str, Tuple[str, int]] = {}
        for prefix in prefixes:
            if not prefix:
                continue
            continuation = None
            while True:
                page = await super()._get_artifact_content_information(
                    name,
                    experiment_id,
                    name,
                    path=prefix,
                    continuation_token_parameter=continuation,
                )
                for item in page.value or []:
                    if item.path and item.content_uri:
                        uri_map[item.path] = (item.content_uri, item.content_length or 0)
                continuation = page.continuation_token
                if not continuation:
                    break

        artifacts_root = dest_root / _ARTIFACTS_DIR
        artifacts_root.mkdir(parents=True, exist_ok=True)
        _sweep_tmp_files(artifacts_root)

        # Dedup by destination path before launching workers.
        work: Dict[Path, str] = {}
        for path in paths:
            entry = uri_map.get(path)
            if entry is None:
                _logger.warning(
                    "[JobsOperations] Artifact '%s' was listed but no contentUri was returned; skipping.",
                    path,
                )
                continue
            content_uri, _ = entry
            try:
                local_path = _safe_join(artifacts_root, path)
            except ValueError as exc:
                _logger.warning("[JobsOperations] Skipping unsafe artifact path '%s': %s", path, exc)
                continue
            work.setdefault(local_path, content_uri)

        if not work:
            return

        _logger.info(
            "[JobsOperations] Downloading %d default artifact file(s) for job '%s' to '%s'.",
            len(work),
            name,
            artifacts_root,
        )

        workers = max(1, min(_MAX_CONCURRENCY, len(work)))
        total_bytes = 0
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(_download_artifact_to_path, uri, local_path, _MAX_CONCURRENCY): local_path
                for local_path, uri in work.items()
            }
            for future in as_completed(futures):
                local_path = futures[future]
                try:
                    total_bytes += future.result()
                except Exception:
                    _logger.error("[JobsOperations] Failed to download artifact to '%s'.", local_path)
                    raise

        _logger.info(
            "[JobsOperations] Downloaded %d default artifact file(s) (%.2f MB) for job '%s'.",
            len(work),
            total_bytes / (1024 * 1024),
            name,
        )
