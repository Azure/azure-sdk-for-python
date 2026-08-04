import pytest


def pytest_addoption(parser):
    parser.addoption("--fast", action="store_true", default=False, help="skip slow integration tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: tests that may take several minutes")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--fast"):
        return

    skip_slow = pytest.mark.skip(reason="skipped by --fast")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
