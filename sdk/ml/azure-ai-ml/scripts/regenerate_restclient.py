import logging
import os
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


def regenerate_restclient(api_tag, verbose):
    readme_path = Path("./swagger/machinelearningservices/resource-manager/readme.md")
    restclient_path = Path("./azure/ai/ml/_restclient/")
    command_args = {"shell": system() == "Windows", "stream_stdout": verbose}

    api_tag_arg = api_tag.lower() if api_tag else None
    if not api_tag_arg or api_tag_arg == MULTI_API_TAG:
        tag_arg = f"--{MULTI_API_TAG}"
    else:
        tag_arg = f"--tag={api_tag_arg}"

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
