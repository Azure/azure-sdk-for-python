import argparse
import logging
from pathlib import Path
import tempfile

from .swaggertosdk.SwaggerToSdkNewCLI import (
    build_project,
)
from .swaggertosdk.SwaggerToSdkCore import (
    CONFIG_FILE,
    read_config,
    solve_relative_path,
    extract_conf_from_readmes,
    get_input_paths,
    get_repo_tag_meta,
)

_LOGGER = logging.getLogger(__name__)


def generate(
    config_path, sdk_folder, project_pattern, readme, restapi_git_folder, autorest_bin=None, force_generation=False
):

    sdk_folder = Path(sdk_folder).expanduser()
    config = read_config(sdk_folder, config_path)

    global_conf = config["meta"]
    repotag = get_repo_tag_meta(global_conf)
    global_conf["autorest_options"] = solve_relative_path(global_conf.get("autorest_options", {}), sdk_folder)
    global_conf["envs"] = solve_relative_path(global_conf.get("envs", {}), sdk_folder)
    global_conf["advanced_options"] = solve_relative_path(global_conf.get("advanced_options", {}), sdk_folder)
    if restapi_git_folder:
        restapi_git_folder = Path(restapi_git_folder).expanduser()

    # Look for configuration in Readme
    if readme:
        swagger_files_in_pr = [readme]
    else:
        if not restapi_git_folder:
            raise ValueError("RestAPI folder must be set if you don't provide a readme.")
        swagger_files_in_pr = list(restapi_git_folder.glob("specification/**/readme.md"))
    _LOGGER.info(f"Readme files: {swagger_files_in_pr}")
    extract_conf_from_readmes(
        swagger_files_in_pr, restapi_git_folder, repotag, config, force_generation=force_generation
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        for project, local_conf in config.get("projects", {}).items():
            if readme:
                if str(readme) not in project:
                    _LOGGER.info("Skip project %s (readme was %s)", project, readme)
                    continue
            else:
                if project_pattern and not any(p in project for p in project_pattern):
                    _LOGGER.info("Skip project %s", project)
                    continue
            local_conf["autorest_options"] = solve_relative_path(local_conf.get("autorest_options", {}), sdk_folder)

            if readme and readme.startswith("http"):
                # Simplify here, do not support anything else than Readme.md
                absolute_markdown_path = readme
                _LOGGER.info(f"HTTP Markdown input: {absolute_markdown_path}")
            else:
                markdown_relative_path, optional_relative_paths = get_input_paths(global_conf, local_conf)

                _LOGGER.info(f"Markdown input: {markdown_relative_path}")
                _LOGGER.info(f"Optional inputs: {optional_relative_paths}")

                absolute_markdown_path = None
                if markdown_relative_path:
                    absolute_markdown_path = Path(restapi_git_folder or "", markdown_relative_path).resolve()
                if optional_relative_paths:
                    local_conf.setdefault("autorest_options", {})["input-file"] = [
                        Path(restapi_git_folder or "", input_path).resolve() for input_path in optional_relative_paths
                    ]

            build_project(temp_dir, project, absolute_markdown_path, sdk_folder, global_conf, local_conf, autorest_bin)
    return config


def generate_main():
    """Main method"""

    parser = argparse.ArgumentParser(
        description="Build SDK using Autorest, offline version.", formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--rest-folder",
        "-r",
        dest="restapi_git_folder",
        default=None,
        help="Rest API git folder. [default: %(default)s]",
    )
    parser.add_argument(
        "--project",
        "-p",
        dest="project",
        action="append",
        help="Select a specific project. Do all by default. You can use a substring for several projects.",
    )
    parser.add_argument("--readme", "-m", dest="readme", help="Select a specific readme. Must be a path")
    parser.add_argument(
        "--config",
        "-c",
        dest="config_path",
        default=CONFIG_FILE,
        help="The JSON configuration format path [default: %(default)s]",
    )
    parser.add_argument(
        "--autorest", dest="autorest_bin", help="Force the Autorest to be executed. Must be a executable command."
    )
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="Should I force generation if SwaggerToSdk tag is not found",
    )
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Verbosity in INFO mode")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")

    parser.add_argument(
        "--sdk-folder", "-s", dest="sdk_folder", default=".", help="A Python SDK folder. [default: %(default)s]"
    )

    args = parser.parse_args()
    main_logger = logging.getLogger()
    if args.verbose or args.debug:
        logging.basicConfig()
        main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    generate(
        args.config_path,
        args.sdk_folder,
        args.project,
        args.readme,
        args.restapi_git_folder,
        args.autorest_bin,
        args.force,
    )


if __name__ == "__main__":
    generate_main()
