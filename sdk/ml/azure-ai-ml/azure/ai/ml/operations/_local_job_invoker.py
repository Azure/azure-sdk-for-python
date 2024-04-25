# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import base64
import io
import json
import logging
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.parse
import zipfile
from pathlib import Path
from threading import Thread
from typing import Any, Dict, Optional, Tuple

from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils.utils import DockerProxy
from azure.ai.ml.constants._common import (
    AZUREML_RUN_SETUP_DIR,
    AZUREML_RUNS_DIR,
    EXECUTION_SERVICE_URL_KEY,
    INVOCATION_BASH_FILE,
    INVOCATION_BAT_FILE,
    LOCAL_JOB_FAILURE_MSG,
    DefaultOpenEncoding,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException, MlException
from azure.core.credentials import TokenCredential
from azure.core.exceptions import AzureError

docker = DockerProxy()
module_logger = logging.getLogger(__name__)


def unzip_to_temporary_file(job_definition: JobBaseData, zip_content: Any) -> Path:
    temp_dir = Path(tempfile.gettempdir(), AZUREML_RUNS_DIR, job_definition.name)
    temp_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir


def _get_creationflags_and_startupinfo_for_background_process(
    os_override: Optional[str] = None,
) -> Dict:
    args: Dict = {
        "startupinfo": None,
        "creationflags": None,
        "stdin": None,
        "stdout": None,
        "stderr": None,
        "shell": False,
    }
    os_name = os_override if os_override is not None else os.name
    if os_name == "nt":
        # Windows process creation flag to not reuse the parent console.

        # Without this, the background service is associated with the
        # starting process's console, and will block that console from
        # exiting until the background service self-terminates. Elsewhere,
        # fork just does the right thing.

        CREATE_NEW_CONSOLE = 0x00000010
        args["creationflags"] = CREATE_NEW_CONSOLE

        # Bug Item number: 2895261
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
        startupinfo.wShowWindow = subprocess.SW_HIDE  # type: ignore
        args["startupinfo"] = startupinfo

    else:
        # On MacOS, the child inherits the parent's stdio descriptors by
        # default this can block the parent's stdout/stderr from closing even
        # after the parent has exited.

        args["stdin"] = subprocess.DEVNULL
        args["stdout"] = subprocess.DEVNULL
        args["stderr"] = subprocess.STDOUT

    # filter entries with value None
    return {k: v for (k, v) in args.items() if v}


def patch_invocation_script_serialization(invocation_path: Path) -> None:
    content = invocation_path.read_text()
    searchRes = re.search(r"([\s\S]*)(--snapshots \'.*\')([\s\S]*)", content)
    if searchRes:
        patched_json = searchRes.group(2).replace('"', '\\"')
        patched_json = patched_json.replace("'", '"')
        invocation_path.write_text(searchRes.group(1) + patched_json + searchRes.group(3))


def invoke_command(project_temp_dir: Path) -> None:
    if os.name == "nt":
        invocation_script = project_temp_dir / AZUREML_RUN_SETUP_DIR / INVOCATION_BAT_FILE
        # There is a bug in Execution service on the serialized json for snapshots.
        # This is a client-side patch until the service fixes it, at which point it should
        # be a no-op
        patch_invocation_script_serialization(invocation_script)
        invoked_command = ["cmd.exe", "/c", "{0}".format(invocation_script)]
    else:
        invocation_script = project_temp_dir / AZUREML_RUN_SETUP_DIR / INVOCATION_BASH_FILE
        subprocess.check_output(["chmod", "+x", invocation_script])
        invoked_command = ["/bin/bash", "-c", "{0}".format(invocation_script)]

    env = os.environ.copy()
    env.pop("AZUREML_TARGET_TYPE", None)
    subprocess.Popen(  # pylint: disable=consider-using-with
        invoked_command,
        cwd=project_temp_dir,
        env=env,
        **_get_creationflags_and_startupinfo_for_background_process(),
    )


def get_execution_service_response(
    job_definition: JobBaseData, token: str, requests_pipeline: HttpPipeline
) -> Tuple[Dict[str, str], str]:
    """Get zip file containing local run information from Execution Service.

    MFE will send down a mock job contract, with service 'local'.
    This will have the URL for contacting Execution Service, with a URL-encoded JSON object following the '&fake='
    string (aka EXECUTION_SERVICE_URL_KEY constant below). The encoded JSON should be the body to pass from the
    client to ES. The ES response will be a zip file containing all the scripts required to invoke a local run.

    :param job_definition: Job definition data
    :type job_definition: JobBaseData
    :param token: The bearer token to use when retrieving information from Execution Service
    :type token: str
    :param requests_pipeline: The HttpPipeline to use when sending network requests
    :type requests_pipeline: HttpPipeline
    :return: Execution service response and snapshot ID
    :rtype: Tuple[Dict[str, str], str]
    """
    try:
        local = job_definition.properties.services.get("Local", None)

        (url, encodedBody) = local.endpoint.split(EXECUTION_SERVICE_URL_KEY)
        body = urllib.parse.unquote_plus(encodedBody)
        body_dict: Dict = json.loads(body)
        response = requests_pipeline.post(url, json=body_dict, headers={"Authorization": "Bearer " + token})
        response.raise_for_status()
        return (response.content, body_dict.get("SnapshotId", None))
    except AzureError as err:
        raise SystemExit(err) from err
    except Exception as e:
        msg = "Failed to read in local executable job"
        raise JobException(
            message=msg,
            target=ErrorTarget.LOCAL_JOB,
            no_personal_data_message=msg,
            error_category=ErrorCategory.SYSTEM_ERROR,
        ) from e


def is_local_run(job_definition: JobBaseData) -> bool:
    if not job_definition.properties.services:
        return False
    local = job_definition.properties.services.get("Local", None)
    return local is not None and EXECUTION_SERVICE_URL_KEY in local.endpoint


class CommonRuntimeHelper:
    COMMON_RUNTIME_BOOTSTRAPPER_INFO = "common_runtime_bootstrapper_info.json"
    COMMON_RUNTIME_JOB_SPEC = "common_runtime_job_spec.json"
    VM_BOOTSTRAPPER_FILE_NAME = "vm-bootstrapper"
    LOCAL_JOB_ENV_VARS = {
        "RUST_LOG": "1",
        "AZ_BATCHAI_CLUSTER_NAME": "fake_cluster_name",
        "AZ_BATCH_NODE_ID": "fake_id",
        "AZ_BATCH_NODE_ROOT_DIR": ".",
        "AZ_BATCH_CERTIFICATES_DIR": ".",
        "AZ_BATCH_NODE_SHARED_DIR": ".",
        "AZ_LS_CERT_THUMBPRINT": "fake_thumbprint",
    }
    DOCKER_IMAGE_WARNING_MSG = (
        "Failed to pull required Docker image. "
        "Please try removing all unused containers to free up space and then re-submit your job."
    )
    DOCKER_CLIENT_FAILURE_MSG = (
        "Failed to create Docker client. Is Docker running/installed?\n "
        "For local submissions, we need to build a Docker container to run your job in.\n Detailed message: {}"
    )
    DOCKER_DAEMON_FAILURE_MSG = (
        "Unable to communicate with Docker daemon. Is Docker running/installed?\n "
        "For local submissions, we need to build a Docker container to run your job in.\n Detailed message: {}"
    )
    DOCKER_LOGIN_FAILURE_MSG = "Login to Docker registry '{}' failed. See error message: {}"
    BOOTSTRAP_BINARY_FAILURE_MSG = (
        "Azure Common Runtime execution failed. See detailed message below for troubleshooting "
        "information or re-submit with flag --use-local-runtime to try running on your local runtime: {}"
    )

    def __init__(self, job_name: str):
        self.common_runtime_temp_folder = os.path.join(Path.home(), ".azureml-common-runtime", job_name)
        if os.path.exists(self.common_runtime_temp_folder):
            shutil.rmtree(self.common_runtime_temp_folder)
        Path(self.common_runtime_temp_folder).mkdir(parents=True)
        self.vm_bootstrapper_full_path = os.path.join(
            self.common_runtime_temp_folder,
            CommonRuntimeHelper.VM_BOOTSTRAPPER_FILE_NAME,
        )
        self.stdout = open(  # pylint: disable=consider-using-with
            os.path.join(self.common_runtime_temp_folder, "stdout"), "w+", encoding=DefaultOpenEncoding.WRITE
        )
        self.stderr = open(  # pylint: disable=consider-using-with
            os.path.join(self.common_runtime_temp_folder, "stderr"), "w+", encoding=DefaultOpenEncoding.WRITE
        )

    # Bug Item number: 2885723
    def get_docker_client(self, registry: Dict) -> "docker.DockerClient":  # type: ignore
        """Retrieves the Docker client for performing docker operations.

        :param registry: Registry information
        :type registry: Dict[str, str]
        :return: Docker client
        :rtype: docker.DockerClient
        """
        try:
            client = docker.from_env(version="auto")
        except docker.errors.DockerException as e:
            msg = self.DOCKER_CLIENT_FAILURE_MSG.format(e)
            raise MlException(message=msg, no_personal_data_message=msg) from e

        try:
            client.version()
        except Exception as e:
            msg = self.DOCKER_DAEMON_FAILURE_MSG.format(e)
            raise MlException(message=msg, no_personal_data_message=msg) from e

        if registry:
            try:
                client.login(
                    username=registry.get("username"),
                    password=registry.get("password"),
                    registry=registry.get("url"),
                )
            except Exception as e:
                raise RuntimeError(self.DOCKER_LOGIN_FAILURE_MSG.format(registry.get("url"), e)) from e
        else:
            raise RuntimeError("Registry information is missing from bootstrapper configuration.")

        return client

    # Bug Item number: 2885719
    def copy_bootstrapper_from_container(self, container: "docker.models.containers.Container") -> None:  # type: ignore
        """Copy file/folder from container to local machine.

        :param container: Docker container
        :type container: docker.models.containers.Container
        """
        path_in_container = CommonRuntimeHelper.VM_BOOTSTRAPPER_FILE_NAME
        path_in_host = self.vm_bootstrapper_full_path

        try:
            data_stream, _ = container.get_archive(path_in_container)
            tar_file = path_in_host + ".tar"
            with open(tar_file, "wb") as f:
                for chunk in data_stream:
                    f.write(chunk)
            with tarfile.open(tar_file, mode="r") as tar:
                for file_name in tar.getnames():
                    tar.extract(file_name, os.path.dirname(path_in_host))
            os.remove(tar_file)
        except docker.errors.APIError as e:
            msg = f"Copying {path_in_container} from container has failed. Detailed message: {e}"
            raise MlException(message=msg, no_personal_data_message=msg) from e  # pylint: disable=W0718

    def get_common_runtime_info_from_response(self, response: Any) -> Tuple[Dict[str, str], str]:
        """Extract common-runtime info from Execution Service response.

        :param response: Content of zip file from Execution Service containing all the
            scripts required to invoke a local run.
        :type response: Dict[str, str]
        :return: Bootstrapper info and job specification
        :rtype: Tuple[Dict[str, str], str]
        """

        with zipfile.ZipFile(io.BytesIO(response)) as zip_ref:
            bootstrapper_path = f"{AZUREML_RUN_SETUP_DIR}/{self.COMMON_RUNTIME_BOOTSTRAPPER_INFO}"
            job_spec_path = f"{AZUREML_RUN_SETUP_DIR}/{self.COMMON_RUNTIME_JOB_SPEC}"
            if not all(file_path in zip_ref.namelist() for file_path in [bootstrapper_path, job_spec_path]):
                raise RuntimeError(f"{bootstrapper_path}, {job_spec_path} are not in the execution service response.")

            with zip_ref.open(bootstrapper_path, "r") as bootstrapper_file:
                bootstrapper_json = json.loads(base64.b64decode(bootstrapper_file.read()))
            with zip_ref.open(job_spec_path, "r") as job_spec_file:
                job_spec = job_spec_file.read().decode("utf-8")

        return bootstrapper_json, job_spec

    def get_bootstrapper_binary(self, bootstrapper_info: Dict) -> None:
        """Copy bootstrapper binary from the bootstrapper image to local machine.

        :param bootstrapper_info:
        :type bootstrapper_info: Dict[str, str]
        """
        Path(self.common_runtime_temp_folder).mkdir(parents=True, exist_ok=True)

        # Pull and build the docker image
        registry: Any = bootstrapper_info.get("registry")
        docker_client = self.get_docker_client(registry)
        repo_prefix = bootstrapper_info.get("repo_prefix")
        repository = registry.get("url")
        tag = bootstrapper_info.get("tag")

        if repo_prefix:
            bootstrapper_image = f"{repository}/{repo_prefix}/boot/vm-bootstrapper/binimage/linux:{tag}"
        else:
            bootstrapper_image = f"{repository}/boot/vm-bootstrapper/binimage/linux:{tag}"

        try:
            boot_img = docker_client.images.pull(bootstrapper_image)
        except Exception as e:
            module_logger.warning(self.DOCKER_IMAGE_WARNING_MSG)
            raise e

        boot_container = docker_client.containers.create(image=boot_img, command=[""])
        self.copy_bootstrapper_from_container(boot_container)

        boot_container.stop()
        boot_container.remove()

    def execute_bootstrapper(self, bootstrapper_binary: str, job_spec: str) -> subprocess.Popen:
        """Runs vm-bootstrapper with the job specification passed to it. This will build the Docker container, create
        all necessary files and directories, and run the job locally. Command args are defined by Common Runtime team
        here: https://msdata.visualstudio.com/Vienna/_git/vienna?path=/src/azureml- job-runtime/common-
        runtime/bootstrapper/vm-bootstrapper/src/main.rs&ver
        sion=GBmaster&line=764&lineEnd=845&lineStartColumn=1&lineEndColumn=6&li neStyle=plain&_a=contents.

        :param bootstrapper_binary: Binary file path for VM bootstrapper
            (".azureml-common-runtime/<job_name>/vm-bootstrapper")
        :type bootstrapper_binary: str
        :param job_spec: JSON content of job specification
        :type job_spec: str
        :return process: Subprocess running the bootstrapper
        :rtype process: subprocess.Popen
        """
        cmd = [
            bootstrapper_binary,
            "--job-spec",
            job_spec,
            "--skip-auto-update",  # Skip the auto update
            # "Disable the standard Identity Responder and use a dummy command instead."
            "--disable-identity-responder",
            "--skip-cleanup",  # "Keep containers and volumes for debug."
        ]

        env = self.LOCAL_JOB_ENV_VARS

        process = subprocess.Popen(  # pylint: disable=consider-using-with
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.common_runtime_temp_folder,
            encoding="utf-8",
        )
        _log_subprocess(process.stdout, self.stdout)
        _log_subprocess(process.stderr, self.stderr)

        if self.check_bootstrapper_process_status(process):
            return process
        process.terminate()
        process.kill()
        raise RuntimeError(LOCAL_JOB_FAILURE_MSG.format(self.stderr.read()))

    def check_bootstrapper_process_status(self, bootstrapper_process: subprocess.Popen) -> Optional[int]:
        """Check if bootstrapper process status is non-zero.

        :param bootstrapper_process: bootstrapper process
        :type bootstrapper_process: subprocess.Popen
        :return: return_code
        :rtype: int
        """
        return_code = bootstrapper_process.poll()
        if return_code:
            self.stderr.seek(0)
            raise RuntimeError(self.BOOTSTRAP_BINARY_FAILURE_MSG.format(self.stderr.read()))
        return return_code


def start_run_if_local(
    job_definition: JobBaseData,
    credential: TokenCredential,
    ws_base_url: str,
    requests_pipeline: HttpPipeline,
) -> str:
    """Request execution bundle from ES and run job. If Linux or WSL environment, unzip and invoke job using job spec
    and bootstrapper. Otherwise, invoke command locally.

    :param job_definition: Job definition data
    :type job_definition: JobBaseData
    :param credential: Credential to use for authentication
    :type credential: TokenCredential
    :param ws_base_url: Base url to workspace
    :type ws_base_url: str
    :param requests_pipeline: The HttpPipeline to use when sending network requests
    :type requests_pipeline: HttpPipeline
    :return: snapshot ID
    :rtype: str
    """
    token = credential.get_token(ws_base_url + "/.default").token
    (zip_content, snapshot_id) = get_execution_service_response(job_definition, token, requests_pipeline)

    try:
        temp_dir = unzip_to_temporary_file(job_definition, zip_content)
        invoke_command(temp_dir)
    except Exception as e:
        msg = LOCAL_JOB_FAILURE_MSG.format(e)
        raise MlException(message=msg, no_personal_data_message=msg) from e

    return snapshot_id


def _log_subprocess(output_io: Any, file: Any, show_in_console: bool = False) -> None:
    def log_subprocess() -> None:
        for line in iter(output_io.readline, ""):
            if show_in_console:
                print(line, end="")
            file.write(line)

    thread = Thread(target=log_subprocess)
    thread.daemon = True
    thread.start()
