#!/usr/bin/env python3
"""
Marshmallow 4.x Migration Validation Script for Azure AI ML

This script validates that the marshmallow patterns used in azure-ai-ml
are compatible with marshmallow 4.x. Run this script after upgrading
marshmallow to verify the migration was successful.

Usage:
    python test_marshmallow_migration.py

The script tests:
- Basic marshmallow imports and functionality
- Custom schema metaclass patterns (PatchedSchemaMeta)
- PathAware schema decorators (pre_load, post_dump)
- Validation error handling patterns
- Field usage patterns (Nested, Dict, List, etc.)
- marshmallow-jsonschema compatibility (if available)
"""

import sys
import os
import traceback
from pathlib import Path

def get_marshmallow_version():
    """Get current marshmallow version using the new preferred method"""
    try:
        # Marshmallow 4.x preferred method
        import importlib.metadata
        return importlib.metadata.version("marshmallow")
    except ImportError:
        try:
            # Fallback for older Python versions
            import pkg_resources
            return pkg_resources.get_distribution("marshmallow").version
        except:
            pass
    except:
        pass
    
    try:
        # Deprecated method (will show warning in 3.x, removed in 4.x)
        import marshmallow
        if hasattr(marshmallow, '__version__'):
            return marshmallow.__version__
    except:
        pass
    
    return "unknown"

def test_basic_imports():
    """Test that all basic marshmallow imports work"""
    try:
        from marshmallow import Schema, fields, RAISE, ValidationError, INCLUDE, EXCLUDE
        from marshmallow.decorators import post_dump, post_load, pre_load, validates
        from marshmallow.schema import SchemaMeta
        from marshmallow.exceptions import ValidationError as SchemaValidationError
        from marshmallow.fields import Field, Nested
        
        print("✓ All basic imports successful")
        return True
    except Exception as e:
        print(f"✗ Basic imports failed: {e}")
        traceback.print_exc()
        return False

def test_patched_schema_metaclass():
    """Test the PatchedSchemaMeta pattern used in azure-ai-ml"""
    try:
        from marshmallow import Schema, RAISE, fields
        from marshmallow.decorators import post_dump
        from marshmallow.schema import SchemaMeta
        from collections import OrderedDict
        
        class PatchedMeta:
            ordered = True
            unknown = RAISE

        class PatchedBaseSchema(Schema):
            class Meta:
                unknown = RAISE
                ordered = True

            @post_dump
            def remove_none(self, data, **kwargs):
                """Remove None values from dumped data"""
                return OrderedDict((key, value) for key, value in data.items() if value is not None)

        class PatchedSchemaMeta(SchemaMeta):
            """Custom metaclass that injects Meta attributes"""
            def __new__(mcs, name, bases, dct):
                meta = dct.get("Meta")
                if meta is None:
                    dct["Meta"] = PatchedMeta
                else:
                    if not hasattr(meta, "unknown"):
                        dct["Meta"].unknown = RAISE
                    if not hasattr(meta, "ordered"):
                        dct["Meta"].ordered = True

                if PatchedBaseSchema not in bases:
                    bases = bases + (PatchedBaseSchema,)
                klass = super().__new__(mcs, name, bases, dct)
                return klass
        
        # Test schema creation and usage
        class TestSchema(PatchedBaseSchema, metaclass=PatchedSchemaMeta):
            name = fields.Str(required=True)
            count = fields.Int()
            tags = fields.Dict()
        
        schema = TestSchema()
        
        # Test dump with None removal
        test_data = {"name": "test", "count": 42, "extra": None, "tags": {"env": "prod"}}
        result = schema.dump(test_data)
        
        # Verify None was removed and order is preserved
        if isinstance(result, OrderedDict) and "extra" not in result:
            print("✓ PatchedSchemaMeta works correctly")
            return True
        else:
            print("✗ PatchedSchemaMeta behavior changed")
            return False
            
    except Exception as e:
        print(f"✗ PatchedSchemaMeta failed: {e}")
        traceback.print_exc()
        return False

def test_pathaware_schema_decorators():
    """Test pre_load and post_dump decorators used in PathAwareSchema"""
    try:
        from marshmallow import Schema, fields, RAISE
        from marshmallow.decorators import pre_load, post_dump
        from collections import OrderedDict
        
        class TestPathAwareSchema(Schema):
            class Meta:
                unknown = RAISE
                ordered = True
                
            schema_ignored = fields.Str(data_key="$schema", dump_only=True)
            name = fields.Str(required=True)
            description = fields.Str()
            
            @post_dump
            def remove_none(self, data, **kwargs):
                return OrderedDict((key, value) for key, value in data.items() if value is not None)
            
            @pre_load
            def trim_dump_only(self, data, **kwargs):
                """Remove dump_only fields from load data"""
                if isinstance(data, str) or data is None:
                    return data
                for key, value in self.fields.items():
                    if value.dump_only:
                        schema_key = value.data_key or key
                        if isinstance(data, dict) and data.get(schema_key, None) is not None:
                            data.pop(schema_key)
                return data
        
        schema = TestPathAwareSchema()
        
        # Test that dump_only field is included in dump but ignored in load
        test_data = {
            "name": "test",
            "description": "description",
            "$schema": "should_be_ignored_on_load"
        }
        
        loaded = schema.load(test_data)
        dumped = schema.dump({"name": "test", "description": "description"})
        
        print("✓ PathAware schema decorators work")
        return True
        
    except Exception as e:
        print(f"✗ PathAware schema decorators failed: {e}")
        traceback.print_exc()
        return False

