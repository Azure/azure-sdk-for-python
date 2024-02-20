# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import pytest

from azure.ai.ml._local_endpoints.vscode_debug.devcontainer_resolver import DevContainerResolver


@pytest.fixture
def environment():
    yield {"KEY": "VALUE"}


@pytest.fixture
def input_labels():
    yield {"KEY": "VALUE"}


@pytest.fixture
def output_labels():
    yield ["--label=KEY=VALUE"]


@pytest.fixture
def input_mounts():
    yield {
        "/home/app-scripts:/usr/local/share/app-scripts": {
            "/home/app-scripts": {"bind": "/usr/local/share/app-scripts"}
        }
    }


@pytest.fixture
def output_mounts():
    yield ["source=/home/app-scripts,target=/usr/local/share/app-scripts,type=bind"]


@pytest.fixture
def overrideCommand():
    yield True


@pytest.fixture
def extensions():
    yield ["ms-python.python", "ms-toolsai.vscode-ai-inference"]


@pytest.fixture
def settings():
    yield {
        "launch": {
            "configurations": [
                {
                    "name": "Azure ML: Debug Local Endpoint",
                    "type": "python",
                    "request": "attach",
                    "listen": {
                        "host": "127.0.0.1",
                        "port": 0,
                    },
                    "azuremlext": "local_inference_debug",
                }
            ]
        },
        "python.defaultInterpreterPath": "/opt/miniconda/envs/inf-conda-env/bin/python",
    }


@pytest.mark.unittest
class TestDevContainerResolver:
    def test_resolve_devcontainer_json_image(
        self,
        environment,
        overrideCommand,
        settings,
        extensions,
        input_mounts,
        output_mounts,
        input_labels,
        output_labels,
    ):
        devcontainer = DevContainerResolver(
            image="ubuntu:20.04",
            dockerfile_path="../Dockerfile",
            environment=environment,
            mounts=input_mounts,
            labels=input_labels,
        )
        assert devcontainer._properties.get("image") == "ubuntu:20.04"
        assert devcontainer._properties.get("build") is None
        assert devcontainer._properties.get("containerEnv") == environment
        assert devcontainer._properties.get("mounts") == output_mounts
        assert devcontainer._properties.get("runArgs") == output_labels
        assert devcontainer._properties.get("overrideCommand") == overrideCommand
        assert devcontainer._properties.get("settings") == settings
        assert devcontainer._properties.get("extensions") == extensions

    def test_resolve_devcontainer_json_build(
        self,
        environment,
        overrideCommand,
        settings,
        extensions,
        input_mounts,
        output_mounts,
        input_labels,
        output_labels,
    ):
        build_context = "/home/user/.azureml/inferencing/endpoint/deployment/"
        build_target = "image_name:tag"
        devcontainer = DevContainerResolver(
            build_context=build_context,
            build_target=build_target,
            dockerfile_path="../Dockerfile",
            environment=environment,
            mounts=input_mounts,
            labels=input_labels,
        )
        assert devcontainer._properties.get("image") is None
        assert devcontainer._properties.get("build")
        assert devcontainer._properties.get("build").get("context") == build_context
        assert devcontainer._properties.get("build").get("target") == build_target
        assert devcontainer._properties.get("containerEnv") == environment
        assert devcontainer._properties.get("mounts") == output_mounts
        assert devcontainer._properties.get("runArgs") == output_labels
        assert devcontainer._properties.get("overrideCommand") == overrideCommand
        assert devcontainer._properties.get("settings") == settings
        assert devcontainer._properties.get("extensions") == extensions
