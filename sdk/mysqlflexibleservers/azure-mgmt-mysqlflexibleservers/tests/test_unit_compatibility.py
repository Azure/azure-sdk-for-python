from azure.mgmt.mysqlflexibleservers import MySQLManagementClient

# After migrate to Typespec, we should keep compatibility with existing LROs
# This test file ensures lro_options of existing LROs keep unchanged.


def test_advanced_threat_protection_settings_begin_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    # Mock the _update_initial method
    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.advanced_threat_protection_settings,
        "_update_initial",
        return_value=mock_response,
    )

    poller = client.advanced_threat_protection_settings.begin_update(
        resource_group_name="test-rg",
        server_name="test-server",
        advanced_threat_protection_name="test",
        parameters={},
    )

    # to keep compatibility, the lro_options shall always be set to {'final-state-via': 'location'}
    assert poller._polling_method._lro_options == {"final-state-via": "location"}


def test_advanced_threat_protection_settings_begin_update_put(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.advanced_threat_protection_settings,
        "_update_put_initial",
        return_value=mock_response,
    )

    poller = client.advanced_threat_protection_settings.begin_update_put(
        resource_group_name="test-rg",
        server_name="test-server",
        advanced_threat_protection_name="test",
        parameters={},
    )

    assert poller._polling_method._lro_options == {"final-state-via": "location"}


def test_azure_ad_administrators_begin_delete(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.azure_ad_administrators, "_delete_initial", return_value=mock_response
    )

    poller = client.azure_ad_administrators.begin_delete(
        resource_group_name="test-rg",
        server_name="test-server",
        administrator_name="test-admin",
    )

    assert poller._polling_method._lro_options == {"final-state-via": "location"}


def test_backup_and_export_begin_create(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.backup_and_export, "_create_initial", return_value=mock_response
    )

    poller = client.backup_and_export.begin_create(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options == {"final-state-via": "location"}


def test_configurations_begin_batch_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.configurations, "_batch_update_initial", return_value=mock_response
    )

    poller = client.configurations.begin_batch_update(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options == {
        "final-state-via": "azure-async-operation"
    }


def test_long_running_backup_begin_create(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.long_running_backup, "_create_initial", return_value=mock_response
    )

    poller = client.long_running_backup.begin_create(
        resource_group_name="test-rg",
        server_name="test-server",
        backup_name="test-backup",
        parameters={},
    )

    assert poller._polling_method._lro_options == {
        "final-state-via": "azure-async-operation"
    }


def test_servers_migration_begin_cutover_migration(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.servers_migration,
        "_cutover_migration_initial",
        return_value=mock_response,
    )

    poller = client.servers_migration.begin_cutover_migration(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options == {
        "final-state-via": "azure-async-operation"
    }


def test_servers_begin_delete(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.servers, "_delete_initial", return_value=mock_response)

    poller = client.servers.begin_delete(
        resource_group_name="test-rg",
        server_name="test-server",
    )

    assert poller._polling_method._lro_options == {
        "final-state-via": "azure-async-operation"
    }


def test_servers_begin_detach_v_net(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.servers, "_detach_v_net_initial", return_value=mock_response
    )

    poller = client.servers.begin_detach_v_net(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options == {
        "final-state-via": "azure-async-operation"
    }


def test_servers_begin_reset_gtid(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.servers, "_reset_gtid_initial", return_value=mock_response
    )

    poller = client.servers.begin_reset_gtid(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options == {
        "final-state-via": "azure-async-operation"
    }


def test_azure_ad_administrators_begin_create_or_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.azure_ad_administrators,
        "_create_or_update_initial",
        return_value=mock_response,
    )

    poller = client.azure_ad_administrators.begin_create_or_update(
        resource_group_name="test-rg",
        server_name="test-server",
        administrator_name="test-admin",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_configurations_begin_create_or_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.configurations, "_create_or_update_initial", return_value=mock_response
    )

    poller = client.configurations.begin_create_or_update(
        resource_group_name="test-rg",
        server_name="test-server",
        configuration_name="test-config",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_configurations_begin_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.configurations, "_update_initial", return_value=mock_response
    )

    poller = client.configurations.begin_update(
        resource_group_name="test-rg",
        server_name="test-server",
        configuration_name="test-config",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_databases_begin_create_or_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.databases, "_create_or_update_initial", return_value=mock_response
    )

    poller = client.databases.begin_create_or_update(
        resource_group_name="test-rg",
        server_name="test-server",
        database_name="test-db",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_databases_begin_delete(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.databases, "_delete_initial", return_value=mock_response)

    poller = client.databases.begin_delete(
        resource_group_name="test-rg",
        server_name="test-server",
        database_name="test-db",
    )

    assert poller._polling_method._lro_options is None


def test_firewall_rules_begin_create_or_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.firewall_rules, "_create_or_update_initial", return_value=mock_response
    )

    poller = client.firewall_rules.begin_create_or_update(
        resource_group_name="test-rg",
        server_name="test-server",
        firewall_rule_name="test-rule",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_firewall_rules_begin_delete(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.firewall_rules, "_delete_initial", return_value=mock_response
    )

    poller = client.firewall_rules.begin_delete(
        resource_group_name="test-rg",
        server_name="test-server",
        firewall_rule_name="test-rule",
    )

    assert poller._polling_method._lro_options is None


def test_maintenances_begin_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(
        client.maintenances, "_update_initial", return_value=mock_response
    )

    poller = client.maintenances.begin_update(
        resource_group_name="test-rg",
        server_name="test-server",
        maintenance_name="test-maintenance",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_servers_begin_create(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.servers, "_create_initial", return_value=mock_response)

    poller = client.servers.begin_create(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_servers_begin_failover(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.servers, "_failover_initial", return_value=mock_response)

    poller = client.servers.begin_failover(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_servers_begin_restart(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.servers, "_restart_initial", return_value=mock_response)

    poller = client.servers.begin_restart(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options is None


def test_servers_begin_start(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.servers, "_start_initial", return_value=mock_response)

    poller = client.servers.begin_start(
        resource_group_name="test-rg",
        server_name="test-server",
    )

    assert poller._polling_method._lro_options is None


def test_servers_begin_stop(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.servers, "_stop_initial", return_value=mock_response)

    poller = client.servers.begin_stop(
        resource_group_name="test-rg",
        server_name="test-server",
    )

    assert poller._polling_method._lro_options is None


def test_servers_begin_update(mocker):
    client = MySQLManagementClient(
        credential="fake-credential",
        subscription_id="00000000-0000-0000-0000-000000000000",
    )

    mock_response = mocker.Mock()
    mock_response.http_response = mocker.Mock()
    mock_response.http_response.read = mocker.Mock()
    mock_response.http_response.status_code = 200
    mock_response.http_response.headers = {}

    mocker.patch.object(client.servers, "_update_initial", return_value=mock_response)

    poller = client.servers.begin_update(
        resource_group_name="test-rg",
        server_name="test-server",
        parameters={},
    )

    assert poller._polling_method._lro_options is None
