# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from dataclasses import asdict, dataclass, field, replace
import logging
import os
from omegaconf.omegaconf import OmegaConf
import sys
from typing import Any, Dict, List
import warnings


log = logging.getLogger(__name__)


# Freeze single "empty list" so by-reference comparison of default values works.
_EMPTY_LIST = []


@dataclass(frozen=True)
class Configuration:
    # TODO: should this be handled via enum?
    activation_method: str = field(default="all")
    compliant_branch: str = field(default="^refs/heads/main$")
    source_branch: str = field(default="")
    component_cli_version: str = field(default="0.9.13")
    component_specification_glob: str = field(default="**/spec.yaml")
    # TODO: consider a way of supporting both this and `*.yaml` as defaults.
    configuration_file: str = field(default="aml-build-configuration.yml")
    log_format: str = field(default="%(message)s")
    # Registration in registries is surprisingly slow.
    shell_command_timeout_in_seconds: int = field(default=1000)
    number_of_cores_parallel: int = field(default=0)
    # TODO: should this be handled via enum?
    signing_mode: str = field(default="aml")
    verbose: bool = field(default=False)
    working_directory: str = field(default_factory=lambda: os.getcwd())
    workspaces: List[str] = field(
        default_factory=lambda: _EMPTY_LIST, metadata={"nargs": "*"}
    )
    makecat_directory: str = field(default=r"C:\Program Files (x86)\Windows Kits")
    makecat_default: str = field(default=r"10\bin\x64\makecat.exe")
    # allow_duplicate_versions is on path to deprecation. Please avoid using it
    allow_duplicate_versions: bool = field(default=False)
    fail_if_version_exists: bool = field(default=False)
    use_build_number: bool = field(default=False)
    all_component_version: str = field(default="")
    disable_telemetry: bool = field(default=False)
    suppress_adding_repo_pr_tags: bool = field(default=False)
    enable_component_validation: bool = field(default=False)
    fail_if_pattern_not_found_in_component_validation: bool = field(default=False)
    component_validation: dict = field(default_factory=dict)
    dependency_hints: dict = field(default_factory=dict)
    registries: List[str] = field(
        default_factory=lambda: _EMPTY_LIST, metadata={"nargs": "*"}
    )
    detect_changes_in_unzipped_folder: bool = field(default=False)
    validation_workspace: str = field(default="")


def load_configuration() -> Configuration:
    """
    Create configuration object from "implicit" command line arguments and
    environment variables.
    """
    # Strip away the first argument, which is the name of the file being
    # executed.
    args = sys.argv[1:]
    env = os.environ
    rv = load_configuration_from_args_and_env(args, dict(env))
    return rv


def load_configuration_from_args(args) -> dict:
    """
    Load a "minimal" configuration dictionary from command line arguments. This
    strips away any values which are default, so that merging with the default
    and file-based configuration objects works properly.
    """
    from argparse_dataclass import ArgumentParser

    default_config = Configuration()
    parser = ArgumentParser(Configuration)

    cli_config = parser.parse_args(args)
    # Strangely, calling `asdict` changes the object reference for the value
    # if it is an empty array.
    cli_config_vars = asdict(cli_config)

    for key in list(cli_config_vars.keys()):

        # Compare by reference so that you can override with default values like
        # the empty list: https://stackoverflow.com/a/14080980.
        if getattr(cli_config, key) is getattr(default_config, key):
            del cli_config_vars[key]

    return cli_config_vars


def load_configuration_from_args_and_env(
    args: List[str], env: Dict[str, Any]
) -> Configuration:
    """
    Load configuration file from provided command line arguments and environment
    variables.

    Priority is documented at https://aka.ms/aml/amlbuild , from lowest to
    highest:
    - default value
    - configuration file
    - environment variables
    - command line arguments (highest priority)
    """
    # Create default config
    default_config = Configuration()

    # Load config from command line
    cli_config = load_configuration_from_args(args)

    # Load config parameters specified in environment variables
    env_config = {
        key.lower(): value
        for key, value in env.items()
        if key.lower() in asdict(default_config).keys()
    }
    print(f"Load the config in the environment variables: {env_config}")

    # Merge cli config and env config
    # Priority: cli > env
    if env_config:
        print(
            "Merge the config in the environment variables with the config in the command line."
        )
        cli_config = OmegaConf.merge(env_config, cli_config)

    working_directory = (
        cli_config.get("working_directory") or default_config.working_directory  # type: ignore
    )

    cli_config_path = cli_config.get("configuration_file")  # type: ignore
    file_config = None
    if cli_config_path is not None:
        try:
            print("Loading user provided configuration file")
            file_config = OmegaConf.load(cli_config_path)
        except FileNotFoundError:
            print(
                f"***ERROR: the configuration file path provided {cli_config_path} does not exist in your working directory {working_directory}, so both preparation and registration will fail."
            )
    elif os.path.isfile(default_config.configuration_file):
        print(
            "Configuration file does not exist. Loading default configuration file aml-build-configuration.yml.",
        )
        file_config = OmegaConf.load(default_config.configuration_file)
    else:
        warnings.warn(
            "User provided/default configuration file does not exist. Using default configuration.",
            UserWarning,
        )

    if file_config is None:
        print("Configuration file is empty. Using default configuration.")
        cli_and_file_config = cli_config
    else:
        print("Overriding default configuration by configuration file.")
        cli_and_file_config = OmegaConf.merge(file_config, cli_config)

    if cli_and_file_config.get("workspaces") is None:  # type: ignore
        log.error(
            "Workspace is not configured. Please update in your configuration file."
        )

    if cli_and_file_config.get("allow_duplicate_versions") is not None:  # type: ignore
        if cli_and_file_config.get("fail_if_version_exists") is None:  # type: ignore
            cli_and_file_config.update(
                {
                    "fail_if_version_exists": not cli_and_file_config.get(
                        "allow_duplicate_versions"  # type: ignore
                    )
                }
            )
            warnings.warn(
                "We recommend against using the parameter allow_duplicate_versions. Please specify fail_if_version_exists instead.",
                UserWarning,
            )
        else:
            raise ValueError(
                "Please don't specify both allow_duplicate_versions and fail_if_version_exists. Check out https://aka.ms/aml/amlbuild for more information."
            )
        print("Please refer to https://aka.ms/aml/amlbuild for more information.")

    config = OmegaConf.merge(default_config, cli_and_file_config)
    config = Configuration(**config)  # type: ignore

    # Load the environment variable of source branch into config
    if "BUILD_SOURCEBRANCH" in env.keys():
        config = replace(config, source_branch=env["BUILD_SOURCEBRANCH"])
    else:
        warnings.warn("BUILD_SOURCEBRANCH is not in the environment variable list.")

    # Load the environment variable of build number into config, if user_build_number=True
    if config.use_build_number:
        if "BUILD_BUILDNUMBER" in env.keys():
            if config.all_component_version:
                log.warning(
                    f"The build number {env['BUILD_BUILDNUMBER']} overwrites the value of all_component_version {config.all_component_version}"
                )
            config = replace(config, all_component_version=env["BUILD_BUILDNUMBER"])
        else:
            raise ValueError(
                "BUILD_BUILDNUMBER is not in the environment variable list."
            )

    return config
