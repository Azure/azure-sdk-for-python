# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


## -------- General Local Endpoint Errors -------- ##


from typing import Union
from azure.ai.ml._ml_exceptions import MlException, ErrorCategory, ErrorTarget


class LocalEndpointNotFoundError(MlException):
    def __init__(self, endpoint_name: str, deployment_name: str = None, error_category=ErrorCategory.USER_ERROR):
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
            no_personal_data_message=f"Local ({resource_type}) is in failed state. Try getting logs to debug scoring script.",
        )


class DockerEngineNotAvailableError(MlException):
    def __init__(self, error_category=ErrorCategory.UNKNOWN):
        msg = "Please make sure Docker Engine is installed and running. https://docs.docker.com/engine/install/"
        super().__init__(
            message=msg, no_personal_data_message=msg, target=ErrorTarget.LOCAL_ENDPOINT, error_category=error_category
        )


class MultipleLocalDeploymentsFoundError(MlException):
    def __init__(self, endpoint_name: str, error_category=ErrorCategory.UNKNOWN):
        super().__init__(
            message=f"Multiple deployments found for local endpoint ({endpoint_name}), please specify deployment name.",
            no_personal_data_message="Multiple deployments found for local endpoint, please specify deployment name.",
            error_category=error_category,
            target=ErrorTarget.LOCAL_ENDPOINT,
        )


class InvalidLocalEndpointError(MlException):
    def __init__(self, message: str, no_personal_data_message: str, error_category=ErrorCategory.USER_ERROR):
        super().__init__(
            message=message,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message=no_personal_data_message,
            error_category=error_category,
        )


class LocalEndpointImageBuildError(MlException):
    def __init__(self, error: Union[str, Exception], error_category=ErrorCategory.UNKNOWN):
        err = f"Building the local endpoint image failed with error: {str(error)}"
        super().__init__(
            err,
            message=err,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Building the local endpoint image failed with error.",
            error_category=error_category,
            error=error if error is Exception else None,
        )


class LocalEndpointImageBuildCondaError(LocalEndpointImageBuildError):
    def __init__(self, error: Union[str, Exception], conda_file_path: str, conda_yaml_contents: str):
        err = f"Issue creating conda environment:\n{error}"
        if conda_file_path:
            err += f"\nPlease check configuration of the conda yaml source: {conda_file_path}"
        err += f"\n\nConda yaml contents:\n{conda_yaml_contents}\n"
        super().__init__(err)


class CloudArtifactsNotSupportedError(MlException):
    def __init__(
        self,
        endpoint_name: str,
        invalid_artifact: str,
        deployment_name: str = None,
        error_category=ErrorCategory.USER_ERROR,
    ):
        resource_name = (
            f"local deployment ({endpoint_name} / {deployment_name})"
            if deployment_name
            else f"local endpoint ({endpoint_name})"
        )
        err = f"Local endpoints only support local artifacts. '{invalid_artifact}' in {resource_name} referenced cloud artifacts."
        super().__init__(
            message=err,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Local endpoints only support local artifacts.",
            error_category=error_category,
        )


class RequiredLocalArtifactsNotFoundError(MlException):
    def __init__(
        self,
        endpoint_name: str,
        required_artifact: str,
        required_artifact_type: str,
        deployment_name: str = None,
        error_category=ErrorCategory.USER_ERROR,
    ):
        resource_name = (
            f"Local deployment ({endpoint_name} / {deployment_name})"
            if deployment_name
            else f"Local endpoint ({endpoint_name})"
        )
        err = f"Local endpoints only support local artifacts. {resource_name} did not contain required local artifact '{required_artifact}' of type '{required_artifact_type}'."
        super().__init__(
            message=err,
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Resource group did not contain required local artifact.",
            error_category=error_category,
        )


## -------- VSCode Debugger Errors -------- ##


class InvalidVSCodeRequestError(MlException):
    def __init__(self, error_category=ErrorCategory.USER_ERROR, msg=None):
        super().__init__(
            message=msg, target=ErrorTarget.LOCAL_ENDPOINT, no_personal_data_message=msg, error_category=error_category
        )


class VSCodeCommandNotFound(MlException):
    def __init__(self, output=None, error_category=ErrorCategory.USER_ERROR):
        error_msg = f" due to error: [{output}]" if output else ""
        super().__init__(
            message=f"Could not start VSCode instance{error_msg}. Please make sure the VSCode command 'code' is installed and accessible from PATH environment variable. See https://code.visualstudio.com/docs/editor/command-line#_common-questions.\n",
            target=ErrorTarget.LOCAL_ENDPOINT,
            no_personal_data_message="Could not start VSCode instance.",
            error_category=error_category,
        )
