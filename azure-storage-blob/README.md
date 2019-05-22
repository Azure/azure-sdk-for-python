# Azure Storage Python SDK


## BlobServiceClient API
```python
azure.storage.blob.BlobServiceClient(uri, credentials=None, configuration=None)

BlobServiceClient.make_url(protocol=None, sas_token=None)

BlobServiceClient.generate_shared_access_signature(
    resource_types, permission, expiry, start=None, ip=None, protocol=None)

# Returns dict of account information (SKU and account type)
BlobServiceClient.get_account_information(timeout=None)

# Returns ServiceStats 
BlobServiceClient.get_service_stats(timeout=None)

# Returns ServiceProperties (or dict?)
BlobServiceClient.get_service_properties(timeout=None)

# Returns None
BlobServiceClient.set_service_properties(
    logging=None, hour_metrics=None, minute_metrics=None, cors=None, target_version=None, timeout=None, delete_retention_policy=None, static_website=None)

# Returns a generator of container objects - with names, properties, etc
BlobServiceClient.list_container_properties(
    prefix=None, num_results=None, include_metadata=False, marker=None, timeout=None)

# Returns a ContainerClient
BlobServiceClient.get_container_client(container, snaphot=None)
```

## ContainerClient API
```python
azure.storage.blob.ContainerClient(
    uri, credentials=None, container_name=None, configuration=None,
    protocol=DEFAULT_PROTOCOL, endpoint_suffix=SERVICE_HOST_BASE, custom_domain=None)


ContainerClient.make_url(protocol=None, sas_token=None)

ContainerClient.generate_shared_access_signature(
    resource_types, permission, expiry, start=None, ip=None, protocol=None)

# Returns None
ContainerClient.create_container(
    metadata=None, public_access=None, timeout=None)

# Returns None
ContainerClient.delete_container(
    lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Returns a Lease object, that can be run in a context manager
ContainerClient.acquire_lease(
    lease_duration=-1,
    proposed_lease_id=None,
    if_modified_since=None,
    if_unmodified_since=None,
    if_match=None,
    if_none_match=None, timeout=None)

# Returns approximate time remaining in the lease period, in seconds
ContainerClient.break_lease(
    lease_break_period=None,
    if_modified_since=None,
    if_unmodified_since=None,
    if_match=None,
    if_none_match=None, timeout=None)

# Returns dict of account information (SKU and account type)
ContainerClient.get_account_infomation(timeout=None)

# Returns ContainerProperties
ContainerClient.get_container_properties(container, lease=None, timeout=None)

# Returns metadata as dict
ContainerClient.get_container_metadata(container, lease=None, timeout=None)

# Returns container-updated property dict (Etag and last modified)
ContainerClient.set_container_metadata(container, metadata=None, lease=None, if_modified_since=None, timeout=None)

# Returns access policies as a dict
ContainerClient.get_container_acl(container, lease=None, timeout=None)

# Returns container-updated property dict (Etag and last modified)
ContainerClient.set_container_acl(
    container, signed_identifiers=None, public_access=None lease=None, if_modified_since=None, if_unmodified_since=None, timeout=None)

# Returns a iterable (auto-paging) response of BlobProperties
ContainerClient.list_blob_properties(prefix=None, include=None, timeout=None)

# Returns a generator that honors directory hierarchy 
ContainerClient.walk_blob_propertes(prefix=None, include=None, delimiter="/", timeout=None)

# Blob type enum
azure.storage.blob.BlobType.BlockBlob
azure.storage.blob.BlobType.PageBlob
azure.storage.blob.BlobType.AppendBlob

# Returns a BlobClient
ContainerClient.get_blob_client(blob, blob_type=BlobType.BlockBlob, snapshot=None)
```

