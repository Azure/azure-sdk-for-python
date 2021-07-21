import pytest
from azure.eventhub.extensions.checkpointstoretable import TableCheckpointStore

def test_constructor():
    client = TableCheckpointStore()
    assert client is not None
