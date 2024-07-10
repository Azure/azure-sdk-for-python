# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
# pylint: disable=client-accepts-api-version-keyword
import binascii
import re

from azure.ai.ml._local_endpoints.utilities.commandline_utility import run_cli_command
from azure.ai.ml._local_endpoints.vscode_debug.devcontainer_resolver import DevContainerResolver
from azure.ai.ml.exceptions import VSCodeCommandNotFound


class VSCodeClient(object):
    # pylint: disable=client-method-has-more-than-5-positional-arguments
    def create_dev_container_json(
        self,
        azureml_container,  # pylint: disable=unused-argument
        endpoint_name: str,  # pylint: disable=unused-argument
        deployment_name: str,  # pylint: disable=unused-argument
        build_directory: str,
        image_name: str,
        environment: dict,
        volumes: list,
        labels: dict,
    ) -> str:
        devcontainer = DevContainerResolver(
            image=image_name,
            environment=environment,
            mounts=volumes,  # type: ignore[arg-type]
            labels=labels,
        )
        devcontainer.write_file(build_directory)
        return str(devcontainer.local_path)

    def invoke_dev_container(self, devcontainer_path: str, app_path: str) -> None:
        hex_encoded_devcontainer_path = _encode_hex(devcontainer_path)
        command = [
            "code",
            "--folder-uri",
            f"vscode-remote://dev-container+{hex_encoded_devcontainer_path}{app_path}",
        ]
        try:
            run_cli_command(command)
        except Exception as e:
            # pylint: disable=no-member
            output = e.output.decode(encoding="UTF-8")  # type: ignore[attr-defined]
            raise VSCodeCommandNotFound(output) from e


def _encode_hex(path: str):
    vscode_path = re.sub("\\s+", "", path)  # pylint: disable=specify-parameter-names-in-call
    return binascii.hexlify(vscode_path.encode()).decode("ascii")
