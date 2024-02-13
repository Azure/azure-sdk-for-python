import os
from uuid import uuid4
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from azure.core.exceptions import ResourceExistsError
from dotenv import find_dotenv, load_dotenv


def main():
    load_dotenv(find_dotenv())
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    # prepare 400 configuration settings
    for i in range(400):
        client.add_configuration_setting(
            ConfigurationSetting(
                key="sample_key_" + str(i),
                label="sample_label_" + str(i),
            )
        )
    # there will have 4 pages in list result, there are 100 configuration settings per page.
    
    # print page etags
    print("**********************print page etags*****************************")
    page_etags = []
    items = client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*")
    iterator = items.by_page() # azure.core.paging.PageIterator obj
    for page in iterator:
        etag = iterator._response.http_response.headers['Etag']
        page_etags.append(etag)
        print(f"ETag: {etag}")
    
    # monitor page updates
    print("**********************monitor page updates*****************************")
    response = client.list_configuration_settings(page_etags=page_etags, key_filter="sample_key_*", label_filter="sample_label_*")
    for page in response:
        if page:
            for item in page:
                print(f"Key: {item.key}, Label: {item.label}")
        else:
            print(page)
    # expected output: [None, None, None, None, None]
    
    # add a configuration setting
    client.add_configuration_setting(
        ConfigurationSetting(
            key="sample_key_201",
            label="sample_label_202",
        )
    )
    # there will have 5 pages in list result, first 4 pages with 100 items and the last page with one item
    
    # print page etags after updates
    print("*****************print page etags after updates**********************************")
    items = client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*")
    iterator = items.by_page() # azure.core.paging.PageIterator obj
    for page in iterator:
        etag = iterator._response.http_response.headers['Etag']
        print(f"ETag: {etag}")
    
    # monitor page updates
    print("**********************monitor page updates*****************************")
    response = client.list_configuration_settings(page_etags=page_etags, key_filter="sample_key_*", label_filter="sample_label_*")
    for page in response:
        if page:
            for item in page:
                print(f"Key: {item.key}, Label: {item.label}")
        else:
            print(page)
    # expected output: [<first page items>, <second page items>, <third page items>, <fourth page items>, <fifth page items>]
    
    # for page_etag, continuation_token in zip(page_etags, continuation_tokens):
    #     result = client.monitor_single_page_configuration_settings(page_etag=page_etag, continuation_token=continuation_token, key_filter="sample_key_*", label_filter="sample_label_*")
    #     if result:
    #         for configuration_setting in result:
    #             print(f"Key: {configuration_setting.key}, Label: {configuration_setting.label}")
    #     print(result)               

    # clean up
    print("*************************clean up**************************")
    count = 0
    for item in client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*"):
        client.delete_configuration_setting(item.key, label=item.label)
        count += 1
    print(count)


if __name__ == "__main__":
    main()