from typing import Callable, Union
from devtools_testutils import AzureRecordedTestCase, is_live
import pytest

from azure.ai.ml import MLClient

from azure.ai.ml.entities import (
    ModelPackage,
    ModelConfiguration,
    AzureMLOnlineInferencingServer,
)


@pytest.mark.timeout(600)
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.production_experiences_test
class TestModelPackage(AzureRecordedTestCase):
    def test_model_package_workspace(self, client: MLClient):
        package_config = ModelPackage(
            target_environment="my-package-name",
            inferencing_server=AzureMLOnlineInferencingServer(),
            model_configuration=ModelConfiguration(mode="Copy"),
        )

        client.models.package("test-model-1", "1", package_config)
