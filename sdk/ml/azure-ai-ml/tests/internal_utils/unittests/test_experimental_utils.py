import logging
import pytest
import unittest
from azure.ai.ml._utils._experimental import experimental, _warning_cache
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from marshmallow.schema import Schema
from azure.ai.ml._schema.core.fields import NestedField, ExperimentalField
from azure.ai.ml.constants import (
    EXPERIMENTAL_FIELD_MESSAGE,
    EXPERIMENTAL_CLASS_MESSAGE,
    EXPERIMENTAL_METHOD_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
)


@experimental
class ExperimentalClass(RestTranslatableMixin):
    def __init__(self, value=5):
        self._value = value
        pass

    @experimental
    def experimental_method(self):
        pass

    @classmethod
    def _from_rest_object(cls, rest_obj) -> "ExperimentalClass":
        return ExperimentalClass()

    @property
    def value(self):
        return self._value

    @value.setter
    @experimental
    def value(self, value):
        pass


@experimental
def experimental_function():
    pass


class DummySchema(Schema):
    pass


class FooSchema(Schema):
    mock_field = NestedField(DummySchema)


class BarSchema(Schema):
    mock_field = ExperimentalField(NestedField(DummySchema))


@pytest.mark.unittest
class TestExperimentalUtils(unittest.TestCase):
    def setUp(self):
        _warning_cache.clear()

    def test_experimental_decorator_on_class(self):
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            _ = ExperimentalClass()

        self.assertTrue(EXPERIMENTAL_CLASS_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

        self.assertTrue(ExperimentalClass.__doc__.startswith(".. note::"))
        self.assertTrue(EXPERIMENTAL_CLASS_MESSAGE in ExperimentalClass.__doc__)
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in ExperimentalClass.__doc__)

    def test_experimental_decorator_on_method(self):
        obj = ExperimentalClass()
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            obj.experimental_method()

        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

        self.assertTrue(ExperimentalClass.experimental_method.__doc__.startswith(".. note::"))
        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in ExperimentalClass.experimental_method.__doc__)
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in ExperimentalClass.experimental_method.__doc__)

    def test_experimental_decorator_on_property(self):
        obj = ExperimentalClass()
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            obj.value = 5

        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

        self.assertTrue(ExperimentalClass.experimental_method.__doc__.startswith(".. note::"))
        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in ExperimentalClass.experimental_method.__doc__)
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in ExperimentalClass.experimental_method.__doc__)

    def test_experimental_decorator_on_function(self):
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            experimental_function()

        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

        self.assertTrue(ExperimentalClass.experimental_method.__doc__.startswith(".. note::"))
        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in ExperimentalClass.experimental_method.__doc__)
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in ExperimentalClass.experimental_method.__doc__)

    def test_experimental_decorator_no_duplicated_warnings(self):
        # call experimental function multiple times
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            for x in range(5):
                experimental_function()

        self.assertEquals(1, len(cm.output))
        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

        # call experimental class method multiple times
        obj = ExperimentalClass()
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            for x in range(5):
                obj.experimental_method()

        self.assertEquals(1, len(cm.output))
        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

        # call experimental class method multiple times
        obj = ExperimentalClass()
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            for x in range(5):
                obj.value = 5

        self.assertEquals(1, len(cm.output))
        self.assertTrue(EXPERIMENTAL_METHOD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

    def test_experimental_decorator_should_show_no_warning_when_load_from_rest(self):
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            # We want to assert there are no warnings, but the 'assertLogs' method does not support that.
            # Therefore, we are adding a dummy warning, and then we will assert it is the only warning.
            logging.getLogger(experimental.__module__).warning("Dummy warning")
            ExperimentalClass._from_rest_object(dict())

        self.assertEquals(1, len(cm.output))

    def test_experimental_decorator_should_show_no_warning_when_load_from_schema(self):
        with self.assertLogs(experimental.__module__, "WARNING") as cm:
            # We want to assert there are no warnings, but the 'assertLogs' method does not support that.
            # Therefore, we are adding a dummy warning, and then we will assert it is the only warning.
            logging.getLogger(experimental.__module__).warning("Dummy warning")
            schema = FooSchema()
            input_data = {"mock_field": {}}
            schema.load(input_data)

        self.assertEquals(1, len(cm.output))

    def test_experimental_field(self):
        with self.assertLogs(ExperimentalField.__module__, "WARNING") as cm:
            schema = BarSchema()
            input_data = {"mock_field": {}}
            schema.load(input_data)

        self.assertEquals(1, len(cm.output))
        self.assertTrue(EXPERIMENTAL_FIELD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])

    def test_experimental_field_no_duplicated_warnings(self):
        with self.assertLogs(ExperimentalField.__module__, "WARNING") as cm:
            schema = BarSchema()
            input_data = {"mock_field": {}}

            # load multiple times
            for x in range(5):
                schema.load(input_data)

        self.assertEquals(1, len(cm.output))
        self.assertTrue(EXPERIMENTAL_FIELD_MESSAGE in cm.output[0])
        self.assertTrue(EXPERIMENTAL_LINK_MESSAGE in cm.output[0])
