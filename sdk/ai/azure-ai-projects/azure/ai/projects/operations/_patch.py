# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from functools import wraps
import inspect
from collections.abc import MutableMapping
from io import IOBase
from typing import Any, Callable, IO, List, Optional, Union, cast, overload

from azure.core.tracing.decorator import distributed_trace
from ..models._patch import (
    _FOUNDRY_FEATURES_HEADER_NAME,
    _BETA_OPERATION_FEATURE_HEADERS,
    _has_header_case_insensitive,
)
from .. import models as _models
from ._patch_agents import AgentsOperations
from ._patch_datasets import DatasetsOperations
from ._patch_evaluation_rules import EvaluationRulesOperations
from ._patch_telemetry import TelemetryOperations
from ._patch_connections import ConnectionsOperations
from ._patch_memories import BetaMemoryStoresOperations
from ._patch_models import BetaModelsOperations
from ._operations import (
    BetaAgentsOperations as BetaAgentsOperationsGenerated,
    BetaDatasetsOperations as BetaDatasetsOperationsGenerated,
    BetaEvaluationTaxonomiesOperations,
    BetaEvaluatorsOperations as BetaEvaluatorsOperationsGenerated,
    BetaInsightsOperations,
    BetaOperations as GeneratedBetaOperations,
    BetaRedTeamsOperations,
    BetaRoutinesOperations,
    BetaSchedulesOperations,
    BetaSkillsOperations,
)


