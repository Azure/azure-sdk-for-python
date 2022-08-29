# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging
from pathlib import Path

from azure.ai.ml.constants import LocalEndpointConstants

module_logger = logging.getLogger(__name__)


class AzureMlImageContext(object):
    """Entity holding context for building the Azure ML specific image.

    :attribute docker_azureml_app_path: the name of the online endpoint
    :type endpoint_name: str
    :param deployment_name: the name of the deployment under online endpoint
    :type deployment_name: str
    :param yaml_code_directory_path: Local directory of user code files.
        Originates in endpoint yaml configuration and is parsed by Endpoint schema.
        Should be absolute path.
    :type yaml_code_directory_path: str
    :param yaml_code_scoring_script_path: File name of scoring script from endpoint yaml configuration.
    :type yaml_code_scoring_script_path: str
    :param yaml_model_file_path: Path of model file from endpoint yaml configuration and parsed by Endpoint schema.
        Should be absolute path.
    :type yaml_model_file_path: str
    """

    def __init__(
        self,
        endpoint_name: str,
        deployment_name: str,
        yaml_code_directory_path: str,
        yaml_code_scoring_script_file_name: str,
        model_directory_path: str,
        model_mount_path: str = "",
    ):
        """Constructor for AzureMlImageContext.

        :param endpoint_name: the name of the online endpoint
        :type endpoint_name: str
        :param deployment_name: the name of the deployment under online endpoint
        :type deployment_name: str
        :param yaml_code_directory_path: Local directory of user code files.
            Originates in endpoint yaml configuration and is parsed by Endpoint schema.
            Should be absolute path.
        :type yaml_code_directory_path: str
        :param yaml_code_scoring_script_path: File name of scoring script from endpoint yaml configuration.
        :type yaml_code_scoring_script_path: str
        :param model_directory_path: Path of model directory to be mounted. Should be absolute path.
        :type model_directory_path: str
        :return: AzureMlImageContext
        """
        self._docker_azureml_app_path = LocalEndpointConstants.AZUREML_APP_PATH

        local_model_mount_path = str(model_directory_path)
        docker_azureml_model_dir = f"{self.docker_azureml_app_path}azureml-models/{model_mount_path}"
        self._volumes = {
            f"{local_model_mount_path}:{docker_azureml_model_dir}:z": {
                local_model_mount_path: {"bind": docker_azureml_model_dir}
            },
        }
        self._environment = {
            LocalEndpointConstants.ENVVAR_KEY_AZUREML_MODEL_DIR: docker_azureml_model_dir,  # ie. /var/azureml-app/azureml-models/
            LocalEndpointConstants.ENVVAR_KEY_AZUREML_INFERENCE_PYTHON_PATH: LocalEndpointConstants.CONDA_ENV_BIN_PATH,
        }

        if yaml_code_directory_path:
            local_code_mount_path = str(yaml_code_directory_path)
            docker_code_folder_name = Path(yaml_code_directory_path).name
            docker_code_mount_path = f"{self.docker_azureml_app_path}{docker_code_folder_name}/"
            self._volumes.update(
                {
                    f"{local_code_mount_path}:{docker_code_mount_path}": {
                        local_code_mount_path: {"bind": docker_code_mount_path}
                    }
                }
            )
            self._environment[
                LocalEndpointConstants.ENVVAR_KEY_AML_APP_ROOT
            ] = docker_code_mount_path  # ie. /var/azureml-app/onlinescoring
            self._environment[
                LocalEndpointConstants.ENVVAR_KEY_AZUREML_ENTRY_SCRIPT
            ] = yaml_code_scoring_script_file_name  # ie. score.py

        self.ports = {"5001/tcp": 5001}

    @property
    def docker_azureml_app_path(self) -> str:
        """Returns the app path inside the local endpoint container.

        :return: str
        """
        return self._docker_azureml_app_path

    @property
    def docker_conda_file_name(self) -> str:
        """Returns the name of the conda file to copy into docker image.

        :return: str
        """
        return self._docker_conda_file_name

    @property
    def volumes(self) -> dict:
        """Returns the volumes to mount when running the Azure ML Image
        locally.

        :return: dict
        """
        return self._volumes

    @property
    def environment(self) -> dict:
        """Returns the environment variables to set when running the Azure ML
        Image locally.

        :return: dict
        """
        return self._environment
