# Storage Blob Service SDK Migration Guide from <= 2.x to 12.x

In this section, we list the main changes you need to be aware of when converting your Storage Blob SDK library from version <= 2.X to version 12.X.
In version 12 we also support asynchronous APIs.

## Converting Core Classes
<= 2.X synchronous classes have been replaced. New asynchronous counterparts added.

| <= 2.X Classes (Clients)  | V12 Clients | NEW Asynchronous clients |
|---:|---:|---:|
| BlockBlobService  | BlobServiceClient | BlobServiceClient |
| PageBlobService   | ContainerClient   | ContainerClient   |
| AppendBlobService |  BlobClient       | BlobClient        | 
|                   |                   |                   |   

## Version <= 2.X to Version 12 API Mapping

<table border="1" cellspacing="0" cellpadding="0">
    <tbody>
        <tr>
            <td width="353" colspan="2" valign="top">
                <p align="right">
                    Version &lt;= 2.X
                </p>
            </td>
            <td width="270" colspan="2" valign="top">
                <p align="right">
                    Version 12.X
                </p>
            </td>
        </tr>
        <tr>
            <td width="353" colspan="2" valign="top">
                <p align="right">
                    Note: Any class means any of BlockBlobService,
                    AppendBlobService or PageBlobService class.
                </p>
            </td>
            <td width="270" colspan="2" valign="top">
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    API Name
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Class(es) it belongs to
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    API Name
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    Class(es) it belongs to
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    make_blob_url
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    It’s an attribute on BlobClient, you can instantiate a
                    BlobClient and call blob_client.url to get the url.
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    make_container_url
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    It’s an attribute on ContainerClient, you can instantiate a
                    ContainerClient and call container_client.url to get the url.
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    generate_account_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    generate_account_sas
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    It’s not a class method.
                </p>
                <p align="right">
                    Just import from azure.storage.blob directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    generate_container_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    generate_container_sas
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    It’s not a class method.
                </p>
                <p align="right">
                    Just import from azure.storage.blob directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    generate_blob_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    generate_blob_sas
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    It’s not a class method.
                </p>
                <p align="right">
                    Just import from azure.storage.blob directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_user_delegation_key
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_user_delegation_key
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_service_stats
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_service_stats
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_blob_service_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_service_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_service_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_service_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_account_information
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_account_information
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobServiceClient, ContainerClient or BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_containers
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    list_containers
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_container
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_container
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobServiceClient or ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_container_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" rowspan="2" valign="top">
                <p align="right">
                    get_container_properties
                </p>
            </td>
            <td width="107" rowspan="2" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_container_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_container_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_container_metadata
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_container_acl
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_container_access_policy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_container_acl
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_container_access_policy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    delete_container
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_container
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    acquire_container_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    acquire_lease
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
                <p align="right">
                    or BlobLeaseClient obtained by calling acquire_lease.
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    renew_container_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    renew
                </p>
            </td>
            <td width="107" rowspan="4" valign="top">
                <p align="right">
                    BlobLeaseClient
                </p>
                <p align="right">
                    This client can be obtained by calling acquire_lease on
                    ContainerClient.
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    release_container_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    release
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    break_container_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    break
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    change_container_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    change
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_blobs
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    list_blobs
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_blob_names
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    We are considering adding it back.
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    N/A
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" rowspan="2" valign="top">
                <p align="right">
                    get_blob_properties
                </p>
            </td>
            <td width="107" rowspan="2" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_blob_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_http_headers
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_blob_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_blob_metadata
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    exists
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    exists
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_to_path
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" rowspan="4" valign="top">
                <p align="right">
                    download_blob
                </p>
            </td>
            <td width="107" rowspan="4" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_to_stream
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_to_bytes
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_blob_to_text
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    acquire_blob_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    acquire_lease
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
                <p align="right">
                    or BlobLeaseClient obtained by calling acquire_lease.
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    renew_blob_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    renew
                </p>
            </td>
            <td width="107" rowspan="4" valign="top">
                <p align="right">
                    BlobLeaseClient
                </p>
                <p align="right">
                    This client can be obtained by calling acquire_lease on
                    BlobClient.
                </p>
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    release_blob_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    release
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    break_blob_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    break
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    change_blob_lease
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    change
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    snapshot_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_snapshot
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    copy_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    start_copy_from_url
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    abort_copy_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    abort_copy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    delete_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_blob
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient or BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    batch_delete_blobs
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_blobs
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient.
                </p>
                <p align="right">
                    We will consider adding this api to BlobServiceClient if we
                    get any customer ask.
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    undelete_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Any class
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    undelete_blob
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    put_block
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    Stage_block
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    put_block_list
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    commit_block_list
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_block_list
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_block_list
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    put_block_from_url
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    stage_block_from_url
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_blob_from_path
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService or PageBlobService
                </p>
            </td>
            <td width="163" rowspan="8" valign="top">
                <p align="right">
                    upload_blob
                </p>
            </td>
            <td width="107" rowspan="8" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_blob_from_stream
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService or PageBlobService
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_blob_from_bytes
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService or PageBlobService
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_blob_from_text
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService or PageBlobService
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    append_blob_from_path
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    AppendBlobService
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    append_blob_from_bytes
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    AppendBlobService
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    append_blob_from_text
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    AppendBlobService
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    append_blob_from_stream
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    AppendBlobService
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_standard_blob_tier
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_standard_blob_tier
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    batch_set_standard_blob_tier
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    BlockBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_standard_blob_tier_blobs
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ContainerClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    AppendBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_append_blob
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    append_block
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    AppendBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    append_block
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    append_block_from_url
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    AppendBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    append_block_from_url
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_page_blob
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_premium_page_blob_tier
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_premium_page_blob_tier
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    incremental_copy_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    start_copy_from_url
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    update_page
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    upload_page
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    update_page_from_url
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    upload_pages_from_url
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    clear_page
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    clear_page
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_page_ranges
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" rowspan="2" valign="top">
                <p align="right">
                    get_page_ranges
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_page_ranges_diff
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_sequence_number
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_sequence_number
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    resize_blob
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    PageBlobService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    resize_blob
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    BlobClient
                </p>
            </td>
        </tr>
    </tbody>
