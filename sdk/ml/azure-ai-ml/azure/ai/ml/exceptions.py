# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains exception module in Azure Machine Learning SDKv2.

This includes enums and classes for exceptions.
"""
from azure.core.exceptions import AzureError
import logging
from enum import Enum
from typing import Iterable, Optional, Union

from azure.core.exceptions import AzureError

module_logger = logging.getLogger(__name__)


class ValidationErrorType(Enum):
    """Error types to be specified when using ValidationException class.
    This is a section with an typo
    Types are then used in raise_error.py to format a detailed error message for users.
    When using ValidationException, specify the type that best describes the nature of the error being captured.
    If no type fits, add a new enum here and update raise_error.py to handle it.

    Types of validation errors:

    * INVALID_VALUE -> One or more schema fields are invalid (e.g. incorrect type or format)
    * UNKNOWN_FIELD -> A least one unrecognized schema parameter is specified
    * MISSING_FIELD -> At least one required schema parameter is missing
    * FILE_OR_FOLDER_NOT_FOUND -> One or more files or folder paths do not exist
    * CANNOT_SERIALIZE -> Same as "Cannot dump". One or more fields cannot be serialized by marshmallow.
    * CANNOT_PARSE -> YAML file cannot be parsed
    * RESOURCE_NOT_FOUND -> Resource could not be found
    * GENERIC -> Undefined placeholder. Avoid using.
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
    """Error Category based on error source."""

    USER_ERROR = "UserError"
    SYSTEM_ERROR = "SystemError"
    UNKNOWN = "Unknown"


class ErrorTarget:
    """Error Targets corresponding to the entity where the error was triggered."""

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
    DATA_TRANSFER_JOB = "DataTransferJob"
    LOCAL_JOB = "LocalJob"
    MODEL = "Model"
    ONLINE_DEPLOYMENT = "OnlineDeployment"
    ONLINE_ENDPOINT = "OnlineEndpoint"
    ASSET = "Asset"
    DATASTORE = "Datastore"
    BLOB_DATASTORE = "BlobDatastore"
    FILE_DATASTORE = "FileDatastore"
    GEN1_DATASTORE = "Gen1Datastore"
    GEN2_DATASTORE = "Gen2Datastore"
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
    REGISTRY = "Registry"
    UNKNOWN = "Unknown"
    FEATURE_SET = "FeatureSet"
    FEATURE_STORE_ENTITY = "FeatureStoreEntity"


class MlException(AzureError):
    """The base class for all exceptions raised in AzureML SDK code base.

    If there is a need to define a custom exception type, that custom exception type should extend from this class.
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return the base class where all exceptions raised in the AzureML SDK codebase.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data. This will be pushed to telemetry logs.
        :type no_personal_data_message: str
        :param target: Name of the element that caused the exception to be thrown, defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        :param error: The original exception if any
        :type error: Exception
        """
        self._error_category = error_category
        self._target = target
        self._no_personal_data_message = no_personal_data_message
        super().__init__(message, *args, **kwargs)

    @property
    def target(self) -> ErrorTarget:
        """Return the error target.

        :return: Error target
        :rtype: azure.ai.ml.exceptions.ErrorTarget
        """
        return self._target

    @target.setter
    def target(self, value: ErrorTarget) -> None:
        """Set error target.

        :param value: Error target
        :type value: azure.ai.ml.exceptions.ErrorTarget
        """
        self._target = value

    @property
    def no_personal_data_message(self) -> str:
        """Return the error message without personal data.

        :return: Error message without personal data
        :rtype: str
        """
        return self._no_personal_data_message

    @no_personal_data_message.setter
    def no_personal_data_message(self, value: str) -> None:
        """Set the error message without personal data.

        :param value: Error message without personal data
        :type value: str
        """
        self._no_personal_data_message = value

    @property
    def error_category(self) -> ErrorCategory:
        """Return the error category.

        :return: Error category
        :rtype: azure.ai.ml.exceptions.ErrorCategory
        """
        return self._error_category

    @error_category.setter
    def error_category(self, value: ErrorCategory) -> None:
        """Set the error category.

        :param value: Error category
        :type value: azure.ai.ml.exceptions.ErrorCategory
        """
        self._error_category = value


