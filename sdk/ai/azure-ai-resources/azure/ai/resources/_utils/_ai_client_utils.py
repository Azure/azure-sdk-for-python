# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
from itertools import product
from pathlib import Path
from typing import Optional, Dict, Union

from azure.ai.ml._file_utils.file_utils import traverse_up_path_and_find_file
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

def find_config_file_path(
    path: Optional[Union[os.PathLike, str]] = None,
    file_name: Optional[str] = None,
) -> str:
    path = Path(".") if path is None else Path(path)

    if path.is_file():
        config_file_path = path
    else:
        # Based on priority
        # Look in config dirs like .azureml, aml_config or plain directory
        # with None
        directories_to_look = [".azureml", "aml_config", None]
        if file_name:
            files_to_look = [file_name]
        else:
            files_to_look = ["config.json", "project.json"]

        config_file_path = None
        for curr_dir, curr_file in product(directories_to_look, files_to_look):
            config_file_path = traverse_up_path_and_find_file(
                path=path,
                file_name=curr_file,
                directory_name=curr_dir,
                num_levels=20,
            )
            if config_file_path:
                break

        if not config_file_path:
            msg = (
                "We could not find config.json in: {} or in its parent directories. "
                "Please provide the full path to the config file or ensure that "
                "config.json exists in the parent directories."
            )
            raise ValidationException(
                message=msg.format(path),
                no_personal_data_message=msg.format("[path]"),
                target=ErrorTarget.GENERAL,
                error_category=ErrorCategory.USER_ERROR,
            )
    
    return config_file_path  # type: ignore[return-value]

def get_config_info(config_file_path: Union[str, os.PathLike]) -> Dict[str, str]:
    with open(config_file_path, encoding="utf-8-sig") as config_file:
        config = json.load(config_file)

    # Checking the keys in the config.json file to check for required parameters.
    scope = config.get("Scope")
    if not scope:
        hasMandatoryFields = "subscription_id" in config and "resource_group" in config
        hasProjectNameField = "project_name" in config or "workspace_name" in config
        if not hasMandatoryFields or not hasProjectNameField:
            msg = (
                "The config file found in: {} does not seem to contain the required "
                "parameters. Please make sure it contains your subscription_id, "
                "resource_group, and with project_name or workspace_name."
            )
            raise ValidationException(
                message=msg.format(config_file_path),
                no_personal_data_message=msg.format("[config_file_path]"),
                target=ErrorTarget.GENERAL,
                error_category=ErrorCategory.USER_ERROR,
            )
        # User provided ARM parameters take precedence over values from config.json
        subscription_id = config["subscription_id"]
        resource_group_name = config["resource_group"]
        project_name = config["project_name"] if "project_name" in config else config["workspace_name"]
    else:
        pieces = scope.split("/")
        # User provided ARM parameters take precedence over values from config.json
        subscription_id = pieces[2]
        resource_group_name = pieces[4]
        project_name = pieces[8]

    return {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group_name,
        "project_name": project_name,
    }
