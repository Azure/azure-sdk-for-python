"""Tests for Cosmos query validation and alias handling."""

import pytest

from azure.cosmos.fabric_mapper.config import MirrorServingConfiguration
from azure.cosmos.fabric_mapper.errors import UnsupportedCosmosQueryError
from azure.cosmos.fabric_mapper.translate import translate


@pytest.fixture
def config():
    return MirrorServingConfiguration("server.example", "database", "container")


def test_source_alias_is_preserved(config):
    result = translate(
        "SELECT p.id FROM products p WHERE p.active = true", None, config
    )

    assert result.sql == "SELECT p.id FROM [dbo].[container] AS p WHERE p.active = 1"


def test_source_alias_with_as_is_preserved(config):
    result = translate("SELECT p.id FROM products AS p", None, config)

    assert result.sql == "SELECT p.id FROM [dbo].[container] AS p"


def test_top_is_parsed_separately_from_projection(config):
    result = translate("SELECT TOP 5 * FROM c", None, config)

    assert result.sql == "SELECT TOP 5 * FROM [dbo].[container] AS c"


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "SELECT * FROM c WHERE c.active = true AND c.deleted = false",
            "SELECT * FROM [dbo].[container] AS c WHERE c.active = 1 AND c.deleted = 0",
        ),
        (
            "SELECT * FROM c WHERE c.deleted = null",
            "SELECT * FROM [dbo].[container] AS c WHERE c.deleted IS NULL",
        ),
        (
            "SELECT * FROM c WHERE c.deleted != null",
            "SELECT * FROM [dbo].[container] AS c WHERE c.deleted IS NOT NULL",
        ),
        (
            "SELECT c.from FROM c WHERE c.order = 1",
            "SELECT c.[from] FROM [dbo].[container] AS c WHERE c.[order] = 1",
        ),
        (
            "SELECT c.true, c.false FROM c",
            "SELECT c.[true], c.[false] FROM [dbo].[container] AS c",
        ),
        (
            "SELECT * FROM c WHERE (c.deleted) = null",
            "SELECT * FROM [dbo].[container] AS c WHERE (c.deleted) IS NULL",
        ),
        (
            "SELECT c.join, c.union, c.select FROM c",
            "SELECT c.[join], c.[union], c.[select] FROM [dbo].[container] AS c",
        ),
    ],
)
def test_cosmos_expressions_are_rewritten_for_fabric(config, query, expected):
    assert translate(query, None, config).sql == expected


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM c WHERE 1=1; DROP TABLE victims--",
        "SELECT * FROM c WHERE 1=1 DROP TABLE victims",
        "SELECT * FROM c WHERE 1=1 DELETE FROM victims",
        "SELECT * FROM c WHERE 1=1 EXEC dangerous_proc",
        "SELECT * FROM c WHERE 1=1 BEGIN TRANSACTION",
        "SELECT * FROM c WHERE 1=1 SET ROWCOUNT 1",
        "SELECT SUSER_SNAME() FROM c",
        "SELECT CRYPT_GEN_RANDOM(8000) FROM c",
        "SELECT VALUE c.id, c.name FROM c",
        "SELECT TOP 5 * FROM c ORDER BY c.id OFFSET 10 LIMIT 20",
        "SELECT * FROM c WHERE c.x + c.y = null",
        "SELECT * FROM c WHERE null = c.x + c.y",
        "SELECT * FROM c -- comment",
        "SELECT * FROM c WHERE c.id IN (SELECT VALUE x.id FROM x)",
        "SELECT * FROM c WHERE CONTAINS(c.name, 'admin')",
        "SELECT * FROM c JOIN child IN c.children",
    ],
)
def test_unsupported_or_stacked_sql_is_rejected(config, query):
    with pytest.raises(UnsupportedCosmosQueryError):
        translate(query, None, config)
