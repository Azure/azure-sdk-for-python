from typing import Any, IO, Optional, Union
from collections.abc import MutableMapping
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.async_paging import AsyncItemPaged, AsyncList
from .. import models as _models
from .operations import ConversationAuthoringTrainedModelOperations

JSON = MutableMapping[str, Any]

class ConversationAuthoringTrainedModelClientAsync:
    def __init__(self, operations: ConversationAuthoringTrainedModelOperations, project_name: str, trained_model_label: str):
        self._operations = operations
        self._project_name = project_name
        self._trained_model_label = trained_model_label

    async def begin_evaluate_model(
        self,
        body: Union[
            _models.ConversationAuthoringEvaluationDetails,
            JSON,
            IO[bytes]
        ],
        **kwargs: Any
    ) -> AsyncLROPoller[_models.ConversationAuthoringEvaluationJobResult]:
        return await self._operations.begin_evaluate_model(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            body=body,
            **kwargs,
        )

    async def begin_load_snapshot(
        self,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_load_snapshot(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            **kwargs,
        )

    async def delete_trained_model(
        self,
        **kwargs: Any
    ) -> None:
        return await self._operations.delete_trained_model(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            **kwargs,
        )

    async def get_evaluation_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringEvaluationState:
        return await self._operations.get_evaluation_status(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    async def get_load_snapshot_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringLoadSnapshotState:
        return await self._operations.get_load_snapshot_status(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    async def get_model_evaluation_results(
        self,
        *,
        skip: Optional[int] = None,
        string_index_type: Union[str, _models.StringIndexType],
        top: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[_models.AnalyzeConversationAuthoringUtteranceEvaluationResult]:
        return self._operations.get_model_evaluation_results(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            skip=skip,
            string_index_type=string_index_type,
            top=top,
            **kwargs,
        )

    async def get_model_evaluation_summary(self, **kwargs: Any) -> _models.ConversationAuthoringEvalSummary:
        return await self._operations.get_model_evaluation_summary(
            self._project_name,
            self._trained_model_label,
            **kwargs
        )

    async def get_trained_model(self, **kwargs: Any) -> _models.ConversationAuthoringProjectTrainedModel:
        return await self._operations.get_trained_model(
            self._project_name,
            self._trained_model_label,
            **kwargs
        )
    
__all__ = ["ConversationAuthoringTrainedModelClientAsync"]