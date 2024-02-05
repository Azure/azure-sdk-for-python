# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import Union


def get_root_path() -> str:
    """Gets the root directory for the drive.

    NOTE: On Windows, it returns 'C:\' or the path to the root dir for the drive.
          On Linux, it returns '/'.
    :return: Path to the root directory for the drive.
    :rtype: str
    """
    return os.path.realpath(os.sep)


def traverse_up_path_and_find_file(path, file_name, directory_name=None, num_levels=None) -> str:
    """
    Traverses up the provided path until we find the file, reach a directory
    that the user does not have permissions to, or if we reach num_levels (if set by the user).
    NOTE: num_levels=2 would mean that we search the current directory and two levels above (inclusive).
    :param path: Path to traverse up from.
    :type path: Optional[Union[PathLike, str]] = None
    :param file_name: The name of the file to look for, including the file extension.
    :type file_name: str
    :param directory_name: (optional)The name of the directory that the file should be in. ie) /aml_config/config.json
    :type directory_name: str
    :param num_levels: Number of levels to traverse up the path for (inclusive).
    :type num_levels: int
    :return: Path to the file that we found, or an empty string if we couldn't find the file.
    :rtype: str
    """
    current_path: Union[Path, str] = Path(path)
    if directory_name is not None:
        file_name = os.path.join(directory_name, file_name)

    current_level = 0
    root_path = get_root_path()
    while True:
        path_to_check = os.path.join(current_path, file_name)
        if os.path.isfile(path_to_check):
            return path_to_check

        if str(current_path) == root_path or (num_levels is not None and num_levels == current_level):
            break
        current_path = os.path.realpath(os.path.join(current_path, os.path.pardir))
        current_level = current_level + 1

    return ""
