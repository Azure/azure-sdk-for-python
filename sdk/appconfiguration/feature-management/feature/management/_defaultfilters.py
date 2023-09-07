# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from ._featurefilters import FeatureFilter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import logging
import hashlib


class TargetingException(Exception):
    pass


class TimeWindowFilter(FeatureFilter):
    def evaluate(self, context, **kwargs):
        """Determain if the feature flag is enabled for the given context"""
        start = context.get("parameters", {}).get("Start")
        end = context.get("parameters", {}).get("End")

        current_time = datetime.now(timezone.utc)

        if not start and not end:
            logging.warn("TimeWindowFilter: Either Start or End are required to have as a parameter")
            return False

        start_time = parsedate_to_datetime(start) if start else None
        end_time = parsedate_to_datetime(end) if end else None

        return (start_time is None or start_time <= current_time) and (end_time is None or current_time < end_time)


class TargetingFilter(FeatureFilter):
    @staticmethod
    def _is_targeted(contextId, rollout_percentage):
        """Determine if the user is targeted for the given context"""
        # Alway return true if rollout percentage is 100
        if rollout_percentage == 100:
            return True

        hashed_contextId = hashlib.sha256(contextId.encode()).hexdigest()
        contextMarker = abs(int(hashed_contextId, 16))
        percentage = (contextMarker / (2**256 - 1)) * 100

        return percentage < rollout_percentage

    def _target_group(self, target_user, target_group, group, feature_flag_name):
        group_rollout_percentage = group.get("RolloutPercentage", 0)
        audienceContextId = target_user + "\n" + feature_flag_name + "\n" + group.get("Name", "")

        return self._is_targeted(audienceContextId, group_rollout_percentage)

    def evaluate(self, context, **kwargs):
        """Determain if the feature flag is enabled for the given context"""
        target_user = kwargs.pop("user", None)
        target_groups = kwargs.pop("groups", [])
        ignore_case = kwargs.pop("ignore_case", False)

        if not target_user and not (target_groups and len(target_groups) > 0):
            logging.warn("TargetingFilter: Name or Groups are required parameters")
            return False

        audience = context.get("parameters", {}).get("Audience", None)
        feature_flag_name = context.get("name", None)
        if not audience:
            raise TargetingException("Audience is required for TargetingFilter")

        users = audience.get("Users", [])
        groups = audience.get("Groups", [])
        default_rollout_percentage = audience.get("DefaultRolloutPercentage", 0)

        # Validate the audience settings
        if default_rollout_percentage < 0 or default_rollout_percentage > 100:
            raise TargetingException("DefaultRolloutPercentage must be between 0 and 100")

        for group in groups:
            if group.get("RolloutPercentage") < 0 or group.get("RolloutPercentage") > 100:
                raise TargetingException("RolloutPercentage must be between 0 and 100")

        exclusions = context.get("Exclusion", {})
        excluded_users = exclusions.get("Users", [])
        excluded_groups = exclusions.get("Groups", [])

        # Check if the user is excluded
        if target_user in excluded_users:
            return False

        # Check if the user is in an excluded group
        for group in excluded_groups:
            if group.get("Name") in target_groups:
                return False

        # Check if the user is targeted
        if target_user in users:
            return True

        # Check if the user is in a targeted group
        for group in groups:
            for target_group in target_groups:
                group_name = group.get("Name", "")
                if ignore_case:
                    target_group = target_group.lower()
                    group_name = group_name.lower()
                if group_name == target_group:
                    if self._target_group(target_user, target_group, group, feature_flag_name):
                        return True

        # Check if the user is in the default rollout
        contextId = target_user + "\n" + feature_flag_name
        return self._is_targeted(contextId, default_rollout_percentage)
