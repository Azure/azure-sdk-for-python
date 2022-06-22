import pytest
import yaml

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._utils.utils import camel_to_snake
from marshmallow import RAISE
from azure.ai.ml._restclient.v2021_10_01.models import (
    DefaultScaleSettings as RestDefaultScaleSettings,
    TargetUtilizationScaleSettings as RestTargetUtilizationScaleSettings,
)
from azure.ai.ml.entities import DefaultScaleSettings, TargetUtilizationScaleSettings


@pytest.mark.unittest
class TestScaleSettings:
    def test_target_utilization_scale_settings_from_object(self) -> None:
        rest_scale_settings = RestTargetUtilizationScaleSettings(
            min_instances=1,
            max_instances=2,
            polling_interval="PT1S",
            target_utilization_percentage=30,
        )
        scale_settings = TargetUtilizationScaleSettings._from_rest_object(settings=rest_scale_settings)
        assert scale_settings.scale_type == camel_to_snake(rest_scale_settings.scale_type)
        assert scale_settings.min_instances == rest_scale_settings.min_instances
        assert scale_settings.max_instances == rest_scale_settings.max_instances
        assert scale_settings.polling_interval == 1
        assert scale_settings.target_utilization_percentage == rest_scale_settings.target_utilization_percentage

    def test_auto_scale_settings_to_objects(self) -> None:
        scale_settings = DefaultScaleSettings()
        rest_scale_settings = scale_settings._to_rest_object()
        assert camel_to_snake(rest_scale_settings.scale_type) == scale_settings.scale_type
