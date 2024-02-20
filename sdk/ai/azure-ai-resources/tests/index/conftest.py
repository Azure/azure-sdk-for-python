import logging
import uuid
from pathlib import Path
from typing import List

import pytest
from azure.ai.resources._index._utils.connections import connection_to_credential, get_metadata_from_connection

logger = logging.getLogger(__name__)

@pytest.fixture()
def test_dir():
    test_dir = Path(__file__).parent
    logger.info(f"test directory is {test_dir}")
    return test_dir


@pytest.fixture()
def test_data_dir(test_dir):
    test_data_dir = test_dir / "data"
    logger.info(f"test data directory is {test_data_dir}")
    return test_data_dir