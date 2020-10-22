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

# def flexible_server_key_mgmt_test(instance, resource_group_name, server_name):
#     vault_name = "testvault"
#     # KEY_NAME = SERVER_NAME + "-testkeyname"
#     # uri = https://daeunyim-keyvault.vault.azure.net/

#     parameters = {
#         "identity": {"type": "SystemAssigned"}
#     }
#     result = instance.mgmt_client.server.update(resource_group_name, server_name, parameters)
#     result = result.result()
#     server_identity = result.identity.principalId

#     parameters = {
#         "location": "eastus"
#         "properties":{
#             "enable_soft_delete": True,
#             "enable_purge_protection": True
#         }
#     }
#     result = self.mgmt_client.vaults.create_or_update(resource_group_name, vault_name, parameters=parameters)
#     result = result.result()

#     result = self.mgmt_client.keys.create_or_update(resource_group_name, vault_name, parameters=parameters)
#     result = result.result()

#     # create key
#     key_resp = self.cmd('keyvault key create --name {} -p software --vault-name {}'
#                         .format(key_name, vault_name)).get_output_in_json()

#     self.cmd('keyvault set-policy -g {} -n {} --object-id {} --key-permissions wrapKey unwrapKey get list'
#                 .format(resource_group, vault_name, server_identity))

#     # add server key
#     kid = key_resp['key']['kid']
#     server_key_resp = self.cmd('{} server key create -g {} --name {} --kid {}'
#                                 .format(database_engine, resource_group, server, kid),
#                                 checks=[JMESPathCheck('uri', kid)])

#     server_key_name = server_key_resp.get_output_in_json()['name']


#     import re
#     match = re.match(r'^https(.)+\.vault(.)+\/keys\/[^\/]+\/[0-9a-zA-Z]+$', uri)

#     uri =  "https://daeunyim-keyvault.vault.azure.net/keys/daeunyim-key/71cb64fcb8fd42aeb4cbd363c8e6aca6"
#     vault = uri.split('.')[0].split('/')[-1]
#     key = uri.split('/')[-2]
#     version = uri.split('/')[-1]
#     key_name= '{}_{}_{}'.format(vault, key, version)

#     key_name = 'daeunyim-keyvault_daeunyim-key_71cb64fcb8fd42aeb4cbd363c8e6aca6'

#     BODY = {
#         "properties": {
#         "storageProfile": {
#             "backupRetentionDays": 10,
#             "storageMB": 131072,
#         },
#         "administrator_login_password": "newpa$$w0rd",
#         "ssl_enforcement": "Enabled"
#         }
#     }

#     instance.mgmt_client.servers.update(resource_group_name, server_name)

#     result = instance.mgmt_client.server_keys.create_or_update(resource_group_name, server_name, key_name, uri=URI)
#     result = result.result()

#     result = instance.mgmt_client.server_keys.get(resource_group_name, server_name, key_name)

#     result = instance.mgmt_client.server_keys.list_by_server(resource_group_name, server_name)
#     print(list(result))

#     result = instance.mgmt_client.server_keys.delete(resource_group_name, server_name, key_name)
#     result = result.result()