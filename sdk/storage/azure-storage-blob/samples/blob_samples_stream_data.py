import gzip

from azure.storage.blob import BlobClient, BlobBlock
import uuid

key = '<account key>' # You can also use the connection string and then invoke BlobClient.from_connection_string()

# These sizes are essentially equivalent to the size of your stream's buffer.
max_chunk_get_size = 4 * 1024 * 1024            # 4MB
max_single_get_size = 4 * 1024 * 1024
def stream_gzip():
    """ Function will stream the download of a blob,
        gzip its contents, then stream the upload.
    """
    # The blob to download data from.
    source_blob_client = BlobClient(account_url='https://private.blob.core.windows.net',
                                    container_name='your_container', # example: mycompany-datalake
                                    blob_name='your_blob_path',      # example: path/to/file/in/mycompany-datalake
                                    credential=key,
                                    max_chunk_get_size=max_chunk_get_size,  # the size of chunk is 4M
                                    max_single_get_size=max_single_get_size)
    
    # The blob uploading to.
    destination_blob_client = BlobClient(account_url='https://<account name>.blob.core.windows.net',
                                         container_name='other_container',
                                         blob_name='other_blob_path',
                                         credential=key)
    
    # This returns a StorageStreamDownloader.
    stream = source_blob_client.download_blob()
    block_list = []
    
    # read data in chunk
    for chunk in stream.chunks():
        # process your data (anything can be done here really. `chunk` is a byte array).
        data = gzip.compress(chunk)
        
        # use the put block rest api to upload the chunk to azure storage
        block_id = str(uuid.uuid4())
        destination_blob_client.stage_block(block_id=block_id, data=data)
        block_list.append(BlobBlock(block_id=block_id))
    
    # use the put block list rest api to upload the whole chunk to azure storage and make up one blob
    destination_blob_client.commit_block_list(block_list)
