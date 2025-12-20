# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import numbers
import json
from typing import List
from opentelemetry.sdk.trace import Span


class GenAiTraceVerifier:

    def check_span_attributes(self, span, attributes):
        assert "https://opentelemetry.io/schemas/1.34.0" == span.instrumentation_scope.schema_url

        # Convert the list of tuples to a dictionary for easier lookup
        attribute_dict = dict(attributes)
        attribute_dict["az.namespace"] = "Microsoft.CognitiveServices"

        # First, check that all expected attributes are present in the span
        for expected_attribute_name in attribute_dict.keys():
            if expected_attribute_name not in span.attributes:
                raise AssertionError(
                    f"Expected attribute '{expected_attribute_name}' not found in span. "
                    f"Span has: {list(span.attributes.keys())}"
                )

        # Then, check that all attributes in the span are expected and have correct values
        for attribute_name in span.attributes.keys():
            # Check if the attribute name exists in the input attributes
            if attribute_name not in attribute_dict:
                raise AssertionError("Attribute name " + attribute_name + " not in attribute dictionary")

            attribute_value = attribute_dict[attribute_name]
            if isinstance(attribute_value, list):
                # Check if the attribute value in the span matches the provided list
                if span.attributes[attribute_name] != attribute_value:
                    raise AssertionError(
                        "Attribute value list "
                        + str(span.attributes[attribute_name])
                        + " does not match with "
                        + str(attribute_value)
                    )
            elif isinstance(attribute_value, tuple):
                # Check if the attribute value in the span matches the provided list
                if span.attributes[attribute_name] != attribute_value:
                    raise AssertionError(
                        "Attribute value tuple "
                        + str(span.attributes[attribute_name])
                        + " does not match with "
                        + str(attribute_value)
                    )
            else:
                # Check if the attribute value matches the provided value
                if attribute_value == "+":
                    if not isinstance(span.attributes[attribute_name], numbers.Number):
                        raise AssertionError(
                            "Attribute value " + str(span.attributes[attribute_name]) + " is not a number"
                        )
                    if span.attributes[attribute_name] < 0:
                        raise AssertionError("Attribute value " + str(span.attributes[attribute_name]) + " is negative")
                elif attribute_value != "" and span.attributes[attribute_name] != attribute_value:
                    raise AssertionError(
                        "Attribute value "
                        + str(span.attributes[attribute_name])
                        + " does not match with "
                        + str(attribute_value)
                    )
                # Check if the attribute value in the span is not empty when the provided value is ""
                elif attribute_value == "" and not span.attributes[attribute_name]:
                    raise AssertionError("Expected non-empty attribute value")

        return True

    def check_decorator_span_attributes(self, span: Span, attributes: List[tuple]) -> bool:
        # Convert the list of tuples to a dictionary for easier lookup
        attribute_dict = dict(attributes)

        # Ensure all required attributes are present in the span
        for attribute_name in attribute_dict.keys():
            if attribute_name not in span.attributes:
                raise AssertionError("Required attribute name " + attribute_name + " not found in span attributes")

        for attribute_name in span.attributes.keys():
            # Check if the attribute name exists in the input attributes
            if attribute_name not in attribute_dict:
                raise AssertionError("Attribute name " + attribute_name + " not in attribute dictionary")

            attribute_value = attribute_dict[attribute_name]
            span_value = span.attributes[attribute_name]

            if isinstance(attribute_value, (list, tuple)):
                # Convert both to lists for comparison
                if list(span_value) != list(attribute_value):
                    raise AssertionError(
                        "Attribute value list/tuple " + str(span_value) + " does not match with " + str(attribute_value)
                    )
            elif isinstance(attribute_value, dict):
                # Check if both are dictionaries and compare them
                if not isinstance(span_value, dict) or span_value != attribute_value:
                    raise AssertionError(
                        "Attribute value dict " + str(span_value) + " does not match with " + str(attribute_value)
                    )
            else:
                # Check if the attribute value matches the provided value
                if attribute_value == "+":
                    if not isinstance(span_value, numbers.Number):
                        raise AssertionError("Attribute value " + str(span_value) + " is not a number")
                    if span_value < 0:
                        raise AssertionError("Attribute value " + str(span_value) + " is negative")
                elif attribute_value != "" and span_value != attribute_value:
                    raise AssertionError(
                        "Attribute value " + str(span_value) + " does not match with " + str(attribute_value)
                    )
                # Check if the attribute value in the span is not empty when the provided value is ""
                elif attribute_value == "" and not span_value:
                    raise AssertionError("Expected non-empty attribute value")

        return True

    def is_valid_json(self, my_string):
        try:
            json.loads(my_string)
        except ValueError as e1:
            return False
        except TypeError as e2:
            return False
        return True

    def check_json_string(self, expected_json, actual_json):
        assert self.is_valid_json(expected_json) and self.is_valid_json(actual_json)
        expected_obj = json.loads(expected_json)
        actual_obj = json.loads(actual_json)

        # Handle both dict and list (array) formats
        if isinstance(expected_obj, list) and isinstance(actual_obj, list):
            return self.check_event_lists(expected_obj, actual_obj)
        elif isinstance(expected_obj, dict) and isinstance(actual_obj, dict):
            return self.check_event_attributes(expected_obj, actual_obj)
        else:
            raise AssertionError(
                f"check_json_string: type mismatch - expected {type(expected_obj).__name__}, got {type(actual_obj).__name__}"
            )

    def check_event_lists(self, expected_list, actual_list):
        """Check if two lists match, handling nested dicts/lists."""
        if len(expected_list) != len(actual_list):
            raise AssertionError(
                f"check_event_lists: list lengths do not match: {len(expected_list)} != {len(actual_list)}"
            )

        for i, (expected_item, actual_item) in enumerate(zip(expected_list, actual_list)):
            if isinstance(expected_item, dict) and isinstance(actual_item, dict):
                self.check_event_attributes(expected_item, actual_item)
            elif isinstance(expected_item, list) and isinstance(actual_item, list):
                self.check_event_lists(expected_item, actual_item)
            else:
                # For primitive values, do direct comparison
                if expected_item != actual_item:
                    raise AssertionError(
                        f"check_event_lists: item at index {i} does not match: {expected_item} != {actual_item}"
                    )
        return True

    def check_event_attributes(self, expected_dict, actual_dict):
        if set(expected_dict.keys()) != set(actual_dict.keys()):
            if isinstance(expected_dict, dict):
                expected_val = json.dumps(expected_dict)
            else:
                expected_val = expected_dict
            if isinstance(actual_dict, dict):
                actual_val = json.dumps(actual_dict)
            else:
                actual_val = actual_dict
            raise AssertionError(
                f"check_event_attributes: keys do not match: {set(expected_dict.keys())} != {set(actual_dict.keys())}. The actual dictionaries: {expected_val} != {actual_val}"
            )
        for key, expected_val in expected_dict.items():
            if key not in actual_dict:
                raise AssertionError(f"check_event_attributes: key {key} not found in actuals")
            actual_val = actual_dict[key]

            if self.is_valid_json(expected_val):
                if not self.is_valid_json(actual_val):
                    raise AssertionError(f"check_event_attributes: actual_val for {key} is not valid json")
                self.check_json_string(expected_val, actual_val)
            elif isinstance(expected_val, dict):
                if not isinstance(actual_val, dict):
                    raise AssertionError(f"check_event_attributes: actual_val for {key} is not dict")
                self.check_event_attributes(expected_val, actual_val)
            elif isinstance(expected_val, list):
                if not isinstance(actual_val, list):
                    raise AssertionError(f"check_event_attributes: actual_val for {key} is not list")
                self.check_event_lists(expected_val, actual_val)
            elif isinstance(expected_val, str) and expected_val == "*":
                if actual_val == "":
                    raise AssertionError(f"check_event_attributes: actual_val for {key} is empty")
            elif isinstance(expected_val, str) and expected_val == "+":
                assert isinstance(actual_val, numbers.Number), f"The {key} is not a number."
                assert actual_val > 0, f"The {key} is <0 {actual_val}"
            elif expected_val != actual_val:
                if isinstance(expected_val, dict):
                    expected_val = json.dumps(expected_val)
                if isinstance(actual_val, dict):
                    actual_val = json.dumps(actual_val)
                raise AssertionError(
                    f"check_event_attributes: values do not match for key {key}: {expected_val} != {actual_val}"
                )

    def check_span_events(self, span, expected_events):
        print("Checking span: " + span.name)
        span_events = list(span.events)  # Create a list of events from the span

        for expected_event in expected_events:
            for actual_event in span_events:
                if expected_event["name"] == actual_event.name:
                    self.check_event_attributes(expected_event["attributes"], actual_event.attributes._dict)
                    span_events.remove(actual_event)  # Remove the matched event from the span_events
                    break
            else:
                raise AssertionError("check_span_events: event not found")

        if len(span_events) > 0:  # If there are any additional events in the span_events
            unexpected_event_names = [event.name for event in span_events]
            raise AssertionError(f"check_span_events: unexpected event(s) found: {unexpected_event_names}")

        return True
