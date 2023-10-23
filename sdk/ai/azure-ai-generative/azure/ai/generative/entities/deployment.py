# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass
from typing import Dict, Union

from .managed_identity import ManagedIdentity
from .models import Model, PromptflowModel


@dataclass
class Deployment:
    name: str
    model: Union[str, Model, PromptflowModel]
    app_insights_enabled: bool = True
    data_collector_enabled: bool = True
    endpoint_name: str = None
    environment_variables: Dict[str, str] = None
    instance_type: str = None
    instance_count: str = 1
    managed_identity: ManagedIdentity = None
    properties: Dict[str, str] = None
    tags: Dict[str, str] = None
