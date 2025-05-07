# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import random
import base64
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Mapping, Any
from azure.appconfiguration import (  # type:ignore # pylint:disable=no-name-in-module
    FeatureFlagConfigurationSetting,
)
from ._constants import (
    PERCENTAGE_FILTER_NAMES,
    TIME_WINDOW_FILTER_NAMES,
    TARGETING_FILTER_NAMES,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
    TELEMETRY_KEY,
    METADATA_KEY,
    ETAG_KEY,
    FEATURE_FLAG_REFERENCE_KEY,
    ALLOCATION_ID_KEY,
)

FALLBACK_CLIENT_REFRESH_EXPIRED_INTERVAL = 3600  # 1 hour in seconds
MINIMAL_CLIENT_REFRESH_INTERVAL = 30  # 30 seconds

JSON = Mapping[str, Any]


@dataclass
class _ConfigurationClientWrapperBase:
    endpoint: str

    @staticmethod
    def _generate_allocation_id(feature_flag_value: Dict[str, JSON]) -> Optional[str]:
        """
        Generates an allocation ID for the specified feature.
        seed=123abc\ndefault_when_enabled=Control\npercentiles=0,Control,20;20,Test,100\nvariants=Control,standard;Test,special # pylint:disable=line-too-long

        :param  Dict[str, JSON] feature_flag_value: The feature to generate an allocation ID for.
        :rtype: str
        :return: The allocation ID.
        """

        allocation_id = ""
        allocated_variants = []

        allocation: Optional[JSON] = feature_flag_value.get("allocation")

        if not allocation:
            return None

        # Seed
        allocation_id = f"seed={allocation.get('seed', '')}"

        # DefaultWhenEnabled
        if "default_when_enabled" in allocation:
            allocated_variants.append(allocation.get("default_when_enabled"))

        allocation_id += f"\ndefault_when_enabled={allocation.get('default_when_enabled', '')}"

        # Percentile
        allocation_id += "\npercentiles="

        percentile = allocation.get("percentile")

        if percentile:
            percentile_allocations = sorted(
                (x for x in percentile if x.get("from") != x.get("to")),
                key=lambda x: x.get("from"),
            )

            for percentile_allocation in percentile_allocations:
                if "variant" in percentile_allocation:
                    allocated_variants.append(percentile_allocation.get("variant"))

            allocation_id += ";".join(
                f"{pa.get('from')}," f"{base64.b64encode(pa.get('variant').encode()).decode()}," f"{pa.get('to')}"
                for pa in percentile_allocations
            )

        if not allocated_variants and not allocation.get("seed"):
            return None

        # Variants
        allocation_id += "\nvariants="

        variants_value = feature_flag_value.get("variants")
        if variants_value and (isinstance(variants_value, list) or all(isinstance(v, dict) for v in variants_value)):
            if (
                allocated_variants
                and isinstance(variants_value, list)
                and all(isinstance(v, dict) for v in variants_value)
            ):
                sorted_variants: List[Dict[str, Any]] = sorted(
                    (v for v in variants_value if v.get("name") in allocated_variants),
                    key=lambda v: v.get("name"),
                )

                for v in sorted_variants:
                    allocation_id += f"{base64.b64encode(v.get('name', '').encode()).decode()},"
                    if "configuration_value" in v:
                        allocation_id += (
                            f"{json.dumps(v.get('configuration_value', ''), separators=(',', ':'), sort_keys=True)}"
                        )
                    allocation_id += ";"
                if sorted_variants:
                    allocation_id = allocation_id[:-1]

        # Create a sha256 hash of the allocation_id
        hash_object = hashlib.sha256(allocation_id.encode())
        hash_digest = hash_object.digest()

        # Encode the first 15 bytes in base64 url
        return base64.urlsafe_b64encode(hash_digest[:15]).decode()

    def _feature_flag_telemetry(
        self, endpoint: str, feature_flag: FeatureFlagConfigurationSetting, feature_flag_value: Dict
    ):
        if TELEMETRY_KEY in feature_flag_value:
            if METADATA_KEY not in feature_flag_value[TELEMETRY_KEY]:
                feature_flag_value[TELEMETRY_KEY][METADATA_KEY] = {}
            feature_flag_value[TELEMETRY_KEY][METADATA_KEY][ETAG_KEY] = feature_flag.etag

            if not endpoint.endswith("/"):
                endpoint += "/"
            feature_flag_reference = f"{endpoint}kv/{feature_flag.key}"
            if feature_flag.label and not feature_flag.label.isspace():
                feature_flag_reference += f"?label={feature_flag.label}"
            if feature_flag_value[TELEMETRY_KEY].get("enabled"):
                feature_flag_value[TELEMETRY_KEY][METADATA_KEY][FEATURE_FLAG_REFERENCE_KEY] = feature_flag_reference
                allocation_id = self._generate_allocation_id(feature_flag_value)
                if allocation_id:
                    feature_flag_value[TELEMETRY_KEY][METADATA_KEY][ALLOCATION_ID_KEY] = allocation_id

    def _feature_flag_appconfig_telemetry(
        self, feature_flag: FeatureFlagConfigurationSetting, filters_used: Dict[str, bool]
    ):
        if feature_flag.filters:
            for filter in feature_flag.filters:
                if filter.get("name") in PERCENTAGE_FILTER_NAMES:
                    filters_used[PERCENTAGE_FILTER_KEY] = True
                elif filter.get("name") in TIME_WINDOW_FILTER_NAMES:
                    filters_used[TIME_WINDOW_FILTER_KEY] = True
                elif filter.get("name") in TARGETING_FILTER_NAMES:
                    filters_used[TARGETING_FILTER_KEY] = True
                else:
                    filters_used[CUSTOM_FILTER_KEY] = True


class ConfigurationClientManagerBase:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        endpoint: str,
        user_agent: str,
        retry_total,
        retry_backoff_max,
        replica_discovery_enabled,
        min_backoff_sec,
        max_backoff_sec,
        _load_balancing_enabled: bool,
        **kwargs,
    ):
        self._last_active_client_name = ""
        self._original_endpoint = endpoint
        self._user_agent = user_agent
        self._retry_total = retry_total
        self._retry_backoff_max = retry_backoff_max
        self._replica_discovery_enabled = replica_discovery_enabled
        self._next_update_time: Optional[float] = None
        self._args = dict(kwargs)
        self._min_backoff_sec = min_backoff_sec
        self._max_backoff_sec = max_backoff_sec
        self._load_balancing_enabled = _load_balancing_enabled

    def _calculate_backoff(self, attempts: int) -> float:
        max_attempts = 63
        ms_per_second = 1000  # 1 Second in milliseconds

        min_backoff_milliseconds = self._min_backoff_sec * ms_per_second
        max_backoff_milliseconds = self._max_backoff_sec * ms_per_second

        if self._max_backoff_sec <= self._min_backoff_sec:
            return min_backoff_milliseconds

        calculated_milliseconds = max(1, min_backoff_milliseconds) * (1 << min(attempts, max_attempts))

        if calculated_milliseconds > max_backoff_milliseconds or calculated_milliseconds <= 0:
            calculated_milliseconds = max_backoff_milliseconds

        return min_backoff_milliseconds + (
            random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)  # nosec
        )
