# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Optional
from azure.ai.ml._restclient.v2021_10_01.models import JobBaseData
from azure.identity import ChainedTokenCredential
import requests
import json
import urllib.parse
from pathlib import Path
import tempfile
import zipfile
import os
import subprocess
import re

from azure.ai.ml._ml_exceptions import JobException, ErrorTarget


def get_zip_file(job_definition: JobBaseData, token: str) -> (Any, Optional[str]):
    """MFE will send down a mock job contract, with a service 'local'.
    This will be the url for execution service, with a url encoded json object following the '&fake='
    string. The encoded json should be the body to pass from the client to ES. The ES response
    will be a zip file containing all the scripts required to invoke a local run.
    """
    try:
        local = job_definition.properties.services.get("Local", None)

        (url, encodedBody) = local.endpoint.split("&fake=")
        body = urllib.parse.unquote_plus(encodedBody)
        body = json.loads(body)
        response = requests.post(url=url, json=body, headers={"Authorization": "Bearer " + token})
        response.raise_for_status()
        return (response.content, body.get("SnapshotId", None))
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except Exception:
        msg = "Failed to read in local executable job"
        raise JobException(message=msg, target=ErrorTarget.LOCAL_JOB, no_personal_data_message=msg)


def unzip_to_temporary_file(job_definition: JobBaseData, zip_content: bytes) -> Path:
    temp_dir = Path(tempfile.gettempdir(), "azureml_runs", job_definition.name)
    temp_dir.mkdir(parents=True, exist_ok=True)
    zip_path = temp_dir / "invocation.zip"
    with zip_path.open(mode="wb") as file:
        file.write(zip_content)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    zip_path.unlink()
    return temp_dir


def _get_creationflags_and_startupinfo_for_background_process(os_override: Optional[str] = None) -> None:
    args = {"startupinfo": None, "creationflags": None, "stdin": None, "stdout": None, "stderr": None, "shell": False}
    os_name = os_override if os_override is not None else os.name
    if os_name == "nt":
        """Windows process creation flag to not reuse the parent console.
        Without this, the background service is associated with the
        starting process's console, and will block that console from
        exiting until the background service self-terminates.
        Elsewhere, fork just does the right thing.
        """
        CREATE_NEW_CONSOLE = 0x00000010
        args["creationflags"] = CREATE_NEW_CONSOLE

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        args["startupinfo"] = startupinfo

    else:
        """On MacOS, the child inherits the parent's stdio descriptors by default
        this can block the parent's stdout/stderr from closing even after the parent has exited
        """
        args["stdin"] = subprocess.DEVNULL
        args["stdout"] = subprocess.DEVNULL
        args["stderr"] = subprocess.STDOUT

    # filter entries with value None
    return {arg_name: args[arg_name] for arg_name in args if args[arg_name]}


def patch_invocation_script_serialization(invocation_path: Path) -> None:
    content = invocation_path.read_text()
    searchRes = re.search(r"([\s\S]*)(--snapshots \'.*\')([\s\S]*)", content)
    if searchRes:
        patched_json = searchRes.group(2).replace('"', '\\"')
        patched_json = patched_json.replace("'", '"')
        invocation_path.write_text(searchRes.group(1) + patched_json + searchRes.group(3))


def invoke_command(project_temp_dir: Path) -> None:
    setup_dir_name = "azureml-setup"
    if os.name == "nt":
        invocation_script = project_temp_dir / setup_dir_name / "Invocation.bat"
        # There is a bug in Execution service on the serialized json for snapshots.
        # This is a client-side patch until the service fixes it, at which point it should
        # be a no-op
        patch_invocation_script_serialization(invocation_script)
        invoked_command = ["cmd.exe", "/c", "{0}".format(invocation_script)]
    else:
        invocation_script = project_temp_dir / setup_dir_name / "Invocation.sh"
        subprocess.check_output(["chmod", "+x", invocation_script])
        invoked_command = ["/bin/bash", "-c", "{0}".format(invocation_script)]

    env = os.environ.copy()
    env.pop("AZUREML_TARGET_TYPE", None)
    subprocess.Popen(
        invoked_command, cwd=project_temp_dir, env=env, **_get_creationflags_and_startupinfo_for_background_process()
    )


def is_local_run(job_definition: JobBaseData) -> bool:
    local = job_definition.properties.services.get("Local", None)
    return local is not None and "&fake=" in local.endpoint


def start_run_if_local(job_definition: JobBaseData, credential: ChainedTokenCredential, ws_base_url: str) -> str:
    """Request execution bundle from ES, unzip and invoke run. Return the snapshot ID to set property on update."""
    token = credential.get_token(ws_base_url + "/.default").token
    (zip_content, snapshot_id) = get_zip_file(job_definition, token)
    try:
        temp_dir = unzip_to_temporary_file(job_definition, zip_content)
        invoke_command(temp_dir)
        return snapshot_id
    except Exception:
        msg = "Failed to start local executable job"
        raise JobException(message=msg, target=ErrorTarget.LOCAL_JOB, no_personal_data_message=msg)
