# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=no-name-in-module
from typing import Optional

from .openai import response_create_params   # type: ignore
from . import projects as _azure_ai_projects_models

class CreateResponse(response_create_params.ResponseCreateParamsBase, total=False): # type: ignore
    agent: Optional[_azure_ai_projects_models.AgentReference]
    stream: Optional[bool]
