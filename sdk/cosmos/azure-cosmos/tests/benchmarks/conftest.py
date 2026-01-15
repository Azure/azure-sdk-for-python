# Shared fixtures for benchmark tests

import pytest
import os


@pytest.fixture(scope="session")
def benchmark_config():
    """Configuration for benchmark tests."""
    return {
        "backend": os.environ.get("COSMOS_USE_RUST_BACKEND", "false"),
        "warmup_iterations": 10,
        "min_rounds": 50,
    }

