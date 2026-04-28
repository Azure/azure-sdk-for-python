"""Golden translation tests - verify query translation matches expected SQL."""

import json
from pathlib import Path

from azure.cosmos.fabric_mapper.config import MirrorServingConfiguration
from azure.cosmos.fabric_mapper.translate import translate


def test_golden_translation_fixtures_match():
    """Test that all golden query fixtures translate correctly."""
    fixtures = Path(__file__).parent / "fixtures" / "golden_queries.json"
    data = json.loads(fixtures.read_text(encoding="utf-8"))

    config = MirrorServingConfiguration(
        fabric_server="example.msit-datawarehouse.fabric.microsoft.com",
        fabric_database="spark-load-tests",
        fabric_table="normal-bulk",
        fabric_schema="dbo",
    )

    for item in data:
        res = translate(item["query"], item.get("parameters"), config)
        assert res.sql == item["expected_sql"], f"Failed on {item['name']}: SQL mismatch"
        assert res.params == item["expected_params"], f"Failed on {item['name']}: params mismatch"
        assert res.select_value == item["select_value"], f"Failed on {item['name']}: select_value mismatch"
