import json
import zlib

MAX_CHUNK_SIZE = 1000000
CHAR_SIZE = 4

def _split_chunks(logs):
    chunks = []
    chunk_size = 0
    curr_chunk = []
    for log in logs:
        # each char is 4 bytes
        size = len(json.dumps(log)) * CHAR_SIZE
        if chunk_size + size < MAX_CHUNK_SIZE:
            curr_chunk.append(log)
            chunk_size += size
        else:
            chunks.append(curr_chunk)
            curr_chunk = [log]
            chunk_size = 0
    if len(curr_chunk) > 0:
        chunks.append(curr_chunk)
    return chunks

def _create_gzip_requests(logs):
    requests = []
    chunks = _split_chunks(logs)
    for chunk in chunks:
        zlib_mode = 16 + zlib.MAX_WBITS # for gzip encoding
        _compress = zlib.compressobj(wbits=zlib_mode)
        data = _compress.compress(bytes(json.dumps(chunk), encoding='utf-8'))
        data += _compress.flush()
        requests.append(data)
    return requests
