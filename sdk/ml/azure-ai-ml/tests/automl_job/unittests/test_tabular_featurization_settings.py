import pytest
from azure.ai.ml._restclient.v2022_02_01_preview.models import ColumnTransformer as RestColumnTransformer
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    TableVerticalFeaturizationSettings as RestTabularFeaturizationSettings,
)
from azure.ai.ml.entities._job.automl.tabular import ColumnTransformer, TabularFeaturizationSettings


@pytest.mark.unittest
class TestFeaturizationSettings:
    def test_to_rest(self) -> None:
        featurization_settings = self._get_entity_obj()
        rest_obj = featurization_settings._to_rest_object()
        assert rest_obj == self._get_rest_obj(), "actual: {}, expected: {}".format(rest_obj, self._get_rest_obj())

    def test_from_rest(self) -> None:
        rest_obj = self._get_rest_obj()
        featurization_settings = TabularFeaturizationSettings._from_rest_object(rest_obj)
        assert featurization_settings == self._get_entity_obj(), "actual: {}, expected: {}".format(
            featurization_settings, self._get_entity_obj()
        )

    def test_equality(self) -> None:
        featurization_settings = self._get_entity_obj()
        rest_obj = featurization_settings._to_rest_object()
        featurization_settings_2 = TabularFeaturizationSettings._from_rest_object(rest_obj)
        assert featurization_settings == featurization_settings_2, "actual: {}, expected: {}".format(
            featurization_settings_2, featurization_settings
        )

    def _get_rest_obj(self) -> RestTabularFeaturizationSettings:
        tp = {
            "imputer": [
                RestColumnTransformer(fields=["col3", "col4"], parameters={"strategy": "constant", "fill_value": 0.0}),
                RestColumnTransformer(fields=["col5"], parameters={"strategy": "median"}),
            ],
            "hash_one_hot_encoder": [
                RestColumnTransformer(fields=["col6"], parameters={"number_of_bits": 3}),
            ],
        }
        return RestTabularFeaturizationSettings(
            blocked_transformers=["LabelEncoder", "WordEmbedding"],
            column_name_and_types={
                "col1": "CategoricalHash",
                "col2": "Numeric",
                "col3": "Categorical",
            },
            dataset_language="English",
            transformer_params=tp,
            mode="custom",
            enable_dnn_featurization=True,
        )

    def _get_entity_obj(self) -> TabularFeaturizationSettings:
        ct1 = ColumnTransformer(
            fields=["col3", "col4"],
            parameters={"strategy": "constant", "fill_value": 0.0},
        )
        ct2 = ColumnTransformer(
            fields=["col5"],
            parameters={"strategy": "median"},
        )
        ct3 = ColumnTransformer(
            fields=["col6"],
            parameters={"number_of_bits": 3},
        )

        return TabularFeaturizationSettings(
            blocked_transformers=["LabelEncoder", "WordEmbedding"],
            column_name_and_types={
                "col1": "CategoricalHash",
                "col2": "Numeric",
                "col3": "Categorical",
            },
            dataset_language="English",
            transformer_params={
                "imputer": [ct1, ct2],
                "hash_one_hot_encoder": [ct3],
            },
            mode="custom",
            enable_dnn_featurization=True,
        )
