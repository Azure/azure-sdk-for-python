from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml._azure_environments import CloudArgumentKeys
from azure.ai.ml.exceptions import MlException


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestMLClientInitBranches(AzureRecordedTestCase):
    def test_init_with_cloud_and_cloud_metadata_key_triggers_add_cloud_path(self, client: MLClient) -> None:
        # Provide a cloud name and include CLOUD_METADATA key to exercise that branch.
        # The implementation may raise if the provided cloud is unknown; assert that behavior.
        kwargs = {CloudArgumentKeys.CLOUD_METADATA: {"example": "metadata"}}
        with pytest.raises(MlException) as exc:
            MLClient(credential=client._credential, cloud="MyCloud", **kwargs)
        assert "Unknown cloud environment" in str(exc.value)
