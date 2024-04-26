# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class PromptflowModel:
    """A promptflow model
    
    :param path: The path to the model.
    :type path: Union[str, os.PathLike]
    :param base_image: The base image for the model.
    :type base_image: Optional[str]
    """
    path: Union[str, os.PathLike]
    base_image: Optional[str] = None


@dataclass
class Model:
    """A model asset
    
    :param path: The path to the model.
    :type path: Union[str, os.PathLike]
    :param conda_file: The path to the conda file for the model.
    :type conda_file: Optional[Union[str, os.PathLike]]
    :param loader_module: The loader module for the model.
    :type loader_module: Optional[str]
    :param chat_module: The chat module for the model.
    :type chat_module: Optional[str]
    """
    path: Union[str, os.PathLike]
    conda_file: Optional[Union[str, os.PathLike]] = None
    loader_module: Optional[str] = None
    chat_module: Optional[str] = None
