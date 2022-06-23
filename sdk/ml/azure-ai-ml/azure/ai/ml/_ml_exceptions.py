# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.core.exceptions import AzureError


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
    DATASET = "Dataset"
    ENVIRONMENT = "Environment"
    JOB = "Job"
    COMMAND_JOB = "CommandJob"
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
    UNKNOWN = "Unknown"


class MlException(AzureError):
    """
    The base class for all exceptions raised in AzureML SDK code base. If there is a need to define a custom exception type,
    that custom exception type should extend from this class.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param  no_personal_data_message: The error message without any personal data. This will be pushed to telemetry logs.
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
        **kwargs
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
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(DeploymentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class ComponentException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(ComponentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class DataException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(DataException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class DatastoreException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(DatastoreException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class JobException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(JobException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class ModelException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(ModelException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class AssetException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(AssetException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class ValidationException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(ValidationException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class AssetPathException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(AssetPathException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )


class ImportException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs
    ):
        super(ImportException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs
        )
