# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#
# This file contains Dockerfile instructions as Python classes.
# Using them as str(Cmd) for example will output the proper Dockerfile instruction as a string.

from typing import Optional


class Cmd(object):
    """Python object representation of Docker CMD instruction.

    :param command_array: The command and its arguments as a list of strings.
    :type command_array: list[str]
    """

    def __init__(self, command_array):
        self.command_array = command_array

    def __str__(self) -> str:
        string_arr = [f'"{cmd}"' for cmd in self.command_array]
        return f"CMD [{', '.join(string_arr)}]"


class Copy(object):
    """Python object representation of Docker COPY instruction.

    :param src: The source path(s) to copy from.
    :type src: list[str]
    :param dest: The destination path to copy to.
    :type dest: str
    """

    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __str__(self) -> str:
        from_str = " ".join(self.src)
        return f"COPY {from_str} {self.dest}"


class Env(object):
    """Python object representation of Docker ENV instruction.

    :param key: The environment variable name.
    :type key: str
    :param value: The environment variable value.
    :type value: str
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self) -> str:
        return f"ENV {self.key}={self.value}"


class Expose(object):
    """Python object representation of Docker EXPOSE instruction.

    :param port: The port to expose.
    :type port: int
    """

    def __init__(self, port):
        self.port = port

    def __str__(self) -> str:
        return f"EXPOSE {self.port}"


class From(object):
    """Python object representation of Docker FROM instruction.

    :param base_image_name: The name of the base image.
    :type base_image_name: str
    :param stage_name: The optional build stage name, defaults to None.
    :type stage_name: Optional[str]
    """

    def __init__(self, base_image_name: str, stage_name: Optional[str] = None):
        self.base_image = base_image_name
        self.stage_name = stage_name

    def __str__(self) -> str:
        if self.stage_name is None:
            return f"FROM {self.base_image}"

        return f"FROM {self.base_image} as {self.stage_name}"


class Run(object):
    """Python object representation of Docker RUN instruction.

    :param command: The command to run.
    :type command: str
    """

    def __init__(self, command: str):
        self.command = command

    def __str__(self) -> str:
        return f"RUN {self.command}"


class Workdir(object):
    """Python object representation of Docker WORKDIR instruction.

    :param directory: The working directory path.
    :type directory: str
    """

    def __init__(self, directory: str):
        self.directory = directory

    def __str__(self) -> str:
        return f"WORKDIR {self.directory}"