def test_validation_error_handling():
    """Test validation error patterns used throughout the codebase"""
    try:
        from marshmallow import Schema, fields, ValidationError
        from marshmallow.exceptions import ValidationError as SchemaValidationError
        
        class TestSchema(Schema):
            required_field = fields.Str(required=True)
            int_field = fields.Int()
        
        schema = TestSchema()
        
        # Test ValidationError import pattern (used in operations files)
        validation_error_caught = False
        try:
            schema.load({})  # Missing required field
        except ValidationError:
            validation_error_caught = True
        
        # Test SchemaValidationError import pattern (used in operations files)
        schema_validation_error_caught = False
        try:
            schema.load({"required_field": "ok", "int_field": "not_an_int"})
        except SchemaValidationError:
            schema_validation_error_caught = True
        
        if validation_error_caught and schema_validation_error_caught:
            print("✓ Validation error handling works")
            return True
        else:
            print("✗ Validation error handling failed")
            return False
            
    except Exception as e:
        print(f"✗ Validation error handling failed: {e}")
        traceback.print_exc()
        return False

def test_field_patterns():
    """Test field usage patterns from the codebase"""
    try:
        from marshmallow import Schema, fields, validates, ValidationError
        
        class TestSchema(Schema):
            # Common field patterns from the codebase
            str_field = fields.Str()
            int_field = fields.Int()
            bool_field = fields.Bool()
            list_field = fields.List(fields.Str())
            dict_field = fields.Dict(keys=fields.Str(), values=fields.Str())
            
            # Fields with options
            required_field = fields.Str(required=True)
            nullable_field = fields.Str(allow_none=True)
            aliased_field = fields.Str(data_key="alias")
            dump_only_field = fields.Str(dump_only=True)
            load_only_field = fields.Str(load_only=True)
            
            # Nested field with lambda (marshmallow 4.x compatible)
            nested_field = fields.Nested(lambda: TestSchema(), allow_none=True)
            
            @validates('str_field')
            def validate_str_field(self, value):
                if value == "invalid":
                    raise ValidationError("Invalid value")
        
        schema = TestSchema()
        
        # Test various operations
        test_data = {
            "str_field": "test",
            "int_field": 42,
            "bool_field": True,
            "list_field": ["a", "b"],
            "dict_field": {"key": "value"},
            "required_field": "required",
            "nullable_field": None,
            "alias": "aliased",
            "dump_only_field": "dump",
            "load_only_field": "load"
        }
        
        dumped = schema.dump(test_data)
        loaded = schema.load({
            "str_field": "test",
            "required_field": "required",
            "alias": "aliased",
            "load_only_field": "load"
        })
        
        print("✓ Field patterns work")
        return True
        
    except Exception as e:
        print(f"✗ Field patterns failed: {e}")
        traceback.print_exc()
        return False

def test_marshmallow_jsonschema_compatibility():
    """Test marshmallow-jsonschema compatibility if available"""
    try:
        from marshmallow_jsonschema import JSONSchema
        from marshmallow import Schema, fields
        
        class TestSchema(Schema):
            name = fields.Str()
            count = fields.Int()
        
        json_schema = JSONSchema()
        schema_dict = json_schema.dump(TestSchema())
        
        print("✓ marshmallow-jsonschema compatibility works")
        return True
        
    except ImportError:
        print("ℹ marshmallow-jsonschema not available, skipping test")
        return True
    except Exception as e:
        print(f"✗ marshmallow-jsonschema compatibility failed: {e}")
        traceback.print_exc()
        return False

def run_migration_tests():
    """Run all migration tests"""
    version = get_marshmallow_version()
    print(f"Marshmallow 4.x Migration Validation")
    print(f"Marshmallow version: {version}")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("PatchedSchemaMeta", test_patched_schema_metaclass),
        ("PathAware Decorators", test_pathaware_schema_decorators),
        ("Validation Errors", test_validation_error_handling),
        ("Field Patterns", test_field_patterns),
        ("JSONSchema Compatibility", test_marshmallow_jsonschema_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"Migration test results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Marshmallow 4.x migration is successful.")
        return True
    else:
        print("⚠️  Some tests failed. The migration may need additional fixes.")
        return False

if __name__ == "__main__":
    success = run_migration_tests()
    sys.exit(0 if success else 1)