class BetaEvaluatorsOperations(BetaEvaluatorsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta.evaluators` attribute.
    """

    @overload
    def create_generation_job(
        self,
        job: _models.EvaluatorGenerationJob,
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.EvaluatorGenerationJob: ...

    @overload
    def create_generation_job(
        self,
        job: MutableMapping[str, Any],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.EvaluatorGenerationJob: ...

    @overload
    def create_generation_job(
        self, job: IO[bytes], *, operation_id: Optional[str] = None, **kwargs: Any
    ) -> _models.EvaluatorGenerationJob: ...

    @distributed_trace
    def create_generation_job(
        self,
        job: Union[_models.EvaluatorGenerationJob, MutableMapping[str, Any], IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.EvaluatorGenerationJob:
        """Create an evaluator generation job (non-polling).

        This compatibility method returns the initial queued job like the prior shipped API.
        For the final result, use begin_create_generation_job() which returns an LROPoller.

        Creates an evaluator generation job and returns the initial job resource immediately.
        The service generates rubric-based evaluator definitions from the provided source
        materials asynchronously. Use get_generation_job() to poll for completion.

        :param job: The job to create. Is either a EvaluatorGenerationJob type, a
         MutableMapping[str, Any] type, or a IO[bytes] type. Required.
        :type job: ~azure.ai.projects.models.EvaluatorGenerationJob or MutableMapping[str, Any] or
         IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the job unconditionally. Default value is None.
        :paramtype operation_id: str
        :return: EvaluatorGenerationJob. The EvaluatorGenerationJob is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.EvaluatorGenerationJob
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if isinstance(job, MutableMapping) and not isinstance(job, (IOBase, bytes)):
            job_copy = dict(job)
            for field in (
                "id",
                "result",
                "status",
                "error",
                "created_at",
                "createdAt",
                "finished_at",
                "finishedAt",
                "usage",
            ):
                job_copy.pop(field, None)
            job = job_copy

        cls = kwargs.pop("cls", None)
        kwargs.pop("polling", None)

        def _extract_initial_response(
            pipeline_response, _deserialized, _response_headers
        ):
            response_json = pipeline_response.http_response.json()
            result = _models.EvaluatorGenerationJob(response_json)
            if cls:
                return cls(pipeline_response, result, _response_headers)
            return result

        poller = self.begin_create_generation_job(
            job=cast(Any, job),
            operation_id=operation_id,
            polling=False,
            cls=_extract_initial_response,
            **kwargs
        )

        return cast(_models.EvaluatorGenerationJob, poller.result())


class BetaDatasetsOperations(BetaDatasetsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta.datasets` attribute.
    """

    @overload
    def create_generation_job(
        self,
        job: _models.DataGenerationJob,
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.DataGenerationJob: ...

    @overload
    def create_generation_job(
        self,
        job: MutableMapping[str, Any],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.DataGenerationJob: ...

    @overload
    def create_generation_job(
        self, job: IO[bytes], *, operation_id: Optional[str] = None, **kwargs: Any
    ) -> _models.DataGenerationJob: ...

    @distributed_trace
    def create_generation_job(
        self,
        job: Union[_models.DataGenerationJob, MutableMapping[str, Any], IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.DataGenerationJob:
        """Create a data generation job (non-polling).

        This compatibility method returns the initial queued job like the prior shipped API.
        For the final result, use begin_create_generation_job() which returns an LROPoller.

        Creates a data generation job and returns the initial job resource immediately.
        The service generates synthetic data from the provided configuration asynchronously.
        Use get_generation_job() to poll for completion.

        :param job: The job to create. Is either a DataGenerationJob type, a
         MutableMapping[str, Any] type, or a IO[bytes] type. Required.
        :type job: ~azure.ai.projects.models.DataGenerationJob or MutableMapping[str, Any] or
         IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the job unconditionally. Default value is None.
        :paramtype operation_id: str
        :return: DataGenerationJob. The DataGenerationJob is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.DataGenerationJob
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if isinstance(job, MutableMapping) and not isinstance(job, (IOBase, bytes)):
            job_copy = dict(job)
            for field in (
                "id",
                "result",
                "status",
                "error",
                "created_at",
                "createdAt",
                "finished_at",
                "finishedAt",
                "usage",
            ):
                job_copy.pop(field, None)
            job = job_copy

        cls = kwargs.pop("cls", None)
        kwargs.pop("polling", None)

        def _extract_initial_response(
            pipeline_response, _deserialized, _response_headers
        ):
            response_json = pipeline_response.http_response.json()
            result = _models.DataGenerationJob(response_json)
            if cls:
                return cls(pipeline_response, result, _response_headers)
            return result

        poller = self.begin_create_generation_job(
            job=cast(Any, job),
            operation_id=operation_id,
            polling=False,
            cls=_extract_initial_response,
            **kwargs
        )

        return cast(_models.DataGenerationJob, poller.result())


class BetaAgentsOperations(BetaAgentsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta.agents` attribute.
    """

    @overload
    def create_optimization_job(
        self,
        job: _models.OptimizationJob,
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.OptimizationJob: ...

    @overload
    def create_optimization_job(
        self,
        job: MutableMapping[str, Any],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.OptimizationJob: ...

    @overload
    def create_optimization_job(
        self, job: IO[bytes], *, operation_id: Optional[str] = None, **kwargs: Any
    ) -> _models.OptimizationJob: ...

    @distributed_trace
    def create_optimization_job(
        self,
        job: Union[_models.OptimizationJob, MutableMapping[str, Any], IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.OptimizationJob:
        """Create an agent optimization job (non-polling).

        This compatibility method returns the initial queued job like the prior shipped API.
        For the final result, use begin_create_optimization_job() which returns an LROPoller.

        Creates an agent optimization job and returns the initial queued job resource immediately.
        The service optimizes agent configurations asynchronously.
        Use get_optimization_job() to poll for completion.

        :param job: The job to create. Is either a OptimizationJob type, a
         MutableMapping[str, Any] type, or a IO[bytes] type. Required.
        :type job: ~azure.ai.projects.models.OptimizationJob or MutableMapping[str, Any] or
         IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the job unconditionally. Default value is None.
        :paramtype operation_id: str
        :return: OptimizationJob. The OptimizationJob is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.OptimizationJob
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if isinstance(job, MutableMapping) and not isinstance(job, (IOBase, bytes)):
            job_copy = dict(job)
            for field in (
                "id",
                "result",
                "status",
                "error",
                "created_at",
                "createdAt",
                "finished_at",
                "finishedAt",
                "usage",
                "updated_at",
                "updatedAt",
                "progress",
                "warnings",
            ):
                job_copy.pop(field, None)
            job = job_copy

        cls = kwargs.pop("cls", None)
        kwargs.pop("polling", None)

        def _extract_initial_response(
            pipeline_response, _deserialized, _response_headers
        ):
            response_json = pipeline_response.http_response.json()
            result = _models.OptimizationJob(response_json)
            if cls:
                return cls(pipeline_response, result, _response_headers)
            return result

        poller = self.begin_create_optimization_job(
            job=cast(Any, job),
            operation_id=operation_id,
            polling=False,
            cls=_extract_initial_response,
            **kwargs
        )

        return cast(_models.OptimizationJob, poller.result())


def _method_accepts_keyword_headers(method: Callable[..., Any]) -> bool:
    try:
        signature = inspect.signature(method)
    except (TypeError, ValueError):
        return False

    for parameter in signature.parameters.values():
        if parameter.name == "headers":
            return True
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            return True

    return False


class _OperationMethodHeaderProxy:
    """Proxy that injects the Foundry-Features header into public operation method calls."""

    def __init__(self, operation: Any, foundry_features_value: str):
        object.__setattr__(self, "_operation", operation)
        object.__setattr__(self, "_foundry_features_value", foundry_features_value)

    def __getattr__(self, name: str) -> Any:
        attribute = getattr(self._operation, name)

        if (
            name.startswith("_")
            or not callable(attribute)
            or not _method_accepts_keyword_headers(attribute)
        ):
            return attribute

        @wraps(attribute)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {
                    _FOUNDRY_FEATURES_HEADER_NAME: self._foundry_features_value
                }
            elif not _has_header_case_insensitive(
                headers, _FOUNDRY_FEATURES_HEADER_NAME
            ):
                try:
                    headers[_FOUNDRY_FEATURES_HEADER_NAME] = (
                        self._foundry_features_value
                    )
                except Exception:  # pylint: disable=broad-except
                    # Fall back to replacing invalid/immutable header containers.
                    kwargs["headers"] = {
                        _FOUNDRY_FEATURES_HEADER_NAME: self._foundry_features_value,
                    }

            return attribute(*args, **kwargs)

        return _wrapped

    def __dir__(self) -> list:
        return dir(self._operation)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._operation, name, value)


class BetaOperations(GeneratedBetaOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta` attribute.
    """

    agents: BetaAgentsOperations
    """:class:`~azure.ai.projects.operations.BetaAgentsOperations` operations"""
    evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
    """:class:`~azure.ai.projects.operations.BetaEvaluationTaxonomiesOperations` operations"""
    evaluators: BetaEvaluatorsOperations
    """:class:`~azure.ai.projects.operations.BetaEvaluatorsOperations` operations"""
    insights: BetaInsightsOperations
    """:class:`~azure.ai.projects.operations.BetaInsightsOperations` operations"""
    memory_stores: BetaMemoryStoresOperations
    """:class:`~azure.ai.projects.operations.BetaMemoryStoresOperations` operations"""
    models: BetaModelsOperations
    """:class:`~azure.ai.projects.operations.BetaModelsOperations` operations"""
    red_teams: BetaRedTeamsOperations
    """:class:`~azure.ai.projects.operations.BetaRedTeamsOperations` operations"""
    routines: BetaRoutinesOperations
    """:class:`~azure.ai.projects.operations.BetaRoutinesOperations` operations"""
    schedules: BetaSchedulesOperations
    """:class:`~azure.ai.projects.operations.BetaSchedulesOperations` operations"""
    skills: BetaSkillsOperations
    """:class:`~azure.ai.projects.operations.BetaSkillsOperations` operations"""
    datasets: BetaDatasetsOperations
    """:class:`~azure.ai.projects.operations.BetaDatasetsOperations` operations"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Replace with patched class that includes upload()
        self.evaluators = BetaEvaluatorsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        # Replace with patched class that includes create_optimization_job (non-polling)
        self.agents = BetaAgentsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        # Replace with patched class that includes begin_update_memories
        self.memory_stores = BetaMemoryStoresOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        # Replace with patched class that includes create (3-step upload helper)
        self.models = BetaModelsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        # Replace with patched class that includes create_generation_job (non-polling)
        self.datasets = BetaDatasetsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )

        for (
            property_name,
            foundry_features_value,
        ) in _BETA_OPERATION_FEATURE_HEADERS.items():
            setattr(
                self,
                property_name,
                _OperationMethodHeaderProxy(
                    getattr(self, property_name), foundry_features_value
                ),
            )


__all__: List[str] = [
    "AgentsOperations",
    "BetaAgentsOperations",
    "BetaDatasetsOperations",
    "BetaEvaluationTaxonomiesOperations",
    "BetaEvaluatorsOperations",
    "BetaInsightsOperations",
    "BetaMemoryStoresOperations",
    "BetaModelsOperations",
    "BetaOperations",
    "BetaRedTeamsOperations",
    "BetaRoutinesOperations",
    "BetaSchedulesOperations",
    "BetaSkillsOperations",
    "ConnectionsOperations",
    "DatasetsOperations",
    "EvaluationRulesOperations",
    "TelemetryOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
