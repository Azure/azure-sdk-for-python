# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from dataclasses import dataclass
from typing import Optional

@dataclass
class OperationScope(object):

    subscription_id: str
    resource_group_name: str
    ai_resource_name: Optional[str] = None
    project_name: Optional[str] = None
    registry_name: Optional[str] = None
