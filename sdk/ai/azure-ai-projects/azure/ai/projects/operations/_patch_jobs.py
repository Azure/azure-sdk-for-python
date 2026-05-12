# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customized jobs operations — flat CommandJob UX, no envelope required."""

import hashlib
import logging
import os
from fnmatch import fnmatch
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from azure.core.exceptions import ResourceNotFoundError

from azure.core.paging import ItemPaged

from azure.core.tracing.decorator import distributed_trace

from azure.storage.blob import ContainerClient

from ._operations import BetaJobsOperations as _GeneratedJobsOps
from ._patch_datasets import DatasetsOperations
from ._job_helper import (
    _TERMINAL_JOB_STATUSES,
    _MAX_CONCURRENCY,
    _NAMED_OUTPUTS_DIR,
    _DEFAULT_OUTPUT_NOT_SUPPORTED_MSG,
    _blob_uri_to_prefix,
    _is_folder_marker,
    _ensure_dir,
    _validate_output_for_download,
    _validate_command_job,
)
from ..models._models import BlobReference
from ..models._models import Job as _RestJob
from ..models._models import Input as _Input
from ..models._models import Output as _Output
from ..models._patch_jobs import CommandJob, ServiceInstance, ValidationResult
from ..models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _has_header_case_insensitive
from ..models._enums import _FoundryFeaturesOptInKeys

_logger = logging.getLogger(__name__)


def _resolve_symlink(path: Path) -> Path:
    """Follow symlink chains until the real target is reached."""
    while path.is_symlink():
        link_path = path.resolve()
        if not link_path.is_absolute():
            link_path = path.parent.joinpath(link_path).resolve()
        path = link_path
    return path


