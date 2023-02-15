import pytest

from azure.ai.ml._utils._storage_utils import get_ds_name_and_path_prefix


@pytest.mark.unittest
class TestStorageUtils:
    def test_storage_uri_to_prefix(
        self,
    ) -> None:
        # These are the asset storage patterns supported for download
        reg_uri_1 = "https://ccccccccddddd345.blob.core.windows.net/demoregist-16d33653-20bf-549b-a3c1-17d975359581/ExperimentRun/dcid.5823bbb4-bb28-497c-b9f2-1ff3a0778b10/model"
        reg_uri_2 = "https://ccccccccccc1978ccc.blob.core.windows.net/demoregist-b46fb119-d3f8-5994-a971-a9c730227846/LocalUpload/0c225a0230907e61c00ea33eac35a54d/model.pkl"
        reg_uri_3 = "https://ccccccccddr546ddd.blob.core.windows.net/some-reg-9717e928-33c2-50c2-90f5-f410b12b8727/sklearn_regression_model.pkl"
        workspace_uri_1 = "azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/000000000000000/workspaces/some_test_3/datastores/workspaceblobstore/paths/LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model"

        assert get_ds_name_and_path_prefix(reg_uri_1, "registry_name") == (
            None,
            "ExperimentRun/dcid.5823bbb4-bb28-497c-b9f2-1ff3a0778b10/model",
        )
        assert get_ds_name_and_path_prefix(reg_uri_2, "registry_name") == (
            None,
            "LocalUpload/0c225a0230907e61c00ea33eac35a54d/model.pkl",
        )
        assert get_ds_name_and_path_prefix(reg_uri_3, "registry_name") == (None, "sklearn_regression_model.pkl")
        assert get_ds_name_and_path_prefix(workspace_uri_1) == (
            "workspaceblobstore",
            "LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model",
        )

    def test_storage_uri_to_prefix_malformed(
        self,
    ) -> None:
        reg_uri_bad = "https://ccccccccddd4512d.blob.core.windows.net/5823bbb4-bb28-497c-b9f2-1ff3a0778b10"
        workspace_uri_bad = "azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/000000000000000/workspaces/some_test_3/datastores/workspaceblobstore/path/LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model"

        with pytest.raises(Exception) as e:
            get_ds_name_and_path_prefix(reg_uri_bad, "registry_name")
        assert "Registry asset URI could not be parsed." in str(e.value)

        with pytest.raises(Exception) as e:
            get_ds_name_and_path_prefix(workspace_uri_bad)
        assert "Workspace asset URI could not be parsed." in str(e.value)
