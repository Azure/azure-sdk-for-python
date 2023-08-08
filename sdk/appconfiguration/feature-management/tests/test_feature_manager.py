# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from feature.management import FeatureManager, FeatureFilter
from devtools_testutils import AzureRecordedTestCase


class TestFeatureManagemer(AzureRecordedTestCase):
    # method: feature_manager_creation
    def test_empty_feature_manager_creation(self):
        feature_manager = FeatureManager({})
        assert feature_manager is not None
        assert not feature_manager.is_enabled("Alpha")

    # method: feature_manager_creation
    def test_basic_feature_manager_creation(self):
        feature_flags = {
            "FeatureFlags": [
                {"id": "Alpha", "description": "", "enabled": "true", "conditions": {"client_filters": []}},
                {"id": "Beta", "description": "", "enabled": "false", "conditions": {"client_filters": []}},
            ]
        }

        feature_manager = FeatureManager(feature_flags)
        assert feature_manager is not None
        assert feature_manager.is_enabled("Alpha")
        assert not feature_manager.is_enabled("Beta")

    # method: feature_manager_creation
    def test_feature_manager_creation_with_filters(self):
        feature_flags = {
            "FeatureFlags": [
                {
                    "id": "Alpha",
                    "description": "",
                    "enabled": "true",
                    "conditions": {"client_filters": [{"name": "AllwaysOn", "parameters": {}}]},
                },
                {
                    "id": "Beta",
                    "description": "",
                    "enabled": "false",
                    "conditions": {"client_filters": [{"name": "AllwaysOn", "parameters": {}}]},
                },
                {
                    "id": "Gamma",
                    "description": "",
                    "enabled": "True",
                    "conditions": {"client_filters": [{"name": "AllwaysOff", "parameters": {}}]},
                },
                {
                    "id": "Delta",
                    "description": "",
                    "enabled": "False",
                    "conditions": {"client_filters": [{"name": "AllwaysOff", "parameters": {}}]},
                },
            ]
        }

        feature_manager = FeatureManager(
            feature_flags, feature_filters={"AllwaysOn": AllwaysOn(), "AllwaysOff": AllwaysOff()}
        )
        assert feature_manager is not None
        assert feature_manager.is_enabled("Alpha")
        assert not feature_manager.is_enabled("Beta")
        assert not feature_manager.is_enabled("Gamma")
        assert not feature_manager.is_enabled("Delta")
        assert not feature_manager.is_enabled("Epsilon")


class AllwaysOn(FeatureFilter):
    def evaluate(self, context, **kwargs):
        return True


class AllwaysOff(FeatureFilter):
    def evaluate(self, context, **kwargs):
        return False
