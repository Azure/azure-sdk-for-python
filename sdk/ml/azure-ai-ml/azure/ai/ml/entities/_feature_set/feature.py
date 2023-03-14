# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Optional
from azure.ai.ml.entities._feature_store_entity.data_column_type import _DataColumnType


class _Feature(object):
    def __init__(self, *, name: str, data_type: _DataColumnType, description: Optional[str], **kwargs):
        self.name = name
        self.type = data_type
        self.description = description