class DeploymentException(MlException):
    """Class for all exceptions related to Deployments."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return exception class for Deployments.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(DeploymentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ComponentException(MlException):
    """Class for all exceptions related to Components."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return exception class for Components.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(ComponentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class JobException(MlException):
    """Class for all exceptions related to Jobs."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return exception class for Jobs.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(JobException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ModelException(MlException):
    """Class for all exceptions related to Models."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return exception class for Models.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(ModelException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class AssetException(MlException):
    """Class for all exceptions related to Assets."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return exception class for Assets.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(AssetException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ScheduleException(MlException):
    """Class for all exceptions related to Job Schedules."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return exception class for Schedules.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(ScheduleException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ValidationException(MlException):
    """Class for all exceptions raised as part of client-side schema validation."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        error_type: ValidationErrorType = ValidationErrorType.GENERIC,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.USER_ERROR,
        **kwargs,
    ):
        """Return exception class for schema validation.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param error_type: The error type, chosen from one of the values of ValidationErrorType enum class.
        :type error_type: ValidationErrorType
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(ValidationException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )

        self.raw_error = message  # used for CLI error formatting

        if error_type in list(ValidationErrorType):
            self._error_type = error_type
        else:
            raise Exception(f"Error type {error_type} is not a member of the ValidationErrorType enum class.")

    @property
    def error_type(self) -> ValidationErrorType:
        """Return the error type.

        :return: The error type
        :rtype: azure.ai.ml.exceptions.ValidationErrorType
        """
        return self._error_type

    @error_type.setter
    def error_type(self, value: ValidationErrorType) -> None:
        """Set error type.

        :param value: Error type
        :type value: azure.ai.ml.exceptions.ValidationErrorType
        """
        self._error_type = value


