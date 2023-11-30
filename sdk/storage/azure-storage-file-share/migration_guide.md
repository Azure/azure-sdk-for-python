# Storage File Share Service SDK Migration Guide from <= 2.x to 12.x

In this section, we list the main changes you need to be aware of when converting your Storage Queue SDK library from version <= 2.X to version 12.X.
In version 12 we also support asynchronous APIs.

## Converting Core Classes
<= 2.X synchronous classes have been replaced. Some functionality has been split into separate clients for more logical organization.

| <= 2.X Classes (Clients)  | V12 Clients | NEW Asynchronous clients |
|---:|---:|---:|
| FileService (account-level operations) | ShareServiceClient | aio.ShareServiceClient |
| FileService (share-level operations) | ShareClient | aio.ShareClient |
| FileService (directory-level operations) | ShareDirectoryClient | aio.ShareDirectoryClient |
| FileService (file-level operations) | ShareFileClient | aio.ShareFileClient |

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
                    generate_account_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
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
                    Just import from azure.storage.fileshare directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    generate_share_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    generate_share_sas
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    It’s not a class method.
                </p>
                <p align="right">
                    Just import from azure.storage.fileshare directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    generate_file_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    generate_file_sas
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    It’s not a class method.
                </p>
                <p align="right">
                    Just import from azure.storage.fileshare directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    make_file_url
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                Url (property)
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareServiceClient or ShareDirectoryClient or ShareFileClient or ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_file_service_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_service_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_file_service_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_service_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_shares
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    list_shares
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_share
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_share
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareServiceClient or ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    snapshot_share
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_snapshot
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_share_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_share_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_share_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_share_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_share_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_share_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_share_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_share_metadata
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_share_acl
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_share_access_policy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_share_acl
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_share_access_policy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_share_stats
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_share_stats
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_share_stats_in_bytes
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    N/A
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
                    delete_share
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_share
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareServiceClient or ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_directory
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_directory
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient or ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_directory_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_http_headers
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    delete_directory
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_directory
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient or ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_directory_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_directory_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_directory_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_directory_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_directory_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_directory_metadata
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_directories_and_files
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    list_directories_and_files
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient or ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_handles
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    list_handles
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient or ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    close_handles
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    close_all_handles
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient or ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_file_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_file_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
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
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    exists
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareDirectoryClient (not currently supported on any other clients)
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    resize_file
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    resize_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_file_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_http_headers
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_file_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_file_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    FileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_file_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_file_metadata
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    copy_file
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    start_copy_from_url
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    abort_copy_file
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    abort_copy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    delete_file
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_file
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_file_from_path
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_file_to_path
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    download_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_file_to_stream
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    download_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_file_to_bytes
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    download_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_file_to_text
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    download_file
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    update_range
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    upload_range
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    update_range_from_file_url
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    upload_range_from_url
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    clear_range
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    clear_range
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_ranges
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_ranges
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareFileClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_permission_for_share
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_permission_for_share
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_permission_for_share
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    FileService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_permission_for_share
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    ShareClient
                </p>
            </td>
        </tr>
    </tbody>
</table>
Please note that while some API functionality does not have a 1-1 mapping, the new Track2 File Share Service adds a lot of new functionality and some old functionality may still be possible, but simply presented in a different manner.

## Build Client with Shared Key Credential
Instantiate client in Version 2.X
```python
from azure.storage.file import FileService
service = FileService("<storage-account-name>", "<account-access-key>", endpoint_suffix="<endpoint_suffix>")
```

Instantiate client in Version 12 and use higher-level clients to obtain lower-level clients.
```python
from azure.storage.fileshare import ShareServiceClient, ShareClient, ShareDirectoryClient, ShareFileClient

# Get ShareServiceClient (for account-level operations)
service_client = ShareServiceClient(account_url="https://<my-storage-account-name>.file.core.windows.net/", credential={'account_name': "<storage-account-name>", 'account_key': "<account-access-key>"})

# Get ShareClient (for share-specific operations OR alternatively use constructor directly)
share_client = service_client.get_share_client(share="<share_name>")

# Get ShareDirectoryClient and ShareFileClient (OR alternatively use constructor directly)
directory_client = share_client.get_directory_client("<directory_path>")
file_client = share_client.get_file_client("<file_path>")

```

## Build Client with SAS token

In version 2.X, to generate the SAS token, you needed to instantiate `FileService`, then use the class method to generate the sas token.
```python
from azure.storage.file import FileService
from azure.storage.common import (
    ResourceTypes,
    AccountPermissions,
)
from datetime import datetime, timedelta

service = FileService("<storage-account-name>", "<account-access-key>", endpoint_suffix="<endpoint_suffix>")
                        
token = service.generate_account_shared_access_signature(
    ResourceTypes.CONTAINER,
    AccountPermissions.READ,
    datetime.utcnow() + timedelta(hours=1),
)

# Create a service and use the SAS
sas_service = FileService(
    account_name="<storage-account-name>",
    sas_token=token,
)
```

In V12, SAS token generation is a standalone api, it's no longer a class method.
```python
from datetime import datetime, timedelta
from azure.storage.fileshare import ShareServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions

sas_token = generate_account_sas(
    account_name="<storage-account-name>",
    account_key="<account-access-key>",
    resource_types=ResourceTypes(service=True),
    permission=AccountSasPermissions(read=True),
    expiry=datetime.utcnow() + timedelta(hours=1)
)

share_service_client = ShareServiceClient(account_url="https://<my_account_name>.file.core.windows.net", credential=sas_token)
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

service = FileService("<storage_account_name>", token_credential=token_credential)
```

In V12, you can leverage the azure-identity package.
```python
from azure.identity import DefaultAzureCredential
token_credential = DefaultAzureCredential()

# Instantiate a ShareServiceClient using a token credential
from azure.storage.fileshare import ShareServiceClient
share_service_client = ShareServiceClient("https://<my-storage-account-name>.file.core.windows.net", credential=token_credential)
```
