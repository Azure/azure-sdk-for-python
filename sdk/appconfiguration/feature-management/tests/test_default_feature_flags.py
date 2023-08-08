# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from feature.management import FeatureManager, FeatureFilter
from devtools_testutils import AzureRecordedTestCase


class TestDefaultFeatureFlags(AzureRecordedTestCase):
    # method: feature_manager_creation
    def test_feature_manager_creation_with_targeting(self):
        feature_flags = {
            "FeatureFlags": [
                {
                    "id": "Target",
                    "description": "",
                    "enabled": "true",
                    "conditions": {
                        "client_filters": [
                            {
                                "name": "Microsoft.Targeting",
                                "parameters": {
                                    "Audience": {
                                        "Users": ["Adam"],
                                        "Groups": [{"Name": "Stage1", "RolloutPercentage": 100}],
                                        "DefaultRolloutPercentage": 50,
                                        "Exclusion": {"Users": [], "Groups": []},
                                    }
                                },
                            }
                        ]
                    },
                },
            ]
        }
        feature_manager = FeatureManager(feature_flags)
        assert feature_manager is not None
        # Adam is in the user audience
        assert feature_manager.is_enabled("Target", user="Adam")
        # Brian is not part of the 50% or default 50% of users
        assert not feature_manager.is_enabled("Target", user="Brian")
        # Brian is enabled because all of Stage 1 is enabled
        assert feature_manager.is_enabled("Target", user="Brian", groups=["Stage1"])
        # Brian is not enabled because he is not in Stage 2, group isn't looked at when user is targeted
        assert not feature_manager.is_enabled("Target", user="Brian", groups=["Stage2"])

    # method: feature_manager_creation
    def test_feature_manager_creation_with_timewindow(self):
        feature_flags = {
            "FeatureFlags": [
                {
                    "id": "Alpha",
                    "enabled": "true",
                    "conditions": {
                        "client_filters": [
                            {
                                "name": "Microsoft.TimeWindowFilter",
                                "parameters": {
                                    "Start": "Wed, 01 Jan 2020 00:00:00 GMT",
                                },
                            }
                        ]
                    },
                },
                {
                    "id": "Beta",
                    "enabled": "true",
                    "conditions": {
                        "client_filters": [
                            {
                                "name": "Microsoft.TimeWindowFilter",
                                "parameters": {
                                    "End": "Sat, 01 Jan 3020 00:00:00 GMT",
                                },
                            }
                        ]
                    },
                },
                {
                    "id": "Gamma",
                    "enabled": "true",
                    "conditions": {
                        "client_filters": [
                            {
                                "name": "Microsoft.TimeWindowFilter",
                                "parameters": {
                                    "End": "Wed, 01 Jan 2020 00:00:00 GMT",
                                },
                            }
                        ]
                    },
                },
                {
                    "id": "Delta",
                    "enabled": "true",
                    "conditions": {
                        "client_filters": [
                            {
                                "name": "Microsoft.TimeWindowFilter",
                                "parameters": {
                                    "Start": "Sat, 01 Jan 3020 00:00:00 GMT",
                                },
                            }
                        ]
                    },
                },
                {
                    "id": "Epsilon",
                    "enabled": "true",
                    "conditions": {
                        "client_filters": [
                            {
                                "name": "Microsoft.TimeWindowFilter",
                                "parameters": {
                                    "Start": "Wed, 01 Jan 2020 00:00:00 GMT",
                                    "End": "Sat, 01 Jan 3020 00:00:00 GMT",
                                },
                            }
                        ]
                    },
                },
                {
                    "id": "Foxtrot",
                    "enabled": "true",
                    "conditions": {
                        "client_filters": [
                            {
                                "name": "Microsoft.TimeWindowFilter",
                                "parameters": {
                                    "Start": "Wed, 01 Jan 2020 00:00:00 GMT",
                                    "End": "Fri, 01 Jan 2021 00:00:00 GMT",
                                },
                            }
                        ]
                    },
                },
            ]
        }
        feature_manager = FeatureManager(feature_flags)
        assert feature_manager is not None
        assert feature_manager.is_enabled("Alpha")
        assert feature_manager.is_enabled("Beta")
        assert not feature_manager.is_enabled("Gamma")
        assert not feature_manager.is_enabled("Delta")
        assert feature_manager.is_enabled("Epsilon")
        assert not feature_manager.is_enabled("Foxtrot")
