import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from dotenv import find_dotenv, load_dotenv


def main():
    load_dotenv(find_dotenv())
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    # prepare 400 configuration settings
    for i in range(400):
        client.add_configuration_setting(
            ConfigurationSetting(
                key=f"sample_key_{str(i)}",
                label=f"sample_label_{str(i)}",
            )
        )
    # there will have 4 pages while listing, there are 100 configuration settings per page.
    
    # get page etags
    print("**********************get page etags*****************************")
    page_etags = []
    items = client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*")
    iterator = items.by_page()
    for page in iterator:
        etag = iterator._response.http_response.headers['Etag']
        page_etags.append(etag)
        print(f"ETag: {etag}")
    
    # ETag: "P3Oae4jiSypN6U1OApprRj2k7548_x3IYkn6NHp-wAU" next_link: /kv?key=sample_key_*&label=sample_label_*&api-version=2023-10-01&after=c2FtcGxlX2tleV8xODgKc2FtcGxlX2xhYmVsXzE4OA%3D%3D
    # ETag: "x1HUZXjADggqDwAZfSArFfFgZKhLz439uDIpNY80hqc" next_link: /kv?key=sample_key_*&label=sample_label_*&api-version=2023-10-01&after=c2FtcGxlX2tleV8yNzQKc2FtcGxlX2xhYmVsXzI3NA%3D%3D
    # ETag: "B37CWEtuQhXSOWv2f1T0QBlEMGFUbC1W0UVkKvSAWMM" next_link: /kv?key=sample_key_*&label=sample_label_*&api-version=2023-10-01&after=c2FtcGxlX2tleV8zNjQKc2FtcGxlX2xhYmVsXzM2NA%3D%3D
    # ETag: "X-rxvugJpqrNoZwapRGx5oHI0wDnQRPiBo_MdWXZzoc" next_link: /kv?key=sample_key_*&label=sample_label_*&api-version=2023-10-01&after=c2FtcGxlX2tleV85NQpzYW1wbGVfbGFiZWxfOTU%3D
    # ETag: "GoIDT8F8w0Jko6tIF3FgZz5hrPQgCN-WLTxiwK71vhw" next_link: None
    
    # monitor page updates
    print("**********************monitor page before updates*****************************")
    response = client.list_configuration_settings(page_etags=page_etags, key_filter="sample_key_*", label_filter="sample_label_*")
    for page in response:
        if page:
            print("This page has changes.")
            for item in page:
                print(f"Key: {item.key}, Label: {item.label}")
        else:
            print("No change found.")
    
    # add a configuration setting
    print("**********************add a configuration setting*****************************")
    client.add_configuration_setting(
        ConfigurationSetting(
            key="sample_key_401",
            label="sample_label_402",
        )
    )
    
    # print page etags after updates
    print("*****************print page etags after updates**********************************")
    items = client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*")
    iterator = items.by_page()
    for page in iterator:
        etag = iterator._response.http_response.headers['Etag']
        print(f"ETag: {etag}")
    
    # monitor page updates
    print("**********************monitor page updates*****************************")
    response = client.list_configuration_settings(page_etags=page_etags, key_filter="sample_key_*", label_filter="sample_label_*")
    # List[ItemPages[ConfigurationSetting]]
    for page in response:
        if page:
            print("This page has changes.")
            for item in page:
                print(f"Key: {item.key}, Label: {item.label}")
        else:
            print("No change found.")          

    # clean up
    print("*************************clean up**************************")
    count = 0
    for item in client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*"):
        client.delete_configuration_setting(item.key, label=item.label)
        count += 1
    print(count)
    
    items = client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*")
    print(items is None)


if __name__ == "__main__":
    main()
