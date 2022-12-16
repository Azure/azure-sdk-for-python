# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Dict, Union

from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import FILE_PREFIX
from azure.ai.ml.entities._validation import MutableValidationResult, _ValidationResultBuilder


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
        docker: Dict = None,
        conda: Dict = None,
        os: str = None,
        name: str = None,
        version: str = None,
        python: Dict = None,
    ):
        self.docker = docker
        self.conda = conda
        self.os = os if os else "Linux"
        self.name = name
        self.version = version
        self.python = python

    @staticmethod
    def _parse_file_path(value: str) -> str:
        return value[len(FILE_PREFIX) :] if value.startswith(FILE_PREFIX) else value

    def _validate_conda_section(self, base_path: str, skip_path_validation: bool) -> MutableValidationResult:
        validation_result = _ValidationResultBuilder.success()
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

    def _validate_docker_section(self, base_path: str, skip_path_validation: bool) -> MutableValidationResult:
        validation_result = _ValidationResultBuilder.success()
        if not self.docker:
            return validation_result
        if not self.docker.get(self.BUILD) or not self.docker[self.BUILD].get(self.DOCKERFILE):
            return validation_result
        dockerfile_file = self.docker[self.BUILD][self.DOCKERFILE]
        dockerfile_file = self._parse_file_path(dockerfile_file)
        if not skip_path_validation and not (Path(base_path) / dockerfile_file).is_file():
            validation_result.append_error(
                yaml_path=f"docker.{self.BUILD}.{self.DOCKERFILE}",
                message=f"Dockerfile not exists: {dockerfile_file}",
            )
        return validation_result

    def _validate(self, base_path: str, skip_path_validation: bool = False) -> MutableValidationResult:
        validation_result = _ValidationResultBuilder.success()
        if self.os is not None and self.os not in {"Linux", "Windows"}:
            validation_result.append_error(
                yaml_path="os",
                message=f"Only support 'Linux' and 'Windows', but got {self.os!r}",
            )
        validation_result.merge_with(self._validate_conda_section(base_path, skip_path_validation))
        validation_result.merge_with(self._validate_docker_section(base_path, skip_path_validation))
        return validation_result

    def _resolve_conda_section(self, base_path: Union[Path, str]) -> None:
        if not self.conda:
            return
        if self.conda.get(self.CONDA_DEPENDENCIES_FILE):
            conda_dependencies_file = self.conda.pop(self.CONDA_DEPENDENCIES_FILE)
            self.conda[self.CONDA_DEPENDENCIES] = load_yaml(Path(base_path) / conda_dependencies_file)
            return
        if self.conda.get(self.PIP_REQUIREMENTS_FILE):
            pip_requirements_file = self.conda.pop(self.PIP_REQUIREMENTS_FILE)
            with open(Path(base_path) / pip_requirements_file) as f:
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

    def _resolve_docker_section(self, base_path: Union[Path, str]) -> None:
        if not self.docker:
            return
        if not self.docker.get(self.BUILD) or not self.docker[self.BUILD].get(self.DOCKERFILE):
            return
        dockerfile_file = self.docker[self.BUILD][self.DOCKERFILE]
        if not dockerfile_file.startswith(FILE_PREFIX):
            return
        dockerfile_file = self._parse_file_path(dockerfile_file)
        with open(Path(base_path) / dockerfile_file, "r") as f:
            self.docker[self.BUILD][self.DOCKERFILE] = f.read()
        return

    def resolve(self, base_path: Union[Path, str]) -> None:
        self._resolve_conda_section(base_path)
        self._resolve_docker_section(base_path)
