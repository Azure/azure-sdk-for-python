# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: helpers.py

DESCRIPTION:
    This module loads logger and some utility methods required to run the sample codes.
"""
from pathlib import Path

import json
import logging
import typing


def get_logger(name):
    # create console handler
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    # create Logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


def beautify_json(obj: typing.Dict[str, typing.Any]):
    return json.dumps(obj, indent=4)


def get_image_path(image_file_name: str):
    from .constants import TestImages

    return Path(__file__).resolve().parent / (TestImages.IMAGE_PARENT_FOLDER + "/" + image_file_name)


def read_file_content(file_path: Path):
    with open(file_path, "rb") as fd:
        file_content = fd.read()

    return file_content
