# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-member

from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from marshmallow import INCLUDE

from azure.ai.ml._schema._featureset.featureset_spec_schema import FeaturesetSpecSchema
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._featurestore_entity.data_column import DataColumn


from .feature import Feature


class FeaturesetSpec:
    """FeaturesetSpec for data assets."""

    def __init__(
        self,
        *,
        features: List[Feature],
        index_columns: List[DataColumn],
        **_kwargs,
    ):
        self.features = features
        self.index_columns = index_columns

    @classmethod
    def load(
        cls,
        yaml_path: Union[PathLike, str],
        **kwargs,
    ) -> "FeaturesetSpec":
        """Construct an FeaturesetSpec object from yaml file.

        :param yaml_path: Path to a local file as the source.
        :type PathLike | str

        :return: Constructed FeaturesetSpec object.
        :rtype: FeaturesetSpec
        """
        yaml_dict = load_yaml(yaml_path)
        return cls._load(yaml_data=yaml_dict, yaml_path=yaml_path, **kwargs)

    @classmethod
    def _load(
        cls,
        yaml_data: Optional[Dict],
        yaml_path: Optional[Union[PathLike, str]],
        **kwargs,
    ) -> "FeaturesetSpec":
        yaml_data = yaml_data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
        }
        return load_from_dict(FeaturesetSpecSchema, yaml_data, context, "", unknown=INCLUDE, **kwargs)

    def _to_dict(self) -> Dict:
        return FeaturesetSpecSchema(context={BASE_PATH_CONTEXT_KEY: "./"}, unknown=INCLUDE).dump(self)
