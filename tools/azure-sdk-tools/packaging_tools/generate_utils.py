import json
import logging
import os
import re

from azure_devtools.ci_tools.git_tools import get_add_diff_file_list
from pathlib import Path
from subprocess import check_call

from .swaggertosdk.autorest_tools import build_autorest_options

_LOGGER = logging.getLogger(__name__)
_SDK_FOLDER_RE = re.compile(r"^(sdk/[\w-]+)/(azure[\w-]+)/", re.ASCII)

DEFAULT_DEST_FOLDER = "./dist"


def get_package_names(sdk_folder):
    files = get_add_diff_file_list(sdk_folder)
    matches = {_SDK_FOLDER_RE.search(f) for f in files}
    package_names = {match.groups() for match in matches if match is not None}
    return package_names


def init_new_service(package_name, folder_name):
    setup = Path(folder_name, package_name, "setup.py")
    if not setup.exists():
        check_call(
            f"python -m packaging_tools --build-conf {package_name} -o {folder_name}",
            shell=True,
        )
        ci = Path(folder_name, "ci.yml")
        if not ci.exists():
            with open("ci_template.yml", "r") as file_in:
                content = file_in.readlines()
            name = package_name.replace("azure-", "").replace("mgmt-", "")
            content = [line.replace("MyService", name) for line in content]
            with open(str(ci), "w") as file_out:
                file_out.writelines(content)


def update_servicemetadata(sdk_folder, data, config, folder_name, package_name, spec_folder, input_readme):

    readme_file = str(Path(spec_folder, input_readme))
    global_conf = config["meta"]
    local_conf = config["projects"][readme_file]

    cmd = ["autorest", input_readme]
    cmd += build_autorest_options(global_conf, local_conf)

    # metadata
    metadata = {
        "autorest": global_conf["autorest_options"]["version"],
        "use": global_conf["autorest_options"]["use"],
        "commit": data["headSha"],
        "repository_url": data["repoHttpsUrl"],
        "autorest_command": " ".join(cmd),
        "readme": input_readme,
    }

    _LOGGER.info("Metadata json:\n {}".format(json.dumps(metadata, indent=2)))

    package_folder = Path(sdk_folder, folder_name, package_name).expanduser()
    if not os.path.exists(package_folder):
        _LOGGER.info(f"Package folder doesn't exist: {package_folder}")
        _LOGGER.info("Failed to save metadata.")
        return

    metadata_file_path = os.path.join(package_folder, "_meta.json")
    with open(metadata_file_path, "w") as writer:
        json.dump(metadata, writer, indent=2)
    _LOGGER.info(f"Saved metadata to {metadata_file_path}")

    # Check whether MANIFEST.in includes _meta.json
    require_meta = "include _meta.json\n"
    manifest_file = os.path.join(package_folder, "MANIFEST.in")
    if not os.path.exists(manifest_file):
        _LOGGER.info(f"MANIFEST.in doesn't exist: {manifest_file}")
        return

    includes = []
    write_flag = False
    with open(manifest_file, "r") as f:
        includes = f.readlines()
        if require_meta not in includes:
            includes = [require_meta] + includes
            write_flag = True

    if write_flag:
        with open(manifest_file, "w") as f:
            f.write("".join(includes))
