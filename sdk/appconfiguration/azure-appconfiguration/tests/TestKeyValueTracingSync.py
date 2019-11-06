import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler

def main():
    connection_string = os.environ['AZURE_APPCONFIG_CONNECTION_STRING']
    print(connection_string)

    exporter = AzureExporter(
        instrumentation_key="4ab2a2c3-5590-4b5f-a075-77a994c1bc3c"
    )

    tracer = Tracer(exporter=exporter, sampler=AlwaysOnSampler())
    with tracer.span(name="azconfig") as span:
        client = AzureAppConfigurationClient.from_connection_string(connection_string)
        #keyvalue1 = client.get_key_value('tracing1')
        #print(keyvalue1.value)
        newkeyvalue = ConfigurationSetting()
        newkeyvalue.key = "tracing1"
        newkeyvalue.value = "aaa"
        newkeyvalue.content_type = "testtype"
        newkeyvalue.tags = {
            "tag1": "value1",
            "tag2": "value2",
        }
        #client.delete_configuration_setting('test2')
        client.add_configuration_setting(newkeyvalue)
        #client.add_configuration_setting(newkeyvalue)
        keyvalue2 = client.get_configuration_setting('tracing1')
        print(keyvalue2.value)
        client.delete_configuration_setting('tracing1')
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

    #keyvalues = list(client.list_revisions('test2'))
    #currentkeyvalue = keyvalues[0]

    #print(currentkeyvalue)

if __name__ == "__main__":
    main()