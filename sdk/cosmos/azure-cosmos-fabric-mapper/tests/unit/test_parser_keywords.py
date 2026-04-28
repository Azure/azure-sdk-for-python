"""Tests for parser handling of SQL keywords in column names."""
import pytest
from azure.cosmos.fabric_mapper.translate.parser import parse_cosmos_sql

class TestParserKeywordColumnNames:
    """Verify parser handles column names containing SQL keywords."""

    def test_order_in_column_name(self):
        ast = parse_cosmos_sql("SELECT c.order_date FROM c")
        assert "order_date" in ast.select_expr

    def test_group_in_column_name(self):
        ast = parse_cosmos_sql("SELECT c.group_name FROM c")
        assert "group_name" in ast.select_expr

    def test_from_in_column_name(self):
        ast = parse_cosmos_sql("SELECT c.id, c.data FROM c WHERE c.from_source = @src")
        assert "from_source" in ast.where_expr

    def test_offset_in_column_name(self):
        ast = parse_cosmos_sql("SELECT c.offset_val FROM c")
        assert "offset_val" in ast.select_expr

    def test_having_in_column_name(self):
        ast = parse_cosmos_sql("SELECT c.category FROM c GROUP BY c.category HAVING COUNT(1) > 0")
        assert ast.having_expr is not None

    def test_order_by_with_keyword_column(self):
        ast = parse_cosmos_sql("SELECT c.order_date FROM c ORDER BY c.order_date")
        assert "order_date" in ast.order_by


class TestParserStringLiteralKeywords:
    """Verify parser handles SQL keywords inside single-quoted string literals."""

    def test_string_literal_with_order_keyword(self):
        ast = parse_cosmos_sql("SELECT * FROM c WHERE c.name = 'ORDER processing'")
        assert "'ORDER processing'" in ast.where_expr

    def test_string_literal_with_group_keyword(self):
        ast = parse_cosmos_sql("SELECT * FROM c WHERE c.status = 'GROUP therapy'")
        assert "'GROUP therapy'" in ast.where_expr

    def test_string_literal_with_offset_keyword(self):
        ast = parse_cosmos_sql("SELECT * FROM c WHERE c.type = 'OFFSET value'")
        assert "'OFFSET value'" in ast.where_expr

    def test_multiple_string_literals(self):
        ast = parse_cosmos_sql("SELECT * FROM c WHERE c.a = 'ORDER' AND c.b = 'GROUP'")
        assert "'ORDER'" in ast.where_expr
        assert "'GROUP'" in ast.where_expr
