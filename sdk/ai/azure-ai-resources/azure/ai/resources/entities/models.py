# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class PromptflowModel:
    path: Union[str, os.PathLike]
    base_image: Optional[str] = None


@dataclass
class Model:
    path: Union[str, os.PathLike]
    conda_file: Optional[Union[str, os.PathLike]] = None
    loader_module: Optional[str] = None
    chat_module: Optional[str] = None
