# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
Tests that verify model exports and field .value properties are correct.

Covers:
  1. All models in __all__ are importable from azure.ai.contentunderstanding.models.
  2. The .value property exists at runtime on each field class.
  3. The TYPE_CHECKING redeclarations are properly exported through __init__.py
     (i.e. they are listed in _patch.py's __all__).
  4. The runtime .value getter returns the correct underlying value_* attribute.
"""

import datetime
import pytest
from typing import Any, Dict, List, Optional

import azure.ai.contentunderstanding.models as models_module
from azure.ai.contentunderstanding.models import __all__ as models_all
from azure.ai.contentunderstanding.models import (
    ContentField,
    StringField,
    IntegerField,
    NumberField,
    BooleanField,
    DateField,
    TimeField,
    ArrayField,
    ObjectField,
    JsonField,
)
from azure.ai.contentunderstanding.models._patch import __all__ as patch_all


# Expected .value return types for TYPE_CHECKING redeclarations
FIELD_VALUE_TYPES = {
    "ContentField": (ContentField, Any),
    "StringField": (StringField, Optional[str]),
    "IntegerField": (IntegerField, Optional[int]),
    "NumberField": (NumberField, Optional[float]),
    "BooleanField": (BooleanField, Optional[bool]),
    "DateField": (DateField, Optional[str]),
    "TimeField": (TimeField, Optional[str]),
    "ArrayField": (ArrayField, Optional[List[Any]]),
    "ObjectField": (ObjectField, Optional[Dict[str, Any]]),
    "JsonField": (JsonField, Optional[Any]),
}


class TestModelExports:
    """Verify every model in __all__ is a real, importable symbol."""

    @pytest.mark.parametrize("name", models_all)
    def test_model_importable(self, name):
        """Every name in models.__all__ must be an importable, non-None attribute."""
        attr = getattr(models_module, name, None)
        assert attr is not None, (
            f"'{name}' is in models.__all__ but is not importable from "
            f"azure.ai.contentunderstanding.models"
        )

    @pytest.mark.parametrize("name", models_all)
    def test_model_is_class_or_type(self, name):
        """Every exported model should be a class, enum, or type alias."""
        attr = getattr(models_module, name)
        assert isinstance(attr, type) or callable(attr), (
            f"'{name}' should be a class or callable, got {type(attr)}"
        )

    def test_key_models_importable(self):
        """Explicitly test commonly used models are importable."""
        from azure.ai.contentunderstanding.models import (  # noqa: F401
            AnalysisResult,
            ContentAnalyzer,
            ContentAnalyzerConfig,
            DocumentContent,
            DocumentPage,
            DocumentTable,
            DocumentParagraph,
            AnalysisInput,
            AnalysisContent,
            CopyAuthorization,
        )

    def test_all_count_minimum(self):
        """Guard against __all__ accidentally shrinking (e.g. regeneration drops models)."""
        assert len(models_all) >= 69, (
            f"Expected at least 69 exports in models.__all__, got {len(models_all)}. "
            f"Did a regeneration drop models?"
        )


class TestFieldValueProperty:
    """Test that .value property exists on all field types at runtime."""

    @pytest.mark.parametrize("field_name,field_info", FIELD_VALUE_TYPES.items())
    def test_value_property_exists(self, field_name, field_info):
        """Verify .value is a property on each field class."""
        field_class, _ = field_info
        assert hasattr(field_class, "value"), (
            f"{field_name} should have a .value property"
        )
        assert isinstance(
            getattr(field_class, "value"), property
        ), f"{field_name}.value should be a property, got {type(getattr(field_class, 'value'))}"


class TestFieldExportsInPatchAll:
    """Test that all field TYPE_CHECKING redeclarations are exported via __all__."""

    @pytest.mark.parametrize("field_name", FIELD_VALUE_TYPES.keys())
    def test_field_in_patch_all(self, field_name):
        """Each field with a TYPE_CHECKING redeclaration must be in _patch.py's __all__.

        Without this, 'from ._patch import *' in __init__.py's TYPE_CHECKING block
        won't export the redeclared class, and type checkers will fall back to the
        generated _models version which lacks .value.
        """
        assert field_name in patch_all, (
            f"{field_name} must be in _patch.py __all__ for TYPE_CHECKING export to work. "
            f"Current __all__: {patch_all}"
        )


class TestFieldValueRuntime:
    """Test that .value returns the correct underlying attribute at runtime."""

    def test_string_field_value(self):
        sf = StringField({"valueString": "hello"})
        assert sf.value == "hello"

    def test_integer_field_value(self):
        nf = IntegerField({"valueInteger": 42})
        assert nf.value == 42

    def test_number_field_value(self):
        nf = NumberField({"valueNumber": 3.14})
        assert nf.value == 3.14

    def test_boolean_field_value(self):
        bf = BooleanField({"valueBoolean": True})
        assert bf.value is True

    def test_date_field_value(self):
        df = DateField({"valueDate": "2025-01-01"})
        assert df.value == datetime.date(2025, 1, 1)

    def test_time_field_value(self):
        tf = TimeField({"valueTime": "12:30:00"})
        assert tf.value == datetime.time(12, 30)

    def test_array_field_value(self):
        af = ArrayField({"valueArray": [{"valueString": "a"}]})
        assert af.value is not None
        assert len(af.value) == 1

    def test_object_field_value(self):
        of = ObjectField({"valueObject": {"key": {"valueString": "val"}}})
        assert of.value is not None
        assert "key" in of.value

    def test_json_field_value(self):
        jf = JsonField({"valueJson": {"arbitrary": "data"}})
        assert jf.value == {"arbitrary": "data"}

    def test_content_field_value_via_subclass(self):
        """ContentField.value works when accessed on a typed subclass."""
        sf = StringField({"valueString": "test"})
        # Access through the base class type annotation
        cf: ContentField = sf
        assert cf.value == "test"

    def test_field_value_none_when_empty(self):
        """Fields with no value_* set should return None."""
        sf = StringField({})
        assert sf.value is None
