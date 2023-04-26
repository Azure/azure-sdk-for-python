# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import pytest

from azure.ai.ml._local_endpoints.vscode_debug.devcontainer_properties import (
    AppPort,
    Build,
    ContainerEnv,
    Extensions,
    ForwardPorts,
    Image,
    Mounts,
    Name,
    OverrideCommand,
    RunArgs,
    Settings,
)


@pytest.mark.unittest
class TestDevContainerProperties:
    def test_image(self):
        prop = Image("ubuntu:20.04")
        assert {"image": "ubuntu:20.04"} == prop.to_dict()

    def test_build(self):
        prop = Build(
            dockerfile_path="../Dockerfile",
            build_context="/home/user/.azureml/inferencing/endpoint/deployment/",
            args={"ARG1": "VALUE1"},
            target="image_name:1",
        )
        assert {
            "build": {
                "dockerfile": "../Dockerfile",
                "context": "/home/user/.azureml/inferencing/endpoint/deployment/",
                "args": {"ARG1": "VALUE1"},
                "target": "image_name:1",
            }
        } == prop.to_dict()

    def test_containerenv(self):
        prop = ContainerEnv(environment_variables={"VAR1": "VALUE1"})
        assert {"containerEnv": {"VAR1": "VALUE1"}} == prop.to_dict()

    def test_mounts(self):
        prop = Mounts(mounts=["source=/app-scripts,target=/usr/local/share/app-scripts,type=bind,consistency=cached"])
        assert {
            "mounts": ["source=/app-scripts,target=/usr/local/share/app-scripts,type=bind,consistency=cached"]
        } == prop.to_dict()

    def test_name(self):
        prop = Name(name="endpoint:deployment")
        assert {"name": "endpoint:deployment"} == prop.to_dict()

    def test_forward_ports(self):
        prop = ForwardPorts(port=5001)
        assert {"forwardPorts": [5001]} == prop.to_dict()

    def test_app_ports(self):
        prop = AppPort(port=5001)
        assert {"appPort": [5001]} == prop.to_dict()

    def test_run_args(self):
        prop = RunArgs(name="container_name", labels=["--label=key=value"])
        assert {"runArgs": ["--label=key=value", "--name=container_name"]} == prop.to_dict()

    def test_override_command(self):
        prop = OverrideCommand()
        assert {"overrideCommand": True} == prop.to_dict()

    def test_extensions(self):
        prop = Extensions()
        assert {"extensions": ["ms-python.python", "ms-toolsai.vscode-ai-inference"]} == prop.to_dict()

    def test_settings(self):
        prop = Settings()
        assert {
            "settings": {
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
        } == prop.to_dict()
