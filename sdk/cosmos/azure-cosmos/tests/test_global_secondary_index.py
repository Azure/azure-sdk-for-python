# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Unit tests for GlobalSecondaryIndexDefinition."""

import pytest
from azure.cosmos._global_secondary_index import GlobalSecondaryIndexDefinition


class TestGlobalSecondaryIndexDefinition:
    """Tests for GlobalSecondaryIndexDefinition class."""

    def test_constructor_valid(self):
        """Test valid construction."""
        gsi = GlobalSecondaryIndexDefinition("source-container", "SELECT c.email, c.name FROM c")
        assert gsi.source_container_id == "source-container"
        assert gsi.definition == "SELECT c.email, c.name FROM c"
        assert gsi.source_container_rid is None
        assert gsi.status is None

    def test_constructor_rejects_none_source_container_id(self):
        """Test that None source_container_id raises ValueError."""
        with pytest.raises(ValueError, match="source_container_id cannot be None or empty"):
            GlobalSecondaryIndexDefinition(None, "SELECT c.email FROM c")

    def test_constructor_rejects_empty_source_container_id(self):
        """Test that empty source_container_id raises ValueError."""
        with pytest.raises(ValueError, match="source_container_id cannot be None or empty"):
            GlobalSecondaryIndexDefinition("", "SELECT c.email FROM c")

    def test_constructor_rejects_whitespace_source_container_id(self):
        """Test that whitespace-only source_container_id raises ValueError."""
        with pytest.raises(ValueError, match="source_container_id cannot be None or empty"):
            GlobalSecondaryIndexDefinition("   ", "SELECT c.email FROM c")

    def test_constructor_rejects_none_definition(self):
        """Test that None definition raises ValueError."""
        with pytest.raises(ValueError, match="definition cannot be None or empty"):
            GlobalSecondaryIndexDefinition("source-container", None)

    def test_constructor_rejects_empty_definition(self):
        """Test that empty definition raises ValueError."""
        with pytest.raises(ValueError, match="definition cannot be None or empty"):
            GlobalSecondaryIndexDefinition("source-container", "")

    def test_constructor_rejects_whitespace_definition(self):
        """Test that whitespace-only definition raises ValueError."""
        with pytest.raises(ValueError, match="definition cannot be None or empty"):
            GlobalSecondaryIndexDefinition("source-container", "   ")

    def test_to_dict_basic(self):
        """Test _to_dict produces correct wire format."""
        gsi = GlobalSecondaryIndexDefinition("my-source", "SELECT c.email FROM c")
        result = gsi._to_dict()
        assert result == {
            "sourceCollectionId": "my-source",
            "definition": "SELECT c.email FROM c",
        }

    def test_to_dict_with_server_fields(self):
        """Test _to_dict includes server-populated fields when present."""
        gsi = GlobalSecondaryIndexDefinition("my-source", "SELECT c.email FROM c")
        gsi._source_container_rid = "Z4oBANAPOuI="
        gsi._status = "Active"
        result = gsi._to_dict()
        assert result == {
            "sourceCollectionId": "my-source",
            "definition": "SELECT c.email FROM c",
            "sourceCollectionRid": "Z4oBANAPOuI=",
            "status": "Active",
        }

    def test_from_dict_valid(self):
        """Test _from_dict correctly deserializes."""
        data = {
            "sourceCollectionId": "source-container-id",
            "definition": "SELECT c.email, c.name FROM c",
            "sourceCollectionRid": "Z4oBANAPOuI=",
            "status": "Active",
        }
        gsi = GlobalSecondaryIndexDefinition._from_dict(data)
        assert gsi is not None
        assert gsi.source_container_id == "source-container-id"
        assert gsi.definition == "SELECT c.email, c.name FROM c"
        assert gsi.source_container_rid == "Z4oBANAPOuI="
        assert gsi.status == "Active"

    def test_from_dict_minimal(self):
        """Test _from_dict with only required fields."""
        data = {
            "sourceCollectionId": "source-container",
            "definition": "SELECT c.id FROM c",
        }
        gsi = GlobalSecondaryIndexDefinition._from_dict(data)
        assert gsi is not None
        assert gsi.source_container_id == "source-container"
        assert gsi.definition == "SELECT c.id FROM c"
        assert gsi.source_container_rid is None
        assert gsi.status is None

    def test_from_dict_returns_none_for_none_input(self):
        """Test _from_dict returns None for None input."""
        assert GlobalSecondaryIndexDefinition._from_dict(None) is None

    def test_from_dict_returns_none_for_missing_source_collection_id(self):
        """Test _from_dict returns None when sourceCollectionId is missing."""
        data = {"definition": "SELECT c.email FROM c"}
        assert GlobalSecondaryIndexDefinition._from_dict(data) is None

    def test_from_dict_returns_none_for_missing_definition(self):
        """Test _from_dict returns None when definition is missing."""
        data = {"sourceCollectionId": "source-container"}
        assert GlobalSecondaryIndexDefinition._from_dict(data) is None

    def test_from_dict_returns_none_for_empty_dict(self):
        """Test _from_dict returns None for empty dict."""
        assert GlobalSecondaryIndexDefinition._from_dict({}) is None

    def test_roundtrip(self):
        """Test serialization roundtrip."""
        original = GlobalSecondaryIndexDefinition("src-container", "SELECT c.name FROM c")
        original._source_container_rid = "abc123="
        original._status = "InitialBuildAfterCreate"
        
        wire_dict = original._to_dict()
        restored = GlobalSecondaryIndexDefinition._from_dict(wire_dict)
        
        assert restored is not None
        assert restored.source_container_id == original.source_container_id
        assert restored.definition == original.definition
        assert restored.source_container_rid == original.source_container_rid
        assert restored.status == original.status

    def test_all_status_values_accepted(self):
        """Test that all documented status values can be read."""
        statuses = [
            "Initializing",
            "InitialBuildAfterCreate",
            "InitialBuildAfterRestore",
            "Active",
            "DeleteInProgress",
        ]
        for status in statuses:
            data = {
                "sourceCollectionId": "src",
                "definition": "SELECT c.id FROM c",
                "status": status,
            }
            gsi = GlobalSecondaryIndexDefinition._from_dict(data)
            assert gsi is not None
            assert gsi.status == status

    def test_unknown_status_accepted(self):
        """Test that unknown status values are accepted for forward-compatibility."""
        data = {
            "sourceCollectionId": "src",
            "definition": "SELECT c.id FROM c",
            "status": "SomeNewFutureStatus",
        }
        gsi = GlobalSecondaryIndexDefinition._from_dict(data)
        assert gsi is not None
        assert gsi.status == "SomeNewFutureStatus"

    def test_properties_are_readonly(self):
        """Test that server-populated properties cannot be set directly via public API."""
        gsi = GlobalSecondaryIndexDefinition("src", "SELECT c.id FROM c")
        with pytest.raises(AttributeError):
            gsi.source_container_id = "new-value"
        with pytest.raises(AttributeError):
            gsi.definition = "new-value"
        with pytest.raises(AttributeError):
            gsi.source_container_rid = "new-value"
        with pytest.raises(AttributeError):
            gsi.status = "new-value"

    def test_import_from_azure_cosmos(self):
        """Test that GlobalSecondaryIndexDefinition is importable from azure.cosmos."""
        from azure.cosmos import GlobalSecondaryIndexDefinition as GSI
        assert GSI is GlobalSecondaryIndexDefinition

    def test_dual_write_pattern(self):
        """Test that dual-write produces both keys in the definition dict."""
        gsi = GlobalSecondaryIndexDefinition("source-container", "SELECT c.email FROM c")
        gsi_dict = gsi._to_dict()

        # Simulate the dual-write pattern used in database.py
        definition = {}
        definition["globalSecondaryIndexDefinition"] = gsi_dict
        definition["materializedViewDefinition"] = gsi_dict

        # Both keys must be present with identical content
        assert "globalSecondaryIndexDefinition" in definition
        assert "materializedViewDefinition" in definition
        assert definition["globalSecondaryIndexDefinition"] == definition["materializedViewDefinition"]
        assert definition["globalSecondaryIndexDefinition"]["sourceCollectionId"] == "source-container"
        assert definition["globalSecondaryIndexDefinition"]["definition"] == "SELECT c.email FROM c"
