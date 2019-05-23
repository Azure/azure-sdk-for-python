# Azure Storage Python SDK


## Shared Key Credentials
```python
azure.storage.blob.SharedKeyCredentials(account_name, account_key)
```

## BlobServiceClient API
```python
azure.storage.blob.BlobServiceClient(account_url, credentials=None, configuration=None)

# Instantiate from a connection string
azure.storage.blob.BlobServiceClient.from_connection_string(connection_str, configuration=None)

BlobServiceClient.make_url(protocol=None, sas_token=None)

BlobServiceClient.generate_shared_access_signature(
    resource_types, permission, expiry, start=None, ip=None, protocol=None)

# Returns dict of account information (SKU and account type)
BlobServiceClient.get_account_information(timeout=None)

# Returns ServiceStats 
BlobServiceClient.get_service_stats(timeout=None)

# Returns ServiceProperties
BlobServiceClient.get_service_properties(timeout=None)

# Returns None
BlobServiceClient.set_service_properties(
    logging=None, hour_metrics=None, minute_metrics=None, cors=None, target_version=None, timeout=None, delete_retention_policy=None, static_website=None)

# Returns a generator of container objects - with names, properties, etc
BlobServiceClient.list_container_properties(starts_with=None, include_metadata=False, timeout=None)

# Returns a ContainerClient
BlobServiceClient.get_container_client(container)

# Returns a BlobClient
BlobServiceClient.get_blob_client(container, blob, blob_type=BlobType.BlockBlob)
```

## ContainerClient API
```python
azure.storage.blob.ContainerClient(
    url, container=None, credentials=None, configuration=None)

# Instantiate from a connection string
azure.storage.blob.ContainerClient.from_connection_string(connection_str, container, configuration=None)

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
ContainerClient.get_container_properties(lease=None, timeout=None)

# Returns metadata as dict
ContainerClient.get_container_metadata(lease=None, timeout=None)

# Returns container-updated property dict (Etag and last modified)
ContainerClient.set_container_metadata(metadata=None, lease=None, if_modified_since=None, timeout=None)

# Returns access policies as a dict
ContainerClient.get_container_acl(lease=None, timeout=None)

# Returns container-updated property dict (Etag and last modified)
ContainerClient.set_container_acl(
    signed_identifiers=None, public_access=None lease=None, if_modified_since=None, if_unmodified_since=None, timeout=None)

# Returns a iterable (auto-paging) response of BlobProperties
ContainerClient.list_blob_properties(starts_with=None, include=None, timeout=None)

# Returns a BlobClient
ContainerClient.get_blob_client(blob, blob_type=BlobType.BlockBlob, snapshot=None)
```

## BlobClient API
```python
azure.storage.blob.BlobClient(
    url, container=None, blob=None, snapshot=None, blob_type=BlobType.BlockBlob, credentials=None configuration=None)

# Instantiate from a connection string
azure.storage.blob.BlobClient.from_connection_string(connection_str, container, blob, configuration=None)

BlobClient.make_url(protocol=None, sas_token=None)

BlobClient.generate_shared_access_signature(
    resource_types, permission, expiry, start=None, ip=None, protocol=None)

# By default, uploads as a BlockBlob, unless alternative blob_type is specified.
# Returns a BlobClient
BlobClient.upload_blob(
    data,
    length=None,
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

# Only works where type is PageBlob or AppendBlob, otherwise raises TypeError
# Returns blob-updated property dict (Etag and last modified)
BlobClient.create_blob(
    content_length=None, content_settings=None, sequence_number=None, metadata=None, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None, premium_page_blob_tier=None)

# Returns snapshot properties
BlobClient.create_snapshot(
    metadata=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, lease=None, timeout=None)

# Returns a CopyStatusPoller object to wait on the operation, check operation status and abort
BlobClient.copy_blob_from_source(
    source_url,
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

# Only works where type is BlockBlob, otherwise raises TypeError
# Returns None
BlobClient.set_standard_blob_tier(standard_blob_tier, timeout=None)

# Only works where type is BlockBlob, otherwise raises TypeError
# Returns None
BlobClient.stage_block(
    block_id, data, validate_content=False, lease=None, timeout=None)

# Only works where type is BlockBlob, otherwise raises TypeError
# Returns None
BlobClient.stage_block_from_url(
    block_id, copy_source_url, source_range_start, source_range_end, source_content_md5=None, lease=None, timeout=None)

# Only works where type is BlockBlob, otherwise raises TypeError
# Returns a tuple of two sets - committed and uncommitted blocks
BlobClient.get_block_list(
    block_list_type=None, snapshot=None, lease=None, timeout=None)

# Only works where type is BlockBlob, otherwise raises TypeError
# Returns blob-updated property dict (Etag and last modified)
BlobClient.commit_block_list(
    block_list, lease=None, content_settings=None, metadata=None, validate_content=False, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises TypeError
# Returns None
BlobClient.set_premium_page_blob_tier(premium_page_blob_tier, timeout=None)

# Only works where type is PageBlob, otherwise raises TypeError
# Returns a list of page ranges
BlobClient.get_page_ranges(
    start_range=None, end_range=None, snapshot=None, lease=None, previous_snapshot_diff=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises TypeError
# Returns blob-updated property dict (Etag and last modified)
BlobClient.set_sequence_number(
    sequence_number_action, sequence_number=None, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises TypeError
# Returns blob-updated property dict (Etag and last modified)
BlobClient.resize_blob(
    content_length, lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises TypeError
# Returns blob-updated property dict (Etag and last modified)
BlobClient.upload_page(
    page, start_range, end_range, lease=None, validate_content=False, if_sequence_number_lte=None, if_sequence_number_lt=None, if_sequence_number_eq=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises TypeError
# Returns blob-updated property dict (Etag and last modified)
BlobClient.clear_page(
    start_range, end_range, lease=None, if_sequence_number_lte=None, if_sequence_number_lt=None, if_sequence_number_eq=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

# Only works where type is PageBlob, otherwise raises TypeError
# Returns a pollable object to check operation status and abort
BlobClient.incremental_copy(
    copy_source, metadata=None, destination_if_modified_since=None, destination_if_unmodified_since=None, destination_if_match=None, destination_if_none_match=None, destination_lease=None, source_lease=None, timeout=None):

# Only works where type is AppendBlob, otherwise raises TypeError
# Returns blob-updated property dict (Etag, last modified, append offset, committed block count)
BlobClient.append_block(
    data, validate_content=False, maxsize_condition=None, appendpos_condition=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)
```

## CopyStatusPoller
```python
# Returns operation status
CopyStatusPoller.status()

# Blocks until operation completes
CopyStatusPoller.wait()

# Blocks until operation completes, then returns BlobProperties of copied blob.
CopyStatusPoller.result()

# Aborts the copy operation if in progress.
CopyStatusPoller.abort()
```

## Lease
```python
BlobStorageLease.renew(
    if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

BlobStorageLease.release(if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

BlobStorageLease.change(
    proposed_lease_id, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None)

```
