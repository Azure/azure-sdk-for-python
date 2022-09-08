# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import pytest

from azure.ai.ml._local_endpoints.dockerfile_instructions import Cmd, Copy, Env, Expose, From, Run, Workdir


@pytest.mark.unittest
class TestDockerfileInstructions:
    def test_cmd(self):
        instruction = Cmd(["echo", "Hello, World"])
        assert 'CMD ["echo", "Hello, World"]' == str(instruction)

    def test_copy(self):
        instruction = Copy(src=["/src/folder1", "/src/folder2"], dest="/dest/folder")
        assert "COPY /src/folder1 /src/folder2 /dest/folder" == str(instruction)

    def test_env(self):
        instruction = Env(key="key", value="value")
        assert "ENV key=value" == str(instruction)

    def test_expose(self):
        instruction = Expose(port=5001)
        assert "EXPOSE 5001" == str(instruction)

    def test_from_no_stage(self):
        instruction = From(base_image_name="ubuntu:latest")
        assert "FROM ubuntu:latest" == str(instruction)

    def test_from_with_stage(self):
        instruction = From(base_image_name="ubuntu:latest", stage_name="inferencing")
        assert "FROM ubuntu:latest as inferencing" == str(instruction)

    def test_run(self):
        instruction = Run(command="pip install docker")
        assert "RUN pip install docker" == str(instruction)

    def test_workdir(self):
        instruction = Workdir(directory="/var/azureml-app")
        assert "WORKDIR /var/azureml-app" == str(instruction)
