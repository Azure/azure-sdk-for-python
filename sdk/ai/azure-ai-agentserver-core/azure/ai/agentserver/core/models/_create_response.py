from typing import Any, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .projects import models as _azure_ai_projects_models
from .openai import response_create_params

class CreateResponse(response_create_params.ResponseCreateParamsBase, total=False):
    agent: Optional[_azure_ai_projects_models.AgentReference]
    stream: Optional[bool]
