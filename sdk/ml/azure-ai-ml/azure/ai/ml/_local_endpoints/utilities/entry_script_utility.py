# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import tarfile
from pathlib import Path

from docker.errors import NotFound
from docker.models.containers import Container

from azure.ai.ml._local_endpoints.errors import InvalidVSCodeRequestError


class EntryScriptUtility:
    def export_container_startup_files(self, container: Container, build_directory: str):
        """Exports the /var/azureml-server/entry.py from the provided Docker
        container to a local folder.

        :param container: Container which contains the azureml-server.
        :type container: Container
        :param build_directory: local temporary folder path to place azureml-server
        :type build_directory: str
        """
        try:
            (entry_script, _) = container.get_archive("/var/azureml-server/entry.py")
        except NotFound:
            raise InvalidVSCodeRequestError(
                msg="Local endpoint VSCode debugging is only supported for images using the Azure ML HTTP Inferencing Server. See more information here: https://docs.microsoft.com/azure/machine-learning/how-to-extend-prebuilt-docker-image-inference"
            )
        entry_script_folder = Path(build_directory, ".azureml-server")
        entry_script_folder.mkdir(parents=True, exist_ok=True)
        entry_script_tar = Path(entry_script_folder, "entry.tar")
        entry_script_py = str(Path(entry_script_folder, "entry.py").resolve())
        with open(entry_script_tar, "wb") as f:
            for chunk in entry_script:
                f.write(chunk)
        with tarfile.open(entry_script_tar) as tar:
            tar.extract("entry.py", str(entry_script_folder.resolve()))
        return entry_script_py

    def update_entry_script(self, entry_script_local_path: str):
        """Edits the /var/azureml-server/entry.py at the local path so it has
        the proper debugger statements.

        :param entry_script_local_path: Path where the entry.py is on local machine.
        :type entry_script_local_path: str
        """
        file_contents = ""
        with open(entry_script_local_path, mode="r") as f:
            file_contents = f.read()
        with open(entry_script_local_path, mode="w") as f:
            f.write(
                "\nimport debugpy\nimport os\ndebugpy.connect(int(os.environ['AZUREML_DEBUG_PORT']))\ndebugpy.wait_for_client()\n\n"
                + file_contents
            )
