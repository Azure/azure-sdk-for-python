# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass


@dataclass
class ManagedIdentity:
    client_id: str = None
    resource_id: str = None
