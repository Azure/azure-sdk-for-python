# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import json
from pathlib import Path
from typing import Optional

from azure.ai.ml._local_endpoints.utilities.wsl_utility import get_wsl_path, in_wsl
from azure.ai.ml._local_endpoints.vscode_debug.devcontainer_properties import (
    AppPort,
    Build,
    ContainerEnv,
    Extensions,
    ForwardPorts,
    Image,
    Mounts,
    OverrideCommand,
    RunArgs,
    Settings,
)
from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException


class DevContainerResolver:
    """DevContainerResolver class represents the collection of properties of a
    devcontainer.json.

    Reference: https://code.visualstudio.com/docs/remote/devcontainerjson-reference
    """

    def __init__(
        self,
        image: str = None,
        dockerfile_path: str = "../Dockerfile",
        build_context: str = None,
        build_target: str = None,
        environment: dict = None,
        mounts: dict = None,
        labels: dict = None,
        port: int = 5001,
    ):
        """Resolves the devcontainer.json based on provided properties.

        :param image: name of local deployment
        :type image: str
        :param dockerfile_path: path to Dockerfile relative to devcontainer.json
        :type dockerfile_path: str
        :param build_context: build directory on user's local system
        :type build_context: str
        :param build_target: directory on user's local system where Dockerfile is located
        :type build_target: str
        :param environment: dictionary of docker environment variables to set in dev container
        :type environment: dict
        :param mounts: dictionary of volumes to mount to dev container
        :type mounts: dict
        :param labels: dictionary of labels to add to dev container
        :type labels: dict
        :param port: Port exposed in Docker image for AzureML service.
        :type port: int
        """
        if not (image or (build_context and dockerfile_path)):
            msg = "Must provide image or build context for devcontainer.json"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.LOCAL_ENDPOINT,
                error_category=ErrorCategory.USER_ERROR,
            )
        self._local_path: Optional[str] = None
        self._properties: Optional[dict] = {}

        self._image: str = image
        self._dockerfile_path: str = dockerfile_path
        self._build_context: str = build_context
        self._build_target: str = build_target
        self._environment: dict = environment
        self._mounts: list = self._reformat_mounts(mounts) if mounts else mounts
        self._labels: list = self._reformat_labels(labels) if labels else labels
        self._port = port
        self._construct()

    @property
    def local_path(self) -> Optional[str]:
        """Returns the local path of the devcontainer.json.

        :return: str
        """
        return self._local_path

    def _construct(self) -> None:
        """Constructs the devcontainer properties based on attributes."""
        if self._image:
            self._properties = Image(image=self._image).to_dict()
        elif self._dockerfile_path and self._build_context:
            self._properties = Build(
                dockerfile_path=self._dockerfile_path,
                build_context=self._build_context,
                target=self._build_target,
            ).to_dict()

        self._properties.update(OverrideCommand().to_dict())
        self._properties.update(Extensions().to_dict())
        self._properties.update(Settings().to_dict())

        if self._environment:
            self._properties.update(ContainerEnv(environment_variables=self._environment).to_dict())
        if self._mounts:
            self._properties.update(Mounts(mounts=self._mounts).to_dict())
        if self._labels:
            self._properties.update(RunArgs(labels=self._labels).to_dict())
        if self._port:
            self._properties.update(AppPort(port=self._port).to_dict())
            self._properties.update(ForwardPorts(port=self._port).to_dict())

    def _reformat_mounts(self, mounts: dict) -> list:
        """Reformat mounts from Docker format to DevContainer format.

        :param mounts: Dictionary with mount information for Docker container. For example,
            {
                "<unique mount key>": {
                    "<local_source>": {
                        "<mount type i.e. bind>": "<container_dest>"
                    }
                }
            }
        :type mounts: dict
        :returns dict: "mounts": ["source=${localWorkspaceFolder}/app-scripts,target=/usr/local/share/app-scripts,type=bind,consistency=cached"]
        """
        devcontainer_mounts = []
        for mount_dict in mounts.values():
            for source, dest in mount_dict.items():
                for mount_type, container_dest in dest.items():
                    devcontainer_mounts.append(f"source={source},target={container_dest},type={mount_type}")
        return devcontainer_mounts

    def _reformat_labels(self, labels: dict) -> list:
        """Reformat labels from Docker format to DevContainer format.

        :param labels: Dictionary with label information for Docker container. For example,
            {
                "key": "value",
                "key1": "value1"
            }
        :type labels: dict
        :returns dict: ["--label=key=value", "--label=key1=value1"]
        """
        devcontainer_labels = []
        for key, value in labels.items():
            devcontainer_labels.append(f"--label={key}={value}")
        return devcontainer_labels

    def write_file(self, directory_path: str) -> None:
        """Writes this devcontainer.json to provided directory.

        :param directory_path: absolute path of local directory to write devcontainer.json.
        :type directory_path: str
        """
        self._local_path = get_wsl_path(directory_path) if in_wsl() else directory_path

        file_path = self._get_devcontainer_file_path(directory_path=directory_path)
        with open(file_path, "w") as f:
            f.write(f"{json.dumps(self._properties, indent=4)}\n")

    def _get_devcontainer_file_path(self, directory_path: str) -> str:
        """Returns the path of the devcontainer in relation to provided
        directory path.

        :param directory_path: absolute path of local directory to write devcontainer.json.
        :type directory_path: str
        """
        devcontainer_path = Path(directory_path, ".devcontainer")
        devcontainer_path.mkdir(parents=True, exist_ok=True)
        file_path = str(Path(devcontainer_path, "devcontainer.json").resolve())
        return file_path
