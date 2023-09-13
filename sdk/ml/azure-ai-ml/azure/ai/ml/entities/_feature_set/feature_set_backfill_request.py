# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union, List

from azure.ai.ml._restclient.v2023_08_01_preview.models import FeatureWindow

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._feature_set.materialization_compute_resource import (
    MaterializationComputeResource,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml._schema._feature_set.feature_set_backfill_schema import (
    FeatureSetBackfillSchema,
)


@experimental
class FeatureSetBackfillRequest(RestTranslatableMixin):
    def __init__(
        self,
        *,
        name: str,
        version: str,
        feature_window: FeatureWindow,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        resource: Optional[MaterializationComputeResource] = None,
        spark_conf: Optional[Dict[str, str]] = None,
        data_availability_status:  Optional[List[str]] = None,
        job_id: Optional[str] = None,
        **kwargs,
    ):
        self.name = name
        self.version = version
        self.feature_window = feature_window
        self.description = description
        self.resource = resource
        self.tags = tags
        self.spark_conf = spark_conf
        self.data_availability_status = data_availability_status
        self.job_id = job_id

    @classmethod
    # pylint: disable=unused-argument
    def _resolve_cls_and_type(cls, data, params_override):
        """Resolve the class to use for deserializing the data. Return current class if no override is provided.

        :param data: Data to deserialize.
        :type data: dict
        :param params_override: Parameters to override, defaults to None
        :type params_override: typing.Optional[list]
        :return: Class to use for deserializing the data & its "type". Type will be None if no override is provided.
        :rtype: tuple[class, typing.Optional[str]]
        """
        return cls, None

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "FeatureSetBackfillRequest":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(FeatureSetBackfillSchema, data, context, **kwargs)
        return FeatureSetBackfillRequest(**loaded_schema)
