from .operations import TextAuthoringTrainedModelOperations
from . import models as _models
from azure.core.polling import LROPoller
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping
from azure.core.paging import ItemPaged

JSON = MutableMapping[str, Any]

class TextAuthoringTrainedModelClient:
    def __init__(self, operations: TextAuthoringTrainedModelOperations, project_name: str, trained_model_label: str):
        self._operations = operations
        self._project_name = project_name
        self._trained_model_label = trained_model_label

    def begin_evaluate_model(
        self,
        body: Union[_models.TextAuthoringEvaluationDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[_models.TextAuthoringEvaluationJobResult]:
        return self._operations.begin_evaluate_model(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            body=body,
            **kwargs,
        )

    def begin_load_snapshot(self, **kwargs: Any) -> LROPoller[None]:
        return self._operations.begin_load_snapshot(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            **kwargs,
        )

    def delete_trained_model(self, **kwargs: Any) -> None:
        return self._operations.delete_trained_model(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            **kwargs,
        )

    def get_evaluation_status(self, job_id: str, **kwargs: Any) -> _models.TextAuthoringEvaluationState:
        return self._operations.get_evaluation_status(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    def get_load_snapshot_status(self, job_id: str, **kwargs: Any) -> _models.TextAuthoringLoadSnapshotState:
        return self._operations.get_load_snapshot_status(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    def get_model_evaluation_results(
        self,
        *,
        skip: Optional[int] = None,
        string_index_type: Union[str, _models.StringIndexType] = _models.StringIndexType.UTF16_CODE_UNIT,
        top: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[_models.TextAuthoringDocumentEvalResult]:
        return self._operations.get_model_evaluation_results(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            skip=skip,
            string_index_type=string_index_type,
            top=top,
            **kwargs,
        )

    def get_model_evaluation_summary(self, **kwargs: Any) -> _models.TextAuthoringEvalSummary:
        return self._operations.get_model_evaluation_summary(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            **kwargs,
        )

    def get_trained_model(self, **kwargs: Any) -> _models.TextAuthoringProjectTrainedModel:
        return self._operations.get_trained_model(
            project_name=self._project_name,
            trained_model_label=self._trained_model_label,
            **kwargs,
        )