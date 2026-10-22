# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from typing import IO, Any, Dict, Optional, Union, cast

from ruamel.yaml import YAML, YAMLError  # cspell:ignore ruamel

from azure.ai.evaluation._constants import DefaultOpenEncoding
from azure.ai.evaluation._legacy.prompty._exceptions import MissingRequiredInputError


def load_yaml(source: Optional[Union[str, PathLike, IO]]) -> Dict:
    # null check - just return an empty dict.
    # Certain CLI commands rely on this behavior to produce a resource
    # via CLI, which is then populated through CLArgs.
    """Load a local YAML file or a readable stream object.

    .. note::

        1. For a local file yaml

        .. code-block:: python

            yaml_path = "path/to/yaml"
            content = load_yaml(yaml_path)

        2. For a readable stream object

        .. code-block:: python

            with open("path/to/yaml", "r", encoding="utf-8") as f:
                content = load_yaml(f)


    :param source: The relative or absolute path to the local file, or a readable stream object.
    :type source: str
    :return: A dictionary representation of the local file's contents.
    :rtype: Dict
    """

    if source is None:
        return {}

    # pylint: disable=redefined-builtin
    input: Optional[IO] = None
    must_open_file = False
    try:  # check source type by duck-typing it as an IOBase
        readable = cast(IO, source).readable()
        if not readable:  # source is misformatted stream or file
            msg = "File Permissions Error: The already-open \n\n inputted file is not readable."
            raise PermissionError(msg)
        # source is an already-open stream or file, we can read() from it directly.
        input = cast(IO, source)
    except AttributeError:
        # source has no writable() function, assume it's a string or file path.
        must_open_file = True

    if must_open_file:  # If supplied a file path, open it.
        try:
            input = open(  # pylint: disable=consider-using-with
                cast(Union[PathLike, str], source), "r", encoding=DefaultOpenEncoding.READ
            )
        except OSError:  # FileNotFoundError introduced in Python 3
            e = FileNotFoundError(f"No such file or directory: {source}")
            raise MissingRequiredInputError(str(e), privacy_info=[str(source)]) from e
    # input should now be a readable file or stream. Parse it.
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        cfg = yaml.load(input)
    except YAMLError as e:
        msg = f"Error while parsing yaml file: {source} \n\n {str(e)}"
        raise YAMLError(msg) from e
    finally:
        if input and must_open_file:
            input.close()

    return cfg or {}


def load_yaml_string(yaml_string: str) -> Dict[str, Any]:
    """Load a yaml string.

    .. code-block:: python

        yaml_string = "some yaml string"
        object = load_yaml_string(yaml_string)


    :param yaml_string: A yaml string.
    :type yaml_string: str
    :return: A dictionary representation of the yaml string.
    :rtype: Dict
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    return yaml.load(yaml_string)
