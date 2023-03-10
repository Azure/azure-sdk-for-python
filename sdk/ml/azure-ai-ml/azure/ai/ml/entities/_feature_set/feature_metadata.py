# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Dict, Optional

from azure.ai.ml.entities._feature_store_entity.data_column_type import DataColumnType


class FeatureMetadata(object):
    def __init__(
        self,
        *,
        name: str,
        data_type: DataColumnType,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        self.FeatureName = name
        self.DataType = data_type
        self.Description = description
        self.Tags = tags