def _load_gitignore_patterns(directory: Path) -> List[str]:
    """Load patterns from a .gitignore file in the given directory."""
    gitignore_file = ".gitignore"
    gitignore = directory / gitignore_file
    if not gitignore.is_file():
        return []
    patterns = []
    with open(gitignore, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


def _is_excluded(rel_path: str, patterns: List[str]) -> bool:
    """Check if a relative path matches any gitignore-style pattern."""
    rel_path = rel_path.replace("\\", "/")
    parts = rel_path.split("/")
    for pattern in patterns:
        stripped = pattern.rstrip("/")
        for part in parts:
            if fnmatch(part, stripped):
                return True
        if fnmatch(rel_path, pattern):
            return True
    return False


def _update_hash(path: Path, sha: "hashlib._Hash") -> None:
    """Read file at *path* in chunks and feed each chunk into *sha*."""
    chunk_size = 1024
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha.update(chunk)


def _collect_files(directory: Path, ignore_patterns: List[str]) -> List[Tuple[Path, str]]:
    """Collect all files in a directory, respecting gitignore patterns and resolving symlinks.

    Returns a sorted list of (resolved_path, relative_posix_path) tuples.
    """
    files: List[Tuple[Path, str]] = []
    for root, _, filenames in os.walk(directory, followlinks=True):
        for filename in filenames:
            abs_path = Path(root, filename)
            rel_path = abs_path.relative_to(directory).as_posix()
            if not _is_excluded(rel_path, ignore_patterns):
                files.append((_resolve_symlink(abs_path), rel_path))
    return sorted(files, key=lambda x: x[1].lower())


def _content_hash(path: Path) -> str:
    """Compute a truncated SHA-256 content hash for a file or directory.

    Respects ``.gitignore`` when hashing directories.
    """
    path = _resolve_symlink(path)
    sha = hashlib.sha256()
    if path.is_file():
        file_list = [(path, path.name)]
    else:
        ignore_patterns = _load_gitignore_patterns(path)
        file_list = _collect_files(path, ignore_patterns)
    sha.update(str(len(file_list)).encode())
    for abs_path, rel_path in file_list:
        sha.update(("#" + rel_path + "#").encode())
        sha.update(str(os.path.getsize(abs_path)).encode())
    for abs_path, _ in file_list:
        _update_hash(abs_path, sha)
    return sha.hexdigest()[:8]


class JobsOperations(_GeneratedJobsOps):
    """Patched Jobs operations that expose a flat :class:`~azure.ai.projects.models.CommandJob`
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

    @distributed_trace
    def validate(
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

    def _resolve_asset_uri(
        self,
        uri: str,
        dataset_name: str,
        base_path: Optional[Union[str, PathLike[str]]] = None,
    ) -> str:
        """Resolve a single URI to a dataset asset URI.

        Three forms are accepted:

        * **Local file or folder path** — uploaded to a new dataset; the dataset URI is returned.
        * **``name:version``** (optionally prefixed with ``azureai:``) — the existing dataset is
          fetched and its URI is returned.
        * **Datastore / remote URI** — returned unchanged.

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
                existing = self._datasets.get(name=dataset_name, version=version)
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
                result = self._datasets.upload_folder(name=dataset_name, version=version, folder=str(local_path))
            else:
                _logger.debug(
                    "[JobsOperations] Uploading file '%s' as dataset '%s' v%s.",
                    local_path,
                    dataset_name,
                    version,
                )
                result = self._datasets.upload_file(name=dataset_name, version=version, file_path=str(local_path))
            if not result.id:
                raise ValueError(f"Dataset upload succeeded but the service did not return a URI for '{local_path}'.")
            _logger.debug("[JobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
            return result.id

        parsed = urlparse(uri)
        if parsed.scheme and not parsed.netloc:
            raw = uri[len("azureai:") :] if uri.startswith("azureai:") else uri
            ds_name, ds_version = raw.split(":", 1)
            _logger.debug("[JobsOperations] Resolving name:version '%s' to dataset URI.", uri)
            result = self._datasets.get(name=ds_name, version=ds_version)
            if not result.id:
                raise ValueError(f"Dataset '{uri}' was fetched but the service did not return a URI.")
            _logger.debug("[JobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
            return result.id

        # Already a datastore / remote URI — pass through unchanged.
        return uri

    def _resolve_code(self, name: str, job: CommandJob) -> None:
        """Resolve ``code`` on the job body to a datastore URI if it is a local path.

        :param name: The job name (used to derive a unique dataset name).
        :type name: str
        :param job: The command job body to mutate in-place.
        :type job: ~azure.ai.projects.models.CommandJob
        """
        if not isinstance(job.code, str):
            return
        dataset_name = f"{name}-code"
        job.code = self._resolve_asset_uri(job.code, dataset_name, base_path=job._base_path)

    def _resolve_input_paths(self, name: str, job: CommandJob) -> None:
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
            job_input.path = self._resolve_asset_uri(job_input.path, dataset_name, base_path=base_path)

    def _resolve_local_paths(self, name: str, job: CommandJob) -> None:
        """Resolve all local paths in the job body to datastore URIs.

        :param name: The job name.
        :type name: str
        :param job: The command job job to mutate in-place.
        :type job: ~azure.ai.projects.models.CommandJob
        """
        self._resolve_code(name, job)
        self._resolve_input_paths(name, job)

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
    ) -> ItemPaged[CommandJob]:
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
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.CommandJob]
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

    @distributed_trace
    def get(self, name: str, **kwargs: Any) -> CommandJob:  # type: ignore[override]
        """Get a training job by name.

        :param name: The name of the job. Required.
        :type name: str
        :return: The job as a flat :class:`~azure.ai.projects.models.CommandJob` with
            ``name`` and ``id`` promoted from the Job resource envelope.
        :rtype: ~azure.ai.projects.models.CommandJob
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        rest_result = super().get(name=name, **kwargs)
        return CommandJob._from_rest_object(rest_result)

    @distributed_trace
    def create_or_update(self, name: str, job: CommandJob, **kwargs: Any) -> CommandJob:  # type: ignore[override]
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
        self._resolve_local_paths(name, job)
        self._inject_preview_header(kwargs)
        # Wrap the flat CommandJob inside the Job envelope required by the wire format
        rest_body = _RestJob(properties=job)
        rest_result = super().create_or_update(name=name, job=rest_body, **kwargs)
        return CommandJob._from_rest_object(rest_result)

    @distributed_trace
    def begin_delete(self, name: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Delete a training job by name.

        Returns 202 Accepted with a Location header to poll for completion,
        or 204 if the job does not exist.

        :param name: The name of the job. Required.
        :type name: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        return super().begin_delete(name=name, **kwargs)

    @distributed_trace
    def begin_cancel(self, name: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Cancel a training job by name.

        Returns 200 if cancelled immediately, or 202 Accepted with a Location header
        to poll for completion.

        :param name: The name of the job. Required.
        :type name: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        return super().begin_cancel(name=name, **kwargs)

    @distributed_trace
    def show_services(  # type: ignore[override]
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
        result = super().show_services(name=name, run_id=name, node_id=node_index, **kwargs)
        if not result or not result.instances:
            return None
        return {
            k: ServiceInstance._from_rest_object(v, node_index)
            for k, v in result.instances.items()
        }

    def _resolve_output_to_blob_ref(self, output_name: str, output: _Output) -> BlobReference:
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
        credential = self._datasets.get_credentials(name=output.asset_name, version=output.asset_version)
        return credential.blob_reference

    def _download_blob_reference(self, blob_ref: BlobReference, destination: Path) -> Tuple[int, int]:
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

        with ContainerClient.from_container_url(container_url=sas_uri) as container_client:
            list_prefix = (prefix + "/") if prefix else ""
            blobs = list(container_client.list_blobs(name_starts_with=list_prefix or None, include=["metadata"]))
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
                downloader = container_client.download_blob(blob=blob_name, max_concurrency=_MAX_CONCURRENCY)
                with open(local_path, "wb") as fh:
                    downloader.readinto(fh)
                file_count += 1
                total_bytes += blob.size or 0
            return file_count, total_bytes

    @distributed_trace
    def download(
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
        job = self.get(name=name, **kwargs)

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
            blob_ref = self._resolve_output_to_blob_ref(output_name, outputs[output_name])
            destination = dest_root / _NAMED_OUTPUTS_DIR / output_name
            _logger.info(
                "[JobsOperations] Downloading output '%s' from '%s' to '%s'.",
                output_name,
                blob_ref.blob_uri,
                destination,
            )
            file_count, total_bytes = self._download_blob_reference(blob_ref, destination)
            _logger.info(
                "[JobsOperations] Downloaded %d file(s) (%.2f MB) for output '%s'.",
                file_count,
                total_bytes / (1024 * 1024),
                output_name,
            )
            return

        if all:
            for out_name, out in outputs.items():
                try:
                    blob_ref = self._resolve_output_to_blob_ref(out_name, out)
                except ValueError as exc:
                    _logger.warning(
                        "[JobsOperations] Skipping output '%s' for job '%s': %s",
                        out_name,
                        name,
                        exc,
                    )
                    continue
                destination = dest_root / _NAMED_OUTPUTS_DIR / out_name
                _logger.info(
                    "[JobsOperations] Downloading output '%s' from '%s' to '%s'.",
                    out_name,
                    blob_ref.blob_uri,
                    destination,
                )
                file_count, total_bytes = self._download_blob_reference(blob_ref, destination)
                _logger.info(
                    "[JobsOperations] Downloaded %d file(s) (%.2f MB) for output '%s'.",
                    file_count,
                    total_bytes / (1024 * 1024),
                    out_name,
                )
            return

        raise NotImplementedError(_DEFAULT_OUTPUT_NOT_SUPPORTED_MSG)
