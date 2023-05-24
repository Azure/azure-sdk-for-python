# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from marshmallow import INCLUDE

from azure.ai.ml._schema._feature_set.featureset_spec_metadata_schema import FeaturesetSpecMetadataSchema
from azure.ai.ml._schema._feature_set.featureset_spec_properties_schema import FeaturesetSpecPropertiesSchema
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._feature_store_entity.data_column import DataColumn

from .feature import Feature
from .source_metadata import SourceMetadata
from .delay_metadata import DelayMetadata
from .feature_transformation_code_metadata import FeatureTransformationCodeMetadata


class FeaturesetSpecMetadata(object):
    """FeaturesetSpecMetadata for feature-set."""

    def __init__(
        self,
        *,
        source: SourceMetadata,
        feature_transformation_code: Optional[FeatureTransformationCodeMetadata] = None,
        features: List[Feature],
        index_columns: List[DataColumn],
        source_lookback: Optional[DelayMetadata] = None,
        temporal_join_lookback: Optional[DelayMetadata] = None,
        **_kwargs,
    ):
        self.source = source
        self.feature_transformation_code = feature_transformation_code
        self.features = features
        self.index_columns = index_columns
        self.source_lookback = source_lookback
        self.temporal_join_lookback = temporal_join_lookback

    @classmethod
    def load(
        cls,
        yaml_path: Union[PathLike, str],
        **kwargs,
    ) -> "FeaturesetSpecMetadata":
        """Construct an FeaturesetSpecMetadata object from yaml file.

        :param yaml_path: Path to a local file as the source.
        :type PathLike | str

        :return: Constructed FeaturesetSpecMetadata object.
        :rtype: FeaturesetSpecMetadata
        """
        yaml_dict = load_yaml(yaml_path)
        return cls._load(yaml_data=yaml_dict, yaml_path=yaml_path, **kwargs)

    @classmethod
    def _load(
        cls,
        yaml_data: Optional[Dict],
        yaml_path: Optional[Union[PathLike, str]],
        **kwargs,
    ) -> "FeaturesetSpecMetadata":
        yaml_data = yaml_data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
        }
        return load_from_dict(FeaturesetSpecMetadataSchema, yaml_data, context, "", unknown=INCLUDE, **kwargs)

    def _to_dict(self) -> Dict:
        return FeaturesetSpecPropertiesSchema(context={BASE_PATH_CONTEXT_KEY: "./"}, unknown=INCLUDE).dump(self)
