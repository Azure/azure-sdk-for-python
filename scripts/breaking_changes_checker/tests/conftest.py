def pytest_configure(config):
    config.addinivalue_line("markers", "slow: tests that may take up to 10 minutes")
