"""Unit tests for default_deployment_template entity."""

import pytest

from azure.ai.ml.entities._assets.default_deployment_template import DefaultDeploymentTemplate


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestDefaultDeploymentTemplateEntity:
    """Test cases for DefaultDeploymentTemplate entity."""

    def test_default_deployment_template_creation_with_asset_id(self) -> None:
        """Test creating a DefaultDeploymentTemplate with asset_id."""
        asset_id = "azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
        template = DefaultDeploymentTemplate(asset_id=asset_id)

        assert template.asset_id == asset_id

    def test_default_deployment_template_asset_id_none(self) -> None:
        """Test creating a DefaultDeploymentTemplate with None asset_id."""
        template = DefaultDeploymentTemplate(asset_id=None)

        assert template.asset_id is None

    def test_default_deployment_template_asset_id_property(self) -> None:
        """Test DefaultDeploymentTemplate asset_id property."""
        asset_id = "azureml://registries/my-registry/deploymenttemplates/my-template/versions/2"
        template = DefaultDeploymentTemplate(asset_id=asset_id)

        # Verify we can read the property
        assert template.asset_id is not None
        assert "my-registry" in template.asset_id
        assert "my-template" in template.asset_id
        assert "versions/2" in template.asset_id
