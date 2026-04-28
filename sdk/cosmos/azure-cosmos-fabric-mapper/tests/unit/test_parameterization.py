"""Parameterization tests - ensure secrets never end up in SQL strings."""

from azure.cosmos.fabric_mapper.config import MirrorServingConfiguration
from azure.cosmos.fabric_mapper.translate import translate


def test_parameter_values_never_interpolated_into_sql():
    """Verify that parameter values are never interpolated into SQL text."""
    config = MirrorServingConfiguration(
        fabric_server="example",
        fabric_database="spark-load-tests",
        fabric_table="normal-bulk",
    )
    secret = "super_secret_value_12345"
    res = translate(
        "SELECT * FROM c WHERE c.partitionKey = @pk",
        parameters=[{"name": "@pk", "value": secret}],
        config=config,
    )
    # Secret must not appear in SQL
    assert secret not in res.sql, "Secret value was interpolated into SQL!"
    # Secret must be in params list
    assert res.params == [secret], "Secret value not in params list"


def test_multiple_parameters_maintain_order():
    """Verify that multiple parameters maintain correct order."""
    config = MirrorServingConfiguration(
        fabric_server="example",
        fabric_database="spark-load-tests",
        fabric_table="normal-bulk",
    )
    res = translate(
        "SELECT * FROM c WHERE c.pk = @pk AND c.status = @status AND c.value > @minValue",
        parameters=[
            {"name": "@pk", "value": "p1"},
            {"name": "@status", "value": "active"},
            {"name": "@minValue", "value": 100},
        ],
        config=config,
    )
    # SQL should have ? placeholders
    assert "?" in res.sql
    assert "@pk" not in res.sql
    assert "@status" not in res.sql
    assert "@minValue" not in res.sql
    # Params should be in correct order
    assert res.params == ["p1", "active", 100]
