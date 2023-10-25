# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from dataclasses import dataclass
from typing import Union


@dataclass
class LangchainModel:
    chain: "langchain.chains.Chain"
    conda_file: Union[str, os.PathLike]


@dataclass
class PromptflowModel:
    path: Union[str, os.PathLike]
    base_image: str = None


@dataclass
class Model:
    path: Union[str, os.PathLike]
    conda_file: Union[str, os.PathLike] = None
    loader_module: str = None
    chat_module: str = None
