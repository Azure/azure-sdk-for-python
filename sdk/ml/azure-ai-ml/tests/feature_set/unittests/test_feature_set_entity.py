# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import json

from azure.ai.ml.entities._assets._artifacts.feature_set import FeatureSet
from azure.ai.ml.entities._load_functions import load_feature_set
from azure.ai.ml._restclient.v2023_10_01.models import (
    FeaturesetContainer,
    FeaturesetContainerProperties,
    FeaturesetVersion,
    FeaturesetVersionProperties,
)


@pytest.mark.unittest
class TestFeatureSetEntity:
    FEATURE_SET = "./tests/test_configs/feature_set/feature_set_full.yaml"
    FEATURE_SET_REST = "./tests/test_configs/feature_set/feature_set_full_rest.json"
    FEATURE_SET_CONTAINER_REST = "./tests/test_configs/feature_set/feature_set_container_rest.json"

    def test_to_rest_object(self) -> None:
        feature_set = load_feature_set(self.FEATURE_SET)

        feature_set_rest = feature_set._to_rest_object()
        assert feature_set_rest.properties.description == feature_set.description
        assert feature_set_rest.properties.tags == feature_set.tags
        assert feature_set_rest.properties.entities == feature_set.entities
        assert feature_set_rest.properties.specification.path == feature_set.specification.path
        assert feature_set_rest.properties.stage == feature_set.stage
        assert (
            str(feature_set_rest.properties.materialization_settings.store_type) == "MaterializationStoreType.OFFLINE"
        )
        assert (
            feature_set_rest.properties.materialization_settings.schedule.frequency
            == feature_set.materialization_settings.schedule.frequency
        )
        assert (
            feature_set_rest.properties.materialization_settings.schedule.interval
            == feature_set.materialization_settings.schedule.interval
        )
        assert (
            feature_set_rest.properties.materialization_settings.spark_configuration
            == feature_set.materialization_settings.spark_configuration
        )
        assert (
            feature_set_rest.properties.materialization_settings.resource.instance_type
            == feature_set.materialization_settings.resource.instance_type
        )
        assert (
            feature_set_rest.properties.materialization_settings.notification.email_on
            == feature_set.materialization_settings.notification.email_on
        )
        assert (
            feature_set_rest.properties.materialization_settings.notification.emails
            == feature_set.materialization_settings.notification.emails
        )

    def test_from_rest_object(self) -> None:
        with open(self.FEATURE_SET_REST, "r") as f:
            feature_set_rest = FeaturesetVersion.deserialize(json.load(f))
            feature_set = FeatureSet._from_rest_object(featureset_rest_object=feature_set_rest)
            assert feature_set.name == feature_set_rest.name
            assert feature_set.description == feature_set_rest.properties.description
            assert feature_set.tags == feature_set_rest.properties.tags
            assert feature_set.entities == feature_set_rest.properties.entities
            assert feature_set.specification.path == feature_set_rest.properties.specification.path
            assert feature_set.stage == feature_set_rest.properties.stage
            assert (
                feature_set.materialization_settings.schedule.frequency
                == feature_set_rest.properties.materialization_settings.schedule.frequency.lower()
            )
            assert (
                feature_set.materialization_settings.schedule.interval
                == feature_set_rest.properties.materialization_settings.schedule.interval
            )
            assert (
                feature_set.materialization_settings.spark_configuration
                == feature_set_rest.properties.materialization_settings.spark_configuration
            )
            assert (
                feature_set.materialization_settings.resource.instance_type
                == feature_set_rest.properties.materialization_settings.resource.instance_type
            )
            assert (
                feature_set.materialization_settings.notification.email_on
                == feature_set_rest.properties.materialization_settings.notification.email_on
            )
            assert (
                feature_set.materialization_settings.notification.emails
                == feature_set_rest.properties.materialization_settings.notification.emails
            )

    def test_from_container_rest_object(self) -> None:
        with open(self.FEATURE_SET_CONTAINER_REST, "r") as f:
            featureset_container_rest = FeaturesetContainer.deserialize(json.load(f))
            feature_set = FeatureSet._from_container_rest_object(featureset_container_rest)
            assert feature_set.name == featureset_container_rest.name
            assert feature_set.description == featureset_container_rest.properties.description
            assert feature_set.tags == featureset_container_rest.properties.tags
            assert feature_set.entities == []
            assert feature_set.specification.path == None
            assert feature_set.version == ""
            assert feature_set.latest_version == featureset_container_rest.properties.latest_version
