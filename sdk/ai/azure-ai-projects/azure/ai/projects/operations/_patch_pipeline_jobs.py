# pylint: disable=line-too-long,protected-access
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customized Pipeline Jobs operations."""

from copy import copy
import logging
from os import PathLike
from typing import Any, List, Optional, Union, overload
from uuid import uuid4

from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from .._configuration import AIProjectClientConfiguration
from ._operations import PipelineJobsOperations as _GeneratedPipelineJobsOperations
from ._patch_datasets import DatasetsOperations
from ._patch_jobs import JobsOperations as _BetaJobsOperations
from ..models._enums import ListViewType, _FoundryFeaturesOptInKeys
from ..models._models import PipelineJobResource as _RestPipelineJobResource
from ..models._patch_jobs import PipelineJob, _from_rest_pipeline_job

_logger = logging.getLogger(__name__)


class PipelineJobsOperations(_GeneratedPipelineJobsOperations):
    """Pipeline-only operations exposed through ``client.pipeline_jobs``.

    The dedicated public ``/pipeline_jobs`` ingress forwards to the existing MFE
    Pipeline implementation. Asset registration is intentionally shared with
    ``client.beta.jobs`` so both surfaces produce identical Code identities.

    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, access it via ``client.pipeline_jobs``.
    """

    _config: AIProjectClientConfiguration
    _JOBS_PREVIEW_HEADER: str = _FoundryFeaturesOptInKeys.JOBS_V1_PREVIEW.value

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Jobs use a preview API version, while the shared Dataset client used
        # for local Code registration must retain the root client's v1 config.
        original_config = self._config
        self._config = copy(original_config)
        self._config.api_version = "2026-01-15-preview"
        self._datasets = DatasetsOperations(
            self._client, original_config, self._serialize, self._deserialize
        )

    # Keep route-specific request handling in the generated Pipeline Jobs class,
    # while reusing the proven local-asset contract from beta.jobs.
    def _resolve_asset_uri(
        self,
        uri: str,
        dataset_name: str,
        base_path: Optional[Union[str, PathLike[str]]] = None,
    ) -> str:
        return _BetaJobsOperations._resolve_asset_uri(self, uri, dataset_name, base_path)  # type: ignore[arg-type]

    def _resolve_pipeline_code(self, name: str, job: PipelineJob) -> None:
        _BetaJobsOperations._resolve_pipeline_code(self, name, job)  # type: ignore[arg-type]

    def _inject_preview_header(self, kwargs: dict) -> None:
        _BetaJobsOperations._inject_preview_header(self, kwargs)  # type: ignore[arg-type]

    @distributed_trace
    def list(
        self,
        *,
        tag: Optional[str] = None,
        list_view_type: Optional[Union[str, ListViewType]] = None,
        properties: Optional[str] = None,
        **kwargs: Any,
    ) -> ItemPaged[PipelineJob]:
        """List Pipeline Jobs with the resource envelope flattened.

        :keyword tag: Filter by tag in ``key=value`` format.
        :paramtype tag: str or None
        :keyword list_view_type: Select active, archived, or all jobs.
        :paramtype list_view_type: str or ~azure.ai.projects.models.ListViewType or None
        :keyword properties: Comma-separated user property filters.
        :paramtype properties: str or None
        :return: An iterator over PipelineJob objects.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.PipelineJob]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)

        def _convert_page(page: List[_RestPipelineJobResource]) -> List[PipelineJob]:
            return [_from_rest_pipeline_job(item) for item in page]

        return super().list(
            tag=tag,
            list_view_type=list_view_type,
            properties=properties,
            cls=_convert_page,
            **kwargs,
        )  # type: ignore[return-value]

    @distributed_trace
    def get(self, name: str, **kwargs: Any) -> PipelineJob:  # type: ignore[override]
        """Get a Pipeline Job by name with the resource envelope flattened.

        :param name: The case-sensitive Pipeline Job name.
        :type name: str
        :return: The requested PipelineJob.
        :rtype: ~azure.ai.projects.models.PipelineJob
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._inject_preview_header(kwargs)
        return _from_rest_pipeline_job(super().get(name=name, **kwargs))

    @overload  # type: ignore[override]
    def create_or_update(
        self,
        name: PipelineJob,
        job: None = None,
        *,
        experiment_name: Optional[str] = None,
        **kwargs: Any,
    ) -> PipelineJob: ...

    @overload
    def create_or_update(
        self,
        name: str,
        job: PipelineJob,
        *,
        experiment_name: None = None,
        **kwargs: Any,
    ) -> PipelineJob: ...

    @distributed_trace
    def create_or_update(  # type: ignore[override]
        self,
        name: Union[str, PipelineJob],
        job: Optional[PipelineJob] = None,
        *,
        experiment_name: Optional[str] = None,
        **kwargs: Any,
    ) -> PipelineJob:
        """Create or update a Pipeline Job through the dedicated ingress.

        :param name: The Pipeline Job name, or a PipelineJob for an autogenerated name.
        :type name: str or ~azure.ai.projects.models.PipelineJob
        :param job: The PipelineJob when ``name`` is a string.
        :type job: ~azure.ai.projects.models.PipelineJob or None
        :keyword experiment_name: Experiment name for a job-only submission.
        :paramtype experiment_name: str or None
        :return: The created or updated PipelineJob.
        :rtype: ~azure.ai.projects.models.PipelineJob
        :raises TypeError: If arguments do not identify exactly one PipelineJob.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if isinstance(name, PipelineJob):
            if job is not None:
                raise TypeError(
                    "A job cannot be supplied when the first argument is a PipelineJob."
                )
            job = name
            name = f"pipeline-{uuid4().hex}"
            if experiment_name is not None:
                job.experiment_name = experiment_name
        elif not isinstance(name, str) or job is None:
            raise TypeError(
                "create_or_update requires a job name and PipelineJob, or one PipelineJob."
            )
        elif experiment_name is not None:
            raise TypeError(
                "Set job.experiment_name when submitting a PipelineJob with an explicit name."
            )

        if not isinstance(job, PipelineJob):
            raise TypeError("job must be a PipelineJob")

        self._resolve_pipeline_code(name, job)
        self._inject_preview_header(kwargs)
        _logger.debug(
            "[PipelineJobsOperations] Submitting PipelineJob '%s' with %d graph node(s) through /pipeline_jobs.",
            name,
            len(job.jobs or {}),
        )
        # The generated wire contract retains the polymorphic resource envelope
        # so /jobs keeps both Command and Pipeline discriminator mappings.
        rest_body = _RestPipelineJobResource(properties=job)
        return _from_rest_pipeline_job(
            super().create_or_update(name=name, job=rest_body, **kwargs)
        )


__all__ = ["PipelineJobsOperations"]
