# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

module_logger = logging.getLogger(__name__)


class LoadableMixin:
    def load(self, obj: Any) -> None:
        pass