</table>

## Build Client with Shared Key Credential
Instantiate client in Version 2.X
```python
from azure.storage.blob import BlockBlobService
service = BlockBlobService("<storage-account-name>", "<account-access-key>", endpoint_suffix="<endpoint_suffix>")
```

Initiate client in Version 12.
```python
from azure.storage.blob import BlobServiceClient

service = BlobServiceClient(account_url="https://<my-storage-account-name>.blob.core.windows.net/", credential={'account_name': "<storage-account-name>", 'account_key': "<account-access-key>"})
```

## Build Client with SAS token

In version 2.X, to generate the SAS token, you needed to instantiate any of `BlockBlobService`, `AppendBlobService` or `PageBlobService`, then use the class method to generate different level of sas.
```python
from azure.storage.blob import BlockBlobService
from azure.storage.common import (
    ResourceTypes,
    AccountPermissions,
)
from datetime import datetime, timedelta

service = BlockBlobService("<storage-account-name>", "<account-access-key>", endpoint_suffix="<endpoint_suffix>")
                        
token = service.generate_account_shared_access_signature(
    ResourceTypes.CONTAINER,
    AccountPermissions.READ,
    datetime.utcnow() + timedelta(hours=1),
)

# Create a service and use the SAS
sas_service = BlockBlobService(
    account_name="<storage-account-name>",
    sas_token=token,
)
```

In V12, SAS token generation is a standalone api, it's no longer a class method.
```python
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions

sas_token = generate_account_sas(
    account_name="<storage-account-name>",
    account_key="<account-access-key>",
    resource_types=ResourceTypes(service=True),
    permission=AccountSasPermissions(read=True),
    expiry=datetime.utcnow() + timedelta(hours=1)
)

blob_service_client = BlobServiceClient(account_url="https://<my_account_name>.blob.core.windows.net", credential=sas_token)
```

## Build Client with OAuth Credentials
V 2.X using oauth credential to instantiate a service client.
```python
from azure.storage.common import (
    TokenCredential,
)
import adal

context = adal.AuthenticationContext(
    str.format("{}/{}", "<active_directory_auth_endpoint>", "<active_directory_tenant_id>"),
    api_version=None, validate_authority=True)

token = context.acquire_token_with_client_credentials(
    "https://storage.azure.com",
    "<active_directory_application_id>",
    "<active_directory_application_secret>")["accessToken"]
token_credential = TokenCredential(token)

service = BlockBlobService("<storage_account_name>", token_credential=token_credential)
```

In V12, you can leverage azure-identity package.
```python
from azure.identity import ClientSecretCredential
token_credential = ClientSecretCredential(
    "<active_directory_tenant_id>",
    "<active_directory_application_id>",
    "<active_directory_application_secret>"
)

# Instantiate a BlobServiceClient using a token credential
from azure.storage.blob import BlobServiceClient
blob_service_client = BlobServiceClient("https://<my-storage-account-name>.blob.core.windows.net", credential=token_credential)
```



## Download Blob
In V2.X, you can call `get_blob_to_stream`, `get_blob_to_path`, `get_blob_to_bytes`, `get_blob_to_text`. These APIs return
a Blob object.
Here's an example of `get_blob_to_text`.
```python
from azure.storage.blob import BlockBlobService
service = BlockBlobService("<storage-account-name>", "<account-access-key>", endpoint_suffix="<endpoint_suffix>")
blob_object = service.get_blob_to_text("<container_name>", "<blob_name>")
text_content = blob_object.content
```

In V12, the download operation can be done through the download_blob API.
Here's the equivalent of `get_blob_to_text`.
```python
from azure.storage.blob import BlobServiceClient
service_client = BlobServiceClient(account_url="https://<my-storage-account-name>.blob.core.windows.net/", credential={'account_name': "<storage-account-name>", 'account_key': "<account-access-key>"})
blob_client = service_client.get_blob_client("<container_name>", "<blob_name>")
stream_downloader = blob_client.download_blob(max_concurrency=2, encoding='UTF-8')
text_content = stream_downloader.readall()
```
