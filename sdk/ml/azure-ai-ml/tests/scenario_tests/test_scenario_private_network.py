# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario test: Secure workspace with managed-network outbound rules.

Customer story:
  "I'm a platform engineer securing an Azure ML workspace.  I need to
  audit the current network posture, allow-list external package repos
  and Azure service endpoints so training jobs can reach them, then
  clean up the temporary rules after validation."

This exercises the workspace + managed-network surface that flows
through the TypeSpec-migrated ``arm_ml_service`` REST client.
"""

import pytest

from azure.ai.ml.entities import FqdnDestination, ServiceTagDestination


def _isolation_enabled(ml_client, workspace_name):
    """Return True if the workspace has managed-network isolation on."""
    ws = ml_client.workspaces.get(workspace_name)
    if ws.managed_network is None:
        return False
    return ws.managed_network.isolation_mode in (
        "AllowInternetOutbound",
        "AllowOnlyApprovedOutbound",
    )


class TestScenarioPrivateNetwork:
    """Secure-workspace managed-network scenario tests."""

    # ------------------------------------------------------------------
    # Scenario 1 — Network posture audit
    #
    # A platform engineer fetches the workspace, inspects the managed-
    # network isolation mode, and enumerates every outbound rule to
    # build a compliance report.
    # ------------------------------------------------------------------
    def test_network_posture_audit(self, ml_client, workspace_name):
        """Audit workspace network config and list all outbound rules.

        Customer action:
          1. ``workspaces.get()`` → read ``managed_network.isolation_mode``
          2. ``workspace_outbound_rules.list()`` → enumerate every rule
          3. For each rule, read its name, type, and destination details
          4. Confirm the workspace entity and the rules API agree

        Speed: ~10 s (read-only, no mutations)
        """
        # Step 1 — fetch workspace and inspect network config
        ws = ml_client.workspaces.get(workspace_name)
        assert ws.managed_network is not None, "managed_network should be populated on workspace GET"
        isolation = ws.managed_network.isolation_mode
        print(f"  Workspace isolation mode: {isolation}")
        assert isolation in ("Disabled", "AllowInternetOutbound", "AllowOnlyApprovedOutbound")

        # Step 2 — enumerate outbound rules via the dedicated operations API
        rules = ml_client.workspace_outbound_rules.list(workspace_name)
        print(f"  Total outbound rules: {len(rules)}")
        for rule in rules:
            print(f"    {rule.type:>16} | {rule.name}")

        # Step 3 — for every rule the operations API returns, spot-check
        # that the basic customer-visible fields (name, type) are populated
        for rule in rules:
            assert rule.name, "Rule is missing a name"
            assert rule.type, "Rule is missing a type"
            # FQDN rules expose .destination
            if rule.type == "FQDN":
                assert rule.destination, f"FQDN rule {rule.name!r} has empty destination"
            # ServiceTag rules expose .service_tag, .protocol, .port_ranges
            if rule.type == "ServiceTag":
                assert rule.service_tag, f"ServiceTag rule {rule.name!r} has empty service_tag"

        # Step 4 — cross-check: workspace entity rules should be a subset
        # of the rules from the dedicated API (the ops API may include
        # system-managed "Required" rules not surfaced on the entity)
        if ws.managed_network.outbound_rules:
            entity_names = {r.name for r in ws.managed_network.outbound_rules}
            ops_names = {r.name for r in rules}
            assert entity_names <= ops_names, (
                f"Workspace entity has rules not returned by the outbound-rules API:\n"
                f"  entity-only: {entity_names - ops_names}"
            )

    # ------------------------------------------------------------------
    # Scenario 2 — Allow-list external package repos for training jobs
    #
    # A data scientist needs pip/conda to install packages inside a
    # managed-network workspace.  They add FQDN rules for pypi.org and
    # conda.anaconda.org, verify the rules are live, then clean up.
    # ------------------------------------------------------------------
    def test_allowlist_package_repos(self, ml_client, workspace_name, rand_name):
        """Add FQDN outbound rules for PyPI and conda, verify, remove.

        Customer action:
          1. Check workspace isolation is enabled (skip otherwise)
          2. Create FQDN rules for pypi.org and conda.anaconda.org
          3. Verify each rule appears in ``workspace_outbound_rules.list()``
          4. Fetch each rule by name and confirm the destination
          5. Remove both rules

        Speed: ~1-3 min (two LRO creates + two LRO deletes)
        """
        if not _isolation_enabled(ml_client, workspace_name):
            pytest.skip(
                "Workspace isolation is Disabled — outbound rule "
                "mutations are rejected.  Use a workspace with "
                "AllowInternetOutbound or AllowOnlyApprovedOutbound."
            )

        pypi_rule_name = rand_name("allow-pypi")
        conda_rule_name = rand_name("allow-conda")
        created_rules = []

        try:
            # ---- Add PyPI ----
            pypi_rule = FqdnDestination(name=pypi_rule_name, destination="pypi.org")
            ml_client.workspace_outbound_rules.begin_create(workspace_name=workspace_name, rule=pypi_rule).result()
            created_rules.append(pypi_rule_name)
            print(f"  ✓ Created FQDN rule: {pypi_rule_name} → pypi.org")

            # ---- Add conda ----
            conda_rule = FqdnDestination(name=conda_rule_name, destination="conda.anaconda.org")
            ml_client.workspace_outbound_rules.begin_create(workspace_name=workspace_name, rule=conda_rule).result()
            created_rules.append(conda_rule_name)
            print(f"  ✓ Created FQDN rule: {conda_rule_name} → conda.anaconda.org")

            # ---- Verify both appear in list ----
            all_rules = ml_client.workspace_outbound_rules.list(workspace_name)
            rule_names = {r.name for r in all_rules}
            assert pypi_rule_name in rule_names, f"{pypi_rule_name} missing from rule list"
            assert conda_rule_name in rule_names, f"{conda_rule_name} missing from rule list"

            # ---- Fetch each by name and check destination ----
            fetched_pypi = ml_client.workspace_outbound_rules.get(
                workspace_name=workspace_name, outbound_rule_name=pypi_rule_name
            )
            assert fetched_pypi.destination == "pypi.org"
            assert fetched_pypi.type == "FQDN"

            fetched_conda = ml_client.workspace_outbound_rules.get(
                workspace_name=workspace_name, outbound_rule_name=conda_rule_name
            )
            assert fetched_conda.destination == "conda.anaconda.org"
            print("  ✓ Both rules verified via GET")

        finally:
            for name in created_rules:
                try:
                    ml_client.workspace_outbound_rules.begin_remove(
                        workspace_name=workspace_name, outbound_rule_name=name
                    ).result()
                    print(f"  ✓ Removed rule: {name}")
                except Exception as exc:
                    print(f"  ⚠ Cleanup of {name!r} failed: {exc}")

    # ------------------------------------------------------------------
    # Scenario 3 — Open an Azure service endpoint via ServiceTag rule
    #
    # A platform engineer needs training jobs to call Azure Front Door.
    # They add a ServiceTag rule with multiple ports, verify it, then
    # clean up.
    # ------------------------------------------------------------------
    def test_open_azure_service_endpoint(self, ml_client, workspace_name, rand_name):
        """Add a ServiceTag outbound rule for Azure Front Door, verify, remove.

        Customer action:
          1. Create a ServiceTag rule for AzureFrontDoor.Frontend on TCP 80,443
          2. Fetch and confirm service_tag, protocol, port_ranges all persisted
          3. Remove the rule

        Speed: ~30-90 s
        """
        if not _isolation_enabled(ml_client, workspace_name):
            pytest.skip("Workspace isolation is Disabled.")

        rule_name = rand_name("allow-afd")
        created = False

        try:
            rule = ServiceTagDestination(
                name=rule_name,
                service_tag="AzureFrontDoor.Frontend",
                protocol="TCP",
                port_ranges="80,443",
            )
            ml_client.workspace_outbound_rules.begin_create(workspace_name=workspace_name, rule=rule).result()
            created = True
            print(f"  ✓ Created ServiceTag rule: {rule_name}")

            # ---- Fetch and verify all fields survived ----
            fetched = ml_client.workspace_outbound_rules.get(
                workspace_name=workspace_name, outbound_rule_name=rule_name
            )
            assert fetched.type == "ServiceTag"
            assert fetched.service_tag == "AzureFrontDoor.Frontend"
            assert fetched.protocol == "TCP"
            assert fetched.port_ranges == "80,443"
            print(f"  ✓ Verified: {fetched.service_tag} " f"({fetched.protocol}:{fetched.port_ranges})")

        finally:
            if created:
                try:
                    ml_client.workspace_outbound_rules.begin_remove(
                        workspace_name=workspace_name, outbound_rule_name=rule_name
                    ).result()
                    print(f"  ✓ Removed rule: {rule_name}")
                except Exception as exc:
                    print(f"  ⚠ Cleanup of {rule_name!r} failed: {exc}")

    # ------------------------------------------------------------------
    # Scenario 4 — Update an allow-listed domain
    #
    # A customer initially allows "example.org" but later needs to
    # switch to "api.example.org".  They update the existing rule
    # rather than delete + recreate.
    # ------------------------------------------------------------------
    def test_update_allowlisted_domain(self, ml_client, workspace_name, rand_name):
        """Create an FQDN rule, update its destination, confirm the change persisted.

        Customer action:
          1. Create FQDN rule for example.org
          2. Update the same rule to point at api.example.org
          3. Fetch and confirm the new destination
          4. Remove the rule

        Speed: ~1-2 min (create LRO + update LRO + delete LRO)
        """
        if not _isolation_enabled(ml_client, workspace_name):
            pytest.skip("Workspace isolation is Disabled.")

        rule_name = rand_name("fqdn-upd")
        created = False

        try:
            # ---- Create original rule ----
            original = FqdnDestination(name=rule_name, destination="example.org")
            ml_client.workspace_outbound_rules.begin_create(workspace_name=workspace_name, rule=original).result()
            created = True

            fetched = ml_client.workspace_outbound_rules.get(
                workspace_name=workspace_name, outbound_rule_name=rule_name
            )
            assert fetched.destination == "example.org"
            print(f"  ✓ Created rule pointing to example.org")

            # ---- Update to new domain ----
            updated = FqdnDestination(name=rule_name, destination="api.example.org")
            ml_client.workspace_outbound_rules.begin_update(workspace_name=workspace_name, rule=updated).result()

            fetched2 = ml_client.workspace_outbound_rules.get(
                workspace_name=workspace_name, outbound_rule_name=rule_name
            )
            assert (
                fetched2.destination == "api.example.org"
            ), f"Expected 'api.example.org' after update, got '{fetched2.destination}'"
            print(f"  ✓ Updated rule: example.org → api.example.org")

        finally:
            if created:
                try:
                    ml_client.workspace_outbound_rules.begin_remove(
                        workspace_name=workspace_name, outbound_rule_name=rule_name
                    ).result()
                    print(f"  ✓ Removed rule: {rule_name}")
                except Exception as exc:
                    print(f"  ⚠ Cleanup of {rule_name!r} failed: {exc}")
