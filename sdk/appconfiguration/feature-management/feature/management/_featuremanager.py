# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._constants import FEATURE_MANAGEMENT_KEY
from ._defaultfilters import TimeWindowFilter, TargetingFilter


class FeatureManager:
    def __init__(self, feature_flags, **kwargs):
        feature_flags = feature_flags.get(FEATURE_MANAGEMENT_KEY, feature_flags)
        feature_flags_lst = feature_flags.get("FeatureFlags", feature_flags)
        self._feature_flags = {}
        for feature_flag in feature_flags_lst:
            self._feature_flags[feature_flag["id"]] = feature_flag

        feature_filters = {}
        feature_filters["Microsoft.TimeWindowFilter"] = TimeWindowFilter()
        feature_filters["Microsoft.Targeting"] = TargetingFilter()
        feature_filters.update(kwargs.pop("feature_filters", {}))
        self._filters = feature_filters

    def is_enabled(self, feature_flag_name, **kwargs):
        feature_flag = self._feature_flags.get(feature_flag_name, None)

        if not feature_flag:
            print("Feature flag not found")
            # Unknown feature flags are disabled by default
            return False

        if not _check_is_true(feature_flag["enabled"]):
            # Feature flags that are disabled are always disabled
            return False

        if len(feature_flag.get("conditions", {"client_filters": []})["client_filters"]) == 0:
            # Feature flags without any filters return evaluate
            return True

        if feature_flag.get("requirement_type", "Any") == "All":
            for feature_filter in feature_flag["conditions"]["client_filters"]:
                if feature_filter["name"] in self._filters:
                    if not self._filters[feature_filter["name"]].evaluate(feature_filter["parameters"], **kwargs):
                        return False
            return True
        else:
            for feature_filter in feature_flag["conditions"]["client_filters"]:
                if feature_filter["name"] in self._filters:
                    if self._filters[feature_filter["name"]].evaluate(feature_filter, **kwargs):
                        return True
            return False

    def list_feature_flag_names(self):
        return self._feature_flags.keys()


def _check_is_true(enabled):
    if enabled.lower() == "true":
        return True
    if enabled.lower() == "false":
        return False
    return enabled
