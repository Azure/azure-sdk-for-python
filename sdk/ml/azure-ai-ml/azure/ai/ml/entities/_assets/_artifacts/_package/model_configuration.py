# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------


from typing import Optional

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_04_01_preview.models import ModelConfiguration as RestModelConfiguration
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


@experimental
class ModelConfiguration:
    """ModelConfiguration.

    :param mode: The mode of the model. Possible values include: "Copy", "Download".
    :type mode: str
    :param mount_path: The mount path of the model.
    :type mount_path: str

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
    def _from_rest_object(cls, rest_obj: RestModelConfiguration) -> "ModelConfiguration":
        return ModelConfiguration(mode=rest_obj.mode, mount_path=rest_obj.mount_path)

    def _to_rest_object(self) -> RestModelConfiguration:
        self._validate()
        return RestModelConfiguration(mode=self.mode, mount_path=self.mount_path)

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
