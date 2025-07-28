from .operations import TextAuthoringExportedModelOperations
from . import models as _models
from azure.core.polling import LROPoller
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class TextAuthoringExportedModel:
    def __init__(
        self,
        operations: TextAuthoringExportedModelOperations,
        project_name: str,
        exported_model_name: str,
    ):
        self._operations = operations
        self._project_name = project_name
        self._exported_model_name = exported_model_name

    def begin_create_or_update_exported_model(
        self,
        body: Union[_models.TextAuthoringExportedModelDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_create_or_update_exported_model(
            project_name=self._project_name,
            exported_model_name=self._exported_model_name,
            body=body,
            **kwargs
        )

    def begin_delete_exported_model(
        self,
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_delete_exported_model(
            project_name=self._project_name,
            exported_model_name=self._exported_model_name,
            **kwargs
        )

    def get_exported_model(
        self,
        **kwargs: Any
    ) -> _models.TextAuthoringExportedTrainedModel:
        return self._operations.get_exported_model(
            project_name=self._project_name,
            exported_model_name=self._exported_model_name,
            **kwargs
        )

    def get_exported_model_job_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.TextAuthoringExportedModelState:
        return self._operations.get_exported_model_job_status(
            project_name=self._project_name,
            exported_model_name=self._exported_model_name,
            job_id=job_id,
            **kwargs
        )

    def get_exported_model_manifest(
        self,
        **kwargs: Any
    ) -> _models.ExportedModelManifest:
        return self._operations.get_exported_model_manifest(
            project_name=self._project_name,
            exported_model_name=self._exported_model_name,
            **kwargs
        )