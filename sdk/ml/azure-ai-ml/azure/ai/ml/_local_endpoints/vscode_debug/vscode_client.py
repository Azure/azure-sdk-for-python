# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import binascii
import re
from azure.ai.ml._local_endpoints.vscode_debug.devcontainer_resolver import DevContainerResolver
from azure.ai.ml._local_endpoints.utilities.entry_script_utility import EntryScriptUtility
from azure.ai.ml._local_endpoints.utilities.commandline_utility import run_cli_command
from azure.ai.ml._local_endpoints.errors import VSCodeCommandNotFound


class VSCodeClient(object):
    def __init__(self, entryscript_utility: EntryScriptUtility = None):
        self._entryscript_utility = entryscript_utility if entryscript_utility else EntryScriptUtility()

    def create_dev_container_json(
        self,
        azureml_container,
        endpoint_name: str,
        deployment_name: str,
        build_directory: str,
        image_name: str,
        environment: dict,
        volumes: list,
        labels: dict,
    ):
        entry_script_local_path = self._entryscript_utility.export_container_startup_files(
            azureml_container, build_directory
        )
        self._entryscript_utility.update_entry_script(entry_script_local_path=entry_script_local_path)
        devcontainer_startup_volumes = {
            f"{entry_script_local_path}:/var/azureml-server/entry.py": {
                entry_script_local_path: {"bind": "/var/azureml-server/entry.py"}
            }
        }
        volumes.update(devcontainer_startup_volumes)
        devcontainer = DevContainerResolver(
            image=image_name,
            environment=environment,
            mounts=volumes,
            labels=labels,
        )
        devcontainer.write_file(build_directory)
        return devcontainer.local_path

    def invoke_dev_container(self, devcontainer_path: str, app_path: str):
        hex_encoded_devcontainer_path = self._encode_hex(devcontainer_path)
        command = ["code", "--folder-uri", f"vscode-remote://dev-container+{hex_encoded_devcontainer_path}{app_path}"]
        try:
            run_cli_command(command)
        except Exception as e:
            output = e.output.decode(encoding="UTF-8")
            raise VSCodeCommandNotFound(output)

    def _encode_hex(self, path: str):
        vscode_path = re.sub("\\s+", "", path)
        return binascii.hexlify(vscode_path.encode()).decode("ascii")
