import contextlib
import json
import logging
import os
import re
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path
from platform import system
from urllib.request import urlopen

module_logger = logging.getLogger(__name__)

MULTI_API_TAG = "multiapi"


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def _run_command(
    commands,
    cwd=None,
    stderr=subprocess.STDOUT,
    shell=False,
    env=None,
    stream_stdout=True,
    throw_on_retcode=True,
    logger=None,
):
    if logger is None:
        logger = module_logger

    if cwd is None:
        cwd = os.getcwd()

    t0 = time.perf_counter()
    try:
        logger.debug("Executing {0} in {1}".format(commands, cwd))
        out = ""
        p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=stderr, cwd=cwd, shell=shell, env=env)
        for line in p.stdout:
            line = line.decode("utf-8").rstrip()
            if line and line.strip():
                logger.debug(line)
                if stream_stdout:
                    sys.stdout.write(line)
                    sys.stdout.write("\n")
                out += line
                out += "\n"
        p.communicate()
        retcode = p.poll()
        if throw_on_retcode:
            if retcode:
                raise subprocess.CalledProcessError(retcode, p.args, output=out, stderr=p.stderr)
        return retcode, out
    finally:
        t1 = time.perf_counter()
        logger.debug("Execution took {0}s for {1} in {2}".format(t1 - t0, commands, cwd))


def run_command(
    commands, cwd=None, stderr=subprocess.STDOUT, shell=False, stream_stdout=True, throw_on_retcode=True, logger=None
):
    _, out = _run_command(
        commands,
        cwd=cwd,
        stderr=stderr,
        shell=shell,
        stream_stdout=stream_stdout,
        throw_on_retcode=throw_on_retcode,
        logger=logger,
    )
    return out


def print_blue(message):
    print(Color.BLUE + message + Color.END)


def download_file(from_url: str, to_path: Path, with_file_name: str) -> None:
    print_blue(f"- Downloading {with_file_name} from {from_url} to {to_path}")

    try:
        response = urlopen(from_url)
    except Exception:
        sys.exit(
            f"Connection error while trying to download file from {from_url}. Please try running the script again."
        )
    with open(f"{to_path}/{with_file_name}", "w") as f:
        f.write(response.read().decode("utf-8"))


def snake_case_to_camel_case(snake_case: str) -> str:
    return "".join(word[0].upper() + word[1:] if len(word) > 1 else word.capitalize() for word in snake_case.split("/"))


@contextlib.contextmanager
def insert_operation_id_in_swagger(swagger_path: str) -> None:
    """For some unknown reason, it will fail to generate the restclient for content-service and saying that there are
    duplicate operations although no operation id is specified. This function will insert distinct operation id for
    those operations that do not have one.

    Reference:
    https://stackoverflow.com/questions/69279224/autorest-error-duplicate-operation-detected-this-is-most-likely-due-to-2-ope

    Origin path:
    "/content/{apiVersion}/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/
    Microsoft.MachineLearningServices/workspaces/{workspaceName}/{originEntityName}/{originActionName}"

    Sample 1:
    originEntityName: snapshots
    originActionName: {snapshotId}/metadataWithCredentials
    method: get
    operationId = Snapshot_GetMetadataWithCredentials

    Sample 2:
    originEntityName: endpoints
    originActionName: {endpointName}/versions/{version}/listKeys
    method: get
    operationId = Endpoint_ListKeysByNameAndVersion
    """
    with open(swagger_path, "r") as f:
        origin_swagger_content = f.read()
        swagger_obj = json.loads(origin_swagger_content)

    for request_url, method_dict in swagger_obj["paths"].items():
        for method, operation_dict in method_dict.items():
            if "operationId" in operation_dict:
                continue

            m = re.match(r".*/workspaces/\{workspaceName}/([^/]+)/(.*)", request_url)
            if not m:
                continue
            entity_name, action_name = m.groups()
            # simple stemming
            if entity_name.endswith("s"):
                entity_name = entity_name[:-1]

            action_name = action_name.replace("{" + entity_name + "Id}", "")
            if "{name}/versions/{version}" in action_name:
                action_name = action_name.replace("{name}/versions/{version}", "")
                action_name += "ByNameAndVersion"

            with_action = False
            for action in ["get", "delete", "list", "createOrUpdate", "update", "create"]:
                if action_name.startswith(action):
                    action_name = action_name.replace(action, action + "/", 1)
                    with_action = True
                    break
                if action_name.endswith(action):
                    action_name = action_name.replace(action, "/" + action, 1)
                    with_action = True
                    break

            if not with_action:
                if method == "put":
                    action_prefix = "createOrUpdate"
                elif method == "post":
                    action_prefix = "create"
                else:
                    action_prefix = method
                action_name = f"{action_prefix}/{action_name}"

            operation_dict["operationId"] = (
                f"{snake_case_to_camel_case(entity_name)}_" f"{snake_case_to_camel_case(action_name)}"
            )

            print(f"Inserting operation id {operation_dict['operationId']} for {request_url} {method}")

    with open(swagger_path, "w") as f:
        json.dump(swagger_obj, f, indent=2)

    yield

    with open(swagger_path, "w") as f:
        f.write(origin_swagger_content)


def regenerate_restclient(api_tag, verbose):
    readme_path = Path("./swagger/machinelearningservices/resource-manager/readme.md")
    restclient_path = Path("./azure/ai/ml/_restclient/")
    command_args = {"shell": system() == "Windows", "stream_stdout": verbose}

    api_tag_arg = api_tag.lower() if api_tag else None
    if not api_tag_arg or api_tag_arg == MULTI_API_TAG:
        tag_arg = f"--{MULTI_API_TAG}"
    else:
        tag_arg = f"--tag={api_tag_arg}"

    with insert_operation_id_in_swagger(
        "./swagger/machinelearningservices/resource-manager/Microsoft.MachineLearn"
        "ingServices/stable/content-service/swagger.json"
    ):
        commands = [
            "autorest",
            "--python",
            "--track2",
            "--version=3.6.2",
            "--use=@autorest/python@5.12.6",
            f"--python-sdks-folder={restclient_path.absolute()}",
            "--package-version=0.1.0",
            tag_arg,
            str(readme_path.absolute()),
            "--modelerfour.lenient-model-deduplication",
            '--title="Azure Machine Learning Workspaces"',
        ]
        print_blue(f"- Running autorest command: {' '.join(commands)}")
        run_command(
            commands,
            throw_on_retcode=True,
            **command_args,
        )


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "-a",
        "--api-tag",
        required=False,
        help="""Specifies which API to generate using autorest. If not supplied, all APIs are targeted.
            Must match the name of a tag in the sdk/ml/azure-ai-ml/swagger/machinelearningservices/resource-manager/readme.md file.""",
    )
    parser.add_argument("-v", "--verbose", action="store_true", required=False, help="turn on verbose output")

    args = parser.parse_args()

    regenerate_restclient(args.api_tag, args.verbose)
