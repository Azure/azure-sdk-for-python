"""Unit tests for default_deployment_template entity."""

import pytest

from azure.ai.ml.entities._assets.default_deployment_template import DeploymentTemplateReference


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestDeploymentTemplateReferenceEntity:
    """Test cases for DeploymentTemplateReference entity."""

    def test_default_deployment_template_creation_with_asset_id(self) -> None:
        """Test creating a DeploymentTemplateReference with asset_id."""
        asset_id = "azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
        template = DeploymentTemplateReference(asset_id=asset_id)

        assert template.asset_id == asset_id

    def test_default_deployment_template_asset_id_none(self) -> None:
        """Test creating a DeploymentTemplateReference with None asset_id."""
        template = DeploymentTemplateReference(asset_id=None)

        assert template.asset_id is None

    def test_default_deployment_template_asset_id_property(self) -> None:
        """Test DeploymentTemplateReference asset_id property."""
        asset_id = "azureml://registries/my-registry/deploymenttemplates/my-template/versions/2"
        template = DeploymentTemplateReference(asset_id=asset_id)

        # Verify we can read the property
        assert template.asset_id is not None
        assert "my-registry" in template.asset_id
        assert "my-template" in template.asset_id
        assert "versions/2" in template.asset_id
