"""Tests for Fabric mapper configuration validation."""

import pytest

from azure.cosmos.fabric_mapper.config import MirrorServingConfiguration
from azure.cosmos.fabric_mapper.errors import ConfigurationError


@pytest.mark.parametrize("field", ["fabric_server", "fabric_database"])
@pytest.mark.parametrize(
    "value", ["host;Encrypt=no", "host\nEncrypt=no", "host{value}"]
)
def test_connection_string_values_reject_delimiters(field, value):
    kwargs = {
        "fabric_server": "server.example",
        "fabric_database": "database",
        "fabric_table": "container",
    }
    kwargs[field] = value

    with pytest.raises(ConfigurationError, match=field):
        MirrorServingConfiguration(**kwargs).validate()
