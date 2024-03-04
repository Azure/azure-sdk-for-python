import os
import json
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from azure.core.exceptions import ResourceNotModifiedError
from azure.core.rest import HttpRequest
from dotenv import find_dotenv, load_dotenv


def main():
    load_dotenv(find_dotenv())
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    with AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING) as client:

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
        
        # monitor page updates
        print("**********************monitor page before updates*****************************")
        
        # continuation_token = None
        # index = 0
        # request = HttpRequest(
        #     method="GET",
        #     url="/kv?key=sample_key_%2A&label=sample_label_%2A&api-version=2023-10-01",
        #     headers={"If-None-Match": page_etags[index], "Accept": "application/vnd.microsoft.appconfig.kvset+json, application/problem+json"}
        # )
        # first_page_response = client.send_request(request)
        # if first_page_response.status_code == 304:
        #     print("No change found.")
        # if first_page_response.status_code == 200:
        #     print("This page has changes.")
        #     items = first_page_response.json()["items"]
        #     for item in items:
        #         print(f"Key: {item['key']}, Label: {item['label']}")
        
        # link = first_page_response.headers.get('Link', None)
        # continuation_token = link[1:link.index(">")] if link else None
        # index += 1
        # while continuation_token:
        #     request = HttpRequest(
        #         method="GET",
        #         url=f"{continuation_token}",
        #         headers={"If-None-Match": page_etags[index]}
        #     )
        #     index += 1
        #     response = client.send_request(request)
        #     if response.status_code == 304:
        #         print("No change found.")
        #     if response.status_code == 200:
        #         print("This page has changes.")
        #         items = response.json()["items"]
        #         for item in items:
        #             print(f"Key: {item['key']}, Label: {item['label']}")
        #     link = response.headers.get('Link', None)
        #     continuation_token = link[1:link.index(">")] if link else None
        
        # solution 2: pass one page etag per API call
        index = 0
        try:
            first_page_response = client.list_configuration_settings(
                key_filter="sample_key_*",
                label_filter="sample_label_*",
                page_etag=page_etags[index] if index < len(page_etags) else None,
            ).by_page()
            next(first_page_response)
            print("No change found.")
            continuation_token = first_page_response.continuation_token
            for item in first_page_response._current_page:
                print(f"Key: {item.key}, Label: {item.label}")
        except ResourceNotModifiedError as e:
            print("This page has changes.")
            link = e.response.headers.get('Link', None)
            continuation_token = link[1:link.index(">")] if link else None
            
        index += 1
        
        while continuation_token:
            try:
                response = client.list_configuration_settings(
                    key_filter="sample_key_*",
                    label_filter="sample_label_*",
                    page_etag=page_etags[index] if index < len(page_etags) else None,
                ).by_page(continuation_token=continuation_token)
                next(response)
                print("No change found.")
                continuation_token = response.continuation_token
                for item in response._current_page:
                    print(f"Key: {item.key}, Label: {item.label}")
            except ResourceNotModifiedError as e:
                print("This page has changes.")
                link = e.response.headers.get('Link', None)
                continuation_token = link[1:link.index(">")] if link else None
                
            index += 1
        
        # add a configuration setting
        print("**********************add a configuration setting*****************************")
        client.add_configuration_setting(
            ConfigurationSetting(
                key="sample_key_201",
                label="sample_label_225",
            )
        )
        
        # print page etags after updates
        print("*****************get page etags after updates**********************************")
        items = client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*")
        iterator = items.by_page()
        for page in iterator:
            etag = iterator._response.http_response.headers['Etag']
            print(f"ETag: {etag}")
        
        # monitor page updates
        print("**********************monitor page after updates*****************************")
        # solution 1: send_request
        # continuation_token = None
        # index = 0
        # request = HttpRequest(
        #     method="GET",
        #     url="/kv?key=sample_key_%2A&label=sample_label_%2A&api-version=2023-10-01",
        #     headers={"If-None-Match": page_etags[index], "Accept": "application/vnd.microsoft.appconfig.kvset+json, application/problem+json"}
        # )
        # first_page_response = client.send_request(request)
        # if first_page_response.status_code == 304:
        #     print("No change found.")
        # if first_page_response.status_code == 200:
        #     print("This page has changes.")
        #     items = first_page_response.json()["items"]
        #     for item in items:
        #         print(f"Key: {item['key']}, Label: {item['label']}")
        
        # link = first_page_response.headers.get('Link', None)
        # continuation_token = link[1:link.index(">")] if link else None
        # index += 1
        # while continuation_token:
        #     request = HttpRequest(
        #         method="GET",
        #         url=f"{continuation_token}",
        #         headers={"If-None-Match": page_etags[index]}
        #     )
        #     index += 1
        #     response = client.send_request(request)
        #     if response.status_code == 304:
        #         print("No change found.")
        #     if response.status_code == 200:
        #         print("This page has changes.")
        #         items = response.json()["items"]
        #         for item in items:
        #             print(f"Key: {item['key']}, Label: {item['label']}")
        #     link = response.headers.get('Link', None)
        #     continuation_token = link[1:link.index(">")] if link else None
        
        # solution 2: pass one page etag per API call
        index = 0
        try:
            first_page_response = client.list_configuration_settings(
                key_filter="sample_key_*",
                label_filter="sample_label_*",
                page_etag=page_etags[index] if index < len(page_etags) else None,
            ).by_page()
            next(first_page_response)
            print("No change found.")
            continuation_token = first_page_response.continuation_token
            for item in first_page_response._current_page:
                print(f"Key: {item.key}, Label: {item.label}")
        except ResourceNotModifiedError as e:
            print("This page has changes.")
            link = e.response.headers.get('Link', None)
            continuation_token = link[1:link.index(">")] if link else None
            
        index += 1
        
        while continuation_token:
            try:
                response = client.list_configuration_settings(
                    key_filter="sample_key_*",
                    label_filter="sample_label_*",
                    page_etag=page_etags[index] if index < len(page_etags) else None,
                ).by_page(continuation_token=continuation_token)
                next(response)
                print("No change found.")
                continuation_token = response.continuation_token
                for item in response._current_page:
                    print(f"Key: {item.key}, Label: {item.label}")
            except ResourceNotModifiedError as e:
                print("This page has changes.")
                link = e.response.headers.get('Link', None)
                continuation_token = link[1:link.index(">")] if link else None
                
            index += 1
            

        # clean up
        print("*************************clean up**************************")
        count = 0
        for item in client.list_configuration_settings(key_filter="sample_key_*", label_filter="sample_label_*"):
            client.delete_configuration_setting(item.key, label=item.label)
            count += 1
        print(count)


if __name__ == "__main__":
    main()
