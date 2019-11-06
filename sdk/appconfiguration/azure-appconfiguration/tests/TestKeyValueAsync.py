from configuration import ConfigurationSetting
from configuration.aio import AzureConfigurationClientAsync
import os
import asyncio

async def main():
    connection_string = os.environ['AZCONFIG_CONNECTION_STRING']
    print(connection_string)

    client = AzureConfigurationClientAsync(connection_string)

    # keyvalue1 = client.get_key_value('test1')
    # print(keyvalue1.value)
    newkeyvalue = ConfigurationSetting()
    newkeyvalue.key = "test2"
    newkeyvalue.value = "aaa"
    newkeyvalue.content_type = "testtype"
    newkeyvalue.tags = {
        "tag1": "value1",
        "tag2": "value2",
        }
    await client.delete_configuration_setting('test2')
    await client.add_configuration_setting(newkeyvalue)
    keyvalue2 = await client.get_configuration_setting('test2')
    print(keyvalue2.value)
    newkeyvalue1 = ConfigurationSetting()
    newkeyvalue1.key="test2"
    newkeyvalue1.value="bbb"
    newkeyvalue1.label=''
    newkeyvalue1.content_type="testtype"
    newkeyvalue1.tags={
        "tag1": "value1",
        "tag2": "value2",
        }
    temp = await client.update_configuration_setting(key='test2', value="bbb")
    keyvalue3 = await client.get_configuration_setting('test2')
    print(keyvalue3.value)
    # client.key_values.delete('test2')
    # client.key_values.delete('test3')
    # keyvalue4 = client.key_values.get('test2')
    # print(keyvalue4.value)

    keyvalue5 = await client.lock_configuration_setting("test2")
    print(keyvalue5.locked)

    keyvalue6 = await client.unlock_configuration_setting("test2")
    print(keyvalue6.locked)

    #keyvalues = list(client.list_key_values('test2'))
    #currentkeyvalue = keyvalues[0]

    #print(currentkeyvalue)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())