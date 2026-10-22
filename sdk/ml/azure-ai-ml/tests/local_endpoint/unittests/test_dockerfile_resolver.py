# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import pytest

from azure.ai.ml._local_endpoints.dockerfile_resolver import DockerfileResolver


@pytest.mark.unittest
class TestDockerfileResolver:
    def test_resolve_base_image(self):
        dockerfile = DockerfileResolver(
            dockerfile=None,
            docker_base_image="ubuntu:latest",
            docker_conda_file_name=None,
            docker_port="5001",
            docker_azureml_app_path="/var/azureml-app",
        )
        expected = '\
FROM ubuntu:latest\n\
RUN mkdir -p /var/azureml-app\n\
WORKDIR /var/azureml-app\n\
CMD ["runsvdir", "/var/runit"]'
        assert expected == str(dockerfile)

    def test_resolve_base_image_with_conda_file(self):
        dockerfile = DockerfileResolver(
            dockerfile=None,
            docker_base_image="ubuntu:latest",
            docker_conda_file_name="conda.yml",
            docker_port="5001",
            docker_azureml_app_path="/var/azureml-app",
        )
        expected = '\
FROM ubuntu:latest\n\
RUN mkdir -p /var/azureml-app\n\
WORKDIR /var/azureml-app\n\
COPY conda.yml /var/azureml-app\n\
RUN conda env create -n inf-conda-env --file conda.yml\n\
CMD ["conda", "run", "--no-capture-output", "-n", "inf-conda-env", "runsvdir", "/var/runit"]'
        assert expected == str(dockerfile)

    def test_resolve_dockerfile(self):
        dockerfile = DockerfileResolver(
            dockerfile="FROM ubuntu:latest\n",
            docker_base_image=None,
            docker_conda_file_name=None,
            docker_port="5001",
            docker_azureml_app_path="/var/azureml-app",
        )
        expected = '\
FROM ubuntu:latest\n\n\
RUN mkdir -p /var/azureml-app\n\
WORKDIR /var/azureml-app\n\
CMD ["runsvdir", "/var/runit"]'
        assert expected == str(dockerfile)

    def test_resolve_dockerfile_with_conda_file(self):
        dockerfile = DockerfileResolver(
            dockerfile="FROM ubuntu:latest\n",
            docker_base_image=None,
            docker_conda_file_name="conda.yml",
            docker_port="5001",
            docker_azureml_app_path="/var/azureml-app",
        )
        expected = '\
FROM ubuntu:latest\n\n\
RUN mkdir -p /var/azureml-app\n\
WORKDIR /var/azureml-app\n\
COPY conda.yml /var/azureml-app\n\
RUN conda env create -n inf-conda-env --file conda.yml\n\
CMD ["conda", "run", "--no-capture-output", "-n", "inf-conda-env", "runsvdir", "/var/runit"]'
        assert expected == str(dockerfile)
