# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_options.py`` — no network, no Cosmos emulator.

Cosmos SDK methods accept a long list of customer-facing keyword
arguments (``pre_trigger_include=``, ``priority=``, ``no_response=``,
``session_token=``, …). The request-byte protocol does not use those names —
it expects a separate "options" dictionary keyed by the internal
strings the service understands (``"preTriggerInclude"``,
``"priorityLevel"``, ``"responsePayloadOnWriteDisabled"``,
``"sessionToken"``, …).

The translation table lives in this one helper, ``_helpers/_options.py``:

* ``COMMON_OPTIONS`` — the kwarg-name → internal-option-key mapping.
* ``compose_options_from_kwargs(kwargs)`` — pulls the recognised
  kwargs out of the dict, translates them to internal keys, and
  returns a fresh options dict.

These two pieces are the seam between customer-facing names and the
byte shape. If they ever drift, the rust path can quietly emit
different request headers than the core-python path, and customer
options get silently dropped on one of the two backends. This file
covers that exact contract:

* The mapping table content is *exactly* what was carried over from
  the legacy ``_base._COMMON_OPTIONS`` on day one of the helper
  refactor — adding or renaming any entry must show up as a test
  diff so it gets reviewed.
* ``compose_options_from_kwargs`` translates correctly, pops
  recognised kwargs out of the input dict (so they aren't forwarded
  twice), leaves unknown kwargs alone, and accepts a pre-built
  ``request_options`` seed that gets overridden by any matching
  kwarg shortcut.
* The kwarg-mapping subset of the new helper agrees byte-for-byte
  with the same subset in the legacy ``_base.build_options``.
"""
import unittest

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._options import (
    COMMON_OPTIONS,
    compose_options_from_kwargs,
    get_common_options,
)


class TestCommonOptionsTableContent(unittest.TestCase):
    """Cover every entry in the kwarg → internal-option-key mapping table.

    The table is the contract. A typo in a customer-facing kwarg name
    would silently make the option drop out of the request; a typo in
    an internal-option-key would silently make the service ignore the
    option. Locking down the whole table here forces any change to come
    in as a reviewable test diff.
    """

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
        """``COMMON_OPTIONS`` must equal the fixed table exactly — no add / remove / rename slips through."""
        self.assertEqual(COMMON_OPTIONS, self.EXPECTED_ENTRIES)

    def test_legacy_alias_in_base_module_is_the_same_object(self):
        """``_base._COMMON_OPTIONS`` is the same dict object — catches a future contributor forking it."""
        from azure.cosmos import _base
        self.assertIs(_base._COMMON_OPTIONS, COMMON_OPTIONS)

    def test_get_common_options_returns_the_canonical_mapping(self):
        """The public read-only accessor returns the canonical dict (identity, not a copy)."""
        self.assertIs(get_common_options(), COMMON_OPTIONS)


class TestComposeOptionsFromKwargs(unittest.TestCase):
    """Behaviour of the pure ``compose_options_from_kwargs`` function.

    These tests cover: empty input, single-kwarg translation, the
    "pop out of the input dict" contract (so the kwarg isn't
    forwarded a second time to azure-core), unknown-kwarg
    pass-through, multi-kwarg translation, the ``request_options``
    seed mechanism, and freshness of the returned dict.
    """

    def test_empty_kwargs_returns_empty_options(self):
        """Empty input → empty options; the input dict is left untouched."""
        kwargs = {}
        self.assertEqual(compose_options_from_kwargs(kwargs), {})
        self.assertEqual(kwargs, {})

    def test_known_kwarg_is_translated_to_internal_key(self):
        """A recognised kwarg becomes its internal option key in the returned dict."""
        kwargs = {"pre_trigger_include": "validateOrder"}
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(options, {"preTriggerInclude": "validateOrder"})

    def test_known_kwarg_is_popped_out_of_kwargs(self):
        """A recognised kwarg is removed from the input dict (not forwarded twice).

        The caller forwards leftover kwargs to azure-core; if we left
        the recognised one in place it would be sent both as an
        option dict entry and as an azure-core kwarg.
        """
        kwargs = {"pre_trigger_include": "validateOrder", "extra": 1}
        compose_options_from_kwargs(kwargs)
        self.assertNotIn("pre_trigger_include", kwargs)
        # Unrecognised kwargs are left alone.
        self.assertEqual(kwargs, {"extra": 1})

    def test_unknown_kwarg_is_left_in_kwargs_and_not_in_options(self):
        """Unrecognised kwargs stay in the input dict and do not appear in the options dict."""
        kwargs = {"some_brand_new_kwarg": "x"}
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(options, {})
        self.assertEqual(kwargs, {"some_brand_new_kwarg": "x"})

    def test_multiple_known_kwargs_all_translated(self):
        """A realistic multi-kwarg call (the common ``create_item`` shape) — all recognised entries translated and popped."""
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
        self.assertEqual(kwargs, {})

    def test_request_options_seed_is_consumed_and_overridden(self):
        """A pre-built ``request_options`` seeds the result; any matching kwarg shortcut overrides it.

        This is how power-users mix a hand-crafted options dict with
        the convenience kwargs in the same call.
        """
        kwargs = {
            "request_options": {"preTriggerInclude": "OLD", "extra_seed": 1},
            "pre_trigger_include": "NEW",
        }
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(
            options,
            {"preTriggerInclude": "NEW", "extra_seed": 1},
        )
        # The request_options key itself is consumed too.
        self.assertNotIn("request_options", kwargs)

    def test_request_options_seed_with_no_kwarg_overrides(self):
        """A seed with no matching kwarg shortcut comes through verbatim."""
        kwargs = {"request_options": {"customKey": "customValue"}}
        options = compose_options_from_kwargs(kwargs)
        self.assertEqual(options, {"customKey": "customValue"})

    def test_returns_a_fresh_dict_each_call(self):
        """Two calls return two distinct dicts — no shared-state bug between calls."""
        first = compose_options_from_kwargs({"priority": "High"})
        second = compose_options_from_kwargs({"priority": "Low"})
        self.assertEqual(first, {"priorityLevel": "High"})
        self.assertEqual(second, {"priorityLevel": "Low"})
        self.assertIsNot(first, second)


class TestParityWithLegacyBuildOptions(unittest.TestCase):
    """Cross-check the kwarg-mapping subset against the legacy ``build_options``.

    ``build_options`` does extra work the new helper deliberately
    does *not* do (stamps ``OperationStartTime``, pulls
    ``read_timeout`` / ``timeout``, handles ``access_condition``).
    For the *kwarg-name → option-key* subset, both implementations
    must agree exactly. This class reproduces the legacy subset
    inline and asserts equality across a representative input table.
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
        """Inline reproduction of just the COMMON_OPTIONS branch of ``_base.build_options``.

        Importing ``build_options`` directly would also run its
        ``OperationStartTime`` stamping and access-condition branch,
        which the helper deliberately does not do — the comparison
        would no longer be apples-to-apples.
        """
        options = dict(kwargs.pop("request_options", {}) or {})
        for kwarg, opt_key in COMMON_OPTIONS.items():
            if kwarg in kwargs:
                options[opt_key] = kwargs.pop(kwarg)
        return options

    def test_kwarg_mapping_subset_matches_legacy(self):
        """For every input shape, helper and legacy produce the same options dict and consume the same kwargs."""
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
