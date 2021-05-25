import zlib

def _decompress_body(body, enc):
    zlib_mode = 16 + zlib.MAX_WBITS if enc == "gzip" else zlib.MAX_WBITS
    decompressor = zlib.decompressobj(wbits=zlib_mode)
    return decompressor.decompress(body)


def _compress_body(body, enc):
    zlib_mode = 16 + zlib.MAX_WBITS if enc == "gzip" else zlib.MAX_WBITS
    compressor = zlib.compressobj(wbits=zlib_mode)
    return compressor.compress(body)
