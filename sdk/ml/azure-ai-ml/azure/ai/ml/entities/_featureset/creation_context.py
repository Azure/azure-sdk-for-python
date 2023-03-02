# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime
from typing import Optional, Union

from azure.ai.ml._utils._experimental import experimental


@experimental
class CreationContext:
    def __init__(self, *, created_time: Optional[Union[str, datetime]], **kwargs):  # pylint: disable=unused-argument
        self.created_time = created_time
