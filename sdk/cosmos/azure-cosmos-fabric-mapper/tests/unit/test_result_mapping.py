"""Result mapping tests - verify tabular rows map to Cosmos-like documents."""

from azure.cosmos.fabric_mapper.driver.base import ResultSet
from azure.cosmos.fabric_mapper.results import map_result_set


def test_result_mapping_to_dicts():
    """Test mapping tabular rows to dict documents."""
    rs = ResultSet(columns=["id", "partitionKey", "value"], rows=[("1", "p1", 100), ("2", "p2", 200)])
    items = map_result_set(rs, select_value=False)
    assert items == [
        {"id": "1", "partitionKey": "p1", "value": 100},
        {"id": "2", "partitionKey": "p2", "value": 200},
    ]


def test_select_value_mapping_scalars():
    """Test SELECT VALUE returns list of scalars, not dicts."""
    rs = ResultSet(columns=["value"], rows=[(1,), (2,), (3,)])
    values = map_result_set(rs, select_value=True)
    assert values == [1, 2, 3]


def test_select_value_with_count():
    """Test SELECT VALUE COUNT(1) returns single value."""
    rs = ResultSet(columns=["count"], rows=[(1000000,)])
    values = map_result_set(rs, select_value=True)
    assert values == [1000000]


def test_empty_result_set():
    """Test empty result set returns empty list."""
    rs = ResultSet(columns=["id", "partitionKey"], rows=[])
    items = map_result_set(rs, select_value=False)
    assert items == []


def test_null_values_preserved():
    """Test that NULL values in results are preserved."""
    rs = ResultSet(columns=["id", "value"], rows=[("1", None), ("2", 100)])
    items = map_result_set(rs, select_value=False)
    assert items == [{"id": "1", "value": None}, {"id": "2", "value": 100}]
