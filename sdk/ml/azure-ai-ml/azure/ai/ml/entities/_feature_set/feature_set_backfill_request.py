# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from azure.ai.ml._schema._feature_set.feature_set_backfill_schema import FeatureSetBackfillSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._feature_set.feature_window import FeatureWindow
from azure.ai.ml.entities._feature_set.materialization_compute_resource import MaterializationComputeResource
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._util import load_from_dict


class FeatureSetBackfillRequest(RestTranslatableMixin):
    """Feature Set Backfill Request

    :param name: The name of the backfill job request
    :type name: str
    :param version: The version of the backfill job request.
    :type version: str
    :param feature_window: The time window for the feature set backfill request.
    :type feature_window: ~azure.ai.ml._restclient.v2023_04_01_preview.models.FeatureWindow
    :param description: The description of the backfill job request. Defaults to None.
    :type description: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict[str, str]]
    :keyword resource: The compute resource settings. Defaults to None.
    :paramtype resource: Optional[~azure.ai.ml.entities.MaterializationComputeResource]
    :param spark_configuration: Specifies the spark configuration. Defaults to None.
    :type spark_configuration: Optional[dict[str, str]]
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        feature_window: Optional[FeatureWindow] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        resource: Optional[MaterializationComputeResource] = None,
        spark_configuration: Optional[Dict[str, str]] = None,
        data_status: Optional[List[str]] = None,
        job_id: Optional[str] = None,
        **kwargs: Any,
    ):
        self.name = name
        self.version = version
        self.feature_window = feature_window
        self.description = description
        self.resource = resource
        self.tags = tags
        self.spark_configuration = spark_configuration
        self.data_status = data_status
        self.job_id = job_id

    @classmethod
    # pylint: disable=unused-argument
    def _resolve_cls_and_type(cls, data: Dict, params_override: Tuple) -> Tuple:
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
        **kwargs: Any,
    ) -> "FeatureSetBackfillRequest":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(FeatureSetBackfillSchema, data, context, **kwargs)
        return FeatureSetBackfillRequest(**loaded_schema)
