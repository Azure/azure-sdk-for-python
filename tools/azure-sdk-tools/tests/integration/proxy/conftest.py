import pytest
from devtools_testutils import test_proxy


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
