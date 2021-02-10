
# storage eg event
eg_storage_dict = {
    "id":"bbab6625-dc56-4b22-abeb-afcc72e5290c",
    "subject":"/blobServices/default/containers/oc2d2817345i200097container/blobs/oc2d2817345i20002296blob",
    "data":{
        "api":"PutBlockList",
        "clientRequestId":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
        "requestId":"831e1650-001e-001b-66ab-eeb76e000000",
        "eTag":"0x8D4BCC2E4835CD0",
        "contentType":"application/octet-stream",
        "contentLength":524288,
        "blobType":"BlockBlob",
        "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
        "sequencer":"00000000000004420000000000028963",
        "storageDiagnostics":{"batchId":"b68529f3-68cd-4744-baa4-3c0498ec19f0"}
    },
    "eventType":"Microsoft.Storage.BlobCreated",
    "dataVersion":"2.0",
    "metadataVersion":"1",
    "eventTime":"2020-08-07T02:28:23.867525Z",
    "topic":"/subscriptions/faa080af-c1d8-40ad-9cce-e1a450ca5b57/resourceGroups/t-swpill-test/providers/Microsoft.EventGrid/topics/eventgridegsub"
}

eg_storage_string = json.dumps(eg_storage_dict)
eg_storage_bytes = eg_storage_string.encode("utf-8")

# custom eg event
eg_custom_dict = {
    "id":"3a30afef-b604-4b67-973e-7dfff7e178a7",
    "subject":"Test EG Custom Event",
    "data":{"team":"event grid squad"},
    "eventType":"Azure.Sdk.Sample",
    "dataVersion":"2.0",
    "metadataVersion":"1",
    "eventTime":"2020-08-07T02:19:05.16916Z",
    "topic":"/subscriptions/f8aa80ae-d1c8-60ad-9bce-e1a850ba5b67/resourceGroups/sample-resource-group-test/providers/Microsoft.EventGrid/topics/egtopicsamplesub"
}
eg_custom_string = json.dumps(eg_custom_dict)
eg_custom_bytes = eg_custom_string.encode("utf-8")
