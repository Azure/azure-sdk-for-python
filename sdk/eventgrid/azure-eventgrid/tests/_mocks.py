import json


# storage cloud event
cloud_storage_dict = {
    "id":"a0517898-9fa4-4e70-b4a3-afda1dd68672",
    "source":"/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}",
    "data":{
        "api":"PutBlockList",
        "client_request_id":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
        "request_id":"831e1650-001e-001b-66ab-eeb76e000000",
        "e_tag":"0x8D4BCC2E4835CD0",
        "content_type":"application/octet-stream",
        "content_length":524288,
        "blob_type":"BlockBlob",
        "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
        "sequencer":"00000000000004420000000000028963",
        "storage_diagnostics":{"batchId":"b68529f3-68cd-4744-baa4-3c0498ec19f0"}
    },
    "type":"Microsoft.Storage.BlobCreated",
    "time":"2020-08-07T01:11:49.765846Z",
    "specversion":"1.0"
}
cloud_storage_string = json.dumps(cloud_storage_dict)
cloud_storage_bytes = cloud_storage_string.encode("utf-8")

# custom cloud event
cloud_custom_dict = {
    "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
    "source":"https://egtest.dev/cloudcustomevent",
    "data":{"team": "event grid squad"},
    "type":"Azure.Sdk.Sample",
    "time":"2020-08-07T02:06:08.11969Z",
    "specversion":"1.0"
}
cloud_custom_string = json.dumps(cloud_custom_dict)
cloud_custom_bytes = cloud_custom_string.encode("utf-8")

# storage eg event
eg_string = "[{\"id\": \"56afc886-767b-d359-d59e-0da7877166b2\", \"topic\": \
	\"/SUBSCRIPTIONS/ID/RESOURCEGROUPS/rg/PROVIDERS/MICROSOFT.ContainerRegistry/test1\", \
	\"subject\": \"test1\", \"eventType\": \"Microsoft.AppConfiguration.KeyValueDeleted\",\
	 \"eventTime\": \"2018-01-02T19:17:44.4383997Z\",\
	 \"data\": {  \"key\":\"key1\",  \"label\":\"label1\",  \"etag\":\"etag1\"},\
	  \"dataVersion\": \"\", \"metadataVersion\": \"1\" },\
	  {\"id\": \"56afc886-767b-d359-d59e-0sdsd34343466b2\", \"topic\": \
	\"/SUBSCRIPTIONS/ID/RESOURCEGROUPS/rg/PROVIDERS/MICROSOFT.ContainerRegistry/test2\", \
	\"subject\": \"test2\", \"eventType\": \"Microsoft.AppConfiguration.KeyValueDeleted\",\
	 \"eventTime\": \"2020-01-02T19:17:44.4383997Z\",\
	 \"data\": {  \"key\":\"key2\",  \"label\":\"label2\",  \"etag\":\"etag2\"},\
	  \"dataVersion\": \"\", \"metadataVersion\": \"1\" }]"

eg_bytes = b"[{\"id\": \"56afc886-767b-d359-d59e-0da7877166b2\", \"topic\": \
	\"/SUBSCRIPTIONS/ID/RESOURCEGROUPS/rg/PROVIDERS/MICROSOFT.ContainerRegistry/test1\", \
	\"subject\": \"test1\", \"eventType\": \"Microsoft.AppConfiguration.KeyValueDeleted\",\
	 \"eventTime\": \"2018-01-02T19:17:44.4383997Z\",\
	 \"data\": {  \"key\":\"key1\",  \"label\":\"label1\",  \"etag\":\"etag1\"},\
	  \"dataVersion\": \"\", \"metadataVersion\": \"1\" },\
	  {\"id\": \"56afc886-767b-d359-d59e-0sdsd34343466b2\", \"topic\": \
	\"/SUBSCRIPTIONS/ID/RESOURCEGROUPS/rg/PROVIDERS/MICROSOFT.ContainerRegistry/test2\", \
	\"subject\": \"test2\", \"eventType\": \"Microsoft.AppConfiguration.KeyValueDeleted\",\
	 \"eventTime\": \"2020-01-02T19:17:44.4383997Z\",\
	 \"data\": {  \"key\":\"key2\",  \"label\":\"label2\",  \"etag\":\"etag2\"},\
	  \"dataVersion\": \"\", \"metadataVersion\": \"1\" }]"

eg_unicode = u"[{\"id\": \"56afc886-767b-d359-d59e-0da7877166b2\", \"topic\": \
	\"/SUBSCRIPTIONS/ID/RESOURCEGROUPS/rg/PROVIDERS/MICROSOFT.ContainerRegistry/test1\", \
	\"subject\": \"test1\", \"eventType\": \"Microsoft.AppConfiguration.KeyValueDeleted\",\
	 \"eventTime\": \"2018-01-02T19:17:44.4383997Z\",\
	 \"data\": {  \"key\":\"key1\",  \"label\":\"label1\",  \"etag\":\"etag1\"},\
	  \"dataVersion\": \"\", \"metadataVersion\": \"1\" },\
	  {\"id\": \"56afc886-767b-d359-d59e-0sdsd34343466b2\", \"topic\": \
	\"/SUBSCRIPTIONS/ID/RESOURCEGROUPS/rg/PROVIDERS/MICROSOFT.ContainerRegistry/test2\", \
	\"subject\": \"test2\", \"eventType\": \"Microsoft.AppConfiguration.KeyValueDeleted\",\
	 \"eventTime\": \"2020-01-02T19:17:44.4383997Z\",\
	 \"data\": {  \"key\":\"key2\",  \"label\":\"label2\",  \"etag\":\"etag2\"},\
	  \"dataVersion\": \"\", \"metadataVersion\": \"1\" }]"



cloud_string = "[{ \"id\":\"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033\",\
    \"source\":\"https://egtest.dev/cloudcustomevent\",\
    \"data\":{\"team\": \"event grid squad\"},\
    \"type\":\"Azure.Sdk.Sample\",\
    \"time\":\"2020-08-07T02:06:08.11969Z\",\
    \"specversion\":\"1.0\" }]"

cloud_bytes = b"[{ \"id\":\"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033\",\
    \"source\":\"https://egtest.dev/cloudcustomevent\",\
    \"data\":{\"team\": \"event grid squad\"},\
    \"type\":\"Azure.Sdk.Sample\",\
    \"time\":\"2020-08-07T02:06:08.11969Z\",\
    \"specversion\":\"1.0\" }]"

cloud_unicode = u"[{ \"id\":\"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033\",\
    \"source\":\"https://egtest.dev/cloudcustomevent\",\
    \"data\":{\"team\": \"event grid squad\"},\
    \"type\":\"Azure.Sdk.Sample\",\
    \"time\":\"2020-08-07T02:06:08.11969Z\",\
    \"specversion\":\"1.0\" }]"

cloud_string_with_data_base64 = "[{ \"id\":\"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033\",\
    \"source\":\"https://egtest.dev/cloudcustomevent\",\
    \"data_base64\":\"base 64 data\",\
    \"type\":\"Azure.Sdk.Sample\",\
    \"time\":\"2020-08-07T02:06:08.11969Z\",\
    \"specversion\":\"1.0\" }]"
