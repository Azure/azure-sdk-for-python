# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os


def resolve_data_file_path(script_file: str, env_var_name: str, default_filename: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(script_file))
    value = os.environ.get(env_var_name)
    if value:
        if os.path.isabs(value):
            return value
        if os.path.dirname(value):
            return os.path.abspath(os.path.join(script_dir, value))
        return os.path.abspath(os.path.join(script_dir, "data", value))
    return os.path.abspath(os.path.join(script_dir, "data", default_filename))
