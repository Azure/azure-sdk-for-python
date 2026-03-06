# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Advanced E2E tests for Deployment Templates.

These tests cover advanced scenarios and integration testing:
- Complex deployment template configurations
- Integration with other Azure ML resources
- Performance and concurrency tests
- Edge cases and boundary conditions
"""

import logging
import pytest

from devtools_testutils import AzureRecordedTestCase
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient, load_deployment_template
from azure.ai.ml.entities import DeploymentTemplate
from azure.ai.ml.entities._deployment.deployment_template_settings import (
    OnlineRequestSettings,
    ProbeSettings
)




logger = logging.getLogger(__name__)


def cleanup_template(client: MLClient, name: str, version: str) -> None:
    """Helper function to clean up existing deployment template.
    
    Args:
        client: ML registry client
        name: Template name
        version: Template version
    """
    try:
        client.deployment_templates.delete(name=name, version=version)
        logger.info(f"Deleted existing template: {name} version {version}")
        sleep_if_live(3)
    except Exception:
        pass  # Template doesn't exist, continue


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_asset_name")
class TestDeploymentTemplateAdvancedE2E(AzureRecordedTestCase):
    """Advanced E2E test class for Deployment Template operations."""

    def test_deployment_template_with_custom_probes(
        self,
        registry_client: MLClient,
        deployment_template_name: str,
    ) -> None:
        """Test creating a deployment template with custom liveness and readiness probes.

        Args:
            registry_client: ML registry client fixture
            deployment_template_name: Generated unique template name
        """
        template_name = deployment_template_name
        cleanup_template(registry_client, template_name, "1")
        
        try:
            # Create liveness probe
            liveness_probe = ProbeSettings(
                initial_delay=60,
                period=5,
                timeout=1,
                failure_threshold=3,
                success_threshold=1,
                scheme="HTTP",
                method="GET",
                path="/health/liveness",
                port=8080
            )

            # Create readiness probe
            readiness_probe = ProbeSettings(
                initial_delay=30,
                period=5,
                timeout=1,
                failure_threshold=3,
                success_threshold=1,
                scheme="HTTP",
                method="GET",
                path="/health/readiness",
                port=8080
            )

            # Create deployment template with probes
            template = DeploymentTemplate(
                name=template_name,
                version="1",
                description="Template with custom probes",
                deployment_template_type="Managed",
                environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                liveness_probe=liveness_probe,
                readiness_probe=readiness_probe,
                instance_count=1,
                allowed_instance_types="Standard_DS2_v2",
                default_instance_type="Standard_DS2_v2",
            )

            logger.info(f"Creating deployment template with custom probes: {template_name}")
            created_template = registry_client.deployment_templates.create_or_update(template)

            # Verify creation
            assert created_template is not None
            assert created_template.liveness_probe is not None
            assert created_template.readiness_probe is not None
            assert created_template.liveness_probe.initial_delay == 60
            assert created_template.readiness_probe.initial_delay == 30

            sleep_if_live(5)

            # Get and verify probes
            retrieved_template = registry_client.deployment_templates.get(
                name=template_name,
                version="1"
            )
            assert retrieved_template.liveness_probe.path == "/health/liveness"
            assert retrieved_template.readiness_probe.path == "/health/readiness"

        finally:
            # Cleanup
            try:
                registry_client.deployment_templates.delete(name=template_name, version="1")
            except Exception as e:
                logger.warning(f"Failed to cleanup template: {e}")

    def test_deployment_template_with_request_settings(
        self,
        registry_client: MLClient,
        deployment_template_name: str,
    ) -> None:
        """Test creating a deployment template with custom request settings.

        Args:`n            registry_client: ML registry client fixture
            deployment_template_name: Generated unique template name
        """
        template_name = deployment_template_name
        cleanup_template(registry_client, template_name, "1")
        
        try:
            # Create request settings
            request_settings = OnlineRequestSettings(
                request_timeout_ms=10000,
                max_concurrent_requests_per_instance=5
            )

            # Create deployment template with request settings
            template = DeploymentTemplate(
                name=template_name,
                version="1",
                description="Template with request settings",
                deployment_template_type="Managed",
                environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                request_settings=request_settings,
                instance_count=2,
                allowed_instance_types="Standard_DS3_v2",
                default_instance_type="Standard_DS3_v2",
            )

            logger.info(f"Creating deployment template with request settings: {template_name}")
            created_template = registry_client.deployment_templates.create_or_update(template)

            # Verify creation
            assert created_template is not None
            assert created_template.request_settings is not None
            assert created_template.request_settings.request_timeout_ms == 10000
            assert created_template.request_settings.max_concurrent_requests_per_instance == 5

            sleep_if_live(5)

            # Get and verify request settings
            retrieved_template = registry_client.deployment_templates.get(
                name=template_name,
                version="1"
            )
            assert retrieved_template.request_settings.request_timeout_ms == 10000

        finally:
            # Cleanup
            try:
                registry_client.deployment_templates.delete(name=template_name, version="1")
            except Exception as e:
                logger.warning(f"Failed to cleanup template: {e}")

    def test_deployment_template_with_complex_environment_variables(
        self,
        registry_client: MLClient,
        deployment_template_name: str,
    ) -> None:
        """Test creating a deployment template with complex environment variables.

        Args:`n            registry_client: ML registry client fixture
            deployment_template_name: Generated unique template name
        """
        template_name = deployment_template_name
        cleanup_template(registry_client, template_name, "1")
        
        try:
            # Create complex environment variables
            env_vars = {
                "MODEL_PATH": "/var/azureml-app/models/primary",
                "BACKUP_MODEL_PATH": "/var/azureml-app/models/backup",
                "LOG_LEVEL": "DEBUG",
                "ENABLE_METRICS": "true",
                "BATCH_SIZE": "32",
                "TIMEOUT_SECONDS": "300",
                "API_VERSION": "v2",
                "CORS_ORIGINS": "http://localhost:3000,https://example.com",
                "MAX_RETRIES": "3",
                "CACHE_ENABLED": "true"
            }

            # Create deployment template
            template = DeploymentTemplate(
                name=template_name,
                version="1",
                description="Template with complex environment variables",
                deployment_template_type="Managed",
                environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                environment_variables=env_vars,
                instance_count=1,
                allowed_instance_types="Standard_DS2_v2",
                default_instance_type="Standard_DS2_v2",
            )

            logger.info(f"Creating deployment template with env vars: {template_name}")
            created_template = registry_client.deployment_templates.create_or_update(template)

            # Verify creation
            assert created_template is not None
            assert created_template.environment_variables is not None
            assert len(created_template.environment_variables) == 10
            assert created_template.environment_variables["MODEL_PATH"] == "/var/azureml-app/models/primary"
            assert created_template.environment_variables["ENABLE_METRICS"] == "true"

            sleep_if_live(5)

            # Get and verify all environment variables
            retrieved_template = registry_client.deployment_templates.get(
                name=template_name,
                version="1"
            )
            assert "CORS_ORIGINS" in retrieved_template.environment_variables
            assert "MAX_RETRIES" in retrieved_template.environment_variables

        finally:
            # Cleanup
            try:
                registry_client.deployment_templates.delete(name=template_name, version="1")
            except Exception as e:
                logger.warning(f"Failed to cleanup template: {e}")

    def test_deployment_template_version_management(
        self,
        registry_client: MLClient,
        deployment_template_name: str,
    ) -> None:
        """Test managing multiple versions of the same deployment template.

        Args:`n            registry_client: ML registry client fixture
            deployment_template_name: Generated unique template name
        """
        template_name = deployment_template_name
        # Clean up all versions from previous runs
        for i in range(1, 6):
            cleanup_template(registry_client, template_name, str(i))
        
        created_versions = []
        
        try:
            # Create multiple versions with different configurations
            for i in range(1, 6):
                template = DeploymentTemplate(
                    name=template_name,
                    version=str(i),
                    description=f"Version {i} of the template",
                    deployment_template_type="Managed",
                    environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                    instance_count=i,  # Different instance count per version
                    allowed_instance_types="Standard_DS2_v2",
                    default_instance_type="Standard_DS2_v2",
                    tags={"version_number": str(i), "test": "version_management"}
                )

                logger.info(f"Creating version {i} of template: {template_name}")
                created = registry_client.deployment_templates.create_or_update(template)
                created_versions.append(created)
                assert created.version == str(i)
                assert created.instance_count == i
                sleep_if_live(2)

            sleep_if_live(5)

            # Verify all versions exist
            for i in range(1, 6):
                retrieved = registry_client.deployment_templates.get(
                    name=template_name,
                    version=str(i)
                )
                assert retrieved.version == str(i)
                assert retrieved.instance_count == i
                assert retrieved.tags["version_number"] == str(i)

            # List all versions
            template_list = registry_client.deployment_templates.list(name=template_name)
            versions = list(template_list)
            
            # Verify we have at least our 5 versions
            assert len(versions) >= 5, f"Expected at least 5 versions but got {len(versions)}"

        finally:
            # Cleanup all versions
            for i in range(1, 6):
                try:
                    registry_client.deployment_templates.delete(name=template_name, version=str(i))
                except Exception as e:
                    logger.warning(f"Failed to cleanup version {i}: {e}")

    def test_deployment_template_with_tags(
        self,
        registry_client: MLClient,
        deployment_template_name: str,
    ) -> None:
        """Test deployment template with various tag combinations.

        Args:`n            registry_client: ML registry client fixture
            deployment_template_name: Generated unique template name
        """
        template_name = deployment_template_name
        cleanup_template(registry_client, template_name, "1")
        
        try:
            # Create template with multiple tags
            tags = {
                "environment": "production",
                "team": "ml-ops",
                "project": "recommendation-system",
                "cost-center": "ML-001",
                "compliance": "pci-dss",
                "version": "2.0",
                "owner": "ml-team@example.com",
                "created-by": "e2e-test"
            }

            template = DeploymentTemplate(
                name=template_name,
                version="1",
                description="Template with comprehensive tags",
                deployment_template_type="Managed",
                environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                tags=tags,
                instance_count=1,
                allowed_instance_types="Standard_DS2_v2",
                default_instance_type="Standard_DS2_v2",
            )

            logger.info(f"Creating deployment template with tags: {template_name}")
            created_template = registry_client.deployment_templates.create_or_update(template)

            # Verify tags
            assert created_template is not None
            assert len(created_template.tags) == 8
            assert created_template.tags["environment"] == "production"
            assert created_template.tags["team"] == "ml-ops"

            sleep_if_live(5)

            # Update tags
            retrieved_template = registry_client.deployment_templates.get(
                name=template_name,
                version="1"
            )
            retrieved_template.tags["updated"] = "true"
            retrieved_template.tags["update-date"] = "2024-01-01"

            updated_template = registry_client.deployment_templates.create_or_update(retrieved_template)
            assert "updated" in updated_template.tags
            assert len(updated_template.tags) == 10

        finally:
            # Cleanup
            try:
                registry_client.deployment_templates.delete(name=template_name, version="1")
            except Exception as e:
                logger.warning(f"Failed to cleanup template: {e}")

    def test_deployment_template_minimal_to_full_update(
        self,
        registry_client: MLClient,
        deployment_template_name: str,
    ) -> None:
        """Test updating a minimal template to a full-featured template.

        Args:`n            registry_client: ML registry client fixture
            deployment_template_name: Generated unique template name
        """
        template_name = deployment_template_name
        cleanup_template(registry_client, template_name, "1")
        
        try:
            # Create minimal template
            minimal_template = DeploymentTemplate(
                name=template_name,
                version="1",
                deployment_template_type="Managed",
                environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                instance_count=1,
                allowed_instance_types="Standard_DS2_v2",
                default_instance_type="Standard_DS2_v2",
            )

            logger.info(f"Creating minimal deployment template: {template_name}")
            created_template = registry_client.deployment_templates.create_or_update(minimal_template)
            assert created_template.description is None
            assert created_template.tags in [None, {}]

            sleep_if_live(5)

            # Create version 2 with full features (templates are immutable, can't update existing version)
            full_template = DeploymentTemplate(
                name=template_name,
                version="2",
                deployment_template_type="Managed",
                environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                description="Upgraded to full-featured template",
                tags={"upgraded": "true", "feature_level": "full"},
                environment_variables={
                    "FEATURE_SET": "complete",
                    "UPGRADED": "true"
                },
                request_settings=OnlineRequestSettings(
                    request_timeout_ms=8000,
                    max_concurrent_requests_per_instance=3
                ),
                instance_count=2,
                allowed_instance_types="Standard_DS2_v2",
                default_instance_type="Standard_DS2_v2",
            )

            logger.info(f"Creating full-featured template version 2: {template_name}")
            updated_template = registry_client.deployment_templates.create_or_update(full_template)

            # Verify upgrade
            assert updated_template.description == "Upgraded to full-featured template"
            assert updated_template.tags["upgraded"] == "true"
            assert updated_template.environment_variables["FEATURE_SET"] == "complete"
            assert updated_template.request_settings.request_timeout_ms == 8000

        finally:
            # Cleanup both versions
            for version in ["1", "2"]:
                try:
                    registry_client.deployment_templates.delete(name=template_name, version=version)
                except Exception as e:
                    logger.warning(f"Failed to cleanup template version {version}: {e}")

    def test_deployment_template_concurrent_versions(
        self,
        registry_client: MLClient,
        deployment_template_name: str,
    ) -> None:
        """Test creating and managing concurrent versions of deployment templates.

        Args:`n            registry_client: ML registry client fixture
            deployment_template_name: Generated unique template name
        """
        template_name = deployment_template_name
        versions = ["1", "2", "3"]
        # Clean up all versions from previous runs
        for version in versions:
            cleanup_template(registry_client, template_name, version)
        
        try:
            # Create all versions
            for version in versions:
                template = DeploymentTemplate(
                    name=template_name,
                    version=version,
                    description=f"Concurrent version {version}",
                    deployment_template_type="Managed",
                    environment="azureml://registries/testFeed/environments/test-sklearn-env/versions/1",
                    instance_count=int(version),
                    allowed_instance_types="Standard_DS2_v2",
                    default_instance_type="Standard_DS2_v2",
                    tags={"version": version}
                )

                logger.info(f"Creating concurrent version {version}: {template_name}")
                registry_client.deployment_templates.create_or_update(template)
                sleep_if_live(2)

            sleep_if_live(5)

            # Verify all versions coexist
            for version in versions:
                retrieved = registry_client.deployment_templates.get(
                    name=template_name,
                    version=version
                )
                assert retrieved.version == version
                assert retrieved.instance_count == int(version)

            # Archive one version while others remain active
            logger.info(f"Archiving version 2 of {template_name}")
            registry_client.deployment_templates.archive(name=template_name, version="2")
            sleep_if_live(3)

            # Verify version 2 is archived, others are not
            v1 = registry_client.deployment_templates.get(name=template_name, version="1")
            v2 = registry_client.deployment_templates.get(name=template_name, version="2")
            v3 = registry_client.deployment_templates.get(name=template_name, version="3")

            assert v1.stage != "Archived"
            assert v2.stage == "Archived"
            assert v3.stage != "Archived"

        finally:
            # Cleanup all versions
            for version in versions:
                try:
                    registry_client.deployment_templates.delete(name=template_name, version=version)
                except Exception as e:
                    logger.warning(f"Failed to cleanup version {version}: {e}")


