# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._models import FeatureFlag, EvaluationContext

class FeatureManager():

    def __init__(self, feature_flags, **kwargs):
        self._parse_feature_flags(feature_flags)
        self._filters = kwargs.get('filters', {})

    def _parse_feature_flags(self, feature_flags_json):
        self._feature_flags = {}
        for feature_flag_json in feature_flags_json:
            enabled_for = []


            client_filters = feature_flag_json.get('conditions', {}).get('client_filters', [])

            for client_filter in client_filters:
                enabled_for.append(EvaluationContext(client_filter['name'], client_filter['parameters']))

            feature_flag_id = feature_flag_json.get('id', None)
            enabled = feature_flag_json.get('enabled', False)
            requirement_type = feature_flag_json.get('conditions', {}).get('requirement_type', "Any")

            feature_flag = FeatureFlag(feature_flag_id, enabled, requirement_type, enabled_for)
            self._feature_flags[feature_flag_id] = feature_flag

    def is_enabled(self, feature_flag_name, **kwargs):
        feature_flag = self._feature_flags.get(feature_flag_name, None)

        if not feature_flag:
            # Unknown feature flags are disabled by default
            return False

        if not feature_flag.evaluate:
            # Feature flags that are disabled are always disabled
            return False

        if len(feature_flag.enabled_for) == 0:
            # Feature flags without any filters return evaluate
            return feature_flag.evaluate
        
        if feature_flag.requirement_type == "All":
            for feature_filter in feature_flag.enabled_for:
                if feature_filter.name in self._filters:
                    if not self._filters[feature_filter.name].evaluate(feature_filter.parameters, **kwargs):
                        return False
            return True
        else:
            for feature_filter in feature_flag.enabled_for:
                if feature_filter.name in self._filters:
                    if self._filters[feature_filter.name].evaluate(feature_filter, **kwargs):
                        return feature_flag.evaluate
            return False
