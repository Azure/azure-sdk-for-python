def flexible_server_firewall_rule_mgmt_test(instance, resource_group_name, server_name):
    firewall_rule_name = server_name + "-testfirewallrule"
    start_ip_address = "0.0.0.0"
    end_ip_address = "255.255.255.255"
    new_start_ip_address = "12.12.12.12"
    new_end_ip_address = "233.233.233.233"

    result = instance.mgmt_client.firewall_rules.create_or_update(resource_group_name, server_name, firewall_rule_name, start_ip_address, end_ip_address)
    result = result.result()
    instance.assertEqual(result.start_ip_address, start_ip_address)
    instance.assertEqual(result.end_ip_address, end_ip_address)

    result = instance.mgmt_client.firewall_rules.create_or_update(resource_group_name, server_name, firewall_rule_name, new_start_ip_address, end_ip_address)
    result = result.result()
    instance.assertEqual(result.start_ip_address, new_start_ip_address)

    result = instance.mgmt_client.firewall_rules.create_or_update(resource_group_name, server_name, firewall_rule_name, new_start_ip_address, new_end_ip_address)
    result = result.result()
    instance.assertEqual(result.end_ip_address, new_end_ip_address)

    result = instance.mgmt_client.firewall_rules.list_by_server(resource_group_name, server_name)
    instance.assertIsNotNone(result)

    result = instance.mgmt_client.firewall_rules.get(resource_group_name, server_name, firewall_rule_name)

    result = instance.mgmt_client.firewall_rules.delete(resource_group_name, server_name, firewall_rule_name)
    result = result.result()


def flexible_server_configuration_mgmt_test(instance, resource_group_name, server_name, config_key_name, default_value, user_value):
   
    result = instance.mgmt_client.configurations.list_by_server(resource_group_name, server_name)
    instance.assertIsNotNone(result)
    
    result = instance.mgmt_client.configurations.get(resource_group_name, server_name, config_key_name)
    instance.assertTrue(result.value, default_value)
    instance.assertTrue(result.source, "system-default")
    
    result = instance.mgmt_client.configurations.update(resource_group_name, server_name, config_key_name, value=user_value, source='user-override')
    result = result.result()
    instance.assertTrue(result.value, user_value)
    instance.assertTrue(result.source, "user-override")


def flexible_server_database_mgmt_test(instance, resource_group_name, server_name):
    database_name = "testdatabase"
    result = instance.mgmt_client.databases.create_or_update(resource_group_name, server_name, database_name, charset='utf8', collation='utf8_general_ci')
    result = result.result()
    instance.assertEqual(result.name, database_name)
    instance.assertEqual(result.charset, 'utf8')
    instance.assertEqual(result.collation, 'utf8_general_ci')

    result = instance.mgmt_client.databases.get(resource_group_name, server_name, database_name)

    result = instance.mgmt_client.databases.list_by_server(resource_group_name, server_name)
    instance.assertIsNotNone(result)

    result = instance.mgmt_client.databases.delete(resource_group_name, server_name, database_name)
    result = result.result()
