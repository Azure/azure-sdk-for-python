# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import collections.abc
import logging
from typing import Optional, Union

from azure.ai.ml.constants import InputOutputModes
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._mixins import DictMixin

module_logger = logging.getLogger(__name__)


class InputOutputEntry(DictMixin):
    def __init__(
        self,
        data: Optional[Union[str, "Data"]] = None,
        mode: Optional[str] = InputOutputModes.MOUNT,
        **kwargs,  # pylint: disable=unused-argument
    ):
        # Data will be either a dataset id, inline dataset definition
        self.data = data
        self.mode = mode
        if isinstance(self.data, collections.abc.Mapping) and not isinstance(self.data, Data):
            self.data = Data(**self.data)
