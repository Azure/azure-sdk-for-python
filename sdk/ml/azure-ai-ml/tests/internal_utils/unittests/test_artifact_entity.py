import pytest
from azure.ai.ml.entities._assets import Data


@pytest.mark.unittest
class TestArtifactEntity:
    def test_eq_neq(self) -> None:
        data = Data(name="name", version="16", path=".")
        same_data = Data(name="name", version="16", path=".")
        diff_data = Data(name=data.name, version=data.version, path=data.path, description="different dataset")

        assert data == same_data != diff_data
