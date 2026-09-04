# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy

from test_base import TestBase, servicePreparer


class TestFeature(TestBase):

    @servicePreparer()
    @recorded_by_proxy
    def test_feature(self, **kwargs) -> None:
        created_resource = None

        with self.create_client(**kwargs) as project_client:
            try:
                # TODO(<feature>): exercise the public operation and assert behavior.
                created_resource = project_client
                assert created_resource is not None
            finally:
                if created_resource is not None:
                    # TODO(<feature>): delete any service resources created by the test.
                    pass
