# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.mgmt.platformvalidation import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.aio import PlatformValidationMgmtClient as AsyncPlatformValidationMgmtClient
from azure.mgmt.platformvalidation.models import Operation
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
from devtools_testutils.aio import recorded_by_proxy_async


def assert_operations(operations: list[Operation]) -> None:
    names = {operation.name.lower() for operation in operations if operation.name}
    for action in ("read", "write", "delete"):
        assert f"microsoft.platformvalidation/cloudvalidations/{action}" in names
        assert f"microsoft.platformvalidation/cloudvalidations/validationexecutionplans/{action}" in names
    for operation in operations:
        # PUT and PATCH may advertise the same ARM permission name.
        assert operation.name and operation.name.lower().startswith("microsoft.platformvalidation/")
        assert operation.display is not None
        assert operation.display.operation
        assert operation.display.provider
        assert isinstance(operation.is_data_action, bool)


class TestOperations(AzureMgmtRecordedTestCase):
    @recorded_by_proxy
    def test_list_management_operations(self) -> None:
        with self.create_mgmt_client(PlatformValidationMgmtClient) as client:
            assert_operations(list(client.operations.list()))

    @AzureMgmtRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_list_management_operations_async(self) -> None:
        credential = self.get_credential(AsyncPlatformValidationMgmtClient, is_async=True)
        try:
            async with self.create_client_from_credential(
                AsyncPlatformValidationMgmtClient,
                credential,
                subscription_id=self.get_settings_value("SUBSCRIPTION_ID"),
            ) as client:
                assert_operations([operation async for operation in client.operations.list()])
        finally:
            await credential.close()
