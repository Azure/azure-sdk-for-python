# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass
from typing import Dict, Union

from .managed_identity import ManagedIdentity
from .models import FoundationModel, LocalModel


@dataclass
class Deployment:
    name: str
    model: Union[str, FoundationModel, LocalModel]
    endpoint_name: str = None
    environment_variables: Dict[str, str] = None
    enable_data_collector: bool = False
    instance_type: str = None
    instance_count: str = 1
    managed_identity: ManagedIdentity = None