class AssetPathException(MlException):
    """Class for the exception raised when an attempt is made to update the immutable path of an existing asset."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        """Return exception class for updating an immutable existing asset path.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super(AssetPathException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class EmptyDirectoryError(MlException):
    """Exception raised when an empty directory is provided as input for an I/O operation."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: Optional[ErrorTarget] = ErrorTarget.UNKNOWN,
        error_category: Optional[ErrorCategory] = ErrorCategory.UNKNOWN,
    ):
        """Return exception class for empty directory errors.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        self.message = message
        super(EmptyDirectoryError, self).__init__(
            message=self.message,
            no_personal_data_message=no_personal_data_message,
            target=target,
            error_category=error_category,
        )


class UserErrorException(MlException):
    """Exception raised when invalid or unsupported inputs are provided."""

    def __init__(
        self,
        message,
        no_personal_data_message=None,
        error_category=ErrorCategory.USER_ERROR,
        target: ErrorTarget = ErrorTarget.PIPELINE,
    ):
        """Return exception class for user errors.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data.
        :type no_personal_data_message: str
        :param target: Name of the entity that caused the exception to be thrown., defaults to ErrorTarget.UNKNOWN
        :type target: Optional[azure.ai.ml.exceptions.ErrorTarget]
        :param error_category: Error category, defaults to ErrorCategory.UNKNOWN
        :type error_category: Optional[azure.ai.ml.exceptions.ErrorCategory]
        """
        super().__init__(
            message=message,
            target=target,
            no_personal_data_message=no_personal_data_message,
            error_category=error_category,
        )


class CannotSetAttributeError(UserErrorException):
    """Exception raised when a user tries setting attributes of inputs/outputs."""

    def __init__(self, object_name: str):
        """Return exception for user attribute setting error.

        :param object_name: Name of object
        :type object_name: str
        """
        msg = "It is not allowed to set attribute of %r." % object_name
        super(CannotSetAttributeError, self).__init__(
            message=msg,
            no_personal_data_message="It is not allowed to set attribute of object.",
        )


class UnsupportedParameterKindError(UserErrorException):
    """Exception raised when a user provides an unsupported parameter type."""

    def __init__(self, func_name: str, parameter_kind: Optional[str] = None):
        """Return exception for user parameter type error.

        :param func_name: Function name
        :type func_name: str
        :param parameter_kind: Parameter type, defaults to None
        :type parameter_kind: Optional[str]
        """
        parameter_kind = parameter_kind or "*args or **kwargs"
        msg = "%r: dsl pipeline does not accept %s as parameters." % (func_name, parameter_kind)
        super(UnsupportedParameterKindError, self).__init__(message=msg, no_personal_data_message=msg)


class KeywordError(UserErrorException):
    """Super class of all type keyword error."""

    def __init__(self, message: str, no_personal_data_message: Optional[str] = None):
        """Return keyword error super class.

        :param message: Message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: Error message without any personal data, defaults to None
        :type no_personal_data_message: Optional[str]
        """
        super().__init__(message=message, no_personal_data_message=no_personal_data_message)


class UnexpectedKeywordError(KeywordError):
    """Exception raised when an unexpected keyword parameter is provided in dynamic functions."""

    def __init__(self, func_name: str, keyword: str, keywords: Optional[Iterable[str]] = None):
        """Return exception for unexpected keyword parameter in dynamic functions.

        :param func_name: Function name
        :type func_name: str
        :param keyword: Keyword parameter
        :type keyword: str
        :param keywords: List of keywords, defaults to None
        :type keywords: Optional[Iterable[str]]
        """
        message = "%s() got an unexpected keyword argument %r" % (func_name, keyword)
        message += ", valid keywords: %s." % ", ".join("%r" % key for key in keywords) if keywords else "."
        super().__init__(message=message, no_personal_data_message=message)


class UnexpectedAttributeError(KeywordError, AttributeError):
    """Exception raised when an unexpected keyword is invoked by attribute, e.g. inputs.invalid_key."""

    def __init__(self, keyword, keywords=None):
        message = "Got an unexpected attribute %r" % keyword
        message += ", valid attributes: %s." % ", ".join("%r" % key for key in keywords) if keywords else "."
        super().__init__(message=message, no_personal_data_message=message)


class MissingPositionalArgsError(KeywordError):
    """Exception raised when missing positional keyword parameter in dynamic functions."""

    def __init__(self, func_name, missing_args):
        message = "%s() missing %d required positional argument(s): %s." % (
            func_name,
            len(missing_args),
            ", ".join("%r" % key for key in missing_args) if missing_args else ".",
        )
        super().__init__(message=message, no_personal_data_message=message)


class TooManyPositionalArgsError(KeywordError):
    """Exception raised when too many positional arguments is provided in dynamic functions."""

    def __init__(self, func_name, min_number, max_number, given_number):
        message = "%s() takes %s positional argument but %d were given." % (
            func_name,
            min_number if min_number == max_number else f"{min_number} to {max_number}",
            given_number,
        )
        super().__init__(message=message, no_personal_data_message=message)


class MultipleValueError(KeywordError):
    """Exception raised when giving multiple value of a keyword parameter in dynamic functions."""

    def __init__(self, func_name, keyword):
        message = "%s() got multiple values for argument %r." % (func_name, keyword)
        super().__init__(message=message, no_personal_data_message=message)


class ParamValueNotExistsError(KeywordError):
    """Exception raised when items in non_pipeline_inputs not in keyword parameters in dynamic functions."""

    def __init__(self, func_name, keywords):
        message = "%s() got unexpected params in non_pipeline_inputs %r." % (func_name, keywords)
        super().__init__(message=message, no_personal_data_message=message)


class UnsupportedOperationError(UserErrorException):
    """Exception raised when specified operation is not supported."""

    def __init__(self, operation_name):
        message = "Operation %s is not supported." % operation_name
        super().__init__(message=message, no_personal_data_message=message)


class LocalEndpointNotFoundError(MlException):
    """Exception raised if local endpoint cannot be found."""

    def __init__(
        self,
        endpoint_name: str,
        deployment_name: Optional[str] = None,
        error_category=ErrorCategory.USER_ERROR,
    ):
        resource_name = (
            f"Local deployment ({endpoint_name} / {deployment_name})"
            if deployment_name
            else f"Local endpoint ({endpoint_name})"
        )
        err = f"{resource_name} does not exist."
        resource_type = "deployment" if deployment_name else "endpoint"
        super().__init__(
            message=err,
            error_category=error_category,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message=f"Local ({resource_type}) does not exist.",
        )


class LocalEndpointInFailedStateError(MlException):
    """Exception raised when local endpoint is in Failed state."""

    def __init__(self, endpoint_name, deployment_name=None, error_category=ErrorCategory.UNKNOWN):
        resource_name = (
            f"Local deployment ({endpoint_name} / {deployment_name})"
            if deployment_name
            else f"Local endpoint ({endpoint_name})"
        )
        err = f"{resource_name} is in failed state. Try getting logs to debug scoring script."
        resource_type = "deployment" if deployment_name else "endpoint"
        super().__init__(
            message=err,
            error_category=error_category,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message=(
                f"Local ({resource_type}) is in failed state. Try getting logs to debug scoring script."
            ),
        )


class DockerEngineNotAvailableError(MlException):
    """Exception raised when local Docker Engine is unavailable for local operation."""

    def __init__(self, error_category=ErrorCategory.UNKNOWN):
        msg = "Please make sure Docker Engine is installed and running. https://docs.docker.com/engine/install/"
        super().__init__(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.LOCAL_ENDPOINT,
            error_category=error_category,
        )


class MultipleLocalDeploymentsFoundError(MlException):
    """Exception raised when no deployment name is specified for local endpoint even though multiple deployments
    exist."""

    def __init__(self, endpoint_name: str, error_category=ErrorCategory.UNKNOWN):
        super().__init__(
            message=f"Multiple deployments found for local endpoint ({endpoint_name}), please specify deployment name.",
            no_personal_data_message="Multiple deployments found for local endpoint, please specify deployment name.",
            error_category=error_category,
            target=ErrorTarget.LOCAL_ENDPOINT,
        )


class InvalidLocalEndpointError(MlException):
    """Exception raised when local endpoint is invalid."""

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        error_category=ErrorCategory.USER_ERROR,
    ):
        super().__init__(
            message=message,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message=no_personal_data_message,
            error_category=error_category,
        )


