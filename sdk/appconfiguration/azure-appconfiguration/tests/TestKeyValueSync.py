import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting

def main():
    connection_string = os.environ['AZCONFIG_CONNECTION_STRING']
    print(connection_string)

    client = AzureAppConfigurationClient.from_connection_string(connection_string)

    # keyvalue1 = client.get_key_value('test1')
    # print(keyvalue1.value)
    #newkeyvalue = ConfigurationSetting()
    #newkeyvalue.key = "test2"
    #newkeyvalue.value = "aaa"
    #newkeyvalue.content_type = "testtype"
    #newkeyvalue.tags = {
    #    "tag1": "value1",
    #   "tag2": "value2",
    #    }
    #client.delete_configuration_setting('test2')
    #client.add_configuration_setting(newkeyvalue)
    #client.add_configuration_setting(newkeyvalue)
    #keyvalue2 = client.get_configuration_setting('test2')
    #print(keyvalue2.value)
    #newkeyvalue1 = ConfigurationSetting()
    #newkeyvalue1.key="test2"
    #newkeyvalue1.value="bbb"
    #newkeyvalue1.label=''
    #newkeyvalue1.content_type="testtype"
    #newkeyvalue1.tags={
    #    "tag1": "value1",
    #    "tag2": "value2",
    #    }
    #temp = client.update_configuration_setting(key='test2', value="bbb")
    #temp = client.add_key_value(newkeyvalue1)
    #keyvalue3 = client.get_configuration_setting('test2')
    #print(keyvalue3.value)
    # client.key_values.delete('test2')
    # client.key_values.delete('test3')
    # keyvalue4 = client.key_values.get('test2')
    # print(keyvalue4.value)

    #keyvalue5 = client.lock_configuration_setting("test2")
    #print(keyvalue5.locked)

    #keyvalue6 = client.unlock_configuration_setting("test2")
    #print(keyvalue6.locked)

    keyvalues = list(client.list_revisions('test2'))
    currentkeyvalue = keyvalues[0]

    #print(currentkeyvalue)

if __name__ == "__main__":
    main()