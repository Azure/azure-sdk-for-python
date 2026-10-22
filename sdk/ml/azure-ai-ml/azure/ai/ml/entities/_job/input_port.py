# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Optional, Union

module_logger = logging.getLogger(__name__)


class InputPort:
    def __init__(self, *, type_string: str, default: Optional[str] = None, optional: Optional[bool] = False):
        self.type_string = type_string
        self.optional = optional
        if self.type_string == "number" and default is not None:
            self.default: Union[float, Optional[str]] = float(default)
        else:
            self.default = default