class LocalEndpointImageBuildError(MlException):
    """Exception raised when local endpoint's Docker image build is unsuccessful."""

    def __init__(self, error: Union[str, Exception], error_category=ErrorCategory.UNKNOWN):
        err = f"Building the local endpoint image failed with error: {str(error)}"
        super().__init__(
            message=err,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Building the local endpoint image failed with error.",
            error_category=error_category,
            error=error if error is Exception else None,
        )


class CloudArtifactsNotSupportedError(MlException):
    """Exception raised when remote cloud artifacts are used with local endpoints.

    Local endpoints only support local artifacts.
    """

    def __init__(
        self,
        endpoint_name: str,
        invalid_artifact: str,
        deployment_name: Optional[str] = None,
        error_category=ErrorCategory.USER_ERROR,
    ):
        resource_name = (
            f"local deployment ({endpoint_name} / {deployment_name})"
            if deployment_name
            else f"local endpoint ({endpoint_name})"
        )
        err = (
            "Local endpoints only support local artifacts. '%s' in '%s' referenced cloud artifacts.",
            invalid_artifact,
            resource_name,
        )
        super().__init__(
            message=err,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Local endpoints only support local artifacts.",
            error_category=error_category,
        )


class RequiredLocalArtifactsNotFoundError(MlException):
    """Exception raised when local artifact is not provided for local endpoint."""

    def __init__(
        self,
        endpoint_name: str,
        required_artifact: str,
        required_artifact_type: str,
        deployment_name: Optional[str] = None,
        error_category=ErrorCategory.USER_ERROR,
    ):
        resource_name = (
            f"Local deployment ({endpoint_name} / {deployment_name})"
            if deployment_name
            else f"Local endpoint ({endpoint_name})"
        )
        err = (
            (
                "Local endpoints only support local artifacts. '%s' did not contain required local artifact '%s'"
                " of type '%s'."
            ),
            resource_name,
            required_artifact,
            required_artifact_type,
        )
        super().__init__(
            message=err,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Resource group did not contain required local artifact.",
            error_category=error_category,
        )


class JobParsingError(MlException):
    """Exception that the job data returned by MFE cannot be parsed."""

    def __init__(self, error_category, no_personal_data_message, message, *args, **kwargs):
        super(JobParsingError, self).__init__(
            message=message,
            target=ErrorTarget.JOB,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class PipelineChildJobError(MlException):
    """Exception that the pipeline child job is not supported."""

    ERROR_MESSAGE_TEMPLATE = "az ml job {command} is not supported on pipeline child job, {prompt_message}."
    PROMPT_STUDIO_UI_MESSAGE = "please go to studio UI to do related actions{url}"
    PROMPT_PARENT_MESSAGE = "please use this command on pipeline parent job"

    def __init__(self, job_id: str, command: str = "parse", prompt_studio_ui: bool = False):
        from azure.ai.ml.entities._job._studio_url_from_job_id import studio_url_from_job_id

        if prompt_studio_ui:
            url = studio_url_from_job_id(job_id)
            if url:
                url = f": {url}"
            prompt_message = self.PROMPT_STUDIO_UI_MESSAGE.format(url=url)
        else:
            prompt_message = self.PROMPT_PARENT_MESSAGE

        super(PipelineChildJobError, self).__init__(
            message=self.ERROR_MESSAGE_TEMPLATE.format(command=command, prompt_message=prompt_message),
            no_personal_data_message="Pipeline child job is not supported currently.",
            target=ErrorTarget.JOB,
            error_category=ErrorCategory.USER_ERROR,
        )
        self.job_id = job_id


## -------- VSCode Debugger Errors -------- ##


class InvalidVSCodeRequestError(MlException):
    """Exception raised when VS Code Debug is invoked with a remote endpoint.

    VSCode debug is only supported for local endpoints.
    """

    def __init__(self, error_category=ErrorCategory.USER_ERROR, msg=None):
        super().__init__(
            message=msg,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message=msg,
            error_category=error_category,
        )


class VSCodeCommandNotFound(MlException):
    """Exception raised when VSCode instance cannot be instantiated."""

    def __init__(self, output=None, error_category=ErrorCategory.USER_ERROR):
        error_msg = f" due to error: [{output}]" if output else ""
        super().__init__(
            message=(
                f"Could not start VSCode instance{error_msg}. Please make sure the VSCode command "
                "'code' is installed and accessible from PATH environment variable. "
                "See https://code.visualstudio.com/docs/editor/command-line#_common-questions.\n"
            ),
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Could not start VSCode instance.",
            error_category=error_category,
        )
