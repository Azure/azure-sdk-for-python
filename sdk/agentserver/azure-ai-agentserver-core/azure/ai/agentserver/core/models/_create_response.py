# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=no-name-in-module  # openai re-exports are dynamically generated
from typing import Optional

# ResponseCreateParamsBase is a TypedDict — mypy cannot verify total=False on mixed bases.
from ._openai import response_create_params   # type: ignore
from . import _projects as _azure_ai_projects_models

class CreateResponse(response_create_params.ResponseCreateParamsBase, total=False): # type: ignore
    agent: Optional[_azure_ai_projects_models.AgentReference]
    stream: Optional[bool]
    tools: Optional[list[_azure_ai_projects_models.Tool]]
