# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async

from test_base import TestBase, servicePreparer


class TestFeatureAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_feature_async(self, **kwargs) -> None:
        created_resource = None

        async with self.create_async_client(**kwargs) as project_client:
            try:
                # TODO(<feature>): exercise the public operation and assert behavior.
                created_resource = project_client
                assert created_resource is not None
            finally:
                if created_resource is not None:
                    # TODO(<feature>): await deletion of service resources created by the test.
                    pass
