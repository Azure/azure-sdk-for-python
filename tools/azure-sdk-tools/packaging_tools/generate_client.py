import argparse
import logging
from pathlib import Path
from subprocess import run
import tomli

_LOGGER = logging.getLogger(__name__)


CONF_NAME = "pyproject.toml"

def check_post_process(folder: Path) -> bool:
    conf_path = folder / CONF_NAME
    if not conf_path.exists():
        return False

    with open(conf_path, "rb") as fd:
        return tomli.load(fd)["generate"]["autorest-post-process"]

def run_post_process(folder: Path) -> None:
    completed_process = run(["autorest", "--postprocess", f"--output-folder={folder}", "--perform-load=false", "--python"], cwd=folder, shell=True)

    if completed_process.returncode != 0:
        raise ValueError("Something happened during autorest post processing: " + str(completed_process))
    _LOGGER.info("Autorest post processing done")

def generate_autorest(folder: Path) -> None:

    readme_path = folder / "swagger" / "README.md"
    completed_process = run(["autorest", readme_path, "--python-sdks-folder=../../"], cwd=folder, shell=True)

    if completed_process.returncode != 0:
        raise ValueError("Something happened with autorest: " + str(completed_process))
    _LOGGER.info("Autorest done")


def generate_typespec(folder: Path) -> None:

    # Turns out, "pwsh" is the name for PowerShell 7 on Windows, that is required for those scripts
    ps_cmd = "pwsh"

    completed_process = run([ps_cmd, "../../../eng/common/scripts/TypeSpec-Project-Sync.ps1", folder], cwd=folder)
    if completed_process.returncode != 0:
        raise ValueError("Something happened with TypeSpec Synx step: " + str(completed_process))

    completed_process = run([ps_cmd, "../../../eng/common/scripts/TypeSpec-Project-Generate.ps1", folder], cwd=folder)
    if completed_process.returncode != 0:
        raise ValueError("Something happened with TypeSpec Generate step: " + str(completed_process))

    _LOGGER.info("TypeSpec done")

def generate(folder: Path = Path(".")) -> None:
    if (folder / "swagger" / "README.md").exists():
        generate_autorest(folder)
        if check_post_process(folder):
            run_post_process(folder)
    elif (folder / "tsp-location.yaml").exists():
        generate_typespec(folder)
    else:
        raise ValueError("Didn't find swagger/README.md nor tsp_location.yaml")


def generate_main() -> None:
    """Main method"""

    parser = argparse.ArgumentParser(
        description="Build SDK using Codegen.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # FIXME, we probably don't need any of that
    # parser.add_argument(
    #     "--rest-folder",
    #     "-r",
    #     dest="restapi_git_folder",
    #     default=None,
    #     help="Rest API git folder. [default: %(default)s]",
    # )
    # parser.add_argument(
    #     "--project",
    #     "-p",
    #     dest="project",
    #     action="append",
    #     help="Select a specific project. Do all by default. You can use a substring for several projects.",
    # )
    # parser.add_argument("--readme", "-m", dest="readme", help="Select a specific readme. Must be a path")
    # parser.add_argument(
    #     "--config",
    #     "-c",
    #     dest="config_path",
    #     default=CONFIG_FILE,
    #     help="The JSON configuration format path [default: %(default)s]",
    # )
    # parser.add_argument(
    #     "--autorest",
    #     dest="autorest_bin",
    #     help="Force the Autorest to be executed. Must be a executable command.",
    # )
    # parser.add_argument(
    #     "-f",
    #     "--force",
    #     dest="force",
    #     action="store_true",
    #     help="Should I force generation if SwaggerToSdk tag is not found",
    # )
    # parser.add_argument(
    #     "--sdk-folder",
    #     "-s",
    #     dest="sdk_folder",
    #     default=".",
    #     help="A Python SDK folder. [default: %(default)s]",
    # )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Verbosity in INFO mode",
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")

    args = parser.parse_args()
    main_logger = logging.getLogger()
    if args.verbose or args.debug:
        logging.basicConfig()
        main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    generate(
        # args.config_path,
        # args.sdk_folder,
        # args.project,
        # args.readme,
        # args.restapi_git_folder,
        # args.autorest_bin,
        # args.force,
    )


if __name__ == "__main__":
    generate_main()
