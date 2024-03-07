# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from marshmallow import INCLUDE

from azure.ai.ml._schema._feature_set.featureset_spec_metadata_schema import FeaturesetSpecMetadataSchema
from azure.ai.ml._schema._feature_set.featureset_spec_properties_schema import FeaturesetSpecPropertiesSchema
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._feature_store_entity.data_column import DataColumn
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .delay_metadata import DelayMetadata
from .feature import Feature
from .feature_transformation_code_metadata import FeatureTransformationCodeMetadata
from .source_metadata import SourceMetadata


class FeaturesetSpecMetadata(object):
    """FeaturesetSpecMetadata for feature-set."""

    def __init__(
        self,
        *,
        source: SourceMetadata,
        feature_transformation_code: Optional[FeatureTransformationCodeMetadata] = None,
        features: List[Feature],
        index_columns: Optional[List[DataColumn]] = None,
        source_lookback: Optional[DelayMetadata] = None,
        temporal_join_lookback: Optional[DelayMetadata] = None,
        **_kwargs: Any,
    ):
        if source.type == "featureset" and index_columns:
            msg = f"You cannot provide index_columns for {source.type} feature source."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.INVALID_VALUE,
                target=ErrorTarget.FEATURE_SET,
                error_category=ErrorCategory.USER_ERROR,
            )
        if not index_columns and source.type != "featureset":
            msg = f"You need to provide index_columns for {source.type} feature source."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.INVALID_VALUE,
                target=ErrorTarget.FEATURE_SET,
                error_category=ErrorCategory.USER_ERROR,
            )
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
        **kwargs: Any,
    ) -> "FeaturesetSpecMetadata":
        """Construct an FeaturesetSpecMetadata object from yaml file.

        :param yaml_path: Path to a local file as the source.
        :type yaml_path: PathLike | str

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
        **kwargs: Any,
    ) -> "FeaturesetSpecMetadata":
        yaml_data = yaml_data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
        }
        res: FeaturesetSpecMetadata = load_from_dict(
            FeaturesetSpecMetadataSchema, yaml_data, context, "", unknown=INCLUDE, **kwargs
        )

        return res

    def _to_dict(self) -> Dict:
        res: dict = FeaturesetSpecPropertiesSchema(context={BASE_PATH_CONTEXT_KEY: "./"}, unknown=INCLUDE).dump(self)
        return res
