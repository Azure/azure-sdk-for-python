
import pytest

from azure.ai.ml._utils._storage_utils import get_ds_name_and_path_prefix


@pytest.mark.unittest
class TestStorageUtils:
    def test_storage_uri_to_prefix(
        self,
    ) -> None:
        # These are the asset storage patterns supported for download
        reg_uri_1 = 'https://demord45e277ef91c4410a8c.blob.core.windows.net/demoregist-16d33653-20bf-549b-a3c1-17d975359581/ExperimentRun/dcid.5823bbb4-bb28-497c-b9f2-1ff3a0778b10/model'
        reg_uri_2 = 'https://demord45e277ef91c4410a8c.blob.core.windows.net/demoregist-b46fb119-d3f8-5994-a971-a9c730227846/LocalUpload/0c225a0230907e61c00ea33eac35a54d/model.pkl'
        reg_uri_3 = 'https://banire53336a62aa143c383d.blob.core.windows.net/bani-reg-9717e928-33c2-50c2-90f5-f410b12b8727/sklearn_regression_model.pkl'
        workspace_uri_1 = 'azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/000000000000000/workspaces/nthande_test_3/datastores/workspaceblobstore/paths/LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model'

        assert get_ds_name_and_path_prefix(reg_uri_1, "registry_name") == (None,'ExperimentRun/dcid.5823bbb4-bb28-497c-b9f2-1ff3a0778b10/model')
        assert get_ds_name_and_path_prefix(reg_uri_2, "registry_name") == (None, 'LocalUpload/0c225a0230907e61c00ea33eac35a54d/model.pkl')
        assert get_ds_name_and_path_prefix(reg_uri_3, "registry_name") == (None, 'sklearn_regression_model.pkl')
        assert get_ds_name_and_path_prefix(workspace_uri_1) == ('workspaceblobstore','LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model')

        

    