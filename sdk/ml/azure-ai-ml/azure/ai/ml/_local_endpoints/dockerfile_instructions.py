# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#
# This file contains Dockerfile instructions as Python classes.
# Using them as str(Cmd) for example will output the proper Dockerfile instruction as a string.

from typing import Optional


class Cmd(object):
    """Python object representation of Docker CMD instruction."""

    def __init__(self, command_array):
        self.command_array = command_array

    def __str__(self) -> str:
        string_arr = [f'"{cmd}"' for cmd in self.command_array]
        return f"CMD [{', '.join(string_arr)}]"


class Copy(object):
    """Python object representation of Docker COPY instruction."""

    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __str__(self) -> str:
        from_str = " ".join(self.src)
        return f"COPY {from_str} {self.dest}"


class Env(object):
    """Python object representation of Docker ENV instruction."""

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self) -> str:
        return f"ENV {self.key}={self.value}"


class Expose(object):
    """Python object representation of Docker EXPOSE instruction."""

    def __init__(self, port):
        self.port = port

    def __str__(self) -> str:
        return f"EXPOSE {self.port}"


class From(object):
    """Python object representation of Docker FROM instruction."""

    def __init__(self, base_image_name: str, stage_name: Optional[str] = None):
        self.base_image = base_image_name
        self.stage_name = stage_name

    def __str__(self) -> str:
        if self.stage_name is None:
            return f"FROM {self.base_image}"

        return f"FROM {self.base_image} as {self.stage_name}"


class Run(object):
    """Python object representation of Docker RUN instruction."""

    def __init__(self, command: str):
        self.command = command

    def __str__(self) -> str:
        return f"RUN {self.command}"


class Workdir(object):
    """Python object representation of Docker WORKDIR instruction."""

    def __init__(self, directory: str):
        self.directory = directory

    def __str__(self) -> str:
        return f"WORKDIR {self.directory}"
