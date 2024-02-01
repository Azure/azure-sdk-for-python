# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging
from pathlib import Path
from typing import List, Optional

from azure.ai.ml.constants._common import DefaultOpenEncoding
from azure.ai.ml.constants._endpoint import LocalEndpointConstants

from .dockerfile_instructions import Cmd, Copy, From, Run, Workdir

module_logger = logging.getLogger(__name__)


class DockerfileResolver(object):
    """Represents the contents of a Dockerfile and handles writing the Dockerfile to User's system.

    :param docker_base_image: name of local endpoint
    :type docker_base_image: str
    :param docker_conda_file_name: name of conda file to copy into docker image
    :type docker_conda_file_name: str
    :param docker_port: port to expose in docker image
    :type docker_port: str
    :param docker_azureml_app_path: path in docker image to user's azureml app
    :type docker_azureml_app_path: (str, optional)
    """

    def __init__(
        self,
        docker_base_image: str,
        dockerfile: str,
        docker_conda_file_name: Optional[str] = None,
        docker_port: Optional[str] = None,
        docker_azureml_app_path: Optional[str] = None,
        install_debugpy: bool = False,
    ):
        """Constructor of a Dockerfile object.

        :param docker_base_image: base image
        :type docker_base_image: str
        :param dockerfile: contents of dockerfile
        :type dockerfile: str
        :param docker_conda_file_name: name of local endpoint
        :type docker_conda_file_name: str
        :param docker_port: port to expose in docker image
        :type docker_port: str
        :param docker_azureml_app_path: name of local deployment
        :type docker_azureml_app_path: (str, optional)
        :return DockerfileResolver:
        """
        self._instructions: List[object] = []
        self._local_dockerfile_path: Optional[str] = None
        self._dockerfile = dockerfile
        self._docker_base_image = docker_base_image
        self._docker_conda_file_name = docker_conda_file_name
        self._docker_azureml_app_path = docker_azureml_app_path
        self._docker_port = docker_port
        self._construct(install_debugpy=install_debugpy)

    @property
    def local_path(self) -> Optional[str]:
        """Returns the local dockerfile path.

        :return: str
        """
        return self._local_dockerfile_path

    def __str__(self) -> str:
        """Override DockerfileResolver str() built-in func to return the Dockerfile contents as a string.

        :return: Dockerfile Contents
        :rtype: str
        """
        return "" if len(self._instructions) == 0 else "\n".join([str(instr) for instr in self._instructions])

    def _construct(self, install_debugpy: bool = False) -> None:
        """Internal use only.

        Constructs the Dockerfile instructions based on properties.

        :param install_debugpy: Whether to install debugpy. Defaults to False.
        :type install_debugpy: bool
        """
        self._instructions = []
        if self._docker_base_image:
            self._instructions = [From(self._docker_base_image)]
        else:
            self._instructions = [self._dockerfile]
        if self._docker_port:
            self._instructions.extend(
                [
                    Run(f"mkdir -p {self._docker_azureml_app_path}"),
                    Workdir(str(self._docker_azureml_app_path)),
                ]
            )

        if self._docker_conda_file_name and self._docker_azureml_app_path:
            self._instructions.extend(
                [
                    Copy(
                        [
                            f"{self._docker_conda_file_name}",
                        ],
                        self._docker_azureml_app_path,
                    ),
                    Run(
                        (
                            f"conda env create -n {LocalEndpointConstants.CONDA_ENV_NAME} "
                            f"--file {self._docker_conda_file_name}"
                        )
                    ),
                ]
            )
            if install_debugpy:
                self._instructions.extend(
                    [Run(f"conda run -n {LocalEndpointConstants.CONDA_ENV_NAME} pip install debugpy")]
                )
            self._instructions.extend(
                [
                    Cmd(
                        [
                            "conda",
                            "run",
                            "--no-capture-output",
                            "-n",
                            LocalEndpointConstants.CONDA_ENV_NAME,
                            "runsvdir",
                            "/var/runit",
                        ]
                    ),
                ]
            )
        else:
            if install_debugpy:
                self._instructions.extend([Run("pip install debugpy")])
            self._instructions.extend(
                [
                    Cmd(["runsvdir", "/var/runit"]),
                ]
            )

    def write_file(self, directory_path: str, file_prefix: Optional[str] = None) -> None:
        """Writes this Dockerfile to a file in provided directory and file name prefix.

        :param directory_path: absolute path of local directory to write Dockerfile.
        :type directory_path: str
        :param file_prefix: name of Dockerfile prefix
        :type file_prefix: str
        """
        file_name = f"{file_prefix}.Dockerfile" if file_prefix else "Dockerfile"
        self._local_dockerfile_path = str(Path(directory_path, file_name).resolve())
        with open(self._local_dockerfile_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
            f.write(f"{str(self)}\n")
