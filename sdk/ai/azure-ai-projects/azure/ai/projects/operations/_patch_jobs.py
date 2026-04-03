# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customized training/jobs operations — flat CommandJob UX, no envelope required."""

import logging
from datetime import datetime, timezone
from os import PathLike
from pathlib import Path
from typing import Any, List, Optional, Union
from urllib.parse import urlparse

from azure.core.paging import ItemPaged

from azure.core.tracing.decorator import distributed_trace

from ._operations import BetaTrainingJobsOperations as _GeneratedTrainingJobsOps
from ._patch_datasets import DatasetsOperations
from ..models._models import Job as _RestJob
from ..models._models import Input as _Input
from ..models._patch_jobs import CommandJob
from ..models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _has_header_case_insensitive
from ..models._enums import FoundryFeaturesOptInKeys

_logger = logging.getLogger(__name__)


class TrainingJobsOperations(_GeneratedTrainingJobsOps):
    """Patched Jobs operations that expose a flat :class:`~azure.ai.projects.models.CommandJob`
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

    def _resolve_asset_uri(
        self, uri: str, dataset_name: str, base_path: Optional[Union[str, PathLike[str]]] = None
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
            version = "1"
            if local_path.is_dir():
                _logger.debug(
                    "[TrainingJobsOperations] Uploading folder '%s' as dataset '%s' v%s.",
                    local_path,
                    dataset_name,
                    version,
                )
                result = self._datasets.upload_folder(name=dataset_name, version=version, folder=str(local_path))
            else:
                _logger.debug(
                    "[TrainingJobsOperations] Uploading file '%s' as dataset '%s' v%s.",
                    local_path,
                    dataset_name,
                    version,
                )
                result = self._datasets.upload_file(name=dataset_name, version=version, file_path=str(local_path))
            if not result.id:
                raise ValueError(f"Dataset upload succeeded but the service did not return a URI for '{local_path}'.")
            _logger.debug("[TrainingJobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
            return result.id

        parsed = urlparse(uri)
        if parsed.scheme and not parsed.netloc:
            raw = uri[len("azureai:") :] if uri.startswith("azureai:") else uri
            ds_name, ds_version = raw.split(":", 1)
            _logger.debug("[TrainingJobsOperations] Resolving name:version '%s' to dataset URI.", uri)
            result = self._datasets.get(name=ds_name, version=ds_version)
            if not result.id:
                raise ValueError(f"Dataset '{uri}' was fetched but the service did not return a URI.")
            _logger.debug("[TrainingJobsOperations] Resolved '%s' → '%s'.", uri, result.data_uri)
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
        dataset_name = f"{name}-code-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
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
            dataset_name = f"{name}-input-{input_key}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
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

        Accepts a flat :class:`~azure.ai.projects.models.CommandJob` (no ``Job`` envelope
        needed) and returns a :class:`~azure.ai.projects.models.CommandJob` with ``name``
        and ``id`` populated from the service response.

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
