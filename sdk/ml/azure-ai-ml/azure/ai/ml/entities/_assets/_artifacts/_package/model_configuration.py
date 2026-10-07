# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------


from typing import Any, Dict, Optional

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


@experimental
class ModelConfiguration:
    """ModelConfiguration.

    :keyword mode: The mode of the model. Possible values include: "Copy", "Download".
    :paramtype mode: str
    :keyword mount_path: The mount path of the model.
    :paramtype mount_path: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START model_configuration_entity_create]
            :end-before: [END model_configuration_entity_create]
            :language: python
            :dedent: 8
            :caption: Creating a Model Configuration object.
    """

    def __init__(self, *, mode: Optional[str] = None, mount_path: Optional[str] = None):
        self.mode = mode
        self.mount_path = mount_path

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "ModelConfiguration":
        mode = rest_obj.get("mode") if hasattr(rest_obj, "get") else rest_obj.mode
        mount_path = rest_obj.get("mountPath") if hasattr(rest_obj, "get") else rest_obj.mount_path
        return ModelConfiguration(mode=mode, mount_path=mount_path)

    def _to_rest_object(self) -> Dict[str, Any]:
        # ``ModelConfiguration`` was dropped from the arm_ml_service (2025-12) model; build the
        # 2023-04 wire body directly as a dict (JSON-direct). The legacy msrest model omitted ``None``
        # fields on the wire, so only include values that are set.
        self._validate()
        rest_obj: Dict[str, Any] = {}
        if self.mode is not None:
            rest_obj["mode"] = self.mode
        if self.mount_path is not None:
            rest_obj["mountPath"] = self.mount_path
        return rest_obj

    def _validate(self) -> None:
        if self.mode is not None and self.mode.lower() not in ["copy", "download"]:
            msg = "Mode must be either 'Copy' or 'Download'"
            err = ValidationException(
                message=msg,
                target=ErrorTarget.MODEL,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
            log_and_raise_error(err)
