# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Union, List, Dict

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    TableVerticalFeaturizationSettings as RestTabularFeaturizationSettings,
    ColumnTransformer as RestColumnTransformer,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._job.automl.featurization_settings import FeaturizationSettings


module_logger = logging.getLogger(__name__)


class ColumnTransformer(RestTranslatableMixin):
    """Column transformer settings

    :param fields: The fields on which to perform custom featurization
    :type field: List[str]
    :param parameters: parameters used for custom featurization
    :type parameters: Dict[str, Optional[str, float]]
    """

    def __init__(self, *, fields: List[str] = None, parameters: Dict[str, Union[str, float]] = None, **kwargs):
        self.fields = fields
        self.parameters = parameters

    def _to_rest_object(self) -> RestColumnTransformer:
        return RestColumnTransformer(fields=self.fields, parameters=self.parameters)

    @classmethod
    def _from_rest_object(cls, obj: RestColumnTransformer) -> "ColumnTransformer":
        if obj:
            fields = obj.fields
            parameters = obj.parameters
            return ColumnTransformer(fields=fields, parameters=parameters)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ColumnTransformer):
            return NotImplemented
        return self.fields == other.fields and self.parameters == other.parameters

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class TabularFeaturizationSettings(FeaturizationSettings):
    """Featurization settings for an AutoML Job"""

    def __init__(
        self,
        *,
        blocked_transformers: List[str] = None,
        column_name_and_types: Dict[str, str] = None,
        dataset_language: str = None,
        transformer_params: Dict[str, List[ColumnTransformer]] = None,
        mode: str = None,
        enable_dnn_featurization: bool = None,
    ):
        """
        :param blocked_transformers: A list of transformers to ignore when featurizing.
        :type blocked_transformers: List[str]
        :param column_name_and_types: A dictionary of column names and feature types used to update column purpose.
        :type column_name_and_types: Dict[str, str]
        :param dataset_language: The language of the dataset.
        :type dataset_language: str
        :param transformer_params: A dictionary of transformers and their parameters.
        :type transformer_params: Dict[str, List[ColumnTransformer]]
        :param mode: The mode of the featurization.
        :type mode: str
        :param enable_dnn_featurization: Whether to enable DNN featurization.
        :type enable_dnn_featurization: bool
        """
        super().__init__(dataset_language=dataset_language)
        self.blocked_transformers = blocked_transformers
        self.column_name_and_types = column_name_and_types
        self.transformer_params = transformer_params
        self.mode = mode
        self.enable_dnn_featurization = enable_dnn_featurization

    def _to_rest_object(self) -> RestTabularFeaturizationSettings:
        transformer_dict = {}
        if self.transformer_params:
            for key, settings in self.transformer_params.items():
                transformer_dict[key] = [o._to_rest_object() for o in settings]
        return RestTabularFeaturizationSettings(
            blocked_transformers=self.blocked_transformers,
            column_name_and_types=self.column_name_and_types,
            dataset_language=self.dataset_language,
            mode=self.mode,
            transformer_params=transformer_dict,
            enable_dnn_featurization=self.enable_dnn_featurization,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestTabularFeaturizationSettings) -> "TabularFeaturizationSettings":
        rest_transformers_params = obj.transformer_params
        transformer_dict = None
        if rest_transformers_params:
            transformer_dict = {}
            for key, settings in rest_transformers_params.items():
                transformer_dict[key] = [ColumnTransformer._from_rest_object(o) for o in settings]
        transformer_params = transformer_dict

        return TabularFeaturizationSettings(
            blocked_transformers=obj.blocked_transformers,
            column_name_and_types=obj.column_name_and_types,
            dataset_language=obj.dataset_language,
            transformer_params=transformer_params,
            mode=obj.mode,
            enable_dnn_featurization=obj.enable_dnn_featurization,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TabularFeaturizationSettings):
            return NotImplemented
        return (
            super().__eq__(other)
            and self.blocked_transformers == other.blocked_transformers
            and self.column_name_and_types == other.column_name_and_types
            and self.transformer_params == other.transformer_params
            and self.mode == other.mode
            and self.enable_dnn_featurization == other.enable_dnn_featurization
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
