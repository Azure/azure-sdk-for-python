import json
import logging
import os.path
from pathlib import Path
import shutil
import subprocess

_LOGGER = logging.getLogger(__name__)


def autorest_latest_version_finder():
    autorest_bin = shutil.which("autorest")
    cmd_line = "{} --version --json".format(autorest_bin)
    return json.loads(subprocess.check_output(cmd_line.split()).decode().strip())


def autorest_swagger_to_sdk_conf(readme, output_folder, config):
    _LOGGER.info("Looking for swagger-to-sdk section in {}".format(readme))
    autorest_bin = shutil.which("autorest")
    # --input-file=foo is to workaround a bug where the command is not executed at all if no input-file is found (even if we don't care about input-file here)
    cmd_line = "{} {} --perform-load=false --swagger-to-sdk --output-artifact=configuration.json --input-file=foo --output-folder={} --version={}".format(
        autorest_bin, str(readme), str(output_folder), str(config["meta"]["autorest_options"]["version"])
    )
    execute_simple_command(cmd_line.split())
    conf_path = Path(output_folder, "configuration.json")
    with conf_path.open(encoding="utf-8") as fd:
        conf_as_json = json.load(fd)
    print(f'*** conf_as_json: {conf_as_json}')
    print(f'*** swagger-to-sdk: {conf_as_json.get("swagger-to-sdk", [])}')
    swagger_to_sdk_conf = [c for c in conf_as_json.get("swagger-to-sdk", []) if c]
    return swagger_to_sdk_conf


def autorest_bootstrap_version_finder():
    try:
        npm_bin = shutil.which("npm")
        cmd_line = ("{} --json ls autorest -g".format(npm_bin)).split()
        return json.loads(subprocess.check_output(cmd_line).decode().strip())
    except Exception:
        return {}


def merge_options(global_conf, local_conf, key, *, keep_list_order=False):
    """Merge the conf using override: local conf is prioritary over global.

    If keep_list_order is True, list are merged global+local. Might have duplicate.
    If false, duplication are removed.
    """
    global_keyed_conf = global_conf.get(key)  # Could be None
    local_keyed_conf = local_conf.get(key)  # Could be None

    if global_keyed_conf is None or local_keyed_conf is None:
        return global_keyed_conf or local_keyed_conf

    if isinstance(global_keyed_conf, list):
        if keep_list_order:
            options = list(global_keyed_conf)
            options += local_keyed_conf
            return options
        options = set(global_keyed_conf)
    else:
        options = dict(global_keyed_conf)

    options.update(local_keyed_conf)
    return options


def build_autorest_options(global_conf, local_conf):
    """Build the string of the Autorest options"""
    merged_options = merge_options(global_conf, local_conf, "autorest_options") or {}

    def value(x):
        escaped = x if " " not in x else "'" + x + "'"
        return "={}".format(escaped) if escaped else ""

    listify = lambda x: x if isinstance(x, list) else [x]

    sorted_keys = sorted(list(merged_options.keys()))  # To be honest, just to help for tests...
    return [
        "--{}{}".format(key.lower(), value(str(option)))
        for key in sorted_keys
        for option in listify(merged_options[key])
    ]


def generate_code(input_file, global_conf, local_conf, output_dir=None, autorest_bin=None):
    """Call the Autorest process with the given parameters.

    Input file can be a Path instance, a str (will be cast to Path), or a str starting with
    http (will be passed to Autorest as is).
    """
    if not autorest_bin:
        autorest_bin = shutil.which("autorest")
    if not autorest_bin:
        raise ValueError("No autorest found in PATH and no autorest path option used")

    params = [str(input_file)] if input_file else []
    if output_dir:  # For legacy. Define "output-folder" as "autorest_options" now
        params.append("--output-folder={}".format(str(output_dir) + os.path.sep))
    params += build_autorest_options(global_conf, local_conf)

    input_files = local_conf.get("autorest_options", {}).get("input-file", [])

    if not input_file and not input_files:
        raise ValueError("I don't have input files!")

    path_input_files = [pit for pit in input_files if isinstance(pit, Path)]
    if input_file and isinstance(input_file, Path):
        input_path = input_file.parent
    elif path_input_files:
        input_path = path_input_files[0].parent
    else:
        input_path = Path(".")

    cmd_line = autorest_bin.split()
    cmd_line += params
    _LOGGER.info("Autorest cmd line:\n%s", " ".join(cmd_line))

    execute_simple_command(cmd_line, cwd=str(input_path))
    # Checks that Autorest did something if output_dir is under control
    # Note that this can fail if "--output-folder" was overidden by the Readme.
    if output_dir and (not output_dir.is_dir() or next(output_dir.iterdir(), None) is None):
        raise ValueError("Autorest call ended with 0, but no files were generated")


def execute_simple_command(cmd_line, cwd=None, shell=False, env=None):
    def run_command():
        process = subprocess.Popen(
            cmd_line,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
            shell=shell,
            env=env,
            encoding="utf-8",
        )
        output_buffer = []
        for line in process.stdout:
            output_buffer.append(line.rstrip())
            _LOGGER.info(f"==[autorest]" + output_buffer[-1])
        process.wait()
        output = "\n".join(output_buffer)
        if process.returncode:
            # print necessary error info which will be displayed in swagger pr
            for i in range(-min(len(output_buffer), 7), 0):
                print(f"[Autorest] {output_buffer[i]}")
            raise subprocess.CalledProcessError(process.returncode, cmd_line, output)
        return output
    try:
        return run_command()
    except subprocess.CalledProcessError as ex:
        # rerun to ensure the log contains error info
        return run_command()
    except Exception as err:
        _LOGGER.error(err)
        raise
