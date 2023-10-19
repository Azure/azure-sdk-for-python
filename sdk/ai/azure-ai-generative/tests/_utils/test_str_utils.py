from azure.ai.generative._utils._str_utils import build_connection_id
from azure.ai.generative._project_scope import OperationScope

class TestStrUtils:
    def test_passes_with_connection_id(self):
        scope = OperationScope(subscription_id="fake_sub_id", resource_group_name="fake_res_grp_name", project_name="fake_ws_name")
        id = "/subscriptions/test_sub_id/resourceGroups/test_res_grp_name/providers/Microsoft.MachineLearningServices/workspaces/test_ws_name/connections/test_id"
        connection_id = build_connection_id(id, scope)
        print(connection_id)
        assert(connection_id == "/subscriptions/test_sub_id/resourceGroups/test_res_grp_name/providers/Microsoft.MachineLearningServices/workspaces/test_ws_name/connections/test_id")

    def test_passes_with_connection_name(self):
        scope = OperationScope(subscription_id="test_sub_id", resource_group_name="test_res_grp_name", project_name="test_ws_name")
        id = "test_id"
        connection_id = build_connection_id(id, scope)
        assert(connection_id == "/subscriptions/test_sub_id/resourceGroups/test_res_grp_name/providers/Microsoft.MachineLearningServices/workspaces/test_ws_name/connections/test_id")

    def test_passes_with_scope_optional_fields(self):
        scope = OperationScope(subscription_id=None, resource_group_name="test_res_grp_name", project_name="test_ws_name")
        assert(build_connection_id("test_id", scope) == "test_id")
        scope = OperationScope(subscription_id="test_sub_id", resource_group_name=None, project_name="test_ws_name")
        assert(build_connection_id("test_id", scope) == "test_id")
        scope = OperationScope(subscription_id="test_sub_id", resource_group_name="test_res_grp_name", project_name=None)
        assert(build_connection_id("test_id", scope) == "test_id")

    def test_passes_with_empty_id_string(self):
        scope = OperationScope(subscription_id="test_sub_id", resource_group_name="test_res_grp_name", project_name="test_ws_name")
        connection_id = build_connection_id("", scope)
        assert(connection_id == "")

    def test_passes_with_none(self):
        scope = OperationScope(subscription_id="test_sub_id", resource_group_name="test_res_grp_name", project_name="test_ws_name")
        connection_id = build_connection_id(None, scope)
        assert(connection_id == None)
