# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union

from ..._utils.utils import load_yaml
from ...constants._common import FILE_PREFIX, DefaultOpenEncoding
from ...entities._validation import MutableValidationResult, ValidationResultBuilder


class InternalEnvironment:
    # conda section
    CONDA_DEPENDENCIES = "conda_dependencies"
    CONDA_DEPENDENCIES_FILE = "conda_dependencies_file"
    PIP_REQUIREMENTS_FILE = "pip_requirements_file"
    DEFAULT_PYTHON_VERSION = "3.8.5"
    # docker section
    BUILD = "build"
    DOCKERFILE = "dockerfile"

    def __init__(
        self,
        docker: Optional[Dict] = None,
        conda: Optional[Dict] = None,
        os: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        python: Optional[Dict] = None,
    ):
        self.docker = docker
        self.conda = conda
        self.os = os if os else "Linux"
        self.name = name
        self.version = version
        self.python = python
        self._docker_file_resolved = False

    @staticmethod
    def _parse_file_path(value: str) -> str:
        return value[len(FILE_PREFIX) :] if value.startswith(FILE_PREFIX) else value

    def _validate_conda_section(
        self, base_path: Union[str, PathLike], skip_path_validation: bool
    ) -> MutableValidationResult:
        validation_result = ValidationResultBuilder.success()
        if not self.conda:
            return validation_result
        dependencies_field_names = {self.CONDA_DEPENDENCIES, self.CONDA_DEPENDENCIES_FILE, self.PIP_REQUIREMENTS_FILE}
        if len(set(self.conda) & dependencies_field_names) > 1:
            validation_result.append_warning(
                yaml_path="conda",
                message="Duplicated declaration of dependencies, will honor in the order "
                "conda_dependencies, conda_dependencies_file and pip_requirements_file.",
            )
        if self.conda.get(self.CONDA_DEPENDENCIES_FILE):
            conda_dependencies_file = self.conda[self.CONDA_DEPENDENCIES_FILE]
            if not skip_path_validation and not (Path(base_path) / conda_dependencies_file).is_file():
                validation_result.append_error(
                    yaml_path=f"conda.{self.CONDA_DEPENDENCIES_FILE}",
                    message=f"Cannot find conda dependencies file: {conda_dependencies_file!r}",
                )
        if self.conda.get(self.PIP_REQUIREMENTS_FILE):
            pip_requirements_file = self.conda[self.PIP_REQUIREMENTS_FILE]
            if not skip_path_validation and not (Path(base_path) / pip_requirements_file).is_file():
                validation_result.append_error(
                    yaml_path=f"conda.{self.PIP_REQUIREMENTS_FILE}",
                    message=f"Cannot find pip requirements file: {pip_requirements_file!r}",
                )
        return validation_result

    def _validate_docker_section(
        self, base_path: Union[str, PathLike], skip_path_validation: bool
    ) -> MutableValidationResult:
        validation_result = ValidationResultBuilder.success()
        if not self.docker:
            return validation_result
        if not self.docker.get(self.BUILD) or not self.docker[self.BUILD].get(self.DOCKERFILE):
            return validation_result
        dockerfile_file = self.docker[self.BUILD][self.DOCKERFILE]
        dockerfile_file = self._parse_file_path(dockerfile_file)
        if (
            not self._docker_file_resolved
            and not skip_path_validation
            and not (Path(base_path) / dockerfile_file).is_file()
        ):
            validation_result.append_error(
                yaml_path=f"docker.{self.BUILD}.{self.DOCKERFILE}",
                message=f"Dockerfile not exists: {dockerfile_file}",
            )
        return validation_result

    def validate(self, base_path: Union[str, PathLike], skip_path_validation: bool = False) -> MutableValidationResult:
        """Validate the environment section.

        This is a public method but won't be exposed to user given InternalEnvironment is an internal class.

        :param base_path: The base path
        :type base_path: Union[str, PathLike]
        :param skip_path_validation: Whether to skip path validation. Defaults to False
        :type skip_path_validation: bool
        :return: The validation result
        :rtype: MutableValidationResult
        """
        validation_result = ValidationResultBuilder.success()
        if self.os is not None and self.os not in {"Linux", "Windows", "linux", "windows"}:
            validation_result.append_error(
                yaml_path="os",
                message=f"Only support 'Linux' and 'Windows', but got {self.os!r}",
            )
        validation_result.merge_with(self._validate_conda_section(base_path, skip_path_validation))
        validation_result.merge_with(self._validate_docker_section(base_path, skip_path_validation))
        return validation_result

    def _resolve_conda_section(self, base_path: Union[str, PathLike]) -> None:
        if not self.conda:
            return
        if self.conda.get(self.CONDA_DEPENDENCIES_FILE):
            conda_dependencies_file = self.conda.pop(self.CONDA_DEPENDENCIES_FILE)
            self.conda[self.CONDA_DEPENDENCIES] = load_yaml(Path(base_path) / conda_dependencies_file)
            return
        if self.conda.get(self.PIP_REQUIREMENTS_FILE):
            pip_requirements_file = self.conda.pop(self.PIP_REQUIREMENTS_FILE)
            with open(Path(base_path) / pip_requirements_file, encoding=DefaultOpenEncoding.READ) as f:
                pip_requirements = f.read().splitlines()
                self.conda = {
                    self.CONDA_DEPENDENCIES: {
                        "name": "project_environment",
                        "dependencies": [
                            f"python={self.DEFAULT_PYTHON_VERSION}",
                            {
                                "pip": pip_requirements,
                            },
                        ],
                    }
                }
            return

    def _resolve_docker_section(self, base_path: Union[str, PathLike]) -> None:
        if not self.docker:
            return
        if not self.docker.get(self.BUILD) or not self.docker[self.BUILD].get(self.DOCKERFILE):
            return
        dockerfile_file = self.docker[self.BUILD][self.DOCKERFILE]
        if not dockerfile_file.startswith(FILE_PREFIX):
            return
        dockerfile_file = self._parse_file_path(dockerfile_file)
        with open(Path(base_path) / dockerfile_file, "r", encoding=DefaultOpenEncoding.READ) as f:
            self.docker[self.BUILD][self.DOCKERFILE] = f.read()
            self._docker_file_resolved = True
        return

    def resolve(self, base_path: Union[str, PathLike]) -> None:
        self._resolve_conda_section(base_path)
        self._resolve_docker_section(base_path)