## BlobClient API
```python
azure.storage.blob.BlobClient(
    uri, blob_type=BlobType.BlockBlob, credentials=None, container_name=None, blob_name=None, snapshot=None, configuration=None)


BlobClient.make_url(protocol=None, sas_token=None)

BlobClient.generate_shared_access_signature(
    resource_types, permission, expiry, start=None, ip=None, protocol=None)

# By default, uploads as a BlockBlob, unless alternative blob_type is specified.
# Returns a BlobClient
BlobClient.upload_blob(
    data,
    length=None,
    blob_type=BlobType.BlockBlob,
    metadata=None,
    content_settings=None,
    validate_content=False,
    lease=None,
    if_modified_since=None,
    if_unmodified_since=None,
    if_match=None,
    if_none_match=None,
    timeout=None,
    premium_page_blob_tier=None,  # Page only
    sequence_number=None  # Page only
    maxsize_condition=None,  # Append only
    appendpos_condition=None)  # Append only

# Returns a data generator (stream)
BlobClient.download_blob(
    offset=None, length=None, validate_content=False, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Returns None
BlobClient.delete_blob(
    lease=None, delete_snapshots=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Returns None
BlobClient.undelete_blob(timeout=None)

# Returns BlobProperties
BlobClient.get_blob_properties(
    lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Returns blob-updated property dict (Etag and last modified)
BlobClient.set_blob_properties(
    content_settings=None, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Returns a dict of metadata
BlobClient.get_blob_metadata(
    lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Returns blob-updated property dict (Etag and last modified)
BlobClient.set_blob_metadata(
    metadata=None, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Returns snapshot properties
BlobClient.create_snapshot(
    metadata=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, lease=None, timeout=None)

# Returns a pollable object to check operation status and abort
BlobClient.copy_blob_from_source(
    copy_source,
    metadata=None,
    source_if_modified_since=None,
    source_if_unmodified_since=None,
    source_if_match=None,
    source_if_none_match=None,
    destination_if_modified_since=None,
    destination_if_unmodified_since=None,
    destination_if_match=None,
    destination_if_none_match=None,
    destination_lease=None,
    source_lease=None,
    timeout=None,
    premium_page_blob_tier=None,  # Page only
    requires_sync=None)  # Block only

# Returns a Lease object, that can be run in a context manager
BlobClient.acquire_lease(
    lease_duration=-1,
    proposed_lease_id=None,
    if_modified_since=None,
    if_unmodified_since=None,
    if_match=None,
    if_none_match=None, timeout=None)

# Returns approximate time remaining in the lease period, in seconds
BlobClient.break_lease(
    lease_break_period=None,
    if_modified_since=None,
    if_unmodified_since=None,
    if_match=None,
    if_none_match=None, timeout=None)

# Only works where type is BlockBlob, otherwise raises InvalidOperation
# Returns None
BlobClient.set_standard_blob_tier(standard_blob_tier, timeout=None)

# Only works where type is BlockBlob, otherwise raises InvalidOperation
# Returns None
BlobClient.stage_block(
    block_id, data, validate_content=False, lease=None, timeout=None)

# Only works where type is BlockBlob, otherwise raises InvalidOperation
# Returns None
BlobClient.stage_block_from_url(
    block_id, copy_source_url, source_range_start, source_range_end, source_content_md5=None, lease=None, timeout=None)

# Only works where type is BlockBlob, otherwise raises InvalidOperation
# Returns a tuple of two sets - committed and uncommitted blocks
BlobClient.get_block_list(
    block_list_type=None, snapshot=None, lease=None, timeout=None)

# Only works where type is BlockBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag and last modified)
BlobClient.commit_block_list(
    block_list, lease=None, content_settings=None, metadata=None, validate_content=False, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns None
BlobClient.set_premium_page_blob_tier(premium_page_blob_tier, timeout=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag and last modified)
BlobClient.create_pageblob(
    content_length, content_settings=None, sequence_number=None, metadata=None, lease_id=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None, premium_page_blob_tier=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns a list of page ranges
BlobClient.get_page_ranges(
    start_range=None, end_range=None, snapshot=None, lease=None, previous_snapshot_diff=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag and last modified)
BlobClient.set_sequence_number(
    sequence_number_action, sequence_number=None, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag and last modified)
BlobClient.resize_blob(
    content_length, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag and last modified)
BlobClient.update_page(
    page, start_range, end_range, lease=None, validate_content=False, if_sequence_number_lte=None, if_sequence_number_lt=None, if_sequence_number_eq=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag and last modified)
BlobClient.clear_page(
    start_range, end_range, lease=None, if_sequence_number_lte=None, if_sequence_number_lt=None, if_sequence_number_eq=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises InvalidOperation
# Returns a pollable object to check operation status and abort
BlobClient.incremental_copy(
    copy_source, metadata=None, destination_if_modified_since=None, destination_if_unmodified_since=None, destination_if_match=None, destination_if_none_match=None, destination_lease=None, source_lease=None, timeout=None):

# Only works where type is AppendBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag and last modified)
BlobClient.create_appendblob(
    content_settings=None, metadata=None, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is AppendBlob, otherwise raises InvalidOperation
# Returns blob-updated property dict (Etag, last modified, append offset, committed block count)
BlobClient.append_block(
    data, validate_content=False, maxsize_condition=None, appendpos_condition=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)
```

## Lease
```python
BlobStorageLease.renew(
    if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

BlobStorageLease.release(if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

BlobStorageLease.change(
    proposed_lease_id, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

```
