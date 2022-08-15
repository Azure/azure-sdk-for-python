import pytest


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
