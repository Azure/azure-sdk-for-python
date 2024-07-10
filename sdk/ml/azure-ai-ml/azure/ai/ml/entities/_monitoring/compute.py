# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_06_01_preview.models import AmlTokenComputeIdentity, MonitorServerlessSparkCompute
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


class ServerlessSparkCompute:
    """Serverless Spark compute.

    :param runtime_version: The runtime version of the compute.
    :type runtime_version: str
    :param instance_type: The instance type of the compute.
    :type instance_type: str
    """

    def __init__(
        self,
        *,
        runtime_version: str,
        instance_type: str,
    ):
        self.runtime_version = runtime_version
        self.instance_type = instance_type

    def _to_rest_object(self) -> MonitorServerlessSparkCompute:
        self._validate()
        return MonitorServerlessSparkCompute(
            runtime_version=self.runtime_version,
            instance_type=self.instance_type,
            compute_identity=AmlTokenComputeIdentity(
                compute_identity_type="AmlToken",
            ),
        )

    @classmethod
    def _from_rest_object(cls, obj: MonitorServerlessSparkCompute) -> "ServerlessSparkCompute":
        return cls(
            runtime_version=obj.runtime_version,
            instance_type=obj.instance_type,
        )

    def _validate(self) -> None:
        if self.runtime_version != "3.3":
            msg = "Compute runtime version must be 3.3"
            err = ValidationException(
                message=msg,
                target=ErrorTarget.MODEL_MONITORING,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
            log_and_raise_error(err)
