# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_options.py`` â—” no network, no Cosmos emulator.

Two things matter here and both are pinned by these tests:

1. The ``COMMON_OPTIONS`` mapping table content is *exactly* what the
   legacy ``_base._COMMON_OPTIONS`` had on day one of this refactor.
   Any silent drift in the kwarg-name -> internal-option-key mapping
   would make the rust path emit different request headers than the
   core-python path, which is the whole class of bug this helper exists
   to prevent.

2. ``compose_options_from_kwargs`` produces the same options-dict
   content for any given kwargs dict as the legacy ``build_options``
   produces for the kwarg-name-mapping subset of its work (we do not
   compare the side-effect fields legacy adds: OperationStartTime,
   read_timeout, accessCondition).
"""
import unittest

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._options import (
    COMMON_OPTIONS,
    compose_options_from_kwargs,
    get_common_options,
)


class TestCommonOptionsTableContent(unittest.TestCase):
    """The mapping table is the contract; pin every entry."""

    EXPECTED_ENTRIES = {
        "initial_headers": "initialHeaders",
        "pre_trigger_include": "preTriggerInclude",
        "post_trigger_include": "postTriggerInclude",
        "access_condition": "accessCondition",
        "session_token": "sessionToken",
        "resource_token_expiry_seconds": "resourceTokenExpirySeconds",
        "offer_enable_ru_per_minute_throughput": "offerEnableRUPerMinuteThroughput",
        "disable_ru_per_minute_usage": "disableRUPerMinuteUsage",
        "continuation": "continuation",
        "content_type": "contentType",
        "is_query_plan_request": "isQueryPlanRequest",
        "supported_query_features": "supportedQueryFeatures",
        "query_version": "queryVersion",
        "priority": "priorityLevel",
        "no_response": "responsePayloadOnWriteDisabled",
        "retry_write": Constants.Kwargs.RETRY_WRITE,
        "max_item_count": "maxItemCount",
        "throughput_bucket": "throughputBucket",
        "excluded_locations": Constants.Kwargs.EXCLUDED_LOCATIONS,
        "availability_strategy": Constants.Kwargs.AVAILABILITY_STRATEGY,
    }

    def test_table_has_exactly_the_documented_entries(self):
        # Catches accidental additions, removals, and renames in the
        # same assertion. If a contributor adds a new kwarg, they must
        # update this test, which forces them to think about whether
        # the rust path needs the same mapping.
        self.assertEqual(COMMON_OPTIONS, self.EXPECTED_ENTRIES)

    def test_legacy_alias_in_base_module_is_the_same_object(self):
        # ``_base._COMMON_OPTIONS`` is now a re-import of this dict.
        # Same-object assertion catches a future contributor copying
        # the dict into _base.py and silently forking it.
        from azure.cosmos import _base
        self.assertIs(_base._COMMON_OPTIONS, COMMON_OPTIONS)

    def test_get_common_options_returns_the_canonical_mapping(self):
        # Public read-only accessor. Identity check is fine because we
        # return the dict directly typed as Mapping.
        self.assertIs(get_common_options(), COMMON_OPTIONS)


class TestComposeOptionsFromKwargs(unittest.TestCase):
    """Behaviour of the pure compose function."""

    def test_empty_kwargs_returns_empty_options(self):
        kwargs = {}
        self.assertEqual(compose_options_from_kwargs(kwargs), {})
        # And does not invent keys in the original kwargs dict.
        self.assertEqual(kwargs, {})

    def test_known_kwarg_is_translated_to_internal_key(self):
        kwargs = {"pre_trigger_include": "validateOrder"}
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(options, {"preTriggerInclude": "validateOrder"})

    def test_known_kwarg_is_popped_out_of_kwargs(self):
        # The caller forwards remaining kwargs to azure-core; popping
        # avoids handing the same key down twice.
        kwargs = {"pre_trigger_include": "validateOrder", "extra": 1}
        compose_options_from_kwargs(kwargs)
        self.assertNotIn("pre_trigger_include", kwargs)
        # Unrecognised kwargs are left alone.
        self.assertEqual(kwargs, {"extra": 1})

    def test_unknown_kwarg_is_left_in_kwargs_and_not_in_options(self):
        kwargs = {"some_brand_new_kwarg": "x"}
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(options, {})
        self.assertEqual(kwargs, {"some_brand_new_kwarg": "x"})

    def test_multiple_known_kwargs_all_translated(self):
        # The common create_item shape: a few kwargs at once.
        kwargs = {
            "pre_trigger_include": "validateOrder",
            "post_trigger_include": "auditOrder",
            "priority": "High",
            "throughput_bucket": 2,
            "no_response": True,
            "session_token": "1:8#42=-1",
        }
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(
            options,
            {
                "preTriggerInclude": "validateOrder",
                "postTriggerInclude": "auditOrder",
                "priorityLevel": "High",
                "throughputBucket": 2,
                "responsePayloadOnWriteDisabled": True,
                "sessionToken": "1:8#42=-1",
            },
        )
        # All recognised kwargs popped; nothing left over.
        self.assertEqual(kwargs, {})

    def test_request_options_seed_is_consumed_and_overridden(self):
        # If the caller pre-built a request_options dict, it seeds the
        # result and any matching kwarg shortcut overrides its entry.
        kwargs = {
            "request_options": {"preTriggerInclude": "OLD", "extra_seed": 1},
            "pre_trigger_include": "NEW",
        }
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(
            options,
            {"preTriggerInclude": "NEW", "extra_seed": 1},
        )
        # The request_options key was consumed too.
        self.assertNotIn("request_options", kwargs)

    def test_request_options_seed_with_no_kwarg_overrides(self):
        kwargs = {"request_options": {"customKey": "customValue"}}
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(options, {"customKey": "customValue"})

    def test_returns_a_fresh_dict_each_call(self):
        # No accidental shared-state bug between calls.
        first = compose_options_from_kwargs({"priority": "High"})
        second = compose_options_from_kwargs({"priority": "Low"})
        self.assertEqual(first, {"priorityLevel": "High"})
        self.assertEqual(second, {"priorityLevel": "Low"})
        self.assertIsNot(first, second)


class TestParityWithLegacyBuildOptions(unittest.TestCase):
    """Cross-check the kwarg-mapping subset against legacy ``build_options``.

    ``build_options`` does extra work (stamps ``OperationStartTime``,
    pulls ``read_timeout`` / ``timeout``, handles ``access_condition``).
    For the *kwarg-name -> option-key* subset both must agree exactly.
    """

    KWARG_INPUTS = [
        {},
        {"pre_trigger_include": "validateOrder"},
        {
            "pre_trigger_include": "validateOrder",
            "post_trigger_include": "auditOrder",
            "priority": "High",
            "throughput_bucket": 2,
            "no_response": True,
        },
        {"some_unrecognized": "value"},
    ]

    def _compose_options_legacy_subset(self, kwargs):
        # Reproduces only the COMMON_OPTIONS branch of
        # ``_base.build_options`` so the comparison is apples-to-apples
        # with our pure helper. Importing build_options directly would
        # also run its OperationStartTime stamping and access-condition
        # branch, which the helper deliberately does not do.
        options = dict(kwargs.pop("request_options", {}) or {})
        for kwarg, opt_key in COMMON_OPTIONS.items():
            if kwarg in kwargs:
                options[opt_key] = kwargs.pop(kwarg)
        return options

    def test_kwarg_mapping_subset_matches_legacy(self):
        for inputs in self.KWARG_INPUTS:
            with self.subTest(kwargs=inputs):
                helper_in = dict(inputs)
                legacy_in = dict(inputs)
                self.assertEqual(
                    compose_options_from_kwargs(helper_in),
                    self._compose_options_legacy_subset(legacy_in),
                )
                # Both versions consumed the same kwargs.
                self.assertEqual(helper_in, legacy_in)


if __name__ == "__main__":
    unittest.main()
