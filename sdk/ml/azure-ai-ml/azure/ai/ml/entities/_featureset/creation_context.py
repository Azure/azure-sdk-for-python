# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime
from typing import Dict, Optional, Union


class CreationContext:
    def __init__(self, *, created_time: Optional[Union[str, datetime]], **kwargs):
        self.created_time = created_time
