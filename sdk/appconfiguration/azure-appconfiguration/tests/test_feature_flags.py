# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import pytest
from consts import (
    APPCONFIGURATION_ENDPOINT_STRING,
    APPCONFIGURATION_CONNECTION_STRING,
)
from devtools_testutils import EnvironmentVariableLoader, recorded_by_proxy, set_custom_default_matcher
from testcase import AppConfigTestCase
from azure.core.exceptions import ResourceNotFoundError
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    FeatureFlag,
    FeatureFlagConditions,
    FeatureFilter,
    FeatureFlagVariantDefinition,
    FeatureFlagAllocation,
    FeatureFlagTelemetryConfiguration,
    PercentileAllocation,
    RequirementType,
    StatusOverride,
    UserAllocation,
    GroupAllocation,
)

AppConfigPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_endpoint_string=APPCONFIGURATION_ENDPOINT_STRING,
)


class TestFeatureFlagEndpoint(AppConfigTestCase):
    """Tests for the new dedicated feature flag endpoint methods"""

    def create_client(self, *args, **kwargs):
        return self.create_feature_flag_client(*args, **kwargs)

    def test_feature_flag_enabled_defaults_to_false(self):
        feature_flag = FeatureFlag(name="default_disabled")

        assert feature_flag.enabled is False

    def test_feature_flag_models_serialize_nested_values(self):
        conditions = FeatureFlagConditions(
            requirement_type=RequirementType.ALL,
            filters=[FeatureFilter(name="Microsoft.Percentage", parameters={"Value": "50"})],
        )
        feature_flag = FeatureFlag(
            name="serialized_feature",
            enabled=True,
            conditions=conditions,
            variants=[FeatureFlagVariantDefinition(name="variant_a", value="A")],
            allocation=FeatureFlagAllocation(
                percentile=[PercentileAllocation(variant="variant_a", percentile_from=0, percentile_to=50)],
                user=[UserAllocation(variant="variant_a", users=["user_a"])],
                group=[GroupAllocation(variant="variant_a", groups=["group_a"])],
            ),
            telemetry=FeatureFlagTelemetryConfiguration(enabled=True, metadata={"key": "value"}),
        )

        as_dict = feature_flag.as_dict()
        assert as_dict["conditions"]["filters"][0] == {
            "name": "Microsoft.Percentage",
            "parameters": {"Value": "50"},
        }
        assert as_dict["allocation"]["percentile"][0]["percentile_from"] == 0

        serialized = feature_flag.serialize()
        assert serialized["conditions"]["filters"][0]["name"] == "Microsoft.Percentage"
        assert serialized["allocation"]["percentile"][0]["from"] == 0
        assert conditions.as_dict()["filters"][0]["name"] == "Microsoft.Percentage"

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_list_feature_flags(self, appconfiguration_endpoint_string):
        """Test listing feature flags using the dedicated feature flag endpoint."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)

        # Create some feature flags
        feature_flag1 = FeatureFlag(name="feature1", enabled=True)
        feature_flag2 = FeatureFlag(name="feature2", enabled=False)

        client.set_feature_flag(feature_flag1)
        client.set_feature_flag(feature_flag2)

        # List all feature flags
        flags = list(client.list_feature_flags())
        assert len(flags) >= 2
        assert any(f.name == "feature1" for f in flags)
        assert any(f.name == "feature2" for f in flags)

        # Clean up
        client.delete_feature_flag("feature1", label=feature_flag1.label)
        client.delete_feature_flag("feature2", label=feature_flag2.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_list_feature_flags_with_name_filter(self, appconfiguration_endpoint_string):
        """Test listing feature flags with name filter."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)

        # Create feature flags
        feature_flag1 = FeatureFlag(name="my_feature_alpha", enabled=True)
        feature_flag2 = FeatureFlag(name="my_feature_beta", enabled=False)
        feature_flag3 = FeatureFlag(name="other_feature", enabled=True)

        client.set_feature_flag(feature_flag1)
        client.set_feature_flag(feature_flag2)
        client.set_feature_flag(feature_flag3)

        # List with name filter
        flags = list(client.list_feature_flags(name_filter="my_feature*"))
        assert len(flags) >= 2
        assert all("my_feature" in f.name for f in flags)

        # Clean up
        client.delete_feature_flag("my_feature_alpha", label=feature_flag1.label)
        client.delete_feature_flag("my_feature_beta", label=feature_flag2.label)
        client.delete_feature_flag("other_feature", label=feature_flag3.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_get_feature_flag(self, appconfiguration_endpoint_string):
        """Test getting a specific feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)

        # Create a feature flag
        feature_flag = FeatureFlag(name="test_feature_get", enabled=True)
        created = client.set_feature_flag(feature_flag)

        # Get the feature flag using the new endpoint method
        retrieved = client.get_feature_flag("test_feature_get", label=created.label)
        assert retrieved is not None
        assert retrieved.name == "test_feature_get"
        assert retrieved.enabled == True

        # Clean up
        client.delete_feature_flag("test_feature_get", label=created.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_get_feature_flag_not_found(self, appconfiguration_endpoint_string):
        """Test getting a non-existent feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)

        with pytest.raises(ResourceNotFoundError):
            client.get_feature_flag("nonexistent_feature", label=None)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_set_feature_flag(self, appconfiguration_endpoint_string):
        """Test setting a feature flag via the dedicated endpoint."""
        client = self.create_client(appconfiguration_endpoint_string)

        # Create a feature flag
        feature_flag = FeatureFlag(name="test_feature_set", enabled=True)
        set_flag = client.set_feature_flag(feature_flag)

        assert set_flag is not None
        assert set_flag.enabled == True
        assert set_flag.name == "test_feature_set"

        # Clean up
        client.delete_feature_flag("test_feature_set", label=set_flag.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_set_feature_flag_update(self, appconfiguration_endpoint_string):
        """Test updating an existing feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)

        # Create and then update a feature flag
        feature_flag = FeatureFlag(name="test_feature_update", enabled=True)
        created = client.set_feature_flag(feature_flag)

        # Update it
        created.enabled = False
        updated = client.set_feature_flag(created)

        assert updated.enabled == False
        assert updated.etag != created.etag

        # Clean up
        client.delete_feature_flag("test_feature_update", label=updated.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_delete_feature_flag(self, appconfiguration_endpoint_string):
        """Test deleting a feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)

        # Create a feature flag
        feature_flag = FeatureFlag(name="test_feature_delete", enabled=True)
        created = client.set_feature_flag(feature_flag)

        # Delete it using the endpoint method
        client.delete_feature_flag("test_feature_delete", label=created.label)

        # Verify it's deleted
        with pytest.raises(ResourceNotFoundError):
            client.get_feature_flag("test_feature_delete", label=created.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_list_feature_flag_revisions(self, appconfiguration_endpoint_string):
        """Test listing feature flag revisions."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)

        # Create and update a feature flag to create revisions
        feature_flag = FeatureFlag(name="test_feature_revisions", enabled=True)
        created = client.set_feature_flag(feature_flag)

        # Update to create another revision
        created.enabled = False
        updated = client.set_feature_flag(created)

        # List revisions
        revisions = list(client.list_feature_flag_revisions(name_filter="test_feature_revisions"))
        assert len(revisions) >= 1  # At least one revision
        assert all("test_feature_revisions" in r.name for r in revisions)

        # Clean up
        client.delete_feature_flag("test_feature_revisions", label=updated.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_with_label(self, appconfiguration_endpoint_string):
        """Test feature flag operations with labels."""
        client = self.create_client(appconfiguration_endpoint_string)

        # Create feature flags with labels
        feature_flag_prod = FeatureFlag(name="feature_with_label", enabled=True, label="prod")
        feature_flag_staging = FeatureFlag(name="feature_with_label", enabled=False, label="staging")

        client.set_feature_flag(feature_flag_prod)
        client.set_feature_flag(feature_flag_staging)

        # Get specific labeled version
        prod_flag = client.get_feature_flag("feature_with_label", label="prod")
        assert prod_flag is not None
        assert prod_flag.enabled == True

        staging_flag = client.get_feature_flag("feature_with_label", label="staging")
        assert staging_flag is not None
        assert staging_flag.enabled == False

        # Clean up
        client.delete_feature_flag("feature_with_label", label="prod")
        client.delete_feature_flag("feature_with_label", label="staging")

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_with_conditions(self, appconfiguration_endpoint_string):
        """Test a feature flag that uses conditions with client filters."""
        client = self.create_client(appconfiguration_endpoint_string)

        feature_flag = FeatureFlag(
            name="test_feature_conditions",
            enabled=True,
            description="A feature flag gated by client filters",
            conditions=FeatureFlagConditions(
                requirement_type=RequirementType.ALL,
                filters=[
                    FeatureFilter(name="Microsoft.TimeWindow", parameters={"Start": "Mon, 01 Jan 2024 00:00:00 GMT"}),
                    FeatureFilter(name="Microsoft.Percentage", parameters={"Value": 50}),
                ],
            ),
        )
        created = client.set_feature_flag(feature_flag)

        retrieved = client.get_feature_flag("test_feature_conditions", label=created.label)
        assert retrieved is not None
        assert retrieved.description == "A feature flag gated by client filters"
        assert retrieved.conditions is not None
        assert retrieved.conditions.requirement_type == "All"
        assert retrieved.conditions.filters is not None
        assert len(retrieved.conditions.filters) == 2
        filter_names = {f.name for f in retrieved.conditions.filters}
        assert "Microsoft.TimeWindow" in filter_names
        assert "Microsoft.Percentage" in filter_names

        client.delete_feature_flag("test_feature_conditions", label=created.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_with_variants_and_allocation(self, appconfiguration_endpoint_string):
        """Test a feature flag with variants and a full allocation (percentile/user/group)."""
        client = self.create_client(appconfiguration_endpoint_string)

        feature_flag = FeatureFlag(
            name="test_feature_variants",
            enabled=True,
            variants=[
                FeatureFlagVariantDefinition(name="On", value="true", status_override=StatusOverride.ENABLED),
                FeatureFlagVariantDefinition(name="Off", value="false", status_override=StatusOverride.DISABLED),
            ],
            allocation=FeatureFlagAllocation(
                default_when_enabled="On",
                default_when_disabled="Off",
                seed="test-seed",
                percentile=[
                    PercentileAllocation(variant="On", percentile_from=0, percentile_to=50),
                    PercentileAllocation(variant="Off", percentile_from=50, percentile_to=100),
                ],
                user=[UserAllocation(variant="On", users=["alice", "bob"])],
                group=[GroupAllocation(variant="Off", groups=["beta-testers"])],
            ),
        )
        created = client.set_feature_flag(feature_flag)

        retrieved = client.get_feature_flag("test_feature_variants", label=created.label)
        assert retrieved is not None
        assert retrieved.variants is not None
        assert len(retrieved.variants) == 2
        variant_names = {v.name for v in retrieved.variants}
        assert variant_names == {"On", "Off"}

        assert retrieved.allocation is not None
        assert retrieved.allocation.default_when_enabled == "On"
        assert retrieved.allocation.default_when_disabled == "Off"
        assert retrieved.allocation.seed == "test-seed"
        assert retrieved.allocation.percentile is not None
        assert len(retrieved.allocation.percentile) == 2
        assert retrieved.allocation.percentile[0].percentile_from == 0
        assert retrieved.allocation.percentile[0].percentile_to == 50
        assert retrieved.allocation.user is not None
        assert retrieved.allocation.user[0].users == ["alice", "bob"]
        assert retrieved.allocation.group is not None
        assert retrieved.allocation.group[0].groups == ["beta-testers"]

        client.delete_feature_flag("test_feature_variants", label=created.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_with_telemetry_and_tags(self, appconfiguration_endpoint_string):
        """Test a feature flag with telemetry configuration and tags."""
        client = self.create_client(appconfiguration_endpoint_string)

        feature_flag = FeatureFlag(
            name="test_feature_telemetry",
            enabled=True,
            telemetry=FeatureFlagTelemetryConfiguration(
                enabled=True,
                metadata={"owner": "team-a", "tier": "premium"},
            ),
            tags={"env": "test", "team": "core"},
        )
        created = client.set_feature_flag(feature_flag)

        retrieved = client.get_feature_flag("test_feature_telemetry", label=created.label)
        assert retrieved is not None
        assert retrieved.telemetry is not None
        assert retrieved.telemetry.enabled == True
        assert retrieved.telemetry.metadata == {"owner": "team-a", "tier": "premium"}
        assert retrieved.tags == {"env": "test", "team": "core"}

        client.delete_feature_flag("test_feature_telemetry", label=created.label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_full_model_roundtrip(self, appconfiguration_endpoint_string):
        """Test setting and retrieving a feature flag that populates every field of the model."""
        client = self.create_client(appconfiguration_endpoint_string)

        feature_flag = FeatureFlag(
            name="test_feature_full",
            enabled=True,
            label="prod",
            description="A fully populated feature flag",
            conditions=FeatureFlagConditions(
                requirement_type=RequirementType.ANY,
                filters=[
                    # Filter parameters are string-valued per the API spec (Record<string>).
                    FeatureFilter(name="Microsoft.Targeting", parameters={"Audience": "all-users"}),
                ],
            ),
            variants=[
                FeatureFlagVariantDefinition(
                    name="Large", value="large", content_type="text/plain", status_override=StatusOverride.ENABLED
                ),
                FeatureFlagVariantDefinition(name="Small", value="small"),
            ],
            allocation=FeatureFlagAllocation(
                default_when_enabled="Large",
                default_when_disabled="Small",
                seed="full-seed",
                percentile=[PercentileAllocation(variant="Large", percentile_from=0, percentile_to=100)],
                user=[UserAllocation(variant="Large", users=["carol"])],
                group=[GroupAllocation(variant="Small", groups=["internal"])],
            ),
            telemetry=FeatureFlagTelemetryConfiguration(enabled=True, metadata={"origin": "test"}),
            tags={"env": "prod", "critical": "true"},
        )
        created = client.set_feature_flag(feature_flag)

        retrieved = client.get_feature_flag("test_feature_full", label="prod")
        assert retrieved is not None
        assert retrieved.name == "test_feature_full"
        assert retrieved.enabled == True
        assert retrieved.label == "prod"
        assert retrieved.description == "A fully populated feature flag"
        assert retrieved.conditions is not None
        assert retrieved.conditions.requirement_type == "Any"
        assert retrieved.conditions.filters is not None
        assert retrieved.conditions.filters[0].name == "Microsoft.Targeting"
        assert retrieved.variants is not None
        assert len(retrieved.variants) == 2
        assert retrieved.variants[0].content_type == "text/plain"
        assert retrieved.allocation is not None
        assert retrieved.allocation.default_when_enabled == "Large"
        assert retrieved.telemetry is not None
        assert retrieved.telemetry.metadata == {"origin": "test"}
        assert retrieved.tags == {"env": "prod", "critical": "true"}
        assert retrieved.etag is not None
        assert retrieved.last_modified is not None

        client.delete_feature_flag("test_feature_full", label="prod")

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_list_labels(self, appconfiguration_endpoint_string):
        """Test listing feature flag labels using the dedicated feature flag endpoint."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)

        ff_label = "test_ff_label"
        feature_flag = FeatureFlag(name="test_feature_labels", enabled=True, label=ff_label)
        client.set_feature_flag(feature_flag)
        try:
            # The feature flag endpoint only lists feature-flag labels.
            ff_labels = {item.name for item in client.list_labels()}
            assert ff_label in ff_labels

            # name filter narrows the results to the matching label.
            filtered = list(client.list_labels(name=ff_label))
            assert len(filtered) == 1
            assert filtered[0].name == ff_label

            # Negative case: a name filter that matches no label returns no results.
            no_match = list(client.list_labels(name="nonexistent_ff_label"))
            assert no_match == []
        finally:
            client.delete_feature_flag("test_feature_labels", label=ff_label)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_get_feature_flag_wrong_label(self, appconfiguration_endpoint_string):
        """Getting a feature flag with a label it doesn't have raises ResourceNotFoundError."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)

        feature_flag = FeatureFlag(name="test_feature_wrong_label", enabled=True, label="real_label")
        client.set_feature_flag(feature_flag)
        try:
            # The flag exists, but not under this label.
            with pytest.raises(ResourceNotFoundError):
                client.get_feature_flag("test_feature_wrong_label", label="wrong_label")
        finally:
            client.delete_feature_flag("test_feature_wrong_label", label="real_label")
