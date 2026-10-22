# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path

import pytest

from azure.ai.ml._utils._feature_store_utils import read_feature_set_metadata
from azure.ai.ml.entities._feature_set.featureset_spec_metadata import FeaturesetSpecMetadata
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureSetSchema:
    def test_feature_set_spec_load(self) -> None:
        spec_path = "./tests/test_configs/feature_set"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        fspec = FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        assert fspec.feature_transformation_code is not None
        assert fspec.source is not None
        assert len(fspec.features) == 3

        spec_path = "./tests/test_configs/feature_set/custom_source_spec"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        fspec = FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        assert fspec.feature_transformation_code is not None
        assert fspec.source is not None
        assert fspec.source.source_process_code.path == "./source_process_code"
        assert fspec.source.source_process_code.process_class == "source_process.MyDataSourceLoader"
        assert len(fspec.features) == 3
        assert len(fspec.source.kwargs.keys()) == 3

        spec_path = "./tests/test_configs/feature_set/featureset_source_spec"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        fspec = FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        assert fspec.feature_transformation_code is not None
        assert fspec.source is not None
        assert fspec.source.timestamp_column is None
        assert len(fspec.features) == 3
        assert fspec.index_columns is None
        assert fspec.source.source_delay is None
        assert fspec.source.timestamp_column is None

    def test_feature_set_spec_load_failure(self) -> None:
        spec_path = "./tests/test_configs/feature_set/invalid_spec1"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException) as ve:
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec2"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec3"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec4"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec5"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec6"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec7"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec8"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)

        spec_path = "./tests/test_configs/feature_set/invalid_spec9"
        featureset_spec_contents = read_feature_set_metadata(path=spec_path)
        featureset_spec_yaml_path = Path(spec_path, "FeatureSetSpec.yaml")
        with pytest.raises(ValidationException):
            FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)
