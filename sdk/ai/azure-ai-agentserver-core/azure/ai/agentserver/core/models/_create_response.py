# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from .openai import response_create_params
from . import projects as _azure_ai_projects_models

class CreateResponse(response_create_params.ResponseCreateParamsBase, total=False):
    agent: Optional[_azure_ai_projects_models.AgentReference]
    stream: Optional[bool]
