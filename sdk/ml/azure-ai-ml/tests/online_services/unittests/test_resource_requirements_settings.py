import pytest

from azure.ai.ml.entities import ResourceSettings


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestResourceRequirementsSettings:
    def test_resource_requirements_settings_from_object(self) -> None:
        rest_resource_settings = ResourceSettings(cpu="1", memory="1.0Gi", gpu="1")
        resource_settings = ResourceSettings._from_rest_object(settings=rest_resource_settings)
        assert resource_settings.cpu == rest_resource_settings.cpu
        assert resource_settings.memory == rest_resource_settings.memory
        assert resource_settings.gpu == rest_resource_settings.gpu

    def test_resource_requirements_settings_to_objects(self) -> None:
        resource_settings = ResourceSettings(cpu="1", memory="1.0Gi", gpu="1")
        rest_resource_settings = resource_settings._to_rest_object()
        assert resource_settings.cpu == rest_resource_settings.cpu
        assert resource_settings.memory == rest_resource_settings.memory
        assert resource_settings.gpu == rest_resource_settings.gpu
