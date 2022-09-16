# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from enum import Enum

from azure.core.exceptions import AzureError

module_logger = logging.getLogger(__name__)


class ValidationErrorType(Enum):
    """
    Error types to be specified when using ValidationException class.
    Types are then used in raise_error.py to format a detailed error message for users.

    When using ValidationException, specify the type that best describes the nature of the error being captured.
    If no type fits, add a new enum here and update raise_error.py to handle it.

    INVALID_VALUE -> One or more schema fields are invalid (e.g. incorrect type or format)
    UNKNOWN_FIELD -> A least one unrecognized schema parameter is specified
    MISSING_FIELD -> At least one required schema parameter is missing
    FILE_OR_FOLDER_NOT_FOUND -> One or more files or folder paths do not exist
    CANNOT_SERIALIZE -> Same as "Cannot dump". One or more fields cannot be serialized by marshmallow.
    CANNOT_PARSE -> YAML file cannot be parsed
    RESOURCE_NOT_FOUND -> Resource could not be found
    GENERIC -> Undefined placeholder. Avoid using.
    """

    INVALID_VALUE = "INVALID VALUE"
    UNKNOWN_FIELD = "UNKNOWN FIELD"
    MISSING_FIELD = "MISSING FIELD"
    FILE_OR_FOLDER_NOT_FOUND = "FILE OR FOLDER NOT FOUND"
    CANNOT_SERIALIZE = "CANNOT DUMP"
    CANNOT_PARSE = "CANNOT PARSE"
    RESOURCE_NOT_FOUND = "RESOURCE NOT FOUND"
    GENERIC = "GENERIC"


class ErrorCategory:

    USER_ERROR = "UserError"
    SYSTEM_ERROR = "SystemError"
    UNKNOWN = "Unknown"


class ErrorTarget:

    BATCH_ENDPOINT = "BatchEndpoint"
    BATCH_DEPLOYMENT = "BatchDeployment"
    LOCAL_ENDPOINT = "LocalEndpoint"
    CODE = "Code"
    COMPONENT = "Component"
    DATA = "Data"
    ENVIRONMENT = "Environment"
    JOB = "Job"
    COMMAND_JOB = "CommandJob"
    SPARK_JOB = "SparkJob"
    LOCAL_JOB = "LocalJob"
    MODEL = "Model"
    ONLINE_DEPLOYMENT = "OnlineDeployment"
    ONLINE_ENDPOINT = "OnlineEndpoint"
    ASSET = "Asset"
    DATASTORE = "Datastore"
    WORKSPACE = "Workspace"
    COMPUTE = "Compute"
    DEPLOYMENT = "Deployment"
    ENDPOINT = "Endpoint"
    AUTOML = "AutoML"
    PIPELINE = "Pipeline"
    SWEEP_JOB = "SweepJob"
    GENERAL = "General"
    IDENTITY = "Identity"
    ARM_DEPLOYMENT = "ArmDeployment"
    ARM_RESOURCE = "ArmResource"
    ARTIFACT = "Artifact"
    SCHEDULE = "Schedule"
    UNKNOWN = "Unknown"


class MlException(AzureError):
    """
    The base class for all exceptions raised in AzureML SDK code base. If there is a need to define a custom exception type,
    that custom exception type should extend from this class.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data. This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    :param error: The original exception if any.
    :type error: Exception
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        self._error_category = error_category
        self._target = target
        self._no_personal_data_message = no_personal_data_message
        super().__init__(message, *args, **kwargs)

    @property
    def target(self):
        """Return the error target.

        :return: The error target.
        :rtype: ErrorTarget
        """
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def no_personal_data_message(self):
        """Return the error message with no personal data.

        :return: No personal data error message.
        :rtype: str
        """
        return self._no_personal_data_message

    @no_personal_data_message.setter
    def no_personal_data_message(self, value):
        self._no_personal_data_message = value

    @property
    def error_category(self):
        """Return the error category.

        :return: The error category.
        :rtype: ErrorCategory
        """
        return self._error_category

    @error_category.setter
    def error_category(self, value):
        self._error_category = value


class DeploymentException(MlException):
    """
    Class for all exceptions related to Deployments.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(DeploymentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ComponentException(MlException):
    """
    Class for all exceptions related to Components.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(ComponentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class JobException(MlException):
    """
    Class for all exceptions related to Jobs.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(JobException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ModelException(MlException):
    """
    Class for all exceptions related to Models.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(ModelException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class AssetException(MlException):
    """
    Class for all exceptions related to Assets.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(AssetException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ScheduleException(MlException):
    """
    Class for all exceptions related to Job Schedules.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        super(ScheduleException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ValidationException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        error_type: ValidationErrorType = ValidationErrorType.GENERIC,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.USER_ERROR,
        *args,
        **kwargs,
    ):
        """
        Class for all exceptions raised as part of client-side schema validation.

        :param message: A message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: The error message without any personal data.
            This will be pushed to telemetry logs.
        :type no_personal_data_message: str
        :param error_type: The error type, chosen from one of the values of ValidationErrorType enum class.
        :type error_type: ValidationErrorType
        :param target: The name of the element that caused the exception to be thrown.
        :type target: ErrorTarget
        :param error_category: The error category, defaults to Unknown.
        :type error_category: ErrorCategory
        :param error: The original exception if any.
        :type error: Exception
        """
        super(ValidationException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )

        if error_type in list(ValidationErrorType):
            self._error_type = error_type
        else:
            raise Exception(f"Error type {error_type} is not a member of the ValidationErrorType enum class.")

    @property
    def error_type(self):
        """Return the error type.

        :return: The error type.
        :rtype: ValidationErrorType
        """
        return self._error_type

    @error_type.setter
    def error_type(self, value):
        self._error_type = value


class AssetPathException(MlException):
    """
    Class for the exception raised when an attempt is made to update the path of an existing asset. Asset paths are immutable.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(AssetPathException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )
