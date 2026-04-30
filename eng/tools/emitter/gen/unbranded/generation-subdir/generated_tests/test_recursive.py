# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import RecursiveClientTestBase, RecursivePreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestRecursive(RecursiveClientTestBase):
    @RecursivePreparer()
    @recorded_by_proxy
    def test_put(self, recursive_endpoint):
        client = self.create_client(endpoint=recursive_endpoint)
        response = client.put(
            input={"level": 0, "extension": [...]},
        )

        # please add some check logic here by yourself
        # ...

    @RecursivePreparer()
    @recorded_by_proxy
    def test_get(self, recursive_endpoint):
        client = self.create_client(endpoint=recursive_endpoint)
        response = client.get()

        # please add some check logic here by yourself
        # ...